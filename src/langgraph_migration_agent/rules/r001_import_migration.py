import libcst as cst


class R001ImportMigration(cst.CSTTransformer):

    def leave_ImportFrom(self, original_node, updated_node):

        # Check: langgraph.prebuilt
        if (
            isinstance(original_node.module, cst.Attribute)
            and isinstance(original_node.module.value, cst.Name)
            and original_node.module.value.value == "langgraph"
            and original_node.module.attr.value == "prebuilt"
        ):

            # Check imported function
            if (
                len(original_node.names) == 1
                and isinstance(original_node.names[0], cst.ImportAlias)
                and original_node.names[0].name.value == "create_react_agent"
            ):

                # Change module and imported name
                return updated_node.with_changes(
                    module=cst.parse_expression("langchain.agents"),
                    names=[
                        updated_node.names[0].with_changes(
                            name=cst.Name("create_agent")
                        )
                    ]
                )

        return updated_node

   