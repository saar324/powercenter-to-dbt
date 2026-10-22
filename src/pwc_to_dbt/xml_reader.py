"""Read exported facts only. ElementTree does not retrieve external DTDs.

Entity declarations/internal DTD subsets are refused before parsing. This keeps
both external entity access and internal entity expansion outside the reader.
"""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .mapping import (Connection, ConversionError, DataType, Export, InstanceKey,
                      Mapping, MappingKey, Node, Port, Relation)


def _unique(elements: list[ET.Element], label: str) -> dict[str, ET.Element]:
    result = {}
    for element in elements:
        name = element.get("NAME", "")
        if not name or "/" in name or name in result:
            raise ConversionError("error", f"{label}: missing, duplicate or ambiguous name {name!r}")
        result[name] = element
    return result


def _attributes(element: ET.Element) -> dict[str, str]:
    result = {}
    for child in element.findall("TABLEATTRIBUTE"):
        name, value = child.get("NAME", ""), child.get("VALUE", "")
        if name in result and result[name] != value:
            raise ConversionError("error", f"{element.get('NAME')}: conflicting attribute {name}")
        result[name] = value
    return result


def _ports(definition: ET.Element, kind: str) -> tuple[Port, ...]:
    tag = {"SOURCE": "SOURCEFIELD", "TARGET": "TARGETFIELD"}.get(kind, "TRANSFORMFIELD")
    elements = definition.findall(tag)
    _unique(elements, f"{definition.get('NAME')} ports")
    if kind in {"SOURCE", "TARGET"}:
        ordinals = []
        for element in elements:
            raw = element.get("FIELDNUMBER", "")
            if not raw.isdecimal() or int(raw) <= 0:
                raise ConversionError("error", f"{definition.get('NAME')}.{element.get('NAME')}: FIELDNUMBER must be a positive integer")
            ordinals.append(int(raw))
        if len(ordinals) != len(set(ordinals)):
            raise ConversionError("error", f"{definition.get('NAME')}: duplicate FIELDNUMBER")
        elements = [element for _, element in sorted(zip(ordinals, elements), key=lambda pair: pair[0])]
    def integer_metadata(element, attribute):
        raw = element.get(attribute, "0")
        try:
            return int(raw)
        except ValueError as exc:
            raise ConversionError("error", f"{definition.get('NAME')}.{element.get('NAME')}: invalid {attribute}={raw!r}") from exc

    return tuple(Port(
        p.get("NAME", ""),
        DataType(p.get("DATATYPE", ""), integer_metadata(p, "PRECISION"), integer_metadata(p, "SCALE")),
        {"SOURCE": "OUTPUT", "TARGET": "INPUT"}.get(kind, p.get("PORTTYPE", "")),
        p.get("EXPRESSION", ""), p.get("DEFAULTVALUE", ""), p.get("EXPRESSIONTYPE", ""),
        p.get("ISSORTKEY", "NO") == "YES", p.get("SORTDIRECTION", "ASCENDING"),
    ) for p in elements)


def read_xml(path: str | Path) -> Export:
    data = Path(path).read_bytes()
    # Byte-zero removal also detects declarations in UTF-16/32 XML before ET sees them.
    scan = data.replace(b"\x00", b"")
    if re.search(br"<!ENTITY\b|<!DOCTYPE[^>]*\[", scan, flags=re.I):
        raise ConversionError("error", "XML entity declarations and internal DTD subsets are unsupported")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ConversionError("error", f"Malformed XML: {exc}") from exc
    if root.tag != "POWERMART":
        raise ConversionError("unsupported", f"Expected PowerCenter POWERMART root, found {root.tag}")
    mappings = {}
    unconverted = []
    repositories = _unique(root.findall("REPOSITORY"), "repositories")
    for repository in repositories.values():
        for folder in _unique(repository.findall("FOLDER"), "folders").values():
            sources = _unique(folder.findall("SOURCE"), "source definitions")
            targets = _unique(folder.findall("TARGET"), "target definitions")
            reusable = _unique(folder.findall("TRANSFORMATION"), "reusable transformations")
            for mapping in _unique(folder.findall("MAPPING"), "mappings").values():
                key = MappingKey(repository.get("NAME", ""), folder.get("NAME", ""), mapping.get("NAME", ""))
                definitions = dict(reusable)
                definitions.update(_unique(mapping.findall("TRANSFORMATION"), f"{key} transformations"))
                nodes = {}
                for instance in _unique(mapping.findall("INSTANCE"), f"{key} instances").values():
                    name = instance.get("NAME", "")
                    kind = instance.get("TYPE", "")
                    definition_name = instance.get("TRANSFORMATION_NAME", "")
                    definition = {"SOURCE": sources, "TARGET": targets}.get(kind, definitions).get(definition_name)
                    instance_key = InstanceKey(key, name)
                    if definition is None:
                        nodes[name] = Node(instance_key, kind, definition_name, instance.get("TRANSFORMATION_TYPE", ""), (), problem=f"missing definition {definition_name!r}")
                        continue
                    relation = None
                    if kind in {"SOURCE", "TARGET"}:
                        relation = Relation(definition.get("OWNERNAME") or None, definition_name,
                                            definition.get("DATABASETYPE", ""))
                    try:
                        attributes = _attributes(definition) | _attributes(instance)
                        ports = _ports(definition, kind)
                        problem = None
                    except (ConversionError, ValueError) as exc:
                        attributes, ports = {}, ()
                        problem = f"malformed metadata in definition {definition_name!r}: {exc}"
                    nodes[name] = Node(instance_key, kind, definition_name,
                                       definition.get("TYPE", instance.get("TRANSFORMATION_TYPE", "")),
                                       ports, attributes, relation, problem)
                connections = tuple(Connection(c.get("FROMINSTANCE", ""), c.get("FROMFIELD", ""),
                                               c.get("TOINSTANCE", ""), c.get("TOFIELD", ""))
                                    for c in mapping.findall("CONNECTOR"))
                sessions = [s for s in folder.findall(".//SESSION") if s.get("MAPPINGNAME") == key.mapping]
                # Session writer overrides are a separate execution layer. An
                # unimplemented required override must not be silently erased.
                override_names = {"Pre SQL", "Post SQL", "Table Name Prefix", "Target table name", "Target Table Name", "Sql Query", "Source Filter"}
                def mark_problem(name, message):
                    node = nodes[name]
                    problem = f"{node.problem}; {message}" if node.problem else message
                    nodes[name] = replace(node, problem=problem)

                for session in sessions:
                    for setting in session.findall("ATTRIBUTE"):
                        name, value = setting.get("NAME"), setting.get("VALUE")
                        if name == "Treat source rows as" and value != "Insert":
                            for node in tuple(nodes.values()):
                                if node.kind == "TARGET":
                                    mark_problem(node.key.instance, f"unsupported session mode {name}={value!r}")
                        if name == "Incremental Aggregation" and value != "NO":
                            for node in tuple(nodes.values()):
                                if node.transformation_type == "Aggregator":
                                    mark_problem(node.key.instance, f"unsupported session mode {name}={value!r}")
                    for extension in session.findall("SESSIONEXTENSION"):
                        instance_name = extension.get("SINSTANCENAME")
                        if instance_name not in nodes:
                            continue
                        overrides = [a.get("NAME") for a in extension.findall("ATTRIBUTE")
                                     if (a.get("NAME") in override_names and a.get("VALUE", "").strip())
                                     or (a.get("NAME") == "Truncate target table option" and a.get("VALUE") != "NO")
                                     or (extension.get("TYPE") == "WRITER" and a.get("NAME") == "Insert" and a.get("VALUE") != "YES")]
                        if overrides:
                            mark_problem(instance_name, "unsupported required session override: " + ", ".join(overrides))
                precision = tuple(sorted({a.get("VALUE", "") for s in sessions for a in s.iter("ATTRIBUTE")
                                          if a.get("NAME") == "Enable high precision"}))
                mappings[key] = Mapping(key, nodes, connections, precision)
            for command in folder.findall(".//TASK[@TYPE='Command']"):
                unconverted.append(f"{repository.get('NAME')}/{folder.get('NAME')}/{command.get('NAME')}: workflow Command not executed")
    if not mappings:
        raise ConversionError("error", "No mappings found")
    return Export(mappings, sha256(data).hexdigest(), dict(root.attrib), tuple(sorted(unconverted)))
