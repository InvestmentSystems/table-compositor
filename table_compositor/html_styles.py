import typing as tp

import numpy as np

from table_compositor.html_writer import HTMLWriter
from table_compositor.util import df_type_to_str


class td_style(tp.NamedTuple):
    text_align: str
    background_color: str
    color: str
    border: tp.Optional[int]
    font_weight: str
    white_space: str
    padding: str


def td_style_to_str(td_style_):
    """
    convert td_style to str in inline css format.
    """
    return HTMLWriter.style_to_str(td_style_)


default_th_style = td_style(
    text_align="center",
    background_color="#4F81BD",
    color="#FFFFFF",
    font_weight="bold",
    white_space="pre",
    padding="10px",
    border=1,
)

default_numeric_td_style = td_style(
    text_align="right",
    background_color="#FFFFFF",
    color="#000000",
    font_weight="normal",
    white_space="pre",
    padding="10px",
    border=None,
)

default_td_style = td_style(
    text_align="left",
    background_color="#FFFFFF",
    color="#000000",
    font_weight="normal",
    white_space="pre",
    padding="10px",
    border=None,
)

default_table_style = dict(border=1, style="border-collapse:collapse;")


class HTMLWriterDefaults:
    """
    Class provides defaults callback funcs that can be used
    while calling the build_presentation_model.
    """

    @staticmethod
    def _to_dollar_format(v):
        if not isinstance(v, (float, int)):
            return v
        r = "${:0,.0f}".format(v)
        return r

    @staticmethod
    def data_value_func(df, dollar_columns=None):
        """
        Default value that can be used as callback for data_value_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            A function that takes idx, col as arguments and returns the df.loc[idx, col] value
        """

        def _value_func(r, c):
            nonlocal dollar_columns
            dollar_columns = dollar_columns or set()
            if c in dollar_columns:
                return HTMLWriterDefaults._to_dollar_format(
                    df_type_to_str(df.loc[r, c])
                )
            return df_type_to_str(df.loc[r, c])

        return _value_func

    @staticmethod
    def data_style_func(df):
        """
        Default value that can be used as callback for data_style_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            a function table takes idx, col as arguments and returns a dictionary of html style attributes
        """

        def _style_func(r, c):
            if isinstance(df.loc[r, c], (np.int_, float, np.uint)):
                return td_style_to_str(default_numeric_td_style)
            return td_style_to_str(default_td_style)

        return _style_func

    @staticmethod
    def header_value_func(df):
        """
        Default value that can be used as callback for header_value_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            A function that takes node as arguments and returns the node.value
        """

        def _value_func(node):
            return node.value

        return _value_func

    @staticmethod
    def header_style_func(df):
        """
        Default value that can be used as callback for header_style_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            a function table takes `node` as argument and returns a dictionary of html style attributes
        """

        def _style_func(node):
            return td_style_to_str(default_th_style)

        return _style_func

    @staticmethod
    def index_value_func(df):
        """
        Default value that can be used as callback for index_value_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            A function that takes node as arguments and returns the node.value
        """

        def _value_func(node):
            return node.value

        return _value_func

    @staticmethod
    def index_style_func(df):
        """
        Default value that can be used as callback for index_style_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            a function table takes `node` as argument and returns a dictionary of html style attributes
        """

        def _style_func(node):
            return td_style_to_str(default_td_style)

        return _style_func

    @staticmethod
    def index_name_style_func(df):
        """
        Default value that can be used as callback for index_name_style_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            a function table takes index.name as argument and returns a dictionary of html style attributes
        """

        def _style_func(index_name):
            return td_style_to_str(default_th_style)

        return _style_func

    @staticmethod
    def index_name_value_func(df):
        """
        Default value that can be used as callback for index_name_value_func

        Args:
            df: the dataframe that will be used to build the presentation model

        Returns:
            A function that takes index.name as argument and return index.name if not None else ''
        """

        def _value_func(value):
            return value or ""

        return _value_func
