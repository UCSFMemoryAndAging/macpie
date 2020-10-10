from datetime import datetime

import pandas as pd
import pytest

from macpie.exceptions import DateProximityError


def test_params_1():
    d1 = {
        'PIDN': [1, 1, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'Col1': [7, 7, 9]
    }
    primary = pd.DataFrame(data=d1)

    d2 = {
        'PIDN': [1, 2, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'Col1': [7, 8, 9]
    }
    secondary = pd.DataFrame(data=d2)

    # Must pass argument "id_on" OR "id_left_on" and "id_right_on"
    with pytest.raises(DateProximityError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            id_left_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # Must pass argument "id_on" OR "id_left_on" and "id_right_on"
    with pytest.raises(DateProximityError):
        primary.mac.date_proximity(
            secondary,
            id_left_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # id_left_on and id_right_on must be same length
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_left_on='pidn',
            id_right_on=['pidn', 'col1'],
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # Must pass argument "date_on" OR "date_left_on" and "date_right_on"
    with pytest.raises(DateProximityError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            date_left_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # Must pass argument "date_on" OR "date_left_on" and "date_right_on"
    with pytest.raises(DateProximityError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_left_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # Must pass argument "date_on" OR "date_left_on" and "date_right_on"
    with pytest.raises(DateProximityError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # non-unique error
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # non-unique error with left_link_id specified
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            left_link_id='col1',
            merge='partial'
        )


def test_params_2():
    d1 = {
        'PIDN': [1, 2, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'Col1': [7, 8, 9]
    }
    primary = pd.DataFrame(data=d1)

    d2 = {
        'PIDN': [1, 2, 3],
        'DCDate': [datetime(2001, 3, 2), datetime(2001, 3, 2), datetime(2001, 8, 1)],
        'Col1': [7, 8, 9]
    }
    secondary = pd.DataFrame(data=d2)

    # invalid merge option
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='blah'
        )

    # merge suffixes not list-like
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial',
            merge_suffixes='not_list_like'
        )

    # merge suffixes has more than 2 items
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=90,
            merge='partial',
            merge_suffixes=('_x', '_y', '_z')
        )

    # invalid get option
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='blah',
            when='earlier_or_later',
            days=90,
            merge='partial'
        )

    # invalid when option
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='blah',
            days=90,
            merge='partial'
        )

    # days option can't be negative
    with pytest.raises(ValueError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days=-9,
            merge='partial'
        )

    # days option needs to be an integer
    with pytest.raises(TypeError):
        primary.mac.date_proximity(
            secondary,
            id_on='pidn',
            date_on='dcdate',
            get='closest',
            when='earlier_or_later',
            days='asdf',
            merge='partial'
        )
