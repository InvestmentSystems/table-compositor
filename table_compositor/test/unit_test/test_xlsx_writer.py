from pytest import mark
import os
import shutil
import tempfile

from openpyxl import load_workbook

from table_compositor.test.unit_test.conftest import (
    Scenario,
    LayoutT,
    get_scenarios,
)


def get_expected_output_folder(fname: str) -> str:
    base_path = os.path.join(os.path.dirname(__file__), "..", "expected")
    os.makedirs(base_path, exist_ok=True)
    expected_fp = os.path.join(base_path, fname)
    return expected_fp


def _revalidate(expected_fp: str, output_fp: str) -> None:
    # use this to create the initial expected output
    shutil.copyfile(output_fp, expected_fp)


def _compare(expected_fp: str, output_fp: str) -> None:

    ews = load_workbook(expected_fp).active
    ows = load_workbook(output_fp).active

    for i in range(1, ews.max_row):
        for j in range(1, ews.max_column):

            e_cell = ews.cell(row=i, column=j)
            o_cell = ows.cell(row=i, column=j)

            assert e_cell.value == o_cell.value
            assert e_cell.number_format == o_cell.number_format
            assert e_cell.border.left.style == o_cell.border.left.style


@mark.parametrize("scenario", get_scenarios())
def test_xlsx_writer(scenario: Scenario) -> None:
    layout: LayoutT = scenario.func(
        grid=scenario.grid,
        nested=scenario.nested,
        callback_func_cls=scenario.callback_func_cls,
        frame_library=scenario.frame_library,
    )

    # we drop the engine name from the test, since the expected file is the same for both engines
    fname = scenario.name.replace("_" + scenario.engine.__name__, "") + ".xlsx"

    # this is a quick hack to have the same expected fp for for pandas and static_frame
    expected_fname = fname.replace("_static_frame", "").replace("_pandas", "")

    with tempfile.TemporaryDirectory(suffix="table_compositor") as root_temp_dir:
        temp_dir = tempfile.mkdtemp(dir=root_temp_dir)
        output_fp = os.path.join(temp_dir, fname)
        scenario.engine.to_xlsx(
            layout=layout, output_fp=output_fp, orientation=scenario.orientation
        )
        expected_fp = get_expected_output_folder(expected_fname)

        _compare(expected_fp, output_fp)
