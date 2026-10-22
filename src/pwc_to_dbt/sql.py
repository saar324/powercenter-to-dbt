"""Generate SELECT bodies from checked plans. No file or dbt lifecycle writes."""
from .dependencies import slug
from .expressions import convert, literal, quote, translate
from .mapping import ConversionError, ModelArtifact, ModelPlan


def _cte(name: str) -> str:
    return quote("step_" + slug(name))


def _require(node, names):
    for name, supported in names.items():
        value = node.attributes.get(name, "")
        if value not in supported:
            raise ConversionError("unsupported", f"{node.key}: unsupported {name}={value!r}")


def generate(plan: ModelPlan, model_names: dict, *, runtime_date="CURRENT_DATE") -> ModelArtifact:
    mapping = plan.mapping
    if mapping.high_precision != ("NO",):
        raise ConversionError("unsupported", f"{plan.target}: requires recorded Enable high precision=NO, found {mapping.high_precision}")
    ctes, ordering = [], {}
    source_plans = {source.key: source for source in plan.sources}
    for node in plan.ordered_nodes:
        try:
            if node.kind == "TARGET":
                continue
            if any(p.port_type == "LOCAL VARIABLE" for p in node.ports):
                raise ConversionError("unsupported", "stateful local-variable ports")
            if node.kind == "SOURCE":
                source = source_plans[node.key]
                if node.relation.database_type != "Oracle":
                    raise ConversionError("unsupported", f"Storage semantics for {node.relation.database_type!r}")
                quote(source.relation.table)
                if source.relation.schema:
                    quote(source.relation.schema)
                if source.producer:
                    relation = "{{ ref(" + literal(model_names[source.producer]) + ") }}"
                else:
                    relation = "{{ source(" + literal(source.source_name) + ", " + literal(source.table_name) + ") }}"
                consumed = {connection.from_port for connection in mapping.connections
                            if connection.from_instance == node.key.instance
                            and any(candidate.key.instance == connection.to_instance for candidate in plan.ordered_nodes)}
                columns = [f"{convert(quote(p.name), p, oracle_storage=node.relation.database_type == 'Oracle')} AS {quote(p.name)}"
                           for p in node.ports if p.name in consumed]
                body = "SELECT\n  " + ",\n  ".join(columns) + f"\nFROM {relation}"
                ordering[node.key.instance] = []
            else:
                links = [c for c in mapping.connections if c.to_instance == node.key.instance]
                parents = sorted({c.from_instance for c in links})
                aliases = {name: f"p{index}" for index, name in enumerate(parents)}
                inputs = {c.to_port: convert(f"{aliases[c.from_instance]}.{quote(c.from_port)}", node.port(c.to_port)) for c in links}
                kind = node.transformation_type
                if kind == "Joiner":
                    if len(parents) != 2:
                        raise ConversionError("unsupported", "Joiner needs exactly two input instances")
                    _require(node, {"Case Sensitive String Comparison": {"YES"}, "Sorted Input": {"NO"}})
                    roles = {}
                    for parent in parents:
                        flags = {"MASTER" in node.port(c.to_port).port_type for c in links if c.from_instance == parent}
                        if len(flags) != 1:
                            raise ConversionError("unsupported", "Joiner mixes master and detail ports on one input")
                        roles[parent] = flags.pop()
                    if set(roles.values()) != {True, False}:
                        raise ConversionError("unsupported", "Joiner needs distinct master and detail inputs")
                    join_type = node.attributes.get("Join Type")
                    if join_type == "Normal Join":
                        first, second, join = parents[0], parents[1], "INNER JOIN"
                    elif join_type == "Master Outer Join":
                        first = next(p for p in parents if not roles[p])
                        second = next(p for p in parents if roles[p])
                        join = "LEFT JOIN"
                    else:
                        raise ConversionError("unsupported", f"Join Type {join_type!r}")
                    condition = translate(node.attributes.get("Join Condition", ""), inputs)
                    relation = f"{_cte(first)} {aliases[first]}\n{join} {_cte(second)} {aliases[second]} ON {condition}"
                else:
                    if len(parents) != 1:
                        raise ConversionError("unsupported", f"{kind} requires one input stream")
                    relation = f"{_cte(parents[0])} {aliases[parents[0]]}"
                suffix = ""
                sort = []
                if kind == "Source Qualifier":
                    _require(node, {"Sql Query": {""}, "User Defined Join": {""}, "Source Filter": {""},
                                    "Select Distinct": {"NO"}, "Number Of Sorted Ports": {"0"}, "Pre SQL": {""}, "Post SQL": {""}})
                elif kind == "Expression":
                    pass
                elif kind == "Aggregator":
                    _require(node, {"Sorted Input": {"NO"}})
                    groups = [p for p in node.ports if p.expression_type == "GROUPBY"]
                    if not groups:
                        raise ConversionError("unsupported", "Aggregator without an explicit group key")
                    if any((port.expression or port.name) != port.name or port.name not in inputs for port in groups):
                        raise ConversionError("unsupported", "Aggregator group keys must be connected input ports")
                    suffix = "\nGROUP BY " + ", ".join(inputs[p.name] for p in groups)
                elif kind == "Sorter":
                    _require(node, {"Distinct": {"NO"}, "Merge Only": {"NO"}, "Case Sensitive": {"YES", "NO"}, "Null Treated Low": {"YES", "NO"}})
                    for port in node.ports:
                        if not port.sort_key:
                            continue
                        if port.sort_direction not in {"ASCENDING", "DESCENDING"}:
                            raise ConversionError("unsupported", f"Sort direction {port.sort_direction!r}")
                        direction = "ASC" if port.sort_direction == "ASCENDING" else "DESC"
                        nulls = "FIRST" if (node.attributes["Null Treated Low"] == "YES") == (direction == "ASC") else "LAST"
                        insensitive = node.attributes["Case Sensitive"] == "NO" and port.datatype.family == "string"
                        sort.append((port.name, direction, nulls, insensitive))
                    if not sort:
                        raise ConversionError("unsupported", "Sorter has no sort keys")
                    suffix = "\nORDER BY " + ", ".join(_sort_sql(quote(name), direction, nulls, insensitive) for name, direction, nulls, insensitive in sort)
                elif kind != "Joiner":
                    raise ConversionError("unsupported", f"Transformation {kind!r}")
                columns = []
                for port in node.ports:
                    if not port.is_output:
                        continue
                    if kind in {"Expression", "Aggregator"}:
                        expression = port.expression or (port.name if port.is_input else "")
                        if not expression:
                            raise ConversionError("unsupported", f"output {port.name} has no expression")
                        value = translate(expression, inputs, aggregate=kind == "Aggregator", runtime_date=runtime_date,
                                          group_names={p.name for p in groups} if kind == "Aggregator" else None)
                    else:
                        if port.name not in inputs:
                            raise ConversionError("unsupported", f"{kind} output {port.name!r} has no connected passthrough input")
                        value = inputs[port.name]
                    columns.append(f"{convert(value, port, output_default=True)} AS {quote(port.name)}")
                if not columns:
                    raise ConversionError("error", "no output columns")
                if kind not in {"Joiner", "Aggregator", "Sorter"}:
                    previous = ordering.get(parents[0], [])
                    for name, direction, nulls, insensitive in previous:
                        connected = next((c.to_port for c in links if c.from_port == name), None)
                        output = next((p.name for p in node.ports if p.is_output and (p.expression or p.name) == connected), None)
                        if output:
                            sort.append((output, direction, nulls, insensitive))
                        else:
                            sort = []
                            break
                ordering[node.key.instance] = sort
                body = "SELECT\n  " + ",\n  ".join(columns) + f"\nFROM {relation}{suffix}"
            ctes.append(f"{_cte(node.key.instance)} AS (\n{body}\n)")
        except ConversionError as exc:
            raise ConversionError(exc.status, f"{plan.target}: instance {node.key.instance}: {exc}") from exc
    links = [c for c in mapping.connections if c.to_instance == plan.target.instance]
    parents = {c.from_instance for c in links}
    if len(parents) != 1:
        raise ConversionError("unsupported", f"{plan.target}: target needs one input stream")
    parent = next(iter(parents))
    incoming = {c.to_port: c for c in links}
    target_node = mapping.nodes[plan.target.instance]
    if target_node.relation.database_type != "Oracle":
        raise ConversionError("unsupported", f"{plan.target}: storage semantics for {target_node.relation.database_type!r}")
    final = [f"{convert("target_input." + quote(incoming[p.name].from_port), p, oracle_storage=target_node.relation.database_type == 'Oracle')} AS {quote(p.name)}" for p in plan.columns]
    sort = tuple(_sort_sql("target_input." + quote(name), direction, nulls, insensitive) for name, direction, nulls, insensitive in ordering.get(parent, []))
    body = "WITH\n" + ",\n".join(ctes) + "\nSELECT\n  " + ",\n  ".join(final) + f"\nFROM {_cte(parent)} AS target_input"
    if sort:
        body += "\nORDER BY " + ", ".join(sort)
    return ModelArtifact(plan, body + "\n", sort)


def _sort_sql(value, direction, nulls, insensitive):
    if insensitive:
        value = f"lower({value})"
    return f"{value} {direction} NULLS {nulls}"
