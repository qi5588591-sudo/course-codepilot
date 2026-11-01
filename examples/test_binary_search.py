from solution import binary_search


def test_first():
    assert binary_search([1, 3, 5], 1) == 0


def test_last():
    assert binary_search([1, 3, 5], 5) == 2


def test_single():
    assert binary_search([3], 3) == 0


def test_missing():
    assert binary_search([1, 3, 5], 4) == -1


def test_empty():
    assert binary_search([], 3) == -1
