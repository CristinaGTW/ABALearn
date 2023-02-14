from coverage.cover_utils import covered

def test_covers():
    result = covered("flies(a)")

    assert result == True


def test_not_covers():
    result = covered("flies(c)")

    assert result == False