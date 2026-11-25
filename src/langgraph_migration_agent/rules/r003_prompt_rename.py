import libcst as cst


class R003PromptRename(cst.CSTTransformer):
    """Rename prompt= to system_prompt= on migrated agent calls."""

    def __init__(self, imported_names: dict[str, str]) -> None:
        # Store the function names collected by ImportAnalyzer.
        # This helps us identify calls originating from supported imports.
        self.imported_names = imported_names

    def leave_Call(
        self,
        original_node: cst.Call,
        updated_node: cst.Call,
    ) -> cst.Call:

        # Check whether the function being called is a simple name
        # and whether that name exists in our analyzed imports.
        # If not, leave the function call unchanged.
        if not (
            isinstance(updated_node.func, cst.Name)
            and updated_node.func.value in self.imported_names
        ):
            return updated_node

        # Collect the call arguments after inspecting each one.
        updated_args = []

        # Track whether at least one argument was modified.
        changed = False

        # Iterate through all arguments passed to the function call.
        for arg in updated_node.args:

            # Check three conditions:
            # 1. The argument has a keyword name.
            # 2. The keyword is "prompt".
            # 3. The argument value is a simple string literal.
            if (
                isinstance(arg.keyword, cst.Name)
                and arg.keyword.value == "prompt"
                and isinstance(arg.value, cst.SimpleString)
            ):
                # Replace only the keyword name.
                # The original string value remains unchanged.
                arg = arg.with_changes(
                    keyword=cst.Name("system_prompt")
                )

                # Record that a modification was made.
                changed = True

            # Add the original or modified argument to the new list.
            updated_args.append(arg)

        # Rebuild the function call only if an argument was modified.
        if changed:
            return updated_node.with_changes(args=updated_args)

        # Otherwise, return the original updated call unchanged.
        return updated_node