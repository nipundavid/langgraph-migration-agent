import libcst as cst


class R002CallRename(cst.CSTTransformer):

    def __init__(self, imported_names):
        self.imported_names = imported_names

    def leave_Call(self, original_node, updated_node):

        # TODO: Check if function is a Name

        # TODO: Check if function name exists in imported_names

        # TODO: Rename it to create_agent

        pass