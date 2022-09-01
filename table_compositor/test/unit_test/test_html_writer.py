import os
import typing as tp
import unittest

import numpy as np

import table_compositor.html_writer as htmlw
from table_compositor.presentation_model import PresentationModel
from table_compositor.test.unit_test.conftest import (
    Fixture,
    LayoutT,
    get_scenarios,
)
from table_compositor.util import df_type_to_str

LayoutT = tp.List[tp.Union[PresentationModel, tp.List[PresentationModel]]]


class HtmlCallBackFunc:
    def __init__(self, df):
        self.df = df

    @staticmethod
    def _to_dollar_format(v):
        if not isinstance(v, (np.float, np.int)):
            return v
        r = "${:0,.0f}".format(v)
        return r

    def data_value_func(self, r, c):
        return df_type_to_str(self.df.loc[r, c])

    def data_style_func(self, r, c):
        if isinstance(self.df.loc[r, c], (np.int_, np.float, np.uint)):
            return dict(text_align="right", padding="10px")
        return dict(text_align="left", padding="10px")

    def header_value_func(self, node):
        return node.value

    def header_style_func(self, node):
        return dict(
            text_align="center",
            background_color="#4F81BD",
        )

    def index_value_func(self, node):
        return node.value

    def index_style_func(self, node):
        return dict(
            text_align="center",
            background_color="#4F81BD",
        )

    def index_name_style_func(self, node):
        return dict(text_align="left", padding="10px")

    def index_name_value_func(self, value):
        return value


def get_expected_output_folder(fname: str) -> str:
    base_path = os.path.join(os.path.dirname(__file__), "..", "expected")
    os.makedirs(base_path, exist_ok=True)
    expected_fp = os.path.join(base_path, fname)
    return expected_fp


class TestUnit(unittest.TestCase):
    def _test_helper(self, fixture: Fixture) -> None:
        layout: LayoutT = fixture.fixture_func(
            grid=fixture.grid,
            nested=fixture.nested,
            callback_func_cls=HtmlCallBackFunc,
        )

        # we drop the engine name from the test, since the expected file is the same for both engines
        fname = fixture.name.replace("_" + fixture.engine.__name__, "") + ".html"

        actual_html_str = htmlw.HTMLWriter.to_html(
            layout, orientation=fixture.orientation, border=1
        )

        # drop the libray name since expected file is the same
        expected_fname = fname.replace("_static_frame", "").replace("_pandas", "")
        expected_fp = get_expected_output_folder(expected_fname)

        with open(expected_fp) as f:
            expected_str = f.read()
            self.assertEqual(expected_str, actual_html_str)

    def test_html_writer(self) -> None:
        for fixture in get_scenarios():
            self._test_helper(fixture)


if __name__ == "__main__":
    unittest.main()
