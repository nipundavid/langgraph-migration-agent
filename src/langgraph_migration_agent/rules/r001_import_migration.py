import libcst as cst


class R001ImportMigration(cst.CSTTransformer):
    """Migrate create_react_agent imports to langchain.agents."""

    def __init__(self) -> None:
        # Store issues that require manual review.
        self.diagnostics: list[str] = []

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine | cst.FlattenSentinel[cst.BaseStatement]:

        # Only process lines containing one statement.
        if len(original_node.body) != 1:
            return updated_node

        original_import = original_node.body[0]
        updated_import = updated_node.body[0]

        # We only handle from ... import ... statements.
        if not isinstance(original_import, cst.ImportFrom):
            return updated_node

        if not isinstance(updated_import, cst.ImportFrom):
            return updated_node

        # Check whether the import originates from langgraph.prebuilt.
        is_langgraph_prebuilt = (
            isinstance(original_import.module, cst.Attribute)
            and isinstance(original_import.module.value, cst.Name)
            and original_import.module.value.value == "langgraph"
            and original_import.module.attr.value == "prebuilt"
        )

        if not is_langgraph_prebuilt:
            return updated_node

        # Wildcard imports are outside the current migration scope.
        if not isinstance(original_import.names, tuple):
            return updated_node

        # Find the target import in the original statement.
        target_imports = [
            imported
            for imported in original_import.names
            if isinstance(imported.name, cst.Name)
            and imported.name.value == "create_react_agent"
        ]

        if not target_imports:
            return updated_node

        # Aliased imports are not supported.
        if any(imported.asname is not None for imported in target_imports):
            self.diagnostics.append(
                "R001: Aliased create_react_agent import found. "
                "Import was left unchanged; manual review required."
            )
            return updated_node

        # Find the corresponding nodes in the updated statement.
        updated_target_imports = [
            imported
            for imported in updated_import.names
            if isinstance(imported.name, cst.Name)
            and imported.name.value == "create_react_agent"
        ]

        # Rename the imported symbol as well as its module.
        migrated_aliases = [
            imported.with_changes(
                name=cst.Name("create_agent"),
                comma=cst.MaybeSentinel.DEFAULT,
            )
            for imported in updated_target_imports
        ]

        # Keep every unrelated imported symbol in the original module.
        remaining_imports = [
            imported
            for imported in updated_import.names
            if not (
                isinstance(imported.name, cst.Name)
                and imported.name.value == "create_react_agent"
            )
        ]

        # Build the new import statement for create_agent.
        migrated_import = updated_import.with_changes(
            module=cst.parse_expression("langchain.agents"),
            names=migrated_aliases,
            lpar=None,
            rpar=None,
        )

        # Case 1: Only create_react_agent was imported.
        if not remaining_imports:
            return updated_node.with_changes(
                body=(migrated_import,)
            )

        # Case 2: Mixed import.
        # If there are no parentheses, remove a trailing comma
        # from the final remaining import alias.
        if updated_import.lpar is None:
            last_import = remaining_imports[-1]
            remaining_imports[-1] = last_import.with_changes(
                comma=cst.MaybeSentinel.DEFAULT
            )

        remaining_statement = updated_import.with_changes(
            names=remaining_imports
        )

        # Construct the first new statement.
        migrated_line = cst.SimpleStatementLine(
            body=(migrated_import,),
            leading_lines=original_node.leading_lines,
        )

        # Construct the second statement with the unrelated imports.
        remaining_line = updated_node.with_changes(
            body=(remaining_statement,),
            leading_lines=(),
        )

        # Replace one statement with two statements.
        return cst.FlattenSentinel(
            [migrated_line, remaining_line]
        )