import pytest

from macpie import validatortools


def test_validate_bool_kwarg():

    assert validatortools.validate_bool_kwarg(True, "test") is True

    assert validatortools.validate_bool_kwarg(False, "test") is False

    assert validatortools.validate_bool_kwarg(None, "test") is None

    with pytest.raises(ValueError):
        validatortools.validate_bool_kwarg("not_bool", "test")
