import numpy as np
import itertools
import re
import pandas as pd
import sys
class LogicalExpression:
    
    def __init__(self, expression):
        self.expression = expression
        self.variables = self.getVariables()
        self.operators = self.getOperators()
        self.logicalList = self._createLogicalList()
        
    def getVariables(self) -> list[str]:
        variables = []
        #we need to define the mathematical operators to devide the string input
        operators = ['(', ')', 'and', 'or', 'not', '->', '<->', '<-', 'xor', 'xand']
        temp = self.expression
        variables = []
        for op in operators:
            temp = temp.replace(op, ' ')
            temp = temp.replace('  ', ' ')
        variables = temp.split()
        # print(f"temp: {temp}") #!
        # variables = [var for var in re.split(r'\s+', temp) if var and var not in ('(', ')')]
        variables = sorted(list(set(variables)))
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
                if var in operators:
                    variables.remove(var)
                    
        # print(f"Variables: {variables}")
        return variables
    
    def getOperators(self) -> list[str]:
        operators = []
        variables = self.getVariables()        
        #we need to check which operators aperar in the string
        operator_names = ['(', ')', 'and', 'or', 'not', '->', '<->', '<-', 'xor']
        expressionWithoutVariablesAndSpaces = self.expression.replace(' ', '')
        for var in variables:
            iterOp = r'\b' + re.escape(var) + r'\b'
            expressionWithoutVariablesAndSpaces = re.sub(iterOp, '', expressionWithoutVariablesAndSpaces)
        for op in operator_names:
            if op in expressionWithoutVariablesAndSpaces:
                operators.append(op)
        return operators
    
    #region Logical operators
    def _andOperator(self, a: bool, b: bool) -> bool:
        match (a, b):
            case (True, True):
                return True
            case (_, _):
                return False
    
    def _orOperator(self, a: bool, b) -> bool:
        match (a, b):
            case (False, False):
                return False
            case (_, _):
                return True
    
    def _notOperator(self, a: bool) -> bool:
        return not a
    
    def _xorOperator(self, a, b) -> bool:
        return a != b
    
    def _xandOperator(self, a, b) -> bool:
        return a == b
    
    def _impliesOperator(self, a, b) -> bool:
        return not a or b
    
    def _parenthesisFinder(self) -> list[tuple[int, int]]:
        '''
        This function will retun a list of tuples with the indexes of the parenthesis in the logicalList, the list is in order of evaluation
        '''
        logicalList = self.logicalList
        numberOfParenthesis = logicalList.count('(')
        parenthesisIndexes = []
        alreadyEvaluatedIdexes = []
        for _ in range(numberOfParenthesis):
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
    
    #region Evaluation methods
    def _createLogicalList(self) -> list[str]:
        #we need to check the order of variables and operators to create a list of logical operations
        expression = self.expression
        variables = self.getVariables()
        operators = self.getOperators()
        expression = expression.replace(' ', '')
        for op in operators:
            expression = expression.replace(op, f' {op} ')
        logicalList = expression.split()
        return logicalList
        
    def _individualEvaluator(self, variables: dict[str, bool]) -> bool:
        '''
        This function will evaluate the logical list with the a given set of variables with defined boolean values
        '''
        logicallist = self.logicalList
        # print('')
        # print(f'variables: {variables}') #!debug
        #the first priority is to evalueate the parenthesis
        parenthesisIndexes = self._parenthesisFinder()
        # print(f'parenthesisIndexes: {parenthesisIndexes}') #!debug
        for indexes in parenthesisIndexes: #this list is in order of evaluation
            openIndex, closeIndex = indexes
            subList = logicallist[openIndex+1:closeIndex]
            # print(f'subList: {subList}') #!debug
            boolResult = self._logicListEvaluator(subList, variables)
            # print(f'sub boolResult: {boolResult}') #!debug
            logicallist = logicallist[:openIndex] + [boolResult] + logicallist[closeIndex+2:]  
        # print('done with parenthesis') #!debug
        # print(f'logicallist: {logicallist}') #!debug
        boolResult = self._logicListEvaluator(logicallist, variables)
        # print(f'boolResult: {boolResult}') #!debug
        return boolResult
    
    def _evaluationOrderIndexes(self, elementList: list) -> list[tuple[int, int]]:
        '''
        This function will return the indexes of the operators in the elementList in order of evaluation
        '''
        priorityIndexList = []
        LogicalPriority = ['not', 'and', 'or', '->', '<->', '<-', 'xor']
        for subIndex, element in enumerate(elementList):
            if element in LogicalPriority:
                logicalIndex = LogicalPriority.index(element)
                priorityIndexList.append((logicalIndex, subIndex))        
        priorityIndexList = sorted(priorityIndexList, key=lambda x: x[0])
        return priorityIndexList
            
    def _operatorEvaluator(self, operator: str, opereatorIndex: int, logicalList: list, variables: dict[str, bool]) -> bool:
        for index, element in enumerate(logicalList):
            for variable in list(variables.keys()):
                if element == variable:
                    logicalList[index] = variables[variable]
        match operator:
            case 'and':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
                result = self._andOperator(expression[0], expression[2])
                return result
            case 'or':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
                # print(f'expression: {expression}') #!debug
                result = self._orOperator(expression[0], expression[2])
                return result
            case 'not':
                expression = logicalList[opereatorIndex:opereatorIndex+2]
                result = self._notOperator(expression[1])
                return result
            case '->':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
                result = self._impliesOperator(expression[0], expression[2])
                return result
            case '<-':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
                result = self._impliesOperator(expression[2], expression[0])
                return result
            case '<->':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
                result = self._xorOperator(expression[0], expression[2])
                return result
            case 'xor':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
                result = self._xorOperator(expression[0], expression[2])
                return result
            case __:
                print('wrong logic idiot')
                sys.exit(1)
        pass    
    
    def _replaceBoolResult(self, logicalList: list[str], operatorIndex: int, priorityIndex: int, boolResult: bool) -> list[str]:
        #depending on the operator we need to replace different types of elements
        match priorityIndex:
            case 0:
                # print(f'debug logicalList: {logicalList}') #!debug
                if operatorIndex != 0:
                    logicalList = logicalList[:operatorIndex-1] + [boolResult] + logicalList[operatorIndex+1:]
                if len(logicalList) == 2:
                    logicalList = [boolResult]
                else:
                    logicalList = [boolResult] + logicalList[operatorIndex+2:]
                # print(f'debug logicalList: {logicalList}') #!debug
                return logicalList
            case __:
                # print(f'debug logicalList: {logicalList}') #!debug
                logicalList = logicalList[:operatorIndex-1] + [boolResult] + logicalList[operatorIndex+2:]
                # print(f'debug logicalList: {logicalList}') #!debug
                return logicalList
    
    def _logicListEvaluator(self, logicList: list, variables: dict[str, bool]) -> bool:
        priorityIndexList = self._evaluationOrderIndexes(logicList)
        for priorityIndex in priorityIndexList:
            boolResult = self._operatorEvaluator(logicList[priorityIndex[1]], priorityIndex[1], logicList, variables)
            logicList = self._replaceBoolResult(logicList, priorityIndex[1], priorityIndex[0], boolResult)
        return logicList[0]
    #endregion
    
    #region Results functions and debugging
    def truthTable(self) -> pd.DataFrame:
        variables = self.variables
        n = len(variables)
        combinations = list(itertools.product([False, True], repeat=n))
        # combinations = np.array(combinations)
        truthTable = pd.DataFrame(combinations, columns=variables)
        resultArray = []
        logicalList = self._createLogicalList()
        for index, row in truthTable.iterrows():
            variables = dict(row)
            variables = {key: bool(value) for key, value in variables.items()}
            result = self._individualEvaluator(variables)
            resultArray.append(result)
        truthTable['result'] = resultArray
        return truthTable               

    def evaluate(self, variables: dict[str, bool]) -> None:
        print('Evaluating')
        print('')
        print(f"Expression: {self.expression}")
        print('')
        print(f'Variables: {variables}')
        print('')
        logicalList = self._createLogicalList()
        result = self._individualEvaluator(variables)
        print(f"Result: {result}")
        pass
    
    def debugger(self):
        print('')
        print('Debugging:')
        print('')
        print(f"Expression: {self.expression}")
        print('')
        print('step 1: get variables')
        variables = self.getVariables()
        print(f'Variables: {variables}')
        print('')
        print('step 2: get operators')
        operators = self.getOperators()
        print(f'Operators: {operators}')
        print('')
        print('step 3: get logical list')
        logicalList = self._createLogicalList()
        print(f'Logical list: {logicalList}')
        print('')
        print('step 4: find parenthesis')
        parenthesis = self._parenthesisFinder()
        print(f'parenthesis: {parenthesis}')
        print('')
        print('step 5: test individual evaluator')
        result = self.evaluate({'a': True, 'b': True, 'c': True})
        print('')
        print('step 6: create and evaluate truth table')
        truthTable = self.truthTable()
        print('Truth table:')
        print(truthTable)

if __name__ == "__main__":
    
    # Example usage
    expr = LogicalExpression("a<-(b or (not c))")
    expr.debugger()
    
    '''
    print('##############################################')
    print('                Math Logic                    ')
    print('##############################################')
    print('')
    print('available operators:')
    print('and, or, not, ->, <->, <-, xor, xand')
    print('')
    print('Example usage: a and (b or (not c))')
    print('')
    expression = input('Enter a logical expression: ')
    expr = LogicalExpression(expression)
    analysisType = input('Type of analysis (debug = d, evaluate = e, truthTable = tt): ')
    match analysisType:
        case 'd':
            expr.debugger()
        case 'e':
            variables = {}
            for var in expr.variables:
                value = input(f'Enter value for {var}: ')
                variables[var] = eval(value)
            expr.evaluate(variables)
        case 'tt':
            truthTable = expr.truthTable()
            print(truthTable)
        case __:
            print('Wrong input')
            sys.exit(1)
    '''