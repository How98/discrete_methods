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
        operators = ['(', ')', 'xand', 'xor', 'not', '<->', '->', '<-', 'or', 'and'] #! the order of analysis is important  
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
        # variables = self.getVariables()        
        #we need to check which operators aperar in the string
        operator_names = ['(', ')', 'xand', 'xor', 'not', '<->', '->', '<-', 'or', 'and'] #! again, the order of detection is really important
        stringExpression = self.expression
        # for var in variables:
        #     stringExpression = stringExpression.replace(var, ' ')
        for op in operator_names:
            if op in stringExpression:
                # print(f'op: {op}') #!debug
                # print(f'stringExpression: {stringExpression}') #!debug
                operators.append(op)
                stringExpression = stringExpression.replace(op, ' ').replace('  ', ' ')
        operators = list(set(operators))
        operators = sorted(operators, key=lambda x: len(x), reverse=True)
        return operators
                
        # expressionWithoutVariablesAndSpaces = self.expression.replace(' ', '')
        # for var in variables:
        #     iterOp = r'\b' + re.escape(var) + r'\b'
        #     expressionWithoutVariablesAndSpaces = re.sub(iterOp, '', expressionWithoutVariablesAndSpaces)
        # for op in operator_names:
        #     if op in expressionWithoutVariablesAndSpaces:
        #         operators.append(op)
        # return operators
    
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
            openIndex = logicalList.index('(')
            if openIndex in alreadyEvaluatedIdexes:
                openIndex = logicalList[openIndex+1:].index('(') + openIndex +1
            
            closeIndex = logicalList.index(')')
            if closeIndex in alreadyEvaluatedIdexes:
                closeIndex = logicalList[closeIndex+1:].index(')') + closeIndex + 1

            #we need to check if there's a opening parenthesis before the closing one
            condition = False   
            if logicalList[openIndex+1:closeIndex].count('(') > 0:
                condition =  True
            while condition:
                condition = False
                whileIndex = logicalList[openIndex+1:closeIndex].index('(') + openIndex + 1
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
        # print('individual evaluation') #!debug
        logicallist = self._createLogicalList()
        logicallist = self._variablesToBool(variables, logicallist)
        # print(f'logicallist: {logicallist}') #!debug
        #the first priority is to evalueate the parenthesis
        parenthesisIndexes = self._parenthesisFinder()
        for indexes in parenthesisIndexes: #this list is in order of evaluation
            openIndex, closeIndex = indexes
            subList = logicallist[openIndex+1:closeIndex]
            if len(subList) == 1:
                logicallist = logicallist[:openIndex] + subList + logicallist[closeIndex+1:]
                continue
            boolResult = self._logicListEvaluator(subList, variables)
            logicallist = logicallist[:openIndex] + [boolResult] + logicallist[closeIndex+2:]
        # print(f'logicallist: {logicallist}') #!debug
        boolResult = self._logicListEvaluator(logicallist, variables)
        # print(f'boolResult: {boolResult}') #!debug
        # print('')
        return boolResult
    
    def _evaluationOrderIndexes(self, elementList: list) -> list[tuple[int, int]]:
        '''
        This function will return the indexes of the operators in the elementList in order of evaluation
        '''
        priorityIndexList = []
        LogicalPriority = ['not', 'and', 'or', '->', '<->', '<-', 'xor']
        # print(f'elementList: {elementList}') #!debug
        for subIndex, element in enumerate(elementList):
            if element in LogicalPriority:
                logicalIndex = LogicalPriority.index(element)
                priorityIndexList.append((logicalIndex, subIndex))        
        priorityIndexList = sorted(priorityIndexList, key=lambda x: x[0])
        # print(f'priorityIndexList: {priorityIndexList}') #!debug
        return priorityIndexList
    
    def _maxPriorityIndex(self, elementList: list) -> int:
        indexList = self._evaluationOrderIndexes(elementList)
        return indexList[0]
        
    def _variablesToBool(self, variables: dict[str, bool], logicalList: list[str]) -> list:
        for index, element in enumerate(logicalList):
            for variable in list(variables.keys()):
                if element == variable:
                    logicalList[index] = variables[variable]
        return logicalList
            
    def _operatorEvaluator(self, operator: str, opereatorIndex: int, logicalList: list, variables: dict[str, bool]) -> bool:
        match operator:
            case 'and':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
                result = self._andOperator(expression[0], expression[2])
                return result
            case 'or':
                expression = logicalList[opereatorIndex-1:opereatorIndex+2]
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
                result = self._xandOperator(expression[0], expression[2])
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
                if operatorIndex != 0 and len(logicalList) != 2:
                    logicalList = logicalList[:operatorIndex] + [boolResult] + logicalList[operatorIndex+2:]
                elif len(logicalList) == 2:
                    logicalList = [boolResult]
                else:
                    logicalList = [boolResult] + logicalList[operatorIndex+2:]
                return logicalList
            case __:
                logicalList = logicalList[:operatorIndex-1] + [boolResult] + logicalList[operatorIndex+2:]
                return logicalList
    
    def _logicListEvaluator(self, evaluationList: list, variables: dict[str, bool]) -> bool:
        #new idea
        operators = []
        for element in evaluationList:
            if element in self.operators:
                operators.append(element)
        
        for _ in range(len(operators)):
            priorityIndex = self._maxPriorityIndex(evaluationList)
            boolResult = self._operatorEvaluator(evaluationList[priorityIndex[1]], priorityIndex[1], evaluationList, variables)
            evaluationList = self._replaceBoolResult(evaluationList, priorityIndex[1], priorityIndex[0], boolResult)
            # print(f'evaluationList: {evaluationList}') #!debug
        return evaluationList[0]    
       
    #endregion
    
    #region Results functions and debugging
    def truthTable(self) -> pd.DataFrame:
        variables = self.variables
        n = len(variables)
        combinations = list(itertools.product([False, True], repeat=n))
        # combinations = np.array(combinations)
        truthTable = pd.DataFrame(combinations, columns=variables)
        resultArray = []
        for _, row in truthTable.iterrows():
            variables = dict(row)
            variables = {key: bool(value) for key, value in variables.items()}
            # print('')
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
        # print('')
        # print('step 5: test individual evaluator')
        # result = self.evaluate({'a': True, 'b': False, 'c': True})
        print('')
        print('step 6: create and evaluate truth table')
        truthTable = self.truthTable()
        print('Truth table:')
        print(truthTable)

if __name__ == "__main__":
    
    # Example usage
    # expr = LogicalExpression("a->b and not (c or d)")
    # expr.debugger()
    
    
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
    try:
        expr = LogicalExpression(expression)
        #iternal checking for the expression
        print('Variables: ', expr.variables)
        print('Operators: ', expr.operators)
    except Exception as e:
        print(f'wrong input: {e}')
        sys.exit(1)
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
    