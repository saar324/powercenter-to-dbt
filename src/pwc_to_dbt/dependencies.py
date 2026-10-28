"""Resolve exact identities, validate consumed graphs, and plan model closure."""
import re
from collections import defaultdict
from dataclasses import replace

from .mapping import (ConversionError, Export, InstanceKey, ModelPlan, Node,
                      PlanningResult, PreparationIntent, Relation, SourcePlan,
                      TargetOutcome)


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9_]", "_", value.lower())
    return ("n_" + result) if not result or result[0].isdigit() else result


def _check_collisions(values: dict[InstanceKey, str], label: str) -> None:
    seen = {}
    for key, name in values.items():
        if name in seen:
            raise ConversionError("error", f"{label} collision: {seen[name]} and {key} -> {name}")
        seen[name] = key


def _resolve(value: str, choices: dict, label: str) -> InstanceKey:
    matches = [key for key in choices if str(key) == value]
    if len(matches) != 1:
        raise ConversionError("error", f"Unknown {label} identity {value!r}; use the full inventory identity")
    return matches[0]


def _compatible(source, target) -> bool:
    a, b = source.datatype, target.datatype
    if a.family != b.family:
        return False
    if a.family == "string":
        return b.precision >= a.precision
    if a.family in {"decimal", "number"}:
        return b.scale >= a.scale and b.precision - b.scale >= a.precision - a.scale
    return a == b


def _checked_nodes(mapping, target: Node) -> tuple[Node, ...]:
    incoming = defaultdict(list)
    for connection in mapping.connections:
        incoming[connection.to_instance].append(connection)
    visiting, visited, result = set(), set(), []

    def visit(name: str) -> None:
        if name in visiting:
            raise ConversionError("error", f"{target.key}: cycle at instance {name}")
        if name in visited:
            return
        node = mapping.nodes.get(name)
        if node is None:
            raise ConversionError("error", f"{target.key}: missing instance {name}")
        if node.problem:
            raise ConversionError("unsupported" if node.problem.startswith("unsupported") else "error", f"{target.key}: {name}: {node.problem}")
        visiting.add(name)
        links = incoming[name]
        destinations = set()
        for link in links:
            destination = node.port(link.to_port)
            if not destination.is_input:
                raise ConversionError("error", f"{target.key}: {name}.{link.to_port} is not an input")
            if link.to_port in destinations:
                raise ConversionError("error", f"{target.key}: duplicate input connection {name}.{link.to_port}")
            destinations.add(link.to_port)
            producer = mapping.nodes.get(link.from_instance)
            if producer is None:
                raise ConversionError("error", f"{target.key}: missing instance {link.from_instance}")
            if producer.problem:
                raise ConversionError("unsupported" if producer.problem.startswith("unsupported") else "error", f"{target.key}: {link.from_instance}: {producer.problem}")
            if not producer.port(link.from_port).is_output:
                raise ConversionError("error", f"{target.key}: {link.from_instance}.{link.from_port} is not an output")
            visit(link.from_instance)
        if node.kind != "SOURCE":
            missing = [p.name for p in node.ports if p.is_input and p.name not in destinations]
            if missing:
                raise ConversionError("error", f"{target.key}: {name}: missing input connections {', '.join(missing)}")
        visiting.remove(name)
        visited.add(name)
        result.append(node)

    visit(target.key.instance)
    ctes = {}
    for node in result:
        name = slug(node.key.instance)
        if name in ctes:
            raise ConversionError("error", f"{target.key}: CTE name collision {node.key.instance} / {ctes[name]}")
        ctes[name] = node.key.instance
        names = [p.name.casefold() for p in node.ports]
        if len(names) != len(set(names)):
            raise ConversionError("error", f"{target.key}: case-insensitive port collision in {node.key.instance}")
    return tuple(result)


def _preparation(node: Node, relation_override: dict | None) -> tuple[PreparationIntent, ...]:
    relation = node.relation
    if relation_override is not None:
        if not isinstance(relation_override, dict) or set(relation_override) != {"schema", "table"} or not all(isinstance(x, str) and x for x in relation_override.values()):
            raise ConversionError("error", f"{node.key}: target_relations needs nonempty schema/table")
        if relation.schema and relation_override["schema"] != relation.schema:
            raise ConversionError("error", f"{node.key}: target schema conflicts with XML")
        if relation_override["table"] != relation.table:
            raise ConversionError("error", f"{node.key}: target table conflicts with XML definition")
        relation = replace(relation, schema=relation_override["schema"], schema_origin="explicit configuration")
    intents = []
    for setting in ("Pre SQL", "Post SQL"):
        command = node.attributes.get(setting, "").strip()
        if not command:
            continue
        # Exactly one bounded command, never passed through as executable SQL.
        match = re.fullmatch(r"TRUNCATE\s+TABLE\s+([A-Za-z_][A-Za-z0-9_]*)(?:\.([A-Za-z_][A-Za-z0-9_]*))?\s*;?", command, re.I)
        if setting != "Pre SQL" or not match:
            raise ConversionError("unsupported", f"{node.key}: unsupported required {setting}: {command!r}")
        schema, table = (match[1], match[2]) if match[2] else (None, match[1])
        if relation.schema is None and schema is not None:
            raise ConversionError("error", f"{node.key}: original target schema absent from XML; declare target_relations before translating cleanup")
        if table != relation.table or schema != relation.schema:
            raise ConversionError("unsupported", f"{node.key}: cleanup relation does not match declared original target relation")
        intents.append(PreparationIntent(node.key, "clear", relation, "target instance Pre SQL"))
    return tuple(intents)


def resolve_configuration(export: Export, config: dict | None = None) -> tuple[dict, dict]:
    """Validate exact configuration identities without traversing target graphs."""
    config = {} if config is None else config
    if not isinstance(config, dict) or set(config) - {"bindings", "target_relations"}:
        raise ConversionError("error", "Configuration accepts bindings and target_relations objects only")
    targets, sources = export.targets, export.sources
    bindings = {}
    raw_bindings = config.get("bindings", {})
    raw_relations = config.get("target_relations", {})
    if not isinstance(raw_bindings, dict) or not isinstance(raw_relations, dict):
        raise ConversionError("error", "bindings and target_relations must be objects")
    for source, target in raw_bindings.items():
        if not isinstance(source, str) or not isinstance(target, str):
            raise ConversionError("error", "Binding identities must be strings")
        bindings[_resolve(source, sources, "source")] = _resolve(target, targets, "target")
    relations = {_resolve(k, targets, "target relation"): v for k, v in raw_relations.items()}
    return bindings, relations


def plan(export: Export, selected: list[str] | None = None, config: dict | None = None) -> PlanningResult:
    targets, sources = export.targets, export.sources
    names = {key: slug("__".join((key.mapping.repository, key.mapping.folder, key.mapping.mapping, key.instance))) for key in targets}
    _check_collisions(names, "model name")
    source_names = {key: slug("__".join((key.mapping.repository, key.mapping.folder, key.mapping.mapping, key.instance))) for key in sources}
    _check_collisions(source_names, "source name")
    bindings, relations = resolve_configuration(export, config)
    requested = tuple(sorted({_resolve(value, targets, "selected target") for value in selected})) if selected is not None else tuple(sorted(targets))
    outcomes, plans, visiting = {}, {}, set()

    def build(key: InstanceKey) -> None:
        if key in outcomes or key in plans:
            return
        if key in visiting:
            raise ConversionError("error", f"Cross-mapping binding cycle at {key}")
        visiting.add(key)
        dependencies = []
        try:
            target = targets[key]
            mapping = export.mappings[key.mapping]
            ordered = _checked_nodes(mapping, target)
            source_plans = []
            for node in ordered:
                if node.kind != "SOURCE":
                    continue
                producer = bindings.get(node.key)
                if producer:
                    dependencies.append(producer)
                    build(producer)
                    if producer in outcomes:
                        raise ConversionError("blocked", f"{key}: producer {producer} failed: {outcomes[producer].reason}")
                    output_columns = {p.name: p for p in plans[producer].columns}
                    consumed = {c.from_port for c in mapping.connections if c.from_instance == node.key.instance and any(n.key.instance == c.to_instance for n in ordered)}
                    for field in sorted(consumed):
                        source_port = node.port(field)
                        output = output_columns.get(field)
                        if output is None or not _compatible(output, source_port):
                            raise ConversionError("error", f"{key}: incompatible binding {node.key}.{field} -> {producer}; no column renaming/narrowing is allowed")
                source_plans.append(SourcePlan(node.key, source_names[node.key], "input", node.relation, producer))
            preparations = _preparation(target, relations.get(key))
            plans[key] = ModelPlan(key, names[key], names[key], "converted", target.ports, mapping,
                                   ordered, tuple(source_plans), tuple(sorted(set(dependencies))), preparations)
        except ConversionError as exc:
            outcomes[key] = TargetOutcome(key, exc.status, str(exc), tuple(sorted(set(dependencies))))
        finally:
            visiting.remove(key)

    for key in requested:
        build(key)
    return PlanningResult(plans, outcomes, requested, tuple(sorted(targets)))
