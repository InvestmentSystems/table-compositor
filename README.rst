table-compositor
=================

The table-compositor library provides the API to render data stored in table-like data structures. Currently the library supports rendering data available in a Panda's DataFrames. The DataFrame layout is used as the table layout(including single and multi hierarchical columns/indices) by the library. The table layout is rendered directly on to an XLSX sheet or to a HTML page. Styling and layout attributes can be used to render colorful XLSX or HTML reports. The library also supports rendering of multiple dataframes into a single XLSX sheet or HTML page. The objective of the library is to be able to use the DataFrame as the API to configure the style and layout properties of the report. Callback functions are provided to customize all styling properties. The nice thing about the callback functions are that the style properties are set on cells indexed with index/column values available in the original dataframe used during rendering.

Code: https://github.com/InvestmentSystems/table-compositor

Docs: http://table-compositor.readthedocs.io

Packages: https://pypi.python.org/pypi/table-compositor
