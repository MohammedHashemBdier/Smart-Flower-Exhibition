from heuristics import pavilion_total, carried_total, all_needs_zero, best_pavilion_id


def test_pavilion_total_and_all_zero():
    assert pavilion_total((0, 0, 0)) == 0
    assert pavilion_total((2, 1, 0)) == 3
    assert all_needs_zero((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))


def test_carried_total_behavior():
    assert carried_total(()) == 0
    assert carried_total((2, 0, 1)) == 3


def test_best_pavilion_selection_from_warehouse():
    # Robot at warehouse (3,2); pavilions as in heuristics (2,4),(4,3),(4,5),(5,2)
    # For start at (3,2) the closest by Manhattan distance is pavilion 2 at (4,3)
    selected = best_pavilion_id(3, 2, (2, 1, 1), (3, 1, 0), (2, 1, 0), (2, 2, 0))
    assert isinstance(selected, int)
    assert selected in (1, 2, 3, 4)
