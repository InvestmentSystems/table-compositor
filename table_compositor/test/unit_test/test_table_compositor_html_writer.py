import os
import tempfile
import unittest
from functools import partial

import table_compositor.html_writer as htmlw
import table_compositor.test.unit_test.table_compositor_fixtures as tcfx


def get_expected_output_folder(fname):
    base_path = os.path.join(
            os.path.dirname(__file__),
            '..', 'expected')
    os.makedirs(base_path, exist_ok=True)
    expected_fp = os.path.join(base_path, fname)
    return expected_fp


class TestHTMLWriterMeta(type):
    def __new__(cls, names, bases, attrs):
        def test_func_constructor(name, func_to_call, engine, *args):
            def _func(self):
                layout = func_to_call()
                # we drop the engine name from the test, since the expected file is the same for both engines
                fname = name.replace('_' + engine.__name__, '') + ".html"
                actual_html_str = htmlw.HTMLWriter.to_html(layout, *args, border=1)
                expected_fp = get_expected_output_folder(fname)
                self.compare(expected_fp, actual_html_str)
            return _func

        scenarios = tcfx.get_scenarios()

        for s in scenarios:
            attrs[s.name] = test_func_constructor(s.name, partial(
                    s.fixture_func,
                    grid=s.grid,
                    nested=s.nested,
                    callback_func_cls=tcfx.HtmlCallBackFunc),
                    s.engine_and_callback_funcs_cls[0],
                    s.orientation)

        return type.__new__(cls, names, bases, attrs)

class TestUnit(unittest.TestCase, metaclass=TestHTMLWriterMeta):
    '''
    All test methods will be produced by the metaclass
    '''

    def compare(self, expected_fp, actual_html_str):

        with open(expected_fp) as f:
            expected_str = f.read()
            self.assertEqual(expected_str, actual_html_str)


if __name__ == '__main__':
    unittest.main()
