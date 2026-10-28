"""Write one fresh, deterministic dbt project; own materialization and hooks."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import tempfile

from .mapping import ConversionError, Export, ModelArtifact, PlanningResult, TargetOutcome
from .sql import generate


def json_text(value) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def compile_models(planning: PlanningResult) -> tuple[dict, dict]:
    artifacts, outcomes = {}, dict(planning.outcomes)
    names = {key: plan.model_name for key, plan in planning.plans.items()}

    def emit(key):
        if key in artifacts or key in outcomes:
            return
        plan = planning.plans[key]
        for dependency in plan.dependencies:
            emit(dependency)
        failed = [dependency for dependency in plan.dependencies if dependency not in artifacts]
        if failed:
            outcomes[key] = TargetOutcome(key, "blocked", "Failed producer(s): " + ", ".join(map(str, failed)), plan.dependencies)
            return
        try:
            artifacts[key] = generate(plan, names)
            outcomes[key] = TargetOutcome(key, "emitted", "SQL generated; result verification is separate", plan.dependencies, f"models/{plan.model_name}.sql")
        except ConversionError as exc:
            outcomes[key] = TargetOutcome(key, exc.status, str(exc), plan.dependencies)

    for key in sorted(planning.plans):
        emit(key)
    return artifacts, outcomes


_CLEAR_MACRO = """{% macro pwc_clear(relation) %}
  {% if execute %}
    {% set existing = adapter.get_relation(database=relation.database, schema=relation.schema, identifier=relation.identifier) %}
    {% if existing is not none %}
      {% if existing.type != 'table' %}
        {{ exceptions.raise_compiler_error('PWC cleanup needs a table: ' ~ relation) }}
      {% endif %}
      {{ log('PWC_CLEAR ' ~ relation ~ ' action=delete', info=True) }}
      {{ return('delete from ' ~ relation) }}
    {% endif %}
    {{ log('PWC_CLEAR ' ~ relation ~ ' action=absent', info=True) }}
  {% endif %}
  {{ return('select 1') }}
{% endmacro %}
"""
_SCHEMA_MACRO = """{% macro generate_schema_name(custom_schema_name, node) -%}
  {{ custom_schema_name | trim if custom_schema_name is not none else target.schema }}
{%- endmacro %}
"""


def _model(artifact: ModelArtifact) -> str:
    config = {"materialized": "table", "alias": artifact.plan.alias, "schema": artifact.plan.schema}
    if artifact.plan.preparations:
        config["pre_hook"] = ["{{ pwc_clear(this) }}" for _ in artifact.plan.preparations]
    args = ", ".join(f"{key}={json.dumps(value)}" for key, value in config.items())
    return "{{ config(" + args + ") }}\n\n" + artifact.sql


def write_project(destination: str | Path, export: Export, planning: PlanningResult,
                  artifacts: dict, outcomes: dict, *, report: dict | None = None) -> dict:
    destination = Path(destination).absolute()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ConversionError("error", f"Destination must be absent or empty: {destination}")
    files = {
        "dbt_project.yml": json_text({"name": "powercenter_converted", "version": "1.0.0", "config-version": 2,
                                      "profile": "powercenter_converted", "model-paths": ["models"], "macro-paths": ["macros"],
                                      "clean-targets": ["target", "dbt_packages"]}),
        "profiles.yml": "powercenter_converted:\n  target: local\n  outputs:\n    local:\n      type: duckdb\n      path: \"{{ env_var('PWC_DUCKDB_PATH', 'converter.duckdb') }}\"\n      schema: converted\n      threads: 1\n",
        "macros/pwc_clear.sql": _CLEAR_MACRO,
        "macros/generate_schema_name.sql": _SCHEMA_MACRO,
        ".gitignore": "target/\nlogs/\ndbt_packages/\n*.duckdb\n*.duckdb.wal\n.user.yml\n",
    }
    external = {}
    for artifact in artifacts.values():
        files[f"models/{artifact.plan.model_name}.sql"] = _model(artifact)
        for source in artifact.plan.sources:
            if source.producer is None:
                external[source.source_name] = {"name": source.source_name, "schema": source.relation.schema or "main",
                                                "tables": [{"name": source.table_name, "identifier": source.relation.table,
                                                            "quoting": {"identifier": True}}],
                                                "quoting": {"schema": True, "identifier": True}}
    files["models/sources.yml"] = json_text({"version": 2, "sources": [external[name] for name in sorted(external)]})
    outcome_rows = []
    for key, outcome in sorted(outcomes.items()):
        row = {"target": str(key), "status": outcome.status, "reason": outcome.reason,
               "dependencies": list(map(str, outcome.dependencies)), "artifact": outcome.artifact,
               "requested": key in planning.selected}
        if key in artifacts:
            artifact = artifacts[key]
            row.update({"model_name": artifact.plan.model_name, "alias": artifact.plan.alias, "schema": artifact.plan.schema,
                        "columns": [{"name": p.name, "datatype": asdict(p.datatype)} for p in artifact.plan.columns],
                        "preparations": [{"operation": intent.operation, "original_relation": asdict(intent.original_relation),
                                          "origin": intent.origin} for intent in artifact.plan.preparations],
                        "required_sort": list(artifact.required_sort)})
        outcome_rows.append(row)
    manifest = {"format_version": 1, "input_sha256": export.sha256, "export_metadata": export.metadata,
                "outcomes": outcome_rows,
                "inventory": [{"target": str(key), "selection": "included" if key in outcomes else "unselected"} for key in planning.inventory],
                "unconverted_workflow_commands": list(export.unconverted_commands),
                "verification": "emission only; execution and result equivalence require separate tests"}
    files["conversion-manifest.json"] = json_text(manifest)
    if report is not None:
        files["fivetran-source-report.json"] = json_text(report)
    files["README.md"] = ("# Generated DuckDB dbt project\n\nSupply the declared external input tables, then run from this directory:\n\n"
                           "```sh\ndbt run --project-dir . --profiles-dir .\n```\n\n"
                           "Set PWC_DUCKDB_PATH to an absolute local DuckDB file if needed. Input tables use their exported schema/table names. "
                           "See conversion-manifest.json for exact outcomes, preparation metadata and unselected inventory. "
                           "Emission does not establish source-runtime equivalence.\n")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".pwc-project-", dir=destination.parent))
    try:
        for name, value in sorted(files.items()):
            path = temporary / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8", newline="\n")
        # Recheck immediately before publishing; never mix a run into old files.
        if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
            raise ConversionError("error", f"Destination became nonempty: {destination}")
        os.replace(temporary, destination)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return manifest
