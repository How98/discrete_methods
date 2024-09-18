import numpy as np
import itertools
import re
import pandas as pd
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
        #we need to check which operators aperar in the string
        operator_names = ['+', '-', '*', '/', '(', ')', 'and', 'or', 'not', '->', '<->', '<-', 'xor']
        expressionWithoutVariablesAndSpaces = self.expression.replace(' ', '')
        for var in variables:
            iterOp = r'\b' + re.escape(var) + r'\b'
            expressionWithoutVariablesAndSpaces = re.sub(iterOp, '', expressionWithoutVariablesAndSpaces)
        for op in operator_names:
            if op in expressionWithoutVariablesAndSpaces:
                operators.append(op)
        return operators
    
    #region Logical operators
    def andOperator(self, a: bool, b: bool) -> bool:
        match (a, b):
            case (True, True):
                return True
            case (_, _):
                return False
    
    def orOperator(self, a: bool, b) -> bool:
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
    
    def createLogicalList(self) -> list[str]:
        #we need to check the order of variables and operators to create a list of logical operations
        expression = self.expression
        variables = self.getVariables()
        operators = self.getOperators()
        expression = expression.replace(' ', '')
        for op in operators:
            expression = expression.replace(op, f' {op} ')
        logicalList = expression.split()
        print(f"Logical list: {logicalList}") #!debug
        return logicalList
        
    def truthTable(self, variables: list[str]) -> pd.DataFrame:
        variables = self.getVariables()
        n = len(variables)
        rows = 2**n
        combinations = list(itertools.product([False, True], repeat=n))
        # combinations = [list(comb) for comb in combinations]
        combinations = np.array(combinations)
        # print(f"Combinations: {combinations}") #!debug
        # print(f'variables: {variables}') #!debug
        #we initilize the truth table with the variables all in false then we will change them
        truthTable = pd.DataFrame(combinations, columns=variables)
        truthTable['result'] = False
        print('truthTable:') #!debug
        print(truthTable) #!debug
        pass
        
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
        variables = self.getVariables()
        operators = self.getOperators()
        logicalList = self.createLogicalList()
        self.truthTable(variables)
        
        # self.evaluate(a=True, b=False, c=True)

if __name__ == "__main__":
    # Example usage
    expr = LogicalExpression("a and (b or not c)")
    expr.debugger()
    # print(f"Expression result: {result}")