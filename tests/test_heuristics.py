import pytest

from heuristics import calculate_h, best_pavilion_id, carried_total, has_invalid_coordinates


def test_calculate_h_basic():
    # robot at (1,3), each pavilion needs 1 bouquet
    h = calculate_h(1, 3, (1,), (1,), (1,), (1,))
    assert h == 6


def test_best_pavilion_and_carried_total():
    bid = best_pavilion_id(1, 3, (1,), (1,), (1,), (1,))
    assert bid == 1
    assert carried_total(()) == 0
    assert carried_total((2, 1)) == 3


def test_invalid_coordinates():
    assert has_invalid_coordinates(-1, 0, 5, 5)
    assert has_invalid_coordinates(0, -1, 5, 5)
    assert not has_invalid_coordinates(1, 1, 5, 5)
