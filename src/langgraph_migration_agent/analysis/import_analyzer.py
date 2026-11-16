import libcst as cst

class ImportAnalyzer(cst.CSTVisitor):

    def __init__(self):
        self.imported_names = {}

    def visit_ImportFrom(self, node):

        if (
            isinstance(node.module, cst.Attribute)
            and isinstance(node.module.value, cst.Name)
            and node.module.value.value == "langgraph"
            and node.module.attr.value == "prebuilt"
        ):

            for name in node.names:

                if isinstance(name, cst.ImportAlias):

                    if name.name.value == "create_react_agent":

                        local_name = (
                            name.asname.name.value
                            if name.asname
                            else name.name.value
                        )

                        self.imported_names[local_name] = name.name.value