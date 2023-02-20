from coverage.cover_utils import covered

def test_covers():
    result = covered("prototype/resources/flies_example.pl",["flies(a)","flies(b)"])

    assert result == True


def test_not_covers():
    result = covered("prototype/resources/flies_example.pl",["flies(c)","flies(d)"])

    assert result == False