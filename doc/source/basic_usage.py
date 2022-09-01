# start_imports
import os
import tempfile
import pandas as pd
from table_compositor.table_compositor import build_presentation_model

# There are equivalent classes for using xlsxwriter library. Namely,
# XlsxWriterCompositor and XlsxWriterStyleHelper
from table_compositor.xlsx_writer import OpenPyxlCompositor
from table_compositor.xlsx_styles import OpenPyxlStyleHelper

# end_imports

# start_basic_example_2
def basic_example2():

    df = pd.DataFrame(
        dict(a=[10, 20, 30, 40, 50], b=[0.1, 0.9, 0.2, 0.6, 0.3]), index=[1, 2, 3, 4, 5]
    )

    def style_func(idx, col):
        if col == "b":
            return OpenPyxlStyleHelper.get_style(number_format="0.00%")
        else:
            # for 'a' we do dollar format
            return OpenPyxlStyleHelper.get_style(number_format="$#,##.00")

    # create a presentation model
    # note the OpenPyxlStyleHelper function available in xlsx_styles module. But a return value of style function
    # can be any dict whose keys are attributes of the OpenPyxl cell object.
    presentation_model = build_presentation_model(
        df=df,
        data_value_func=lambda idx, col: df.loc[idx, col] * 10
        if col == "a"
        else df.loc[idx, col],
        data_style_func=style_func,
        header_value_func=lambda node: node.value.capitalize(),
        header_style_func=lambda _: OpenPyxlStyleHelper.default_header_style(),
        index_value_func=lambda node: node.value * 100,
        index_style_func=lambda _: OpenPyxlStyleHelper.default_header_style(),
        index_name_func=lambda _: "Basic Example",
        index_name_style_func=lambda _: OpenPyxlStyleHelper.default_header_style(),
    )

    # create a layout, which is usually a nested list of presentation models
    layout = [presentation_model]

    # render to xlsx
    output_fp = os.path.join(tempfile.gettempdir(), "basic_example2.xlsx")
    OpenPyxlCompositor.to_xlsx(layout=layout, output_fp=output_fp)


# end_basic_example_2

# start_basic_example_3
def basic_example3():

    df = pd.DataFrame(
        dict(
            a=[10, 20, 30, 40],
            b=[0.1, 0.9, 0.2, 0.6],
            d=[50, 60, 70, 80],
            e=[200, 300, 400, 500],
        )
    )
    df.columns = pd.MultiIndex.from_tuples(
        [("A", "x"), ("A", "y"), ("B", "x"), ("B", "y")]
    )
    df.index = pd.MultiIndex.from_tuples([(1, 100), (1, 200), (2, 100), (2, 200)])
    print(df)

    def index_style_func(node):
        # node.key here could be one of (1,), (1, 100), (2,), (2, 100), (2, 200)
        bg_color = "FFFFFF"
        if node.key == (1,) or node.key == (2,):
            bg_color = "9E80B8"
        elif node.key[1] == 100:
            bg_color = "4F90C1"
        elif node.key[1] == 200:
            bg_color = "6DC066"
        return OpenPyxlStyleHelper.get_style(bg_color=bg_color)

    def header_style_func(node):
        bg_color = "FFFFFF"
        if node.key == ("A",) or node.key == ("B",):
            bg_color = "9E80B8"
        elif node.key[1] == "x":
            bg_color = "4F90C1"
        elif node.key[1] == "y":
            bg_color = "6DC066"
        return OpenPyxlStyleHelper.get_style(bg_color=bg_color)

    # create a presentation model
    # note the OpenPyxlStyleHeloer function available in xlsx_styles module. But a return value of style function
    # can be any dict whose keys are attributes of the OpenPyxl cell object.
    presentation_model = build_presentation_model(
        df=df,
        index_style_func=index_style_func,
        header_style_func=header_style_func,
        index_name_func=lambda _: "Multi-Hierarchy Example",
    )

    # create a layout, which is usually a nested list of presentation models
    layout = [presentation_model]

    # render to xlsx
    output_fp = os.path.join(tempfile.gettempdir(), "basic_example3.xlsx")
    OpenPyxlCompositor.to_xlsx(layout=layout, output_fp=output_fp)


# end_basic_example_3


# start_layout_example_1
def layout_example1():

    df = pd.DataFrame(
        dict(a=[10, 20, 30, 40, 50], b=[0.1, 0.9, 0.2, 0.6, 0.3]), index=[1, 2, 3, 4, 5]
    )

    def style_func(idx, col):
        if col == "b":
            return OpenPyxlStyleHelper.get_style(number_format="0.00%")
        else:
            # for 'a' we do dollar format
            return OpenPyxlStyleHelper.get_style(number_format="$#,##.00")

    # create a presentation model
    # note the OpenPyxlStyleHeloer function available in xlsx_styles module. But a return value of style function
    # can be any dict whose keys are attributes of the OpenPyxl cell object.
    presentation_model = build_presentation_model(
        df=df,
        data_value_func=lambda idx, col: df.loc[idx, col] * 10
        if col == "a"
        else df.loc[idx, col],
        data_style_func=style_func,
        header_value_func=lambda node: node.value.capitalize(),
        header_style_func=lambda _: OpenPyxlStyleHelper.default_header_style(),
        index_value_func=lambda node: node.value * 100,
        index_style_func=lambda _: OpenPyxlStyleHelper.default_header_style(),
        index_name_func=lambda _: "Basic Example",
        index_name_style_func=lambda _: OpenPyxlStyleHelper.default_header_style(),
    )

    # start_layout_code_1
    # create a layout, which is usually a nested list of presentation models
    layout = [[presentation_model], [[presentation_model], [presentation_model]]]

    # render to xlsx
    output_fp = os.path.join(tempfile.gettempdir(), "layout_vertical_example1.xlsx")
    # the default value for orientation is 'vertical'
    OpenPyxlCompositor.to_xlsx(
        layout=layout, output_fp=output_fp, orientation="vertical"
    )

    output_fp = os.path.join(tempfile.gettempdir(), "layout_horizontal_example1.xlsx")
    OpenPyxlCompositor.to_xlsx(
        layout=layout, output_fp=output_fp, orientation="horizontal"
    )
    print("Writing xlsx file=", output_fp)

    # mutiple nesting
    layout_complex = [
        presentation_model,
        [presentation_model, [presentation_model, presentation_model]],
    ]

    output_fp = os.path.join(tempfile.gettempdir(), "layout_complex_example1.xlsx")
    OpenPyxlCompositor.to_xlsx(
        layout=layout_complex, output_fp=output_fp, orientation="vertical"
    )
    print("Writing xlsx file=", output_fp)
    # end_layout_code_1


# end_layout_example_1


if __name__ == "__main__":
    basic_example2()
    basic_example3()
    layout_example1()
