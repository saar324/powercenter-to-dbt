"""Whole-export migration facts and a bounded, offline connector catalogue.

Catalogue availability is a technology candidate, never client compatibility.
No target graph traversal, SQL generation, database or network access occurs here.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import json

from .dependencies import resolve_configuration
from .mapping import ConversionError, Export


CATALOGUE = {
    "identity": "fivetran-databases-bounded-v1",
    "review_date": "2026-10-28",
    "source_url": "https://fivetran.com/docs/connectors/databases",
    "scope": "Oracle, PostgreSQL, MySQL and SQL Server only; not an exhaustive vendor catalogue",
    "entries": [
        {"technology": "Oracle", "aliases": ["oracle"],
         "source_url": "https://fivetran.com/docs/connectors/databases/oracle/oracle-connector",
         "limits": ["Tables and materialized views; regular views are excluded"]},
        {"technology": "PostgreSQL", "aliases": ["postgresql", "postgres"],
         "source_url": "https://fivetran.com/docs/connectors/databases/postgresql", "limits": []},
        {"technology": "MySQL", "aliases": ["mysql"],
         "source_url": "https://fivetran.com/docs/connectors/databases/mysql", "limits": []},
        {"technology": "SQL Server", "aliases": ["sql server", "microsoft sql server", "mssql"],
         "source_url": "https://fivetran.com/docs/connectors/databases/sql-server", "limits": []},
    ],
}
CHECKS = ["database version and service", "object types", "permissions", "networking",
          "replication settings", "plan", "destination support"]


def _missing_connection_fields(row):
    return [name for name, key in [("CONNECTIONNAME", "connection_name"),
            ("CONNECTIONSUBTYPE", "connection_subtype"), ("CONNECTIONTYPE", "connection_type")]
            if row[key] is None or not row[key].strip()]


def _canonical(value):
    if value is None or not value.strip():
        return None
    normalized = value.strip().casefold()
    return next((entry["technology"] for entry in CATALOGUE["entries"]
                 if normalized in entry["aliases"]), normalized)


def _connector(database_type, references):
    declared = _canonical(database_type)
    subtypes = {_canonical(row["connection_subtype"]) for row in references}
    subtypes.discard(None)
    conflicting = len(subtypes) > 1 or (declared is not None and any(value != declared for value in subtypes))
    technologies = {declared, *subtypes}
    candidates = [{"technology": entry["technology"], "source_url": entry["source_url"], "limits": list(entry["limits"])}
                  for entry in CATALOGUE["entries"] if entry["technology"] in technologies]
    status = "requires_review" if conflicting else "unknown" if declared is None else (
        "available" if any(entry["technology"] == declared for entry in CATALOGUE["entries"]) else "no_known_match")
    return {"status": status, "candidates": candidates,
            "client_compatibility": "not_verified", "existing_fivetran_configuration": "not_verified",
            "further_checks": list(CHECKS)}


def source_report(export: Export, config: dict | None = None, *, outcomes: dict | None = None) -> dict:
    """Report all definitions/uses, irrespective of selection or SQL support.

    ``outcomes=None`` means report-only: producer availability was not evaluated.
    An outcomes mapping must be the actual result of compile_models.
    """
    bindings, relations = resolve_configuration(export, config)
    for key, relation in relations.items():
        if (not isinstance(relation, dict) or set(relation) != {"schema", "table"}
                or not all(isinstance(value, str) and value for value in relation.values())):
            raise ConversionError("error", f"{key}: target_relations needs nonempty schema/table")
    connections = []
    for reference in export.reader_connections:
        row = asdict(reference)
        row["mapping"] = str(reference.mapping) if reference.mapping is not None else None
        row["source_uses"] = list(map(str, reference.source_uses))
        row["diagnostics"] = sorted(set(row["diagnostics"]) | {
            f"missing {name}" for name in _missing_connection_fields(row)})
        connections.append(row)
    connections.sort(key=lambda row: json.dumps(row, sort_keys=True))
    for index, row in enumerate(connections, 1):
        row["id"] = f"reader-{index:04d}"
    associations = []
    for association in export.source_associations:
        row = asdict(association)
        row["mapping"] = str(association.mapping)
        associations.append(row)
    associations.sort(key=lambda row: json.dumps(row, sort_keys=True))
    definitions = {definition.identity: definition for definition in export.source_definitions}
    uses = {identity: [] for identity in definitions}
    unresolved, all_uses = [], []
    for key, node in sorted(export.sources.items()):
        identity = (key.mapping.repository, key.mapping.folder, node.definition)
        producer = bindings.get(key)
        if producer is None:
            availability, outcome_status = "not_applicable", None
        elif outcomes is None:
            availability, outcome_status = "not_evaluated", None
        elif producer not in outcomes:
            availability, outcome_status = "unselected", None
        else:
            outcome_status = outcomes[producer].status
            availability = "emitted" if outcome_status == "emitted" else "failed_or_blocked"
        references = [row for row in connections if str(key) in row["source_uses"]]
        diagnostics = ["no associated reader connection references"] if not references else []
        if identity not in definitions:
            diagnostics.append("source definition reference is unresolved")
        if node.problem:
            diagnostics.append(node.problem)
        if producer is not None and availability == "failed_or_blocked":
            diagnostics.append(f"bound producer {producer}: {outcomes[producer].reason}")
        row = {"identity": str(key), "mapping": str(key.mapping), "instance": key.instance,
               "definition_reference": {"repository": identity[0], "folder": identity[1], "name": identity[2]},
               "classification": "unresolved" if identity not in definitions else "bound" if producer else "external",
               "producer": str(producer) if producer else None,
               "producer_availability": availability, "producer_outcome": outcome_status,
               "external_ingestion": "required" if producer is None and identity in definitions else "not_established",
               "connection_references": [reference["id"] for reference in references],
               "diagnostics": sorted(set(diagnostics))}
        all_uses.append(row)
        if identity in definitions:
            uses[identity].append(row)
        else:
            unresolved.append(row)
    rows = []
    for identity, definition in sorted(definitions.items()):
        definition_uses = uses[identity]
        classifications = {row["classification"] for row in definition_uses}
        classification = "unused" if not classifications else "mixed" if len(classifications) > 1 else next(iter(classifications))
        reference_ids = {identifier for use in definition_uses for identifier in use["connection_references"]}
        references = [row for row in connections if row["id"] in reference_ids]
        connector = _connector(definition.database_type, references)
        diagnostics = [f"missing {name}" for name, value in [("DATABASETYPE", definition.database_type),
                       ("OWNERNAME", definition.owner_name), ("DBDNAME", definition.database_name)]
                       if value is None or not value.strip()]
        if connector["status"] == "requires_review":
            diagnostics.append("technology declarations conflict")
        if len({row["connection_name"] for row in references if row["connection_name"]}) > 1:
            diagnostics.append("connection names differ across contexts; effective runtime connection is unresolved")
        if any(_missing_connection_fields(row) for row in references):
            diagnostics.append("associated reader connection declaration is incomplete")
        rows.append({"identity": {"repository": identity[0], "folder": identity[1], "name": identity[2]},
                     "metadata": {"NAME": definition.name, "DATABASETYPE": definition.database_type,
                                  "OWNERNAME": definition.owner_name, "DBDNAME": definition.database_name},
                     "classification": classification, "uses": definition_uses, "connector": connector,
                     "diagnostics": sorted(set(diagnostics))})
    return {"format_version": 1, "input_sha256": export.sha256, "scope": "whole_export",
            "catalogue": deepcopy(CATALOGUE), "source_definitions": rows, "unresolved_source_uses": unresolved,
            "source_associations": associations, "reader_connections": connections,
            "unassigned_reader_connections": [row["id"] for row in connections if not row["source_uses"]],
            "counts": {"source_definitions": len(rows), "source_uses": len(all_uses),
                       "unresolved_source_uses": len(unresolved),
                       "definitions_by_classification": dict(sorted(Counter(row["classification"] for row in rows).items())),
                       "uses_by_classification": dict(sorted(Counter(row["classification"] for row in all_uses).items())),
                       "definitions_by_connector_status": dict(sorted(Counter(row["connector"]["status"] for row in rows).items()))},
            "limits": ["Exported table and database names do not establish physical endpoints or runtime relations",
                       "Connection override precedence is not resolved; all exported contexts are retained",
                       "Producer emission does not establish field compatibility for every use or data availability",
                       "No client compatibility, live configuration or migration readiness is verified",
                       "No catalogue match does not establish vendor-wide absence"]}
