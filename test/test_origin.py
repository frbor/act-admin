import pytest

from act.admin.origin import float_or_fatal


def test_float_or_fatal_should_fail() -> None:

    default = 0.8

    for value in ("X", "x0.8", "0.8x", {"trust": 0.8}):

        # https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            float_or_fatal(value, default)

            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code == 1


def test_float_or_fatal_should_succeed() -> None:

    default = 0.8

    assert float_or_fatal("0.5", default) == 0.5
    assert float_or_fatal("0", default) == 0
    assert float_or_fatal("1", default) == 1
    assert float_or_fatal(None, default) == default
    assert float_or_fatal("", default) == default
