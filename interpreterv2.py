# Add to spec:
# - printing out a nil value is undefined

from env_v1 import EnvironmentManager
from type_valuev1 import Type, Value, create_value, get_printable
from intbase import InterpreterBase, ErrorType
from brewparse import parse_program


# Main interpreter class
class Interpreter(InterpreterBase):
    # Unary operations has the highest precedence. Divisions and mulplications
    # have higher precedence than substractions and additions. And they are evaluated
    # from left to right. Comparisons have the lowest precedence.
    # Our parser takes precedence into account when generating ASTs, so no need special handlings
    ARITH_OPS = {"+", "-", "*", "/", "neg"}
    # Comparison operations
    COMP_OPS = {"==", "!=", "<", "<=", ">", ">="}
    # Logical operations (precedence order negation > comparison and arithmetic operations > && > ||)
    # Parser already takes care of it, no special handling nedded.
    LOG_OPS = {"||", "&&", "!", "==", "!="}
    STR_OPS = {"+"}
    # now have constants = {true, false, nil} (TO-DO) checked but not sure completely
    # methods
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.__setup_ops()

    # run a program that's provided in a string
    # usese the provided Parser found in brewparse.py to parse the program
    # into an abstract syntax tree (ast)
    def run(self, program):
        ast = parse_program(program)
        self.__set_up_function_table(ast)
        # print(self.func_name_to_ast)
        main_func = self.__get_func_by_name("main",0)
        self.env = EnvironmentManager()
        self.__run_statements(main_func.get("statements"))

    def __set_up_function_table(self, ast):
        self.func_name_to_ast = {}
        # In function nodes, self.dict hold 3 keys: "name"(map to a string storing function name),
        # "args"(map to a list of Argument Nodes), "statements" (map to a list of statement nodes)
        # Support overloaded functions
        for func_def in ast.get("functions"):
            # Use dictionary of dictionaries to store overloaded functions
            function_name = func_def.get("name")
            num_args = len(func_def.get("args"))
            if (function_name not in self.func_name_to_ast):
                self.func_name_to_ast[function_name] = {}
            self.func_name_to_ast[function_name][num_args] = func_def
        

    # Need to also provide num_args to access overloaded functions
    def __get_func_by_name(self, name, num_args):
        # Allow to call functions anywhere in the file, even before functions are defined
        # Raise error if calling functions that are not defined
        if name not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        return self.func_name_to_ast[name][num_args]
# Statements: function calls, declarations, assignments, if, for, return.(PROCESSING)
# Function print() now support additional type boolean. Print out true or false,
#  no uppercases,no quotes. nil value will not be tested(checked)
    def __run_statements(self, statements):
        # all statements of a function are held in arg3 of the function AST node
        returned_value = Value(Type.NIL, None)
        for statement in statements:
            print(statement)
            if self.trace_output:
                print(statement)
            if statement.elem_type == InterpreterBase.FCALL_NODE:
                returned_value = self.__call_func(statement)
            elif statement.elem_type == "=":
                self.__assign(statement)
            elif statement.elem_type == InterpreterBase.VAR_DEF_NODE:
                self.__var_def(statement)
            elif statement.elem_type == InterpreterBase.IF_NODE:
                result = self.__if(statement)
                # if block has return statement, terminate the function
                if (result is not None):
                    # print(result.value())
                    return result
            elif statement.elem_type == InterpreterBase.FOR_NODE:
                self.__for(statement)
            elif statement.elem_type == InterpreterBase.RETURN_NODE:
                # print(statement.get("expression"))
                # print(self.__return(statement).value())
                return self.__return(statement)
        return returned_value
    # Support recursion via function calls (checked)not entirely sure, could have some potential bugs
    # Support overloaded functions if they take different numbers of parameters(checked)
    # functions can return a value : return a default value of nil if functions
    # don't have return command, or have it but without returned values (TO-DO)
    # can call functions anywhere, even before functions are defined (checked)
    # raise error if calling functions that are not defined (checked)
    # raise ErrorType.NAME_ERROR if calling functions with wrong number of arguments(checked)
    # Don't need to consider the case that defining 2 functions with same names and parameters 
    # Defining functions with name print, inputi, inputs will not be tested 
    def __call_func(self, call_node):
        func_name = call_node.get("name")
        if func_name == "print":
            return self.__call_print(call_node)
        elif func_name in ["inputi", "inputs"]:
            return self.__call_input(call_node)
        # check to see if calling function are defined
        elif func_name in self.func_name_to_ast:
            num_args = len(call_node.get("args"))
            # calling function must have the right num of arguments
            if num_args in self.func_name_to_ast[func_name]:  
                func_node = self.func_name_to_ast[func_name][num_args]
                # print("returned vallue of calling function: ",self.__run_func(call_node, func_node))
                return self.__run_func(call_node, func_node)
            else:
                super().error(ErrorType.NAME_ERROR, f"Function {func_name} not found, wrong num_arg")
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {func_name} not found {self.func_name_to_ast}")

    def __run_func(self, call_node, func_node):
        self.env.enter_scope()
        for arg, para in zip(call_node.get("args"), func_node.get("args")):
            result = self.__eval_expr(arg)
            self.env.create(para.get("name"), result)
            # print(self.env.get(para.get("name")).value())
        return_value = self.__run_statements(func_node.get("statements"))
        # print("Return value after __run_function: ",return_value.value())
        self.env.exit_scope()
        # print("Return value after __run_function: ",return_value)
        return return_value
    
    def __call_print(self, call_ast):
        output = ""
        for arg in call_ast.get("args"):
            result = self.__eval_expr(arg)  # result is a Value object
            output = output + get_printable(result)
        super().output(output)
        return Value(Type.NIL, None) # checked, print() always returns value of nil

    def __call_input(self, call_ast):
        args = call_ast.get("args")
        if args is not None and len(args) == 1:
            result = self.__eval_expr(args[0])
            super().output(get_printable(result))
        elif args is not None and len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR, "No inputi() function that takes > 1 parameter"
            )
        inp = super().get_input()
        if call_ast.get("name") == "inputi":
            return Value(Type.INT, int(inp))
        # we can support inputs here later
        if call_ast.get("name") == "inputs":
            return Value(Type.STRING, inp)

    def __assign(self, assign_ast):
        var_name = assign_ast.get("name")
        value_obj = self.__eval_expr(assign_ast.get("expression"))
        if not self.env.set(var_name, value_obj):
            super().error(
                ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
            )

    def __var_def(self, var_ast):
        var_name = var_ast.get("name")
        if not self.env.create(var_name, Value(Type.INT, 0)):
            super().error(
                ErrorType.NAME_ERROR, f"Duplicate definition for variable {var_name}"
            )
    # if statement may only have if clause or have both if and else clauses, no elif clause
    # conditionals are expressions, variables or values. Generating an error if 
    # these conditionals are not evaluated to a bool type. ErrorType.TYPE_ERROR(checked)
    # if statements have curly brackets around it
    # program also supports nested if(TO-DO) checked but could still have potential bugs
    # self.dict holds 3 keys: "condition", "statements", "else-statements"(map to NONE
    # if no else clause, otherwise statements in this block will be executed once condition is false)(checked)
    def __if(self, if_ast):
        self.env.enter_scope()
        # print(if_ast.get("condition"))
        condition_result = self.__eval_expr(if_ast.get("condition"))
        
        # print(self.env.get("a").value())
        if (condition_result.type() != Type.BOOL):
            super().error(ErrorType.TYPE_ERROR, f"If condition does not return bool value")
        # execute statement in the if block if condition is true
        returned_value = None
        if condition_result.value():
            returned_value = self.__run_statements(if_ast.get("statements"))
            # print(returned_value)
        else:
            else_clause_return = if_ast.get("else-staements")
            if else_clause_return != None:
                # print("running statements in else block")
                returned_value = self.__run_statements(else_clause_return)
        self.env.exit_scope()
        return returned_value

        
    # for(initializtion; condition; update){statement...statement} 
    # "init" maps to initialization: must be an assignment statement of some variables to an initial value(checked)
    # "condition" maps to expressions, variables, values that are evaluated to bool type, otherwise
    # raise an error ErrorType.TYPE_ERROR
    # "update" maps to an assignment statement that performs update of looping variable
    # "statements" maps to a list of statements, which only executed if condition is true
    # Program supports nested loops (TO-DO)checked but not entirely sure
    def __for(self, for_ast):
        self.env.enter_scope()
        initialization = for_ast.get("init")
        if (initialization.elem_type == "="):
            self.__assign(initialization)
        else:
            super().error(ErrorType.TYPE_ERROR,"Initialization in loop must be an assignment")
        loop_flag = True
        while loop_flag:
            condition = self.__eval_expr(for_ast.get("condition"))
            if (condition.type() != Type.BOOL):
                super().error(ErrorType.TYPE_ERROR, "Loop condition must evaluate to bool values")
            statements = for_ast.get("statements")
            if condition.value():
                self.__run_statements(statements)
            else:
                loop_flag = False
            update = for_ast.get("update")
            if update.elem_type == "=":
                self.__assign(update)
            else:
                super().error(ErrorType.TYPE_ERROR, "Update in loops must be an assignment")
        self.env.exit_scope()


    # "expression" maps to returned object, which is an expression, a variable, a value or nothing.
    # immediately terminate the current function and return to a calling function
    # including the cases where return statements in nested "if" or "for" blocks (TO-DO)
    # return statement in main() will terminate the program.(TO-DO)
    # if returning expressions or variables, they are evaluated first before returning to the calling function
    # return nothing means return default value nil
    # 
    def __return(self, return_ast):
        expression = return_ast.get("expression")
        # print(return_ast, expression)
        # print(expression)
        if (expression is None):
            # print("return none")
            return Value(Type.NIL, None)
        # print(isinstance(self.__eval_expr(expression), Value))
        # if isinstance(self.__eval_expr(expression), Value):
            # print(self.__eval_expr(expression).value())
        return self.__eval_expr(expression)


    def __eval_expr(self, expr_ast):
        # print(expr_ast)
        if expr_ast.elem_type == InterpreterBase.INT_NODE:
            # print("return an int here")
            return Value(Type.INT, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.STRING_NODE:
            return Value(Type.STRING, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.BOOL_NODE:
            return Value(Type.BOOL, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.VAR_NODE:
            var_name = expr_ast.get("name")
            val = self.env.get(var_name)
            if val is None:
                super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")
            return val
        # the returned value from the function will be used in the expression
        # print() returns nil
        # && and || muse use strict evaluation.(both arguments must be evaluated in all cases)
        if expr_ast.elem_type == InterpreterBase.FCALL_NODE:
            return self.__call_func(expr_ast)
        if expr_ast.elem_type in (self.ARITH_OPS | self.COMP_OPS | self.LOG_OPS | self.STR_OPS):
            return self.__eval_op(expr_ast)
        if expr_ast.elem_type == InterpreterBase.NIL_NODE:
            return Value(Type.NIL, None)
        
    def __eval_op(self, ops_ast):
        if(ops_ast.elem_type not in ["neg", "!"]):
            # print(ops_ast)
            left_value_obj = self.__eval_expr(ops_ast.get("op1"))
            right_value_obj = self.__eval_expr(ops_ast.get("op2"))
            # print(left_value_obj, right_value_obj)
            # print(left_value_obj, right_value_obj.value())
            # Legal to compare different types (including None) with == and !=
            # Illegal to compare diferent tyes with the rest of comparison operations(checked)
            #  if happened, raise ErrorType.TYPE_ERROR(checked)
            if left_value_obj.type() != right_value_obj.type():
                if ops_ast.elem_type == "==":
                    return Value(Type.BOOL, False)
                elif ops_ast.elem_type == "!=":
                    return Value(Type.BOOL, True)
                else:
                    super().error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible types for {ops_ast.elem_type} operation",)
            if ops_ast.elem_type not in self.op_to_lambda[left_value_obj.type()]:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible operator {ops_ast.elem_type} for type {left_value_obj.type()}",
                )
            f = self.op_to_lambda[left_value_obj.type()][ops_ast.elem_type]
            # print(left_value_obj.value(), right_value_obj.value())
            return f(left_value_obj, right_value_obj)
        else:
            op1_obj = self.__eval_expr(ops_ast.get("op1"))
            if(op1_obj.type()== Type.INT and ops_ast.elem_type == "neg"):
                f = self.op_to_lambda[op1_obj.type()][ops_ast.elem_type]
                # print("negative got here")
                return f(op1_obj)
            if(op1_obj.type() == Type.BOOL and ops_ast.elem_type == "!"):
                f = self.op_to_lambda[op1_obj.type()][ops_ast.elem_type]
                return f(op1_obj)
           
            


    def __setup_ops(self):
        self.op_to_lambda = {Type.INT: {},
                            Type.BOOL: {},
                            Type.STRING: {},
                            Type.NIL: {}
        }
        # set up operations on integers
        # ARITH_OPS = {"+", "-", "*", "/", "-"}
        # # Comparison operations
        # COMP_OPS = {"==", "!=", "<", "<=", ">", ">="}
        # # Logical operations (precedence order negation > comparison and arithmetic operations > && > ||)
        # # Parser already takes care of it, no special handling nedded.
        # Illegal to use arithmetic operation on non-integer types
        int_operation = {
            "+": lambda x, y: Value(x.type(), x.value() + y.value( )),
            "-": lambda x, y: Value(x.type(), x.value() - y.value()),
            "*": lambda x, y: Value(x.type(), x.value() * y.value()),
            "/": lambda x, y: Value(x.type(), x.value() // y.value()),
            "neg": lambda x : Value(x.type(), -x.value()),
            "==": lambda x, y: Value(Type.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.value() != y.value()),
            "<": lambda x, y: Value(Type.BOOL, x.value() < y.value()),
            "<=": lambda x, y: Value(Type.BOOL, x.value() <= y.value()),
            ">": lambda x, y: Value(Type.BOOL, x.value() > y.value()),
            ">=": lambda x, y: Value(Type.BOOL, x.value() >= y.value())
        }
        # LOG_OPS = {"||", "&&", "!", "==", "!="}
        bool_operation = {
            "||": lambda x, y: Value(x.type(), x.value() or y.value()),
            "&&": lambda x, y: Value(x.type(), x.value() and y.value()),
            "!": lambda x : Value(x.type(), not x.value()),
            "==": lambda x, y: Value(x.type(), x.value() == y.value()),
            "!=": lambda x, y: Value(x.type(), x.value() != y.value())
        }
        # STR_OPS = {"+"}
        str_operation = {
            "+": lambda x, y: Value(x.type(), x.value() + y.value()),
            "==": lambda x, y: Value(Type.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.value() != y.value())
        }
        nil_operation = {
            "==": lambda x, y: Value(Type.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.value() != y.value())
        }
        self.op_to_lambda[Type.INT].update(int_operation)
        self.op_to_lambda[Type.BOOL].update(bool_operation)
        self.op_to_lambda[Type.STRING].update(str_operation)
        self.op_to_lambda[Type.NIL].update(nil_operation)

        # add other operators here later for int, string, bool, etc
# def main():
#     program =    """
#      func foo() {
#  print(1);
# }

# func bar() {
#  return nil;
# }

# func main() {
#  var x;
#  x = foo();
#  if (x == nil) {
#   print(2);
#  }
#  var y;
#  y = bar();
#  if (y == nil) {
#   print(3);
#  }
 
# }

# """
#     test = Interpreter()
#     test.run(program)
# main()