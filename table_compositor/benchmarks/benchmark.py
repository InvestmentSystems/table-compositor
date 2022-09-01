"""
Module that will benchmark performance of table compositor when used with different engines
"""

import os
import tempfile
import time
import typing as tp

import numpy as np
import pandas as pd

import table_compositor.table_compositor as tbc
import table_compositor.xlsx_writer as tcew
from table_compositor.xlsx_styles import (
    OpenPyxlStyleHelper,
    XlsxWriterStyleHelper,
)

NUMBER_FORMAT = '_($* #,##0_);_($* (#,##0);_($* "-"??_);_(@_)'


class XlsxCallBackFuncOpenPyxl:
    def __init__(self, df):
        self.df = df

    def data_value_func(self, i, c):
        return self.df.loc[i, c]

    def data_style_func(self, i, c):
        return OpenPyxlStyleHelper.get_style(
            number_format=NUMBER_FORMAT,
            border=OpenPyxlStyleHelper.CustomBorders.thin_black_border,
        )

    def data_style_func_column_level(self, c):
        return OpenPyxlStyleHelper.get_style(
            number_format=NUMBER_FORMAT,
            border=OpenPyxlStyleHelper.CustomBorders.thin_black_border,
        )

    def header_style_func(self, node):
        color = "9BC2E6"
        return OpenPyxlStyleHelper.get_style(
            bg_color=color, border=OpenPyxlStyleHelper.CustomBorders.thin_black_border
        )

    def header_value_func(self, node):
        return node.value

    def index_value_func(self, node):
        return node.value

    def index_style_func(self, node):
        color = "FFFF00"
        return OpenPyxlStyleHelper.get_style(
            bg_color=color, border=OpenPyxlStyleHelper.CustomBorders.thin_black_border
        )

    def index_name_style_func(self, node):
        color = "9BC2E6"
        return OpenPyxlStyleHelper.get_style(
            bg_color=color, border=OpenPyxlStyleHelper.CustomBorders.thin_black_border
        )

    def index_name_value_func(self, value):
        return value


class XlsxCallBackFuncXlsxWriter:
    def __init__(self, df):
        self.df = df

    def data_value_func(self, i, c):
        return self.df.loc[i, c]

    def data_style_func(self, i, c):
        return XlsxWriterStyleHelper.get_style(number_format=NUMBER_FORMAT)

    def data_style_func_column_level(self, c):
        return XlsxWriterStyleHelper.get_style(
            number_format=NUMBER_FORMAT,
            border=XlsxWriterStyleHelper.CustomBorders.thin_black_border,
        )

    def header_style_func(self, node):
        color = "FFFF00"
        return XlsxWriterStyleHelper.get_style(bg_color=color)

    def header_value_func(self, node):
        return node.value

    def index_value_func(self, node):
        return node.value

    def index_style_func(self, node):
        color = "FFFF00"
        return XlsxWriterStyleHelper.get_style(bg_color=color)

    def index_name_style_func(self, node):
        color = "9BC2E6"
        return XlsxWriterStyleHelper.get_style(bg_color=color)

    def index_name_value_func(self, value):
        return value


def prepare_dataframe(n_rows, n_cols):
    columns = ["col_" + str(i) for i in range(0, n_cols)]
    data = np.random.rand(n_rows, n_cols)
    df = pd.DataFrame(data, columns=columns, index=range(0, n_rows))
    return df


def _create_presentation_model(df, callback_func_cls, slow=0):
    call_back_func_inst = callback_func_cls(df)
    if slow == 0:
        presentation_model = tbc.build_presentation_model(
            df=df,
            data_value_func=None,
            data_style_func=None,
            column_style_func=call_back_func_inst.data_style_func_column_level,
            header_value_func=call_back_func_inst.header_value_func,
            header_style_func=call_back_func_inst.header_style_func,
            index_value_func=call_back_func_inst.index_value_func,
            index_style_func=call_back_func_inst.index_style_func,
            index_name_func=call_back_func_inst.index_name_value_func,
            index_name_style_func=call_back_func_inst.index_name_style_func,
        )
    elif slow == 1:
        presentation_model = tbc.build_presentation_model(
            df=df,
            data_value_func=None,
            column_style_func=call_back_func_inst.data_style_func_column_level,
            header_value_func=call_back_func_inst.header_value_func,
            header_style_func=call_back_func_inst.header_style_func,
            index_value_func=call_back_func_inst.index_value_func,
            index_style_func=call_back_func_inst.index_style_func,
            index_name_func=call_back_func_inst.index_name_value_func,
            index_name_style_func=call_back_func_inst.index_name_style_func,
        )
    elif slow == 2:
        presentation_model = tbc.build_presentation_model(
            df=df,
            data_value_func=call_back_func_inst.data_value_func,
            data_style_func=call_back_func_inst.data_style_func,
            header_value_func=call_back_func_inst.header_value_func,
            header_style_func=call_back_func_inst.header_style_func,
            index_value_func=call_back_func_inst.index_value_func,
            index_style_func=call_back_func_inst.index_style_func,
            index_name_func=call_back_func_inst.index_name_value_func,
            index_name_style_func=call_back_func_inst.index_name_style_func,
        )

    return [presentation_model]


def create_presentation_model_for_xlsx_writer(df, slow=0):
    pm = _create_presentation_model(df, XlsxCallBackFuncXlsxWriter, slow=slow)
    return pm


def create_presentation_model_for_openpyxl_writer(df, slow=0):
    pm = _create_presentation_model(df, XlsxCallBackFuncOpenPyxl, slow)
    return pm


def write_using_openpyxl(pm_openpyxl):
    output_fp = os.path.join(tempfile.gettempdir(), "openpyxl_test.xlsx")
    print("file://" + output_fp)
    tcew.XLSXWriter.to_xlsx(
        pm_openpyxl, output_fp, engine=tcew.SupportedEngines.openpyxl
    )


def write_using_xlsxwriter(pm_xlsxwriter):
    output_fp = os.path.join(tempfile.gettempdir(), "xlsxwriter_test.xlsx")
    print("file://" + output_fp)
    tcew.XLSXWriter.to_xlsx(
        pm_xlsxwriter, output_fp, engine=tcew.SupportedEngines.xlsxwriter
    )


def time_xlsx_writing(scenarios: tp.Iterable[tp.Tuple[int, int]]):
    results = pd.DataFrame(index=scenarios)
    for n_row, n_col in scenarios:
        df = prepare_dataframe(n_row, n_col)
        pm_openpyxl = create_presentation_model_for_openpyxl_writer(df, slow=0)
        pm_xlsxwriter = create_presentation_model_for_xlsx_writer(df, slow=0)

        start_time = time.time()
        write_using_openpyxl(pm_openpyxl)
        end_time = time.time() - start_time
        results.loc[(n_row, n_col), "openpyxl"] = end_time

        start_time = time.time()
        write_using_xlsxwriter(pm_xlsxwriter)
        end_time = time.time() - start_time
        results.loc[(n_row, n_col), "xlsxwriter"] = end_time

    results["(xlsxwriter/openpyxl) (%)"] = (
        results["xlsxwriter"] / results["openpyxl"]
    ) * 100

    print(results)
    return results


def time_presentation_model(scenarios: tp.Iterable[tp.Tuple[int, int]]):

    results = pd.DataFrame(index=row_col)
    for n_row, n_col in scenarios:
        df = prepare_dataframe(n_row, n_col)

        start_time = time.time()
        create_presentation_model_for_openpyxl_writer(df, slow=0)
        end_time = time.time() - start_time
        results.loc[(n_row, n_col), "new"] = end_time

        start_time = time.time()
        create_presentation_model_for_openpyxl_writer(df, slow=2)
        end_time = time.time() - start_time
        results.loc[(n_row, n_col), "old"] = end_time

    results["(column_level/cell_level) (%)"] = (
        results["column_level"] / results["cell_level"]
    ) * 100

    print(results)
    return results


if __name__ == "__main__":
    row_col = [(100, 10), (1000, 50), (10000, 100), (10000, 500)]
    results = time_xlsx_writing(row_col)
    results.to_csv("/tmp/writer_results_test_final.txt", sep="\t")
    results = time_presentation_model(row_col)
    results.to_csv("/tmp/pm_results_test_final.txt", sep="\t")
