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
                      Mapping, MappingKey, Node, Port, ReaderConnection, Relation,
                      SourceAssociation, SourceDefinition)


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


def _source_context(repository, folder, mappings):
    """Retain reader declarations without resolving runtime override precedence.

    Only explicit, type-checked associations can attach a connection reference
    to a source use. Inconsistent evidence remains visible and unassigned.
    """
    associations, references = [], []
    repo_name, folder_name = repository.get("NAME", ""), folder.get("NAME", "")
    parents = {child: parent for parent in folder.iter() for child in parent}

    def workflow_of(element):
        while element in parents:
            element = parents[element]
            if element.tag == "WORKFLOW":
                return element.get("NAME")
        return None

    def in_worklet(element):
        while element in parents:
            element = parents[element]
            if element.tag == "WORKLET":
                return True
        return False

    folder_mappings = {key.mapping: value for key, value in mappings.items()
                       if (key.repository, key.folder) == (repo_name, folder_name)}
    qualifier_links = {}
    for element in folder.findall("MAPPING"):
        mapping = folder_mappings[element.get("NAME")]
        links = {}
        for instance in element.findall("INSTANCE"):
            qualifier = mapping.nodes[instance.get("NAME")]
            for associated in instance.findall("ASSOCIATED_SOURCE_INSTANCE"):
                source_name = associated.get("NAME")
                source = mapping.nodes.get(source_name)
                diagnostics = []
                if qualifier.kind != "TRANSFORMATION" or qualifier.transformation_type != "Source Qualifier":
                    diagnostics.append("associated-source owner is not a Source Qualifier")
                if source is None or source.kind != "SOURCE":
                    diagnostics.append("associated source instance is absent or not a SOURCE")
                if source_name in links.get(qualifier.key.instance, []):
                    diagnostics.append("duplicate qualifier association")
                associations.append(SourceAssociation(mapping.key, source_name, qualifier.key.instance,
                                                      "INSTANCE/ASSOCIATED_SOURCE_INSTANCE", diagnostics=tuple(diagnostics)))
                links.setdefault(qualifier.key.instance, []).append(source_name)
        qualifier_links[mapping.key] = links

    sessions = list(folder.iter("SESSION"))
    dsq_association_indices = {}
    contexts = [(session, session, None, []) for session in sessions]
    for task in folder.iter("TASKINSTANCE"):
        if not task.findall("SESSIONEXTENSION"):
            continue
        workflow = workflow_of(task)
        candidates = [session for session in sessions if session.get("NAME") == task.get("TASKNAME")
                      and (workflow_of(session) == workflow or workflow_of(session) is None)]
        # A task-local session takes precedence for identifying its declaration;
        # this does not select an effective connection or override value.
        local = [session for session in candidates if workflow_of(session) == workflow]
        candidates = local or candidates
        valid = len(candidates) == 1 and task.get("TASKTYPE") == "Session"
        contexts.append((task, candidates[0] if valid else None, task.get("NAME"),
                         [] if valid else ["task session reference is absent, ambiguous or not a Session"]))

    for context, session, task_name, context_problems in contexts:
        workflow = workflow_of(context)
        session_name = session.get("NAME") if session is not None else context.get("TASKNAME")
        mapping = folder_mappings.get(session.get("MAPPINGNAME")) if session is not None else None
        common_problems = list(context_problems)
        if in_worklet(context) or (session is not None and in_worklet(session)):
            common_problems.append("worklet scope is unsupported; reader association is unresolved")
        if mapping is None:
            common_problems.append("session mapping is absent or unresolved")
        extensions = context.findall("SESSIONEXTENSION")
        # Overrides may omit source-to-qualifier declarations. Keep the reusable
        # session declarations as explicit association provenance in that case.
        association_extensions = list(extensions)
        if task_name is not None and session is not None:
            association_extensions += session.findall("SESSIONEXTENSION")
        dsq_links, dsq_problems, dsq_declarations = {}, {}, {}
        for extension in association_extensions:
            if extension.get("TYPE") != "READER" or extension.get("DSQINSTNAME") is None:
                continue
            source_name, qualifier_name = extension.get("SINSTANCENAME"), extension.get("DSQINSTNAME")
            problems = list(common_problems)
            if mapping is not None:
                source, qualifier = mapping.nodes.get(source_name), mapping.nodes.get(qualifier_name)
                if source is None or source.kind != "SOURCE":
                    problems.append("DSQ source instance is absent or not a SOURCE")
                if qualifier is None or qualifier.kind != "TRANSFORMATION" or qualifier.transformation_type != "Source Qualifier":
                    problems.append("DSQ instance is absent or not a Source Qualifier")
                if extension.get("TRANSFORMATIONTYPE") != "Source Definition" or extension.get("DSQINSTTYPE") != "Source Qualifier":
                    problems.append("DSQ declaration types are inconsistent")
            declared_mapping = (mapping.key if mapping is not None else
                                MappingKey(repo_name, folder_name, session.get("MAPPINGNAME", "") if session is not None else ""))
            if extension in extensions:
                dsq_association_indices[extension] = len(associations)
                associations.append(SourceAssociation(declared_mapping, source_name, qualifier_name,
                                                      "SESSIONEXTENSION/DSQINSTNAME", session_name, workflow,
                                                      task_name, tuple(problems)))
            dsq_declarations.setdefault(qualifier_name, []).append(extension)
            dsq_links.setdefault(qualifier_name, set()).add(source_name)
            dsq_problems.setdefault(qualifier_name, []).extend(problems)
        source_qualifiers = {}
        for qualifier, names in dsq_links.items():
            for name in names:
                source_qualifiers.setdefault(name, set()).add(qualifier)
        for qualifier, names in dsq_links.items():
            if any(len(source_qualifiers[name]) > 1 for name in names):
                dsq_problems[qualifier].append("source has ambiguous DSQ associations")

        qualifier_problems = {}
        if mapping is not None:
            qualifiers = set(qualifier_links[mapping.key]) | set(dsq_links)
            qualifiers.update(extension.get("SINSTANCENAME") for extension in extensions
                              if extension.get("TYPE") == "READER" and extension.get("TRANSFORMATIONTYPE") == "Source Qualifier")
            for qualifier in qualifiers:
                declared = qualifier_links[mapping.key].get(qualifier, [])
                dsq = dsq_links.get(qualifier, set())
                base_indices = [index for index, association in enumerate(associations)
                                if association.mapping == mapping.key and association.qualifier_instance == qualifier
                                and association.provenance == "INSTANCE/ASSOCIATED_SOURCE_INSTANCE"]
                problems = list(common_problems) + dsq_problems.get(qualifier, [])
                # Only the original declaration errors inform validation. Scoped
                # errors from another session must not invalidate this context.
                problems.extend(problem for index in base_indices for problem in associations[index].diagnostics
                                if not problem.startswith("context "))
                if not declared:
                    problems.append("qualifier source association declaration is absent")
                if not dsq:
                    problems.append("session DSQ source association declaration is absent")
                if declared and dsq and set(declared) != dsq:
                    problems.append("qualifier and session source associations disagree")
                qualifier_problems[qualifier] = sorted(set(problems))
                scope = f"context session={session_name!r} workflow={workflow!r} task={task_name!r}: "
                indices = base_indices + [dsq_association_indices[extension] for extension in dsq_declarations.get(qualifier, [])
                                          if extension in dsq_association_indices]
                for index in indices:
                    association = associations[index]
                    # Mapping and inherited session declarations retain their
                    # actual XML scope; diagnostics identify the failing use.
                    scoped = (association.provenance == "INSTANCE/ASSOCIATED_SOURCE_INSTANCE"
                              or association.task_instance != task_name)
                    additions = [scope + problem if scoped else problem for problem in problems]
                    associations[index] = replace(association, diagnostics=tuple(sorted(set(association.diagnostics) | set(additions))))

        for extension in extensions:
            if extension.get("TYPE") != "READER":
                continue
            reader = extension.get("SINSTANCENAME")
            problems = list(common_problems)
            uses, provenance = set(), []
            if mapping is not None:
                node = mapping.nodes.get(reader)
                if node is None:
                    problems.append("reader instance is absent")
                elif node.kind == "SOURCE" and extension.get("TRANSFORMATIONTYPE") == "Source Definition":
                    if extension.get("DSQINSTNAME") is not None:
                        problems.extend(qualifier_problems.get(extension.get("DSQINSTNAME"),
                                                              dsq_problems.get(extension.get("DSQINSTNAME"), [])))
                    if not problems:
                        uses.add(node.key)
                    provenance.append("SESSIONEXTENSION/SINSTANCENAME (SOURCE)")
                elif (node.kind == "TRANSFORMATION" and node.transformation_type == "Source Qualifier"
                      and extension.get("TRANSFORMATIONTYPE") == "Source Qualifier"):
                    declared = qualifier_links[mapping.key].get(reader, [])
                    dsq = dsq_links.get(reader, set())
                    problems.extend(qualifier_problems.get(reader, []))
                    if declared:
                        provenance.append("INSTANCE/ASSOCIATED_SOURCE_INSTANCE")
                    if dsq:
                        provenance.append("SESSIONEXTENSION/DSQINSTNAME (inherited session declaration)"
                                          if task_name is not None and all(extension not in extensions
                                             for extension in dsq_declarations.get(reader, []))
                                          else "SESSIONEXTENSION/DSQINSTNAME")
                    names = set(declared) | dsq
                    if not names:
                        problems.append("source association is absent")
                    if not problems:
                        uses.update(mapping.nodes[name].key for name in names)
                else:
                    problems.append("reader identity/type is inconsistent")
            connection_refs = extension.findall("CONNECTIONREFERENCE")
            # Source-to-qualifier routing declarations are not missing connections.
            if not connection_refs and extension.get("DSQINSTNAME") is not None:
                continue
            if not connection_refs:
                problems.append("reader connection reference is absent")
            for reference in connection_refs or [None]:
                values = reference.attrib if reference is not None else {}
                references.append(ReaderConnection(
                    repo_name, folder_name, mapping.key if mapping is not None else None,
                    workflow, session_name, task_name, reader,
                    "TASKINSTANCE/SESSIONEXTENSION/CONNECTIONREFERENCE" if task_name is not None
                    else "SESSION/SESSIONEXTENSION/CONNECTIONREFERENCE",
                    values.get("CONNECTIONNAME"), values.get("CONNECTIONSUBTYPE"),
                    values.get("CONNECTIONTYPE"), values.get("CNXREFNAME"),
                    tuple(sorted(uses)), tuple(provenance), tuple(sorted(set(problems)))))
    return associations, references


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
    unconverted, source_definitions, source_associations, reader_connections = [], [], [], []
    repositories = _unique(root.findall("REPOSITORY"), "repositories")
    for repository in repositories.values():
        for folder in _unique(repository.findall("FOLDER"), "folders").values():
            sources = _unique(folder.findall("SOURCE"), "source definitions")
            source_definitions.extend(SourceDefinition(repository.get("NAME", ""), folder.get("NAME", ""),
                                                       source.get("NAME", ""), source.get("DATABASETYPE"),
                                                       source.get("OWNERNAME"), source.get("DBDNAME"))
                                      for source in sources.values())
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
            associations, references = _source_context(repository, folder, mappings)
            source_associations.extend(associations)
            reader_connections.extend(references)
            for command in folder.findall(".//TASK[@TYPE='Command']"):
                unconverted.append(f"{repository.get('NAME')}/{folder.get('NAME')}/{command.get('NAME')}: workflow Command not executed")
    if not mappings:
        raise ConversionError("error", "No mappings found")
    return Export(mappings, sha256(data).hexdigest(), dict(root.attrib), tuple(sorted(unconverted)),
                  tuple(source_definitions), tuple(source_associations), tuple(reader_connections))
