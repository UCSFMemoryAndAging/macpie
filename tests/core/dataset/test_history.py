from pathlib import Path

from macpie.core.dataset import LavaDataset


current_dir = Path(__file__).parent.absolute()


def test_history():
    primary = LavaDataset.from_file(current_dir / "primary.xlsx")
    secondary = LavaDataset.from_file(current_dir / "secondary.xlsx")

    secondary.date_proximity(
        primary,
        get='closest',
        when='earlier_or_later',
        days=90
    )

    secondary.group_by_keep_one()

    assert len(secondary.history) == 2

    record1 = secondary.history[0]
    assert record1['func_name'] == 'date_proximity'

    record2 = secondary.history[1]
    assert record2['func_name'] == 'group_by_keep_one'
