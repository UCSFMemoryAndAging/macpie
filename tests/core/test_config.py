"""
As the config module was adapted from the pandas library,
so are the tests below.
URL: https://github.com/pandas-dev/pandas/blob/73da0ff2cafa1c2edbd54c806b4da6c698584f86/pandas/tests/config/test_config.py    # noqa: E501
Date: 2021-04-09
"""

import pandas as pd
import pandas._config.config as pandas_cf
import pytest

from macpie._config import config as cf
from macpie._config.config import OptionError


class TestConfig:
    @classmethod
    def setup_class(cls):
        from copy import deepcopy

        cls.cf = cf
        cls.gc = deepcopy(getattr(cls.cf, "_global_config"))
        cls.ro = deepcopy(getattr(cls.cf, "_registered_options"))

    def setup_method(self, method):
        setattr(self.cf, "_global_config", {})
        setattr(self.cf, "_registered_options", {})

    def teardown_method(self, method):
        setattr(self.cf, "_global_config", self.gc)
        setattr(self.cf, "_registered_options", self.ro)

    def test_api(self):
        # the pandas object exposes the user API
        assert hasattr(pd, "get_option")
        assert hasattr(pd, "set_option")
        assert hasattr(pd, "reset_option")

    def test_register_option(self):
        self.cf.register_option("a", 1, "doc")

        # can't register an already registered option
        msg = "Option 'a' has already been registered"
        with pytest.raises(OptionError, match=msg):
            self.cf.register_option("a", 1, "doc")

    def test_case_insensitive(self):
        self.cf.register_option("KanBAN", 1, "doc")

        assert self.cf.get_option("kanBaN") == 1
        self.cf.set_option("KanBan", 2)
        assert self.cf.get_option("kAnBaN") == 2

        # gets of non-existent keys fail
        msg = r"No such option exists: 'no_such_option'"
        with pytest.raises(OptionError, match=msg):
            self.cf.get_option("no_such_option")

    def test_get_option(self):
        self.cf.register_option("a", 1, "doc")
        self.cf.register_option("b.c", "hullo", "doc2")
        self.cf.register_option("b.b", None, "doc2")

        # gets of existing keys succeed
        assert self.cf.get_option("a") == 1
        assert self.cf.get_option("b.c") == "hullo"
        assert self.cf.get_option("b.b") is None

        # gets of non-existent keys fail
        msg = r"No such option exists: 'no_such_option'"
        with pytest.raises(OptionError, match=msg):
            self.cf.get_option("no_such_option")

    def test_set_option(self):
        self.cf.register_option("a", 1, "doc")
        self.cf.register_option("b.c", "hullo", "doc2")
        self.cf.register_option("b.b", None, "doc2")

        assert self.cf.get_option("a") == 1
        assert self.cf.get_option("b.c") == "hullo"
        assert self.cf.get_option("b.b") is None

        self.cf.set_option("a", 2)
        self.cf.set_option("b.c", "wurld")
        self.cf.set_option("b.b", 1.1)

        assert self.cf.get_option("a") == 2
        assert self.cf.get_option("b.c") == "wurld"
        assert self.cf.get_option("b.b") == 1.1

        msg = r"No such option exists: 'no.such.key'"
        with pytest.raises(OptionError, match=msg):
            self.cf.set_option("no.such.key", None)

    def test_set_option_multiple(self):
        self.cf.register_option("a", 1, "doc")
        self.cf.register_option("b.c", "hullo", "doc2")
        self.cf.register_option("b.b", None, "doc2")

        assert self.cf.get_option("a") == 1
        assert self.cf.get_option("b.c") == "hullo"
        assert self.cf.get_option("b.b") is None

    def test_reset_option(self):
        self.cf.register_option("a", 1, "doc", validator=pandas_cf.is_int)
        self.cf.register_option("b.c", "hullo", "doc2", validator=pandas_cf.is_str)
        assert self.cf.get_option("a") == 1
        assert self.cf.get_option("b.c") == "hullo"

        self.cf.set_option("a", 2)
        self.cf.set_option("b.c", "wurld")
        assert self.cf.get_option("a") == 2
        assert self.cf.get_option("b.c") == "wurld"

        self.cf.reset_option("a")
        assert self.cf.get_option("a") == 1
        assert self.cf.get_option("b.c") == "wurld"
        self.cf.reset_option("b.c")
        assert self.cf.get_option("a") == 1
        assert self.cf.get_option("b.c") == "hullo"

    def test_reset_option_all(self):
        self.cf.register_option("a", 1, "doc", validator=pandas_cf.is_int)
        self.cf.register_option("b.c", "hullo", "doc2", validator=pandas_cf.is_str)
        assert self.cf.get_option("a") == 1
        assert self.cf.get_option("b.c") == "hullo"

        self.cf.set_option("a", 2)
        self.cf.set_option("b.c", "wurld")
        assert self.cf.get_option("a") == 2
        assert self.cf.get_option("b.c") == "wurld"

    def test_callback(self):
        k = [None]
        v = [None]

        def callback(key):
            k.append(key)
            v.append(self.cf.get_option(key))

        self.cf.register_option("d.a", "foo", cb=callback)
        self.cf.register_option("d.b", "foo", cb=callback)

        del k[-1], v[-1]
        self.cf.set_option("d.a", "fooz")
        assert k[-1] == "d.a"
        assert v[-1] == "fooz"

        del k[-1], v[-1]
        self.cf.set_option("d.b", "boo")
        assert k[-1] == "d.b"
        assert v[-1] == "boo"

        del k[-1], v[-1]
        self.cf.reset_option("d.b")
        assert k[-1] == "d.b"


def test_system_columns():
    prefix = cf.get_option("column.system.prefix")
    assert prefix == "_mp"

    assert cf.get_option("column.system.abs_diff_days") == prefix + '_abs_diff_days'
    assert cf.get_option("column.system.diff_days") == prefix + '_diff_days'
    assert cf.get_option("column.system.duplicates") == prefix + '_duplicates'
    assert cf.get_option("column.system.merge") == prefix + '_merge'

    cf.set_option("column.system.prefix", "_macpie")

    new_prefix = cf.get_option("column.system.prefix")
    assert new_prefix == "_macpie"

    assert cf.get_option("column.system.abs_diff_days") == new_prefix + '_abs_diff_days'
    assert cf.get_option("column.system.diff_days") == new_prefix + '_diff_days'
    assert cf.get_option("column.system.duplicates") == new_prefix + '_duplicates'
    assert cf.get_option("column.system.merge") == new_prefix + '_merge'

    cf.reset_option("column.system.prefix")
    assert prefix == "_mp"
