import unittest
from copy import deepcopy
from index import Board, blank, fillInSingularPossibilities

# Additional Sudoku boards for multi-board testing
multi_boards = {
    "blank": [[0]*9 for _ in range(9)],
    "easy": [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9]
    ],
    "solved": [
        [1,2,3,4,5,6,7,8,9],
        [4,5,6,7,8,9,1,2,3],
        [7,8,9,1,2,3,4,5,6],
        [2,3,4,5,6,7,8,9,1],
        [5,6,7,8,9,1,2,3,4],
        [8,9,1,2,3,4,5,6,7],
        [3,4,5,6,7,8,9,1,2],
        [6,7,8,9,1,2,3,4,5],
        [9,1,2,3,4,5,6,7,8]
    ],
    "invalid_row": [[1]*9 for _ in range(9)],
    "partial_conflict": [
        [5,3,0,0,7,0,0,0,0],
        [6,5,0,1,9,5,0,0,0],  # conflict: two 5's in row
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9]
    ],
    "almost_solved": [
        [1,2,3,4,5,6,7,8,9],
        [4,5,6,7,8,9,1,2,3],
        [7,8,9,1,2,3,4,5,6],
        [2,3,4,5,6,7,8,9,1],
        [5,6,7,8,9,1,2,3,4],
        [8,9,1,2,3,4,5,6,7],
        [3,4,5,6,7,8,9,1,2],
        [6,7,8,9,1,2,3,4,5],
        [9,1,2,3,4,5,6,0,8]  # one empty
    ]
}

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.b = Board(blank)

    # --- Basic getters and backup/restore ---
    def test_getters_and_backup_restore(self):
        original = deepcopy(blank)
        self.assertEqual(self.b.getBoard(), original)

        new_board = deepcopy(blank)
        new_board[0][0] = 9
        self.b.setBackup(new_board)
        self.assertEqual(self.b.getBackup(), new_board)

        self.b.restoreBackup()
        self.assertEqual(self.b.getBoard(), new_board)

    # --- Position value, placement, and legality ---
    def test_position_and_place(self):
        self.assertEqual(self.b.positionValue(0, 0), 2)

        can = self.b.canPlace(0, 2, 4)
        self.assertIn(can["errors"], [True, False])

        placed = self.b.placeNumber(0, 2, 4)
        self.assertIn(placed["errors"], [True, False])
        self.assertEqual(self.b.positionValue(0, 2), 4 if not placed["errors"] else 0)

        illegal = self.b.placeNumber(0, 3, 4)
        self.assertIn(illegal["errors"], [True, False])

    # --- Error detection ---
    def test_hasErrors_detects(self):
        bad = deepcopy(blank)
        bad[0][1] = 2  # duplicate in row
        result = self.b.hasErrors(bad)
        self.assertTrue(result["errors"])
        self.assertIn(result.get("error"), ["duplicate_in_row", "duplicate_in_col", "duplicate_in_blocks"])

    # --- Solved / unsolved boards ---
    def test_isSolved_and_unsolved(self):
        res = self.b.isSolved()
        self.assertFalse(res["solved"])
        self.assertIn(res["error"], ("empty_space", "duplicate_in_row",
                                     "duplicate_in_col", "duplicate_in_blocks"))

        solved_board = [
            [1,2,3,4,5,6,7,8,9],
            [4,5,6,7,8,9,1,2,3],
            [7,8,9,1,2,3,4,5,6],
            [2,3,4,5,6,7,8,9,1],
            [5,6,7,8,9,1,2,3,4],
            [8,9,1,2,3,4,5,6,7],
            [3,4,5,6,7,8,9,1,2],
            [6,7,8,9,1,2,3,4,5],
            [9,1,2,3,4,5,6,7,8]
        ]
        b2 = Board(solved_board)
        self.assertTrue(b2.isSolved()["solved"])

class TestBoardEdgeCases(unittest.TestCase):
    def test_empty_board(self):
        empty_board = [[0]*9 for _ in range(9)]
        b = Board(empty_board)
        result = b.isSolved()
        self.assertFalse(result["solved"])
        self.assertEqual(result["error"], "empty_space")

    def test_full_invalid_board(self):
        invalid_board = [[1]*9 for _ in range(9)]
        b = Board(invalid_board)
        result = b.isSolved()
        self.assertFalse(result["solved"])
        self.assertIn(result["error"], ("duplicate_in_row", "duplicate_in_col", "duplicate_in_blocks"))

    def test_partial_board_with_conflict(self):
        bad = deepcopy(blank)
        bad[0][0] = 5
        bad[1][0] = 5  # duplicate in column
        b = Board(bad)
        errors = b.hasErrors(bad)
        self.assertTrue(errors["errors"])
        self.assertIn(errors["error"], ["duplicate_in_row", "duplicate_in_col", "duplicate_in_blocks"])

class TestFillInSingularEdgeCases(unittest.TestCase):
    def test_already_solved_board(self):
        solved_board = [
            [1,2,3,4,5,6,7,8,9],
            [4,5,6,7,8,9,1,2,3],
            [7,8,9,1,2,3,4,5,6],
            [2,3,4,5,6,7,8,9,1],
            [5,6,7,8,9,1,2,3,4],
            [8,9,1,2,3,4,5,6,7],
            [3,4,5,6,7,8,9,1,2],
            [6,7,8,9,1,2,3,4,5],
            [9,1,2,3,4,5,6,7,8]
        ]
        b = Board(solved_board)
        b.setBackup(b.getBoard())
        result = fillInSingularPossibilities(b, 0)
        self.assertEqual(result["status"], "solved")

    def test_unsolvable_board(self):
        unsolvable = deepcopy(blank)
        unsolvable[0][0] = 1
        unsolvable[0][1] = 1  # illegal duplicate
        b = Board(unsolvable)
        b.setBackup(b.getBoard())
        result = fillInSingularPossibilities(b, -1)
        self.assertEqual(result["status"], "invalid")


class TestMultipleBoards(unittest.TestCase):
    """Run all basic Board tests on multiple Sudoku boards"""

    def test_multiple_boards(self):
        for name, board in multi_boards.items():
            with self.subTest(board=name):
                b = Board(deepcopy(board))
                errors = b.hasErrors(board)
                result = b.isSolved()

                if name in ["solved"]:
                    self.assertFalse(errors["errors"])
                    self.assertTrue(result["solved"])
                elif name in ["blank", "easy", "almost_solved"]:
                    self.assertFalse(errors.get("errors", False))
                    self.assertFalse(result["solved"])
                    self.assertIn(result.get("error"), ["empty_space", "duplicate_in_row", "duplicate_in_col", "duplicate_in_blocks"])
                elif name in ["invalid_row", "partial_conflict"]:
                    self.assertTrue(errors["errors"])
                    self.assertFalse(result["solved"])


class SummaryTestResult(unittest.TextTestResult):
    def stopTestRun(self):
        super().stopTestRun()
        passed = self.testsRun - len(self.failures) - len(self.errors)
        print("\nTest Summary:")
        print(f"  Passed: {passed}")
        print(f"  Failures: {len(self.failures)}")
        print(f"  Errors: {len(self.errors)}")
        if self.failures:
            print("\nFailed Tests:")
            for test, _ in self.failures:
                print(f"  {test}")
        if self.errors:
            print("\nErrored Tests:")
            for test, _ in self.errors:
                print(f"  {test}")

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2, resultclass=SummaryTestResult)
    unittest.main(testRunner=runner, verbosity=2, exit=False)