import libcst as cst


class R002CallRename(cst.CSTTransformer):

    def __init__(self, imported_names):
        self.imported_names = imported_names

    def leave_Call(self, original_node, updated_node):

        # TODO: Check if function is a Name
        if(isinstance(updated_node.func, cst.Name)
           # TODO: Check if function name exists in imported_names
           and updated_node.func.value in self.imported_names):

            return updated_node.with_changes(
                func=cst.Name("create_agent")
            )

        return updated_node