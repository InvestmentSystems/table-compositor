"""
Module that supports operations to map a dataframe to an excel worksheet like entity
and also create Excel files with all fancy formatting.
"""

import itertools as it

import pandas as pd

from table_compositor.html_styles import HTMLWriterDefaults
from table_compositor.presentation_model import (
    IndexNode,
    InternalFrame,
    PresentationElements,
    PresentationLayoutManager,
    PresentationModel,
    StyleWrapper,
)
from table_compositor.xlsx_styles import OpenPyxlStyleHelper, XlsxWriterStyleHelper


def build_presentation_model(
    *,
    df,
    output_format="xlsx",
    data_value_func=None,
    column_style_func=None,
    data_style_func=None,
    header_style_func=None,
    header_value_func=None,
    index_style_func=None,
    index_value_func=None,
    index_name_func=None,
    index_name_style_func=None,
    engine="openpyxl",
    **kwargs,
):
    """Construct and return the presentation model that will be used while rendering to html/xlsx formats. The returned object has all the information required to render the tables in the requested format. The details of the object is transparent to the caller. It is only exposed for certain advanced operations.

    Args:
        df: The dataframe representation of the table. The shape of the dataframe closely resembles the table that will be rendered in the requested format.
        output_format: 'html' or 'xlsx'
        data_value_func: example: lambda idx, col: df.loc[idx, col], assuming df is in the closure. This can be None, if no data transformation is required to the values already present in the source df
        column_style_func: the function can substitute the data_style_func, if the same style can be applied for the whole column. This argument should be prefered over the `data_style_func` argument. Using this option provides better performance since the fewer objects will be created internally and fewer callbacks are made to this function when compared to data_style_func.This argument only applies to the data contained in the dataframe and not the cell where the headers are rendered. For fine grained control at `cell` level, the `data_style_func` argument can be used. For more information on return values of this function, refer to the documentation for `data_style_func` argument.
        data_style_func: used to provide style at the cell level. Example: lambda idx, col: return dict(font=Font(...)), where Font is the openpyxl object and `font` is the attr available in the `cell` instance of openpyxl.
                         For xlsx, the keys in the dict are the attrs of the `cell` object in openpyxl and the values correspond to the value of that attribute. Example are found in xlsx_styles module.
                         For html, the key-value pairs are any values that go into to the style attribute of a td, th cell in html. Examples are found in html_styles module. example: dict(background-color='#F8F8F8').
                         When performance becomes an issue, and cell level control is not needed, it is recommended to use the `column_style_func` argument rathat than this argument.
                         If the prefered engine is XlswWriter, then the style dictionary returned should have key/values compatible with the `Format` object declarted in the `XlsxWriter` library. A reference can be found in ``xlsx_styles.XlsxWriterStyleHelper` class

        header_value_func: func that takes a object of type `IndexNode`. The `IndexNode` contains the attributes that refer to the header being rendered. The returned value from this function is displayed in place of the header in the dataframe at the location. The two properties available on the `IndexNode` object are `value` and `key`. The `key` is useful to identify the exact index and level in context while working with multi-hierarchical columns.
        header_style_func: func that takes a object of type `IndexNode`. The return value of this function is similar to data_style_func.
        index_value_func: func that takes a object of type `IndexNode`. The `IndexNode` contains the attributes that refer to the index being rendered. The returned value from this function is displayed in place of the index in the dataframe at the location.
        index_style_func: func that takes a object of type `IndexNode`. The return value of this function is similar to data_style_func.
        index_name_func: func that returns a string for index name (value to be displayed on top-left corner, above the index column)
        index_name_style: the style value same as data_style_func that will be used to style the cell
        engine: required while building presentation model for xlsx. Argument ignored for HTML rendering. This argument is used to provide the default callback style functions, where the style dictionary returned by the callback functions should be compatible with the engine being used.
        kwargs:
                'hide_index' - if True, then hide the index column, default=False

                'hide_header, - if True, then hide the header, default=False

                'use_convert' - if True, do some conversions from dataframe values to values excel can understand for example np.NaN are converted to NaN strings

    Return:
        A presentation model, to be used to create layout and provide the layout to the html or xlsx writers.

    About the callback functions provided as arguments:

    Note that callback function provided as arguments to this function are provided with either a tuple of index, col arguments are some information regarding the index or headers being rendered. Therefore, a common
    pattern would be to capture the `dataframe` being rendered in a closure of this callback func before passing them as arugments.

    For example:

    df = pd.DataFrame(dict(a=[1, 2, 3]))

    def data_value_func():
        def _inner(idx, col):
             return df.loc[idx, col] * 10.3
        return _inner

    pm = build_presentation_model(df=df, data_value_func=data_value_func())

    """

    if bool(data_style_func) and bool(column_style_func):
        raise ValueError(
            "Only one of data_style_func and column_style_func needs to be set."
        )

    func = _build_presentation_model_for_excel
    if output_format == "html":
        func = _build_presentation_model_for_html
        engine = None
        if not (data_style_func or column_style_func):
            # This is for backwards compatibility
            data_style_func = HTMLWriterDefaults.data_style_func(df)

    internal_frame = InternalFrame(df)
    return func(
        df=internal_frame,
        data_value_func=data_value_func,
        data_style_func=data_style_func,
        header_style_func=header_style_func,
        header_value_func=header_value_func,
        index_style_func=index_style_func,
        index_value_func=index_value_func,
        index_name_func=index_name_func,
        index_name_style_func=index_name_style_func,
        column_style_func=column_style_func,
        engine=engine,
        **kwargs,
    )


def _build_presentation_model_for_excel(
    *,
    df,
    data_value_func,
    data_style_func=None,
    header_style_func=None,
    header_value_func=None,
    index_style_func=None,
    index_value_func=None,
    index_name_func=None,
    index_name_style_func=None,
    column_style_func=None,
    engine="openpyxl",  # for backward compatibility
    **kwargs,
):
    if engine == "xlsxwriter":
        helper_cls = XlsxWriterStyleHelper
    else:
        helper_cls = OpenPyxlStyleHelper

    if not (data_style_func or column_style_func):
        column_style_func = lambda _: helper_cls.get_style()
    header_style_func = header_style_func or (
        lambda x: helper_cls.default_header_style()
    )
    header_value_func = header_value_func or (lambda x: x.value)
    index_style_func = index_style_func or (lambda x: helper_cls.get_style())
    index_value_func = index_value_func or (lambda x: x.value)
    index_name_func = index_name_func or (lambda x: x or "")
    index_name_style_func = index_name_style_func or (
        lambda x: helper_cls.default_header_style()
    )

    return _build_presentation_model(
        df=df,
        data_value_func=data_value_func,
        data_style_func=data_style_func,
        header_style_func=header_style_func,
        header_value_func=header_value_func,
        index_style_func=index_style_func,
        index_value_func=index_value_func,
        index_name_func=index_name_func,
        index_name_style_func=index_name_style_func,
        column_style_func=column_style_func,
        **kwargs,
    )


def _build_presentation_model_for_html(
    *,
    df,
    data_value_func=None,
    data_style_func=None,
    header_style_func=None,
    header_value_func=None,
    index_style_func=None,
    index_value_func=None,
    index_name_func=None,
    index_name_style_func=None,
    column_style_func=None,
    **kwargs,
):
    header_style_func = header_style_func or HTMLWriterDefaults.header_style_func(df)
    header_value_func = header_value_func or HTMLWriterDefaults.header_value_func(df)
    index_style_func = index_style_func or HTMLWriterDefaults.index_style_func(df)
    index_value_func = index_value_func or HTMLWriterDefaults.index_value_func(df)
    index_name_func = index_name_func or HTMLWriterDefaults.index_name_value_func(df)
    index_name_style_func = (
        index_name_style_func or HTMLWriterDefaults.index_name_style_func(df)
    )

    return _build_presentation_model(
        df=df,
        data_value_func=data_value_func,
        data_style_func=data_style_func,
        header_style_func=header_style_func,
        header_value_func=header_value_func,
        index_style_func=index_style_func,
        index_value_func=index_value_func,
        index_name_func=index_name_func,
        index_name_style_func=index_name_style_func,
        column_style_func=column_style_func,
        **kwargs,
    )


def _raise_on_invalid_index(index, label: str):
    # the index and columns of the provided dataframe should be unique. if the index/columns of the dataframe are multi-hierarchical  then at each level the values should be present contigously
    # For example in :
    # df.columns =  df.columns = pd.MultiIndex.from_tuples([('a', 1), ('a', 2), ('b', 1), ('a', 3)])
    # the first level of values turns out to be ['a', 'a', 'b', 'a']. Note that 'a' is
    # not contigous and that is not valid.

    detailed_msg = """\nFor presentation model to process index and columns, the index and columns should be unique. For multi-heirarchical indices, the values should becontiguous at the first level. For example in : \t\n df.columns = pd.MultiIndex.from_tuples([('a', 1), ('a', 2), ('b', 1), ('a', 3)]) \n the first level of values turns out to be ['a', 'a', 'b', 'a']. \n Note that 'a' is not contiguous and therefore the index/column is not a valid value."""

    if not isinstance(index, (pd.MultiIndex, pd.Index)):
        # probably a static-frame
        return

    if isinstance(index, pd.MultiIndex):
        values = index.tolist()
        values_at_first_level, *_ = zip(*values)
        by_group = tuple((k for k, _ in it.groupby(values_at_first_level)))
        if len(set(values_at_first_level)) != len(by_group):
            msg = "".join(
                (
                    label,
                    " not contiguous at the first level.",
                    detailed_msg,
                    "\n Value Passed: ",
                    str(index),
                )
            )
            raise ValueError(msg)
        return

    # if single hierarchical
    if len(set(index)) != len(index):
        msg = "".join(
            (label, " not unique.", detailed_msg, "\n Value Passed: ", str(index))
        )
        raise ValueError(msg)


def _build_presentation_model(
    *,
    df,
    data_value_func,
    data_style_func,
    header_style_func,
    header_value_func,
    index_style_func,
    index_value_func,
    index_name_func,
    index_name_style_func,
    column_style_func=None,
    **kwargs,
):
    """
    Return a DFView tuple (, ) - what could this end up being?

    Args:
        df,
        data_value_func:
        data_style_func:
        header_style_func:
        header_value_func:
        index_style_func:
        index_value_func:
        index_name_func:
        index_name_style_func:
    """

    # cleanup kwargs
    kwargs = kwargs or {}
    kwargs["hide_index"] = kwargs.get("hide_index", False)
    kwargs["hide_header"] = kwargs.get("hide_header", False)
    # FIXME: covert method revisit
    kwargs["use_convert"] = kwargs.get("use_convert", False)

    # table compositor needs indices/column names to be unique.
    if not kwargs["hide_index"]:
        _raise_on_invalid_index(df.index, "index")
    if not kwargs["hide_header"]:
        _raise_on_invalid_index(df.columns, "columns")

    column_index_tree = IndexNode.index_to_index_node(df.columns)
    header_value_view = IndexNode.apply(f=header_value_func, root=column_index_tree)
    header_style_view = IndexNode.apply(
        f=lambda node: StyleWrapper(user_style=header_style_func(node)),
        root=column_index_tree,
    )
    # index
    style_index_view = IndexNode.apply(
        f=lambda node: StyleWrapper(user_style=index_style_func(node)),
        root=IndexNode.index_to_index_node(df.index),
    )
    index_value_view = IndexNode.apply(
        f=index_value_func, root=IndexNode.index_to_index_node(df.index)
    )

    # process df
    value_view = PresentationLayoutManager.apply(data_value_func, df)
    if column_style_func:
        style_view = PresentationLayoutManager.apply_at_column_level(
            lambda c: StyleWrapper(user_style=column_style_func(c)), df
        )
    else:
        style_view = PresentationLayoutManager.apply(
            lambda i, c: StyleWrapper(user_style=data_style_func(i, c)), df
        )

    # index name style
    index_name_values = index_name_func(df.index.name)
    index_name_style = StyleWrapper(user_style=index_name_style_func(df.index.name))

    header = PresentationElements(values=header_value_view, style=header_style_view)
    df_view = PresentationElements(values=value_view, style=style_view)
    index = PresentationElements(values=index_value_view, style=style_index_view)
    index_name = PresentationElements(values=index_name_values, style=index_name_style)

    return PresentationModel(
        header=header,
        index_label=index,
        data=df_view,
        index_name=index_name,
        kwargs=kwargs,
    )
