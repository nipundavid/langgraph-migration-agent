import libcst as cst


class R001ImportMigration(cst.CSTTransformer):
    """Migrate create_react_agent imports to langchain.agents.create_agent."""

    def __init__(self) -> None:
        self.diagnostics: list[str] = []

    def leave_ImportFrom(
        self,
        original_node: cst.ImportFrom,
        updated_node: cst.ImportFrom,
    ) -> cst.ImportFrom:
        is_langgraph_prebuilt = (
            isinstance(original_node.module, cst.Attribute)
            and isinstance(original_node.module.value, cst.Name)
            and original_node.module.value.value == "langgraph"
            and original_node.module.attr.value == "prebuilt"
        )

        if not is_langgraph_prebuilt:
            return updated_node

        imported_names = [
            imported
            for imported in original_node.names
            if isinstance(imported, cst.ImportAlias)
            and isinstance(imported.name, cst.Name)
            and imported.name.value == "create_react_agent"
        ]

        if not imported_names:
            return updated_node

        # Do not move a mixed import statement to another module.
        if len(original_node.names) != 1:
            self.diagnostics.append(
                "R001: Mixed import from langgraph.prebuilt contains "
                "create_react_agent. Import was left unchanged; "
                "manual review or import splitting is required."
            )
            return updated_node

        migrated_import = updated_node.names[0].with_changes(
            name=cst.Name("create_agent")
        )

        return updated_node.with_changes(
            module=cst.parse_expression("langchain.agents"),
            names=[migrated_import],
        )