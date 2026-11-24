import libcst as cst


class ImportAnalyzer(cst.CSTVisitor):
    """Find unaliased create_react_agent imports from langgraph.prebuilt."""

    def __init__(self) -> None:
        self.imported_names: dict[str, str] = {}

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        if not (
            isinstance(node.module, cst.Attribute)
            and isinstance(node.module.value, cst.Name)
            and node.module.value.value == "langgraph"
            and node.module.attr.value == "prebuilt"
        ):
            return

        for imported in node.names:
            if not isinstance(imported, cst.ImportAlias):
                continue

            if not isinstance(imported.name, cst.Name):
                continue

            if (
                imported.name.value == "create_react_agent"
                and imported.asname is None
            ):
                self.imported_names["create_react_agent"] = "create_react_agent"