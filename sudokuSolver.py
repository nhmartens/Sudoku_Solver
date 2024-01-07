import copy

def sudokuSolver(input):
    sudoku = copy.deepcopy(input)
    solutions_count = 0
    def possible(row, column, number):
        for i in range(len(sudoku)):
            if i != column and sudoku[row][i] == number: 
                return False
            
            if i != row and sudoku[i][column] == number: 
                return False
            
        rowSection = (row // 3) * 3
        columnSection = (column // 3) * 3
        for i in range(3):
            for j in range(3):
                if (rowSection + i != row or columnSection + j != column) and sudoku[rowSection + i][columnSection + j] == number:
                    return False
        return True
    
    def validGrid():
        for row_index, row in enumerate(sudoku):
            for col_index, number in enumerate(row):
                if number != 0:
                    if not possible(row_index, col_index, number):
                        return False
        return True


    def solveBacktracking():
        nonlocal solutions_count
        
        for row in range(len(sudoku)):
            for col in range(len(sudoku)):
                if sudoku[row][col] == 0:
                    for digit in range(1,10):
                        if possible(row, col, digit):
                            sudoku[row][col] = digit
                            if solveBacktracking():
                                return True
                            sudoku[row][col] = 0
                    return False
        return True
    if validGrid():
        if solveBacktracking():
            print("Solution found:")
            for row in sudoku:
                print(row)
            print("")
            return sudoku
        else:
            print("No solution has been found")
            return None
    else:
        print("Invalid Grid. Most likely a number has been inaccurately detected")
        return None


memory = {}
def updateMemory(row, column, number):
    rowSection = (row // 3) * 3
    columnSection = (column // 3) * 3
    
    relevantRows = set([rowSection, rowSection + 1, rowSection + 2])
    relevantRows.remove(row)
    relevantColumns = set([columnSection, columnSection + 1, columnSection + 2])
    relevantColumns.remove(column)
    
    keysToDiscard = []
    
    for key, value in memory.items():
        if key[0] == row or key[1] == column:
            value.discard(number)
        elif key[0] in relevantRows and key[1] in relevantColumns:
            value.discard(number)
        if len(value) == 0:
            keysToDiscard.append(key)
    for k in keysToDiscard:
        del memory[k]

def solve(input):
    def possibleSet(row, column):
        output = set([1,2,3,4,5,6,7,8,9])
        for i in range(len(input)):
            output.discard(input[row][i])
            output.discard(input[i][column])
        
        rowSection = (row // 3) * 3
        columnSection = (column // 3) * 3
        
        for i in range(3):
            for j in range(3):
                output.discard(input[rowSection + i][columnSection + j])
        memory[(row, column)] = output
        return output
    
    for row in range(len(input)):
        for column in range(len(input)):
            if (input[row][column] == 0):
                possibleSet(row, column)
                
    while memory:
        copy = memory.copy()
        for key, value in copy.items():
            if len(value) == 1:
                digit = value.pop()
                input[key[0]][key[1]] = digit
                updateMemory(key[0], key[1], digit)
                break
    return input

if __name__ == "__main__":
    sudoku = [
        [9, 0, 5, 0, 6, 0, 0, 0, 0],
        [0, 0, 4, 0, 0, 1, 5, 0, 7],
        [0, 0, 0, 0, 0, 0, 0, 0, 3],
        [0, 0, 9, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 8, 0, 0, 2, 0, 0],
        [6, 0, 0, 0, 0, 7, 8, 5, 0],
        [0, 6, 0, 0, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 0, 5, 3, 8, 0],
        [1, 0, 0, 0, 4, 0, 0, 0, 0]
        ]
    sudokuSolver(sudoku)
