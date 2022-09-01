import os
import unittest
import typing as tp
from functools import partial

import table_compositor.html_writer as htmlw
from table_compositor.presentation_model import PresentationModel
from table_compositor.test.unit_test import fixtures
from table_compositor.xlsx_writer import OpenPyxlCompositor


LayoutT = tp.List[tp.Union[PresentationModel, tp.List[PresentationModel]]]


def get_expected_output_folder(fname: str) -> str:
    base_path = os.path.join(os.path.dirname(__file__), "..", "expected")
    os.makedirs(base_path, exist_ok=True)
    expected_fp = os.path.join(base_path, fname)
    return expected_fp


class TestUnit(unittest.TestCase):
    def _test_helper(
        self,
        name: str,
        func_to_call: tp.Callable[[], LayoutT],
        engine: tp.Type[OpenPyxlCompositor],
        *args: str
    ) -> None:
        layout: LayoutT = func_to_call()

        assert all(isinstance(x, str) for x in args)

        # we drop the engine name from the test, since the expected file is the same for both engines
        fname = name.replace("_" + engine.__name__, "") + ".html"

        actual_html_str = htmlw.HTMLWriter.to_html(layout, *args, border=1)
        # drop the libray name since expected file is the same
        expected_fname = fname.replace("_static_frame", "").replace("_pandas", "")
        expected_fp = get_expected_output_folder(expected_fname)

        with open(expected_fp) as f:
            expected_str = f.read()
            self.assertEqual(expected_str, actual_html_str)

    def test_html_writer(self) -> None:
        scenarios = fixtures.get_scenarios()

        for s in scenarios:
            self._test_helper(
                s.name,
                partial(
                    s.fixture_func,
                    grid=s.grid,
                    nested=s.nested,
                    callback_func_cls=fixtures.HtmlCallBackFunc,
                ),
                s.engine_and_callback_funcs_cls[0],
                s.orientation,
            )


if __name__ == "__main__":
    unittest.main()
