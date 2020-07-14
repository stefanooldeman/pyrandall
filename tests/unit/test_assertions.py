from pyrandall.types import AssertionCall, SkipAssertionCall


def test_value_not_matches():
    ac = AssertionCall("description", "this")
    ac.actual_value = "that"
    assert not ac.passed()
    assert ac.called

def test_value_matches():
    ac = AssertionCall("description", "this")
    ac.actual_value = "this"
    assert ac.passed()
    assert ac.called

def test_skip_passed():
    ac = SkipAssertionCall("description")
    assert ac.passed()
    assert not ac.called
