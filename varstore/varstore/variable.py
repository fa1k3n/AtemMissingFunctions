class VariableError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class Variable():
    def __init__(self, name, value=None):
        self.__name = name
        self.__value = value
        self.__subscriptions = []

    @property
    def name(self):
        return self.__name
    
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        if self.__value != val:  
            self.__value = val
            for cbk in self.__subscriptions:
                if cbk is not None:
                    cbk(self.__name, self.__value)
                
    def subscribe(self, cbk):
        self.__subscriptions.append(cbk)
        return len(self.__subscriptions) - 1

    def unsubscribe(self, sub_id):
        try:
            self.__subscriptions[sub_id] = None
        except IndexError:
            raise VariableError("Unknown subscription id " + str(sub_id))
        
    def __str__(self):
        return self.__name + ": " + str(self.__value)
