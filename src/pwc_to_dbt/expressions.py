"""Small structural expression parser; no SQL text passthrough or eval()."""
from dataclasses import dataclass
import re

from .mapping import ConversionError, DataType, Port


def _safe_template_text(value: str) -> None:
    if any(token in value for token in ("{{", "{%", "{#")):
        raise ConversionError("unsupported", "dbt template delimiters in imported identifiers/literals are unsupported")


def quote(name: str) -> str:
    _safe_template_text(name)
    return '"' + name.replace('"', '""') + '"'


def literal(value: str) -> str:
    _safe_template_text(value)
    return "'" + value.replace("'", "''") + "'"


@dataclass(frozen=True)
class Expr:
    kind: str
    value: str
    args: tuple['Expr', ...] = ()


_TOKEN = re.compile(r"\s*(?:(?P<string>'(?:[^']|'')*')|(?P<number>\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)|(?P<name>[A-Za-z_][A-Za-z0-9_]*)|(?P<operator><=|>=|<>|!=|[(),+*/=<>-]))")
_PRECEDENCE = {"OR": 1, "AND": 2, "=": 3, "!=": 3, "<>": 3, "<": 3, ">": 3, "<=": 3, ">=": 3,
               "+": 4, "-": 4, "*": 5, "/": 5}


def _parse(text: str) -> Expr:
    tokens, index = [], 0
    text = text.strip()
    while index < len(text):
        match = _TOKEN.match(text, index)
        if not match:
            raise ConversionError("unsupported", f"Unsupported expression syntax at {text[index:]!r}")
        tokens.append((match.lastgroup, match.group(match.lastgroup)))
        index = match.end()
    position = 0

    def expression(minimum=0):
        nonlocal position
        if position >= len(tokens):
            raise ConversionError("unsupported", f"Incomplete expression {text!r}")
        kind, value = tokens[position]
        position += 1
        if value == "(":
            left = expression()
            consume(")")
        elif value in {"+", "-"}:
            left = Expr("unary", value, (expression(6),))
        elif kind in {"string", "number"}:
            left = Expr(kind, value)
        elif kind == "name":
            if position < len(tokens) and tokens[position][1] == "(":
                position += 1
                args = []
                if position < len(tokens) and tokens[position][1] != ")":
                    args.append(expression())
                    while position < len(tokens) and tokens[position][1] == ",":
                        position += 1
                        args.append(expression())
                consume(")")
                left = Expr("call", value.upper(), tuple(args))
            else:
                left = Expr("name", value)
        else:
            raise ConversionError("unsupported", f"Unexpected token {value!r}")
        while position < len(tokens):
            operation = tokens[position][1].upper()
            precedence = _PRECEDENCE.get(operation, -1)
            if precedence < minimum:
                break
            position += 1
            left = Expr("binary", operation, (left, expression(precedence + 1)))
        return left

    def consume(expected):
        nonlocal position
        if position >= len(tokens) or tokens[position][1] != expected:
            raise ConversionError("unsupported", f"Expected {expected!r} in {text!r}")
        position += 1

    result = expression()
    if position != len(tokens):
        raise ConversionError("unsupported", f"Unconsumed expression tokens in {text!r}")
    return result


def parse(text: str) -> Expr:
    try:
        return _parse(text)
    except RecursionError as exc:
        raise ConversionError("unsupported", "Expression exceeds supported parser complexity") from exc


def validate_aggregate(expr: Expr, group_names: set[str]) -> None:
    """Reject scalar row references and nested aggregates before SQL emission."""
    pending = [(expr, False)]
    while pending:
        node, inside_aggregate = pending.pop()
        is_aggregate = node.kind == "call" and node.value in {"COUNT", "MIN", "MAX", "SUM"}
        if is_aggregate and inside_aggregate:
            raise ConversionError("unsupported", "Nested aggregate expressions are unsupported")
        if node.kind == "name" and node.value.upper() != "NULL" and not inside_aggregate and node.value not in group_names:
            raise ConversionError("unsupported", f"Ungrouped Aggregator input reference {node.value!r}")
        pending.extend((child, inside_aggregate or is_aggregate) for child in node.args)


def render(expr: Expr, ports: dict[str, str], *, aggregate=False, runtime_date="CURRENT_DATE") -> str:
    def emit(child):
        return render(child, ports, aggregate=aggregate, runtime_date=runtime_date)

    if expr.kind in {"number", "string"}:
        _safe_template_text(expr.value)
        return expr.value
    if expr.kind == "name":
        if expr.value.upper() == "NULL":
            return "NULL"
        if expr.value not in ports:
            raise ConversionError("error", f"Expression references missing input port {expr.value!r}")
        return ports[expr.value]
    if expr.kind == "unary":
        return f"({expr.value}{emit(expr.args[0])})"
    if expr.kind == "binary":
        left, right = map(emit, expr.args)
        if expr.value == "/":
            return f"(CASE WHEN ({left}) IS NULL OR ({right}) IS NULL THEN NULL WHEN ({right}) = 0 THEN CAST('pwc: division by zero' AS DOUBLE) ELSE ({left}) / ({right}) END)"
        return f"({left} {expr.value} {right})"
    name, args = expr.value, expr.args
    arities = {"IIF": 3, "ISNULL": 1, "UPPER": 1, "LTRIM": 1, "RTRIM": 1,
               "TO_CHAR": 2, "TO_DATE": 2, "COUNT": 1, "MIN": 1, "MAX": 1, "SUM": 1}
    if name not in arities or len(args) != arities.get(name):
        raise ConversionError("unsupported", f"Unsupported function or arity {name}/{len(args)}")
    if name in {"COUNT", "MIN", "MAX", "SUM"}:
        if not aggregate:
            raise ConversionError("unsupported", f"Aggregate {name} outside Aggregator")
        return f"{name}({emit(args[0])})"
    if name == "IIF":
        return f"(CASE WHEN {emit(args[0])} THEN {emit(args[1])} ELSE {emit(args[2])} END)"
    if name == "ISNULL":
        return f"({emit(args[0])} IS NULL)"
    if name in {"UPPER", "LTRIM", "RTRIM"}:
        return f"{name}({emit(args[0])})"
    if args[1] != Expr("string", "'DD-MM-YY'"):
        raise ConversionError("unsupported", f"{name} supports only DD-MM-YY")
    value = emit(args[0])
    if name == "TO_CHAR":
        return f"strftime({value}, '%d-%m-%y')"
    century = f"CAST((CAST(EXTRACT(YEAR FROM {runtime_date}) AS INTEGER) // 100) AS VARCHAR)"
    joined = f"({century} || substr({value}, 7, 2) || '-' || substr({value}, 4, 2) || '-' || substr({value}, 1, 2))"
    return (f"(CASE WHEN {value} IS NULL THEN NULL WHEN regexp_full_match({value}, '[0-9]{{2}}-[0-9]{{2}}-[0-9]{{2}}') "
            f"THEN strptime({joined}, '%Y-%m-%d') ELSE CAST('pwc: invalid DD-MM-YY date' AS TIMESTAMP) END)")


def sql_type(datatype: DataType) -> str:
    family = datatype.family
    if family == "string":
        return "VARCHAR"
    if family == "timestamp":
        return "TIMESTAMP"
    if family in {"double", "number"}:
        # Exported bare NUMBER is not NUMBER(p,s). Its metadata scale does not
        # imply integer rounding; the bounded high-precision-NO policy is double.
        return "DOUBLE"
    if family == "integer":
        return {"small integer": "SMALLINT", "integer": "INTEGER", "bigint": "BIGINT"}[datatype.name.lower()]
    if family == "decimal" and 0 < datatype.precision <= 38 and 0 <= datatype.scale <= datatype.precision:
        return f"DECIMAL({datatype.precision},{datatype.scale})"
    raise ConversionError("unsupported", f"Unsupported datatype {datatype}")


def convert(value: str, port: Port, *, oracle_storage=False, output_default=False) -> str:
    target = sql_type(port.datatype)
    if port.datatype.family == "decimal":
        # DuckDB can reject before scale reduction near a precision limit.
        value = f"round({value}, {port.datatype.scale})"
    converted = f"CAST({value} AS {target})"
    if port.datatype.family == "string" and oracle_storage:
        converted = f"NULLIF({converted}, '')"
    fallback = None
    if output_default and port.default:
        default = port.default.strip()
        if default.upper().startswith("ERROR("):
            if not re.fullmatch(r"ERROR\(\s*'(?:[^']|'')*'\s*\)", default, re.I):
                raise ConversionError("unsupported", f"Unsupported output default {default!r}")
        elif default.upper() == "NULL" or re.fullmatch(r"[+-]?\d+(?:\.\d+)?", default):
            fallback = f"CAST({default} AS {target})"
        else:
            raise ConversionError("unsupported", f"Unsupported output default {default!r}")
    if fallback is not None:
        # A struct distinguishes an error from a successful legitimate NULL.
        # Catch conversion before finite/length checks. Wrapping repeated error-
        # producing expressions inside an isfinite CASE can escape DuckDB TRY
        # during optimization; every raw evaluation stays inside TRY here.
        converted = f"(coalesce(TRY(struct_pack(value := {converted})), struct_pack(value := {fallback}))).value"
    if port.datatype.family in {"double", "number"}:
        failure = fallback if fallback is not None else "CAST('pwc: nonfinite numeric value' AS DOUBLE)"
        converted = f"(CASE WHEN NOT isfinite({converted}) THEN {failure} ELSE {converted} END)"
    if port.datatype.family == "string" and port.datatype.precision > 0:
        failure = fallback if fallback is not None else "CAST(CAST('pwc: string exceeds declared precision' AS INTEGER) AS VARCHAR)"
        converted = f"(CASE WHEN length({converted}) > {port.datatype.precision} THEN {failure} ELSE {converted} END)"
    return converted


def translate(text: str, ports: dict[str, str], *, group_names=None, **kwargs) -> str:
    try:
        expression = parse(text)
        if group_names is not None:
            validate_aggregate(expression, group_names)
        return render(expression, ports, **kwargs)
    except RecursionError as exc:
        raise ConversionError("unsupported", "Expression exceeds supported parser complexity") from exc
