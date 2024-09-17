import numpy as np
import itertools
import re

class LogicalExpression:
    
    def __init__(self, expression):
        self.expression = expression
        
    def getVariables(self) -> list[str]:
        variables = []
        #we need to define the mathematical operators to devide the string input
        operators = ['+', '-', '*', '/', '(', ')', 'and', 'or', 'not', '->', '<->', '<-', 'xor', 'xand']
        temp = self.expression
        for op in operators:
            iterVar = r'\b' + re.escape(op) + r'\b'
            temp = re.sub(iterVar, ' ', temp)
        variables = list(set(temp.split()))
        for op in operators:
            for var in variables:
                if op in var:
                    variables.remove(var)
                    new_var = var.replace(op, '')
                    variables.append(new_var)
                    
        # print(f"Variables: {variables}")
        return variables
    
    def getOperators(self) -> list[str]:
        operators = []
        variables = self.getVariables()
        print(f"Variables: {variables}") #!debug
        
        #we need to check which operators aperar in the string
        operator_names = ['+', '-', '*', '/', '(', ')', 'and', 'or', 'not', '->', '<->', '<-', 'xor']
        expressionWithoutVariablesAndSpaces = self.expression.replace(' ', '')
        for var in variables:
            iterOp = r'\b' + re.escape(var) + r'\b'
            expressionWithoutVariablesAndSpaces = re.sub(iterOp, '', expressionWithoutVariablesAndSpaces)
        for op in operator_names:
            if op in expressionWithoutVariablesAndSpaces:
                operators.append(op)
        print(f"Operators: {operators}") #!debug
        return operators
    
    #region Logical operators
    def andOperator(self, a, b) -> bool:
        match (a, b):
            case (True, True):
                return True
            case (_, _):
                return False
    
    def orOperator(self, a, b) -> bool:
        match (a, b):
            case (False, False):
                return False
            case (_, _):
                return True
    
    def notOperator(self, a: bool) -> bool:
        return not a
    
    def xorOperator(self, a, b) -> bool:
        return a != b
    
    def xandOperator(self, a, b) -> bool:
        return a == b
    
    def impliesOperator(self, a, b) -> bool:
        return not a or b
    #endregion        
    
    def createExpression(self):
        pass
        
    def truthTable(self):
        variables = self.getVariables()
        n = len(variables)
        rows = 2**n 
        
    # def evaluate(self, **kwargs):
    #     try:
    #         # Evaluate the expression with the given variables
    #         result = eval(self.expression, {}, kwargs)
    #         return result
    #     except Exception as e:
    #         print(f"Error evaluating expression: {e}")
    #         return None
    
    def debugger(self):
        print(f"Expression: {self.expression}")
        self.getVariables()
        self.getOperators()
        # self.evaluate(a=True, b=False, c=True)

if __name__ == "__main__":
    # Example usage
    expr = LogicalExpression("a and (b or not c)")
    expr.debugger()
    # print(f"Expression result: {result}")