from intbase import InterpreterBase


# Enumerated type for our different language data types
class Type:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"

# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value=None):
        self.t = type
        self.v = value

    def value(self):
        return self.v

    def type(self):
        return self.t


def create_value(val):
    if val == InterpreterBase.TRUE_DEF:
        return Value(Type.BOOL, True)
    elif val == InterpreterBase.FALSE_DEF:
        return Value(Type.BOOL, False)
    elif val == InterpreterBase.NIL_DEF:
        return Value(Type.NIL, None)
    elif isinstance(val, str):
        return Value(Type.STRING, val)
    elif isinstance(val, int):
        # print("create an int here")
        return Value(Type.INT, val)
    else:
        raise ValueError("Unknown value type")


def get_printable(val):
    if (val is None):
        # print("nothing here")
        return "nil"
    elif isinstance(val, Value):
        if val.type() == Type.INT:
            # print("there an int here")
            return str(val.value())
        elif (val.type() == Type.NIL):   
            return "nil"
        elif val.type() == Type.STRING:
            return val.value()
        elif val.type() == Type.BOOL:
            return "true" if val.value() else "false"    
    elif isinstance(val, int):
        return str(val)
    elif isinstance(val, bool):
        # print("native here")
        return ("true" if val else "false")
    elif isinstance(val, str):
        return val

