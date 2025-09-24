import math
from copy import deepcopy
from pprint import pprint
import os
import timeit
import random
import sys

# Detect platform to decide clear-screen command
is_windows = sys.platform.startswith('win')

# Utility function to clear terminal
def clear():
  if is_windows:
    os.system('cls')
  else:
    os.system('clear')

# Initial Sudoku puzzle (0 represents empty spaces)
blank = [[2,8,0,0,0,0,0,0,1],
         [0,0,0,8,0,1,0,0,4],
         [0,0,4,0,7,0,3,0,0],
         [0,2,0,0,5,0,0,6,0],
         [0,0,3,1,0,9,7,0,0],
         [0,1,0,0,8,0,0,5,0],
         [0,0,1,0,6,0,8,0,0],
         [5,0,0,2,0,3,0,0,0],
         [9,0,0,0,0,0,0,1,6]]

class Board:
  """
  Represents a Sudoku board with utility functions to place numbers,
  check validity, and test if the board is solved.
  """

  def __init__(self, board):
    # Store a copy of the board and a backup state
    self.board = deepcopy(board)
    self.backup = deepcopy(board)
    self.lastChoice = 0   # remembers last guess (for random backtracking)

  # --- Getters and setters ---
  def getBoard(self):
    return self.board

  def getBackup(self):
    return self.backup

  def setBackup(self, board):
    self.backup = deepcopy(board)

  def restoreBackup(self):
    self.board = deepcopy(self.backup)

  # --- Validation functions ---
  def isSolved(self):
    """
    Checks if the Sudoku is solved:
      - No empty cells
      - No duplicate numbers in rows, columns, or 3x3 blocks
    Returns a dict with 'solved': True/False and optional error reason.
    """
    result = {'solved': True}
    flippedBoard = [[] for _ in range(9)]  # columns
    blockBoard = [[] for _ in range(9)]    # 3x3 blocks

    for row, rowArray in enumerate(self.board):
      numberFrequency = {}
      for col, value in enumerate(rowArray):
          # Assign values to corresponding block and column
          blockBoard[math.floor(col/3)+(math.floor(row/3) * 3)].append(value)
          flippedBoard[col].append(value)

          # Track duplicates in row
          if value in numberFrequency:
            numberFrequency[value] += 1
          elif value != 0:
            numberFrequency[value] = 1
      # Check row duplicates
      for number, count in numberFrequency.items():
        if count > 1:
          result = {"solved": False, "error": "duplicate_in_row"}

    # Check block duplicates
    for rowArray in blockBoard:
      numberFrequency = {}
      for value in rowArray:
          if value in numberFrequency:
            numberFrequency[value] += 1
          elif value != 0:
            numberFrequency[value] = 1
      for count in numberFrequency.values():
        if count > 1:
          result = {"solved": False, "error": "duplicate_in_blocks"}

    # Check column duplicates
    for rowArray in flippedBoard:
      numberFrequency = {}
      for value in rowArray:
          if value in numberFrequency:
            numberFrequency[value] += 1
          elif value != 0:
            numberFrequency[value] = 1
      for count in numberFrequency.values():
        if count > 1:
          result = {"solved": False, "error": "duplicate_in_col"}

      # If any cell is empty, puzzle is not solved
      for column in rowArray:
        if column == 0:
          result = {"solved": False, "error": "empty_space"}

    return result

  def hasErrors(self, testArray):
    """
    Like isSolved, but checks only for rule violations (duplicates).
    Used when testing potential placements.
    """
    result = {'errors': False}
    flippedBoard = [[] for _ in range(9)]
    blockBoard = [[] for _ in range(9)]

    for row, rowArray in enumerate(testArray):
      numberFrequency = {}
      for col, value in enumerate(rowArray):
          blockBoard[math.floor(col/3)+(math.floor(row/3) * 3)].append(value)
          flippedBoard[col].append(value)

          if value in numberFrequency:
            numberFrequency[value] += 1
          elif value != 0:
            numberFrequency[value] = 1
      for count in numberFrequency.values():
        if count > 1:
          result = {"errors": True, "error": "duplicate_in_row"}

    for rowArray in blockBoard:
      numberFrequency = {}
      for value in rowArray:
          if value in numberFrequency:
            numberFrequency[value] += 1
          elif value != 0:
            numberFrequency[value] = 1
      for count in numberFrequency.values():
        if count > 1:
          result = {"errors": True, "error": "duplicate_in_blocks"}

    for rowArray in flippedBoard:
      numberFrequency = {}
      for value in rowArray:
          if value in numberFrequency:
            numberFrequency[value] += 1
          elif value != 0:
            numberFrequency[value] = 1
      for count in numberFrequency.values():
        if count > 1:
          result = {"errors": True, "error": "duplicate_in_col"}

    return result

  # --- Placement utilities ---
  def placeNumber(self, row, column, value):
    """
    Attempts to place a number at (row, column).
    If the placement causes no rule violation, updates board and returns it.
    Otherwise returns an error.
    """
    oldBoard = deepcopy(self.board)
    oldBoard[row][column] = value
    newBoard = oldBoard

    if not self.hasErrors(newBoard)['errors']:
      self.board = deepcopy(newBoard)
      return {"errors": False, 'board': newBoard}
    else:
      return {"errors": True, "error": "illegal_placement"}

  def canPlace(self, row, column, value):
    """
    Tests whether a value can be placed at (row, column) without committing.
    """
    oldBoard = deepcopy(self.board)
    oldBoard[row][column] = value
    newBoard = oldBoard

    if not self.hasErrors(newBoard)['errors']:
      return {"errors": False, 'board': newBoard}
    else:
      return {"errors": True, "error": "illegal_placement"}

  def positionValue(self, row, column):
    """
    Returns the value at a given position.
    """
    return deepcopy(self.board[row][column])

# --- Create Sudoku board instance ---
sudoku = Board(blank)

clear()
pprint(sudoku.getBoard())

start = timeit.default_timer()

# --- Solving logic ---
def fillInSingularPossibilities(sudoku, n):
  """
  Sudoku solving algorithm:
  - For each empty cell, calculate possible numbers.
  - If a cell has only one possible number, place it.
  - Repeat until no single-possibility cells exist.
  - If stuck, make a guess and backtrack if it leads to an error.
  
  Arguments:
    sudoku: Board instance
    n: control flag for recursion/backtracking
       -1: initial run
        0: normal recursion
        1: backtracking mode
  """
  potentialBoardValues = [[] for _ in range(9)]
  for i in range(9):
    for position in range(9):
      if sudoku.positionValue(i, position) != 0:
        potentialBoardValues[i].append(sudoku.positionValue(i, position))
      else:
        potentialBoardValues[i].append([])

  hasSingular = False
  invalidBoard = False

  # Try to fill cells with a single possible value
  for row, rowArray in enumerate(sudoku.board):
    for col, value in enumerate(rowArray):
      if value == 0:
        # Check all possible numbers 1–9
        for potential in range(1,10):
          if not sudoku.canPlace(row, col, potential)['errors']:
            potentialBoardValues[row][col].append(potential)

        if len(potentialBoardValues[row][col]) == 0:
          # Dead end (no valid number)
          invalidBoard = True

        if len(potentialBoardValues[row][col]) == 1:
          # Single possibility → place it
          hasSingular = True
          sudoku.placeNumber(row, col, potentialBoardValues[row][col][0])
          clear()
          # pprint(sudoku.getBoard())

  # Handle invalid board (backtrack)
  if invalidBoard:
    invalidBoard = False
    sudoku.restoreBackup()
    if n == -1:
      print("Impossible Solve")
      return {"status": "invalid"}
    fillInSingularPossibilities(sudoku, -1)

  # Continue if we placed something
  if hasSingular:
    hasSingular = False
    if n == -1:
      sudoku.setBackup(sudoku.getBoard())
    fillInSingularPossibilities(sudoku, 0)
  else:
    # Check if solved
    if sudoku.isSolved()['solved']:
      clear()
      stop = timeit.default_timer()
      print("Solved sudoku board in", stop-start, "seconds.")
      pprint(sudoku.getBoard())
      return {"status": "solved"}
    else:
      # Backtracking
      if n == 1:
        sudoku.restoreBackup()
        fillInSingularPossibilities(sudoku, 1)
      else:
        # Guess a value in a multi-choice cell
        for row, rowArray in enumerate(potentialBoardValues):
          for col, value in enumerate(rowArray):
            if not isinstance(value, int):  # means it's a list of possibilities
              choice = random.choice(value)
              while choice == sudoku.lastChoice:  # avoid repeating last guess
                choice = random.choice(value)
              sudoku.lastChoice = choice
              sudoku.placeNumber(row, col, choice)
              fillInSingularPossibilities(sudoku, 0)

# --- Run the solver ---
#fillInSingularPossibilities(sudoku, -1)


sudoku = Board(blank)

# index.py
if __name__ == "__main__":
    sudoku = Board(blank)
    clear()
    pprint(sudoku.getBoard())

    start = timeit.default_timer()
    fillInSingularPossibilities(sudoku, -1)
    print("Solved sudoku board in", timeit.default_timer() - start, "seconds.")
    pprint(sudoku.getBoard())

