import pytest

from macpie.util.validators import validate_bool_kwarg


def test_validate_bool_kwarg():

    assert validate_bool_kwarg(True, "test") is True

    assert validate_bool_kwarg(False, "test") is False

    assert validate_bool_kwarg(None, "test") is None

    with pytest.raises(ValueError):
        validate_bool_kwarg("not_bool", "test")
