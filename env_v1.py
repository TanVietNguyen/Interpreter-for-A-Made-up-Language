# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        # Environment is now a stack of dictionaries
        # Each dictionary stores variables at one scope
        self.environment = [{}]

    # Gets value of the variable at the nearest scope 
    def get(self, symbol):
        for scope in reversed(self.environment):
            if symbol in scope:
                return scope[symbol]
        return None

    # Sets value to the variable at the nearest scope
    def set(self, symbol, value):
        for scope in reversed(self.environment):
            if symbol in scope:
                self.environment[self.environment.index(scope)][symbol] = value
                return True
        return False
        
    # Always create the variable at the top of stack, which is where
    # all variables are stored at the current block
    def create(self, symbol, start_val):
        if symbol not in self.environment[-1]: 
          self.environment[-1][symbol] = start_val 
          return True
        return False
    
    def enter_scope(self):
        self.environment.append({})
    
    def exit_scope(self):
        self.environment.pop()
