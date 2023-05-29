from varstore import variable

class Storage:
    def __init__(self):
        self.__store = variable.Variable("root")
        self.__store.value = {}

    def get_variable(self, path):
        path = "root." + path
        return self.__get_variable_rec(path, self.__store)

    def get_path(self, var):
        return self.__get_path_rec(var, self.__store)
    
    def __get_path_rec(self, var, node):
        if var == node:
            return node.name
        for sub_node in node.value:
            ret = self.__get_path_rec(var, node.value[sub_node])
            if ret is not None:
                return node + "." + ret
        return None
    
    def __get_variable_rec(self, path, parent):
        splits = path.split(".")
        name = splits[0]
        var = None
        if parent.value is not None and name in parent.value:
            return parent.value[name]
        if parent.value is None or name not in parent.value:
            parent.value[name] = variable.Variable(name)
            parent.value[name].value = {}
        if len(splits) > 1:
            sub_path = ".".join(splits[1:])
            var = self.__get_variable_rec(sub_path, parent.value[name])
            parent.value[name].value = var
        else:
            var = parent.value[name]
        return var

