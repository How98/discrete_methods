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
        # for op in operators:
        #     iterVar = r'\b' + re.escape(op) + r'\b'
        #     temp = re.sub(iterVar, ' ', temp)
        variables = [var for var in re.split(r'\s+', temp) if var and var not in ('(', ')')]
        # variables = list(set(temp.split()))
        variables = list(set(variables))
        #? this is necesary in case an operator is attached to a variable or if it's empty
        for op in operators:
            for var in variables:
                if op in var:
                    # print(f'var: {var}') #!debug
                    variables.remove(var)
                    new_var = var.replace(op, '')
                    # print(f'new_var: {new_var}') #!debug
                    variables.append(new_var)
                if var == '':
                    variables.remove(var)
                    
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
    
    def parenthesisFinder(self, logicalList: list[str]) -> list[tuple[int, int]]:
        '''
        This function will retun a list of tuples with the indexes of the parenthesis in the logicalList, the list is in order of evaluation
        '''
        numberOfParenthesis = logicalList.count('(')
        parenthesisIndexes = []
        alreadyEvaluatedIdexes = []
        for i in range(numberOfParenthesis):
            # print(f'iteration {i}, alreadyEvaluatedIdexes: {alreadyEvaluatedIdexes}') #!debug
            openIndex = logicalList.index('(')
            # print(f'openIndex: {openIndex}') #!debug
            if openIndex in alreadyEvaluatedIdexes:
                # print('hi') #!debug
                openIndex = logicalList[openIndex+1:].index('(') + openIndex +1
            
            closeIndex = logicalList.index(')')
            # print(f'closeIndex: {closeIndex}') #!debug
            if closeIndex in alreadyEvaluatedIdexes:
                # print('closeIndex in alreadyEvaluatedIdexes') #!debug
                # print(f'logicalList[closeIndex+1:]: {logicalList[closeIndex+1:]}') #!debug
                closeIndex = logicalList[closeIndex+1:].index(')') + closeIndex + 1

            #we need to check if there's a opening parenthesis before the closing one
            condition =  True
            while condition:
                condition = False
                # print(f'openIndex: {openIndex}, closeIndex: {closeIndex}') #!debug
                # print(f'logicalList[openIndex+1:closeIndex]: {logicalList[openIndex+1:closeIndex]}') #!debug
                whileIndex = logicalList[openIndex+1:closeIndex].index('(') + openIndex + 1
                # print(f'whileIndex: {whileIndex}') #!debug
                if whileIndex != openIndex and whileIndex not in alreadyEvaluatedIdexes:
                    openIndex = whileIndex
                    
                else:
                    # print('No more opening parenthesis')
                    condition = False
            parenthesisIndexes.append((openIndex, closeIndex))
            alreadyEvaluatedIdexes.append(openIndex)
            alreadyEvaluatedIdexes.append(closeIndex)
        return parenthesisIndexes
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
        return truthTable
    
    def individualEvaluator(self, variables: list[dict[str, bool]], logicallist: list[str]) -> bool:
        '''
        This function will evaluate the logical list with the a given set of variables with defined boolean values
        '''
        LogicalPriority = ['not', 'and', 'or', '->', '<->', '<-', 'xor']
        #the first priority is to evalueate the parenthesis
        parenthesisIndexes = self.parenthesisFinder(logicallist)
        for indexes in parenthesisIndexes: #this list is in order of evaluation
            openIndex, closeIndex = indexes
            subList = logicallist[openIndex+1:closeIndex]
            print(f'subList: {subList}') #!debug
            # now we need to evaluate the subList
            priorityIndexList = []
            for subIndex, element in enumerate(subList):
                if element in LogicalPriority:
                    logicalIndex = LogicalPriority.index(element)
                    print(f'element: {element}, logicalIndex: {logicalIndex}') #!debug
                    #now we need a function to evaluate based on the logical index
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
        print('')
        print('Debugging:')
        print('')
        print(f"Expression: {self.expression}")
        print('step 1:')
        variables = self.getVariables()
        print(f'Variables: {variables}')
        print('step 2:')
        operators = self.getOperators()
        print(f'Operators: {operators}')
        print('step 3:')
        logicalList = self.createLogicalList()
        print(f'Logical list: {logicalList}')
        print('step 4:')
        parenthesis = self.parenthesisFinder(logicalList)
        print(f'parenthesis: {parenthesis}')
        self.truthTable(variables)
        print('step 5:')
        self.individualEvaluator([('a', True), ('b', False), ('c', True)], logicalList)
        # self.evaluate(a=True, b=False, c=True)

if __name__ == "__main__":
    # Example usage
    expr = LogicalExpression("a and (b or (not c))")
    expr.debugger()
    # print(f"Expression result: {result}")