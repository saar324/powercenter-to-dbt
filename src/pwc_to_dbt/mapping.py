"""Authoritative representation shared by reader, planner, emitter and writer.

Definitions and instances remain distinct. Port types are retained at every
boundary; a connection never means that those types can be discarded.
"""
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True, order=True)
class MappingKey:
    repository: str
    folder: str
    mapping: str

    def __str__(self) -> str:
        return "/".join((self.repository, self.folder, self.mapping))


@dataclass(frozen=True, order=True)
class InstanceKey:
    mapping: MappingKey
    instance: str

    def __str__(self) -> str:
        return f"{self.mapping}/{self.instance}"


@dataclass(frozen=True)
class DataType:
    name: str
    precision: int
    scale: int

    @property
    def family(self) -> str:
        name = self.name.lower()
        if name in {"string", "varchar", "varchar2", "char", "nstring", "nvarchar2"}:
            return "string"
        if name in {"date", "date/time", "timestamp"}:
            return "timestamp"
        if name in {"double", "real", "float"}:
            return "double"
        if name in {"decimal", "number(p,s)"}:
            return "decimal"
        if name == "number":
            return "number"
        if name in {"integer", "small integer", "bigint"}:
            return "integer"
        return "unknown"


@dataclass(frozen=True)
class Port:
    name: str
    datatype: DataType
    port_type: str
    expression: str = ""
    default: str = ""
    expression_type: str = ""
    sort_key: bool = False
    sort_direction: str = "ASCENDING"

    @property
    def is_input(self) -> bool:
        return "INPUT" in self.port_type

    @property
    def is_output(self) -> bool:
        return "OUTPUT" in self.port_type


@dataclass(frozen=True)
class Relation:
    schema: str | None
    table: str
    database_type: str
    schema_origin: str = "export"


@dataclass(frozen=True)
class Node:
    key: InstanceKey
    kind: str
    definition: str
    transformation_type: str
    ports: tuple[Port, ...]
    attributes: dict[str, str] = field(default_factory=dict)
    relation: Relation | None = None
    problem: str | None = None

    def port(self, name: str) -> Port:
        for port in self.ports:
            if port.name == name:
                return port
        raise ConversionError("error", f"{self.key}: missing port {name!r}")


@dataclass(frozen=True)
class Connection:
    from_instance: str
    from_port: str
    to_instance: str
    to_port: str


@dataclass(frozen=True)
class PreparationIntent:
    target: InstanceKey
    operation: Literal["clear"]
    original_relation: Relation
    origin: str


@dataclass(frozen=True)
class Mapping:
    key: MappingKey
    nodes: dict[str, Node]
    connections: tuple[Connection, ...]
    high_precision: tuple[str, ...] = ()
    preparations: dict[str, tuple[PreparationIntent, ...]] = field(default_factory=dict)
    preparation_errors: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Export:
    mappings: dict[MappingKey, Mapping]
    sha256: str
    metadata: dict[str, str]
    unconverted_commands: tuple[str, ...] = ()

    @property
    def targets(self) -> dict[InstanceKey, Node]:
        return {n.key: n for m in self.mappings.values() for n in m.nodes.values() if n.kind == "TARGET"}

    @property
    def sources(self) -> dict[InstanceKey, Node]:
        return {n.key: n for m in self.mappings.values() for n in m.nodes.values() if n.kind == "SOURCE"}


@dataclass(frozen=True)
class SourcePlan:
    key: InstanceKey
    source_name: str
    table_name: str
    relation: Relation
    producer: InstanceKey | None = None


@dataclass(frozen=True)
class ModelPlan:
    target: InstanceKey
    model_name: str
    alias: str
    schema: str
    columns: tuple[Port, ...]
    mapping: Mapping
    ordered_nodes: tuple[Node, ...]
    sources: tuple[SourcePlan, ...]
    dependencies: tuple[InstanceKey, ...]
    preparations: tuple[PreparationIntent, ...]


@dataclass(frozen=True)
class Diagnostic:
    stage: str
    target: str
    message: str


@dataclass(frozen=True)
class TargetOutcome:
    target: InstanceKey
    status: Literal["emitted", "unsupported", "blocked", "error"]
    reason: str
    dependencies: tuple[InstanceKey, ...] = ()
    artifact: str | None = None


@dataclass(frozen=True)
class PlanningResult:
    plans: dict[InstanceKey, ModelPlan]
    outcomes: dict[InstanceKey, TargetOutcome]
    selected: tuple[InstanceKey, ...]
    inventory: tuple[InstanceKey, ...]


@dataclass(frozen=True)
class ModelArtifact:
    plan: ModelPlan
    sql: str
    required_sort: tuple[str, ...] = ()


class ConversionError(ValueError):
    def __init__(self, status: Literal["unsupported", "blocked", "error"], message: str):
        super().__init__(message)
        self.status = status
