import sys
from io import StringIO

from rules import SmartFlowerEngine


def test_engine_reaches_goal_and_prints_solution(capsys):
    engine = SmartFlowerEngine()
    # Run engine; it prints solution to stdout
    engine.reset()
    engine.run()

    captured = capsys.readouterr()
    assert "Success: all pavilion demands were satisfied." in captured.out
    assert "Solution path printed successfully." in captured.out
