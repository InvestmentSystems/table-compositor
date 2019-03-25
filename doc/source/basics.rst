Basics
==========

The purpose of this library is to use the Pandas DataFrame as an interface to represent the layout of a table that needs to be rendered to an xlsx file or as an html table. The library abstracts away the tedious work of working at the `cell` level of an xlsx sheet or a html table. It provides a call-back mechanism by which the user is able to provide values that need to be rendered and also the styling that needs to be used for each cell in the rendered table. The library is also capable of laying out multiple tables in the same sheet which are evenly spaced vertically or horizontally based on the layout configuration provided.

Sample Data
-------------

During the later part of this documentation, we will use the sample data from the Social Security Administration which contains the U.S. child birth name records. We choose this sample data for two reasons. We reuse some of the discussion that are outlined by Wes McKinnery's Python For Data Analysis, 2nd Edition(2017). The same data is also used in the documentation of another library `function-pipe <http://function-pipe.readthedocs.io/en/latest/index.html>` that the Investment Systems Group has open-sourced.

https://www.ssa.gov/oact/babynames/names.zip

Further more, we will assume that a flattened file from all the smaller files in the .zip file is available after we invoke the following function.

Please refer to the :ref:`XLSX Examples` section for code that loads this data.


A Hello World Example: Dataframe to Xlsx
-----------------------------------------

Every use of this library involves four steps.

1. We build a dataframe that resembles the shape of the table that will be rendered.

2. The dataframe is passed as an argument to the  function called
   ``build_presentation_model``. This function accepts a `dataframe` and
   also a number of functions as arguments. We call the value returned
   by this function, the `presentation_model`.

3. Create a `layout` of multiple `presentation models` (if we want more than one table rendered in same xlsx sheet or same html page)

4. Call the `render_xlsx` or `render_html` functions on the respective writers. For xlsx files either OpenPyxlCompositor(uses `openpyxl` library) or XlsxWriterCompositor(uses `xlsxwriter` library). For HTML use the `HTMLWriter`.


A Quick Look at a Xlsx example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We will start with a simple dataframe and render the dataframe as-is to a xlsx file

.. code-block:: python

    import pandas as pd
    from table_compositor.table_compositor import build_presentation_model
    from table_compositior.xlsx_writer import OpenPyxlCompositor
    # Note: use XlsxWriterCompositor to use xlsxwriter library

    sample_df = pd.DataFrame(dict(a=[10, 20, 30, 40, 50], b=[0.1, 0.9,0.2, 0.6,0.3]), index=[1,2,3,4,5])

    # create a presentation model
    # defaults to engine='openpyxl'. Needs to be set to 'xlsxwriter' to use `xlsxwriter` library instead.
    presentation_model = build_presentation_model(df=sample_df)

    # create a layout, which is usually a nested list of presentation models
    layout = [presentation_model]

    # render to xlsx
    output_fp = '/tmp/example1.xlsx'
    OpenPyxlCompositor.to_xlsx(layout, output_fp=output_fp)


Running this code produces the following output:

.. image:: _static/xlsx_basic_example1.png

In the above code snippet, we first created a dataframe called  ``sample_df``.

To render this `dataframe`, we first invoke `build_presentation_model`. The `build_presentation_model` accepts the `dataframe` as its first argument. In this example, we use the `defaults` provided by this method for all other arguments. The `build_presentation_model` returns an `presentation_model` object.

Before we call `OpenPyxlCompositor.to_xlsx` we create a `layout`. A `layout` is a nested list of `presentation_models`. In our case, since we have only one `presentation_model` we create a list with a single element. Later on when we work with multiple presentation models that need to be rendered on to the same sheet, we could create nested list such as `[[model1, model2], [model3]]` etc.

Building the Presentation Model
--------------------------------

The `build_presentation_model` function is the most important interface in this library. This function exposes all the functionality that is required to render beautiful looking excel worksheets or html tables.

We will now build up on our previous example and add styling to the report we generate. Before, we do that lets take a quick look at the signature of `build_presentation__model`.

.. autofunction:: table_compositor.table_compositor.build_presentation_model


Improving on our first iteration
--------------------------------

Now, that we got a overview of the `build_presentation_mode` function, lets try setting these arguments to improve the look of our reports.

Say, we have the following requirements:

1. Display column 'A' as in dollar format.
2. Display column 'B' as percentage values.'
3. Set back-ground color of column 'B' to red if value is less than 50%
4. Capitalize all the column headers and add a yellow background
5. Multiply all index values by 100 while rendering and add a color to the background.
6. Display a 'custom text' on the top left corner, where pandas whole usually display the index name if available.


We update our previous example to do the following:

.. literalinclude:: basic_usage.py
   :linenos:
   :language: python
   :start-after: start_imports
   :end-before: end_imports

.. literalinclude:: basic_usage.py
   :linenos:
   :language: python
   :start-after: start_basic_example_2
   :end-before: end_basic_example_2


On line 3 we create the dataframe.

To satisfy the requirements we listed above we pass the callback function to the `build_presentation_model`. Note that some helper functions are available in  xlsx_style function to create styles for openpyxl. But, any other dict with keys that are `attr` of cell object of openpyxl should work. The above example produces the output as shown below:

.. image:: _static/xlsx_basic_example2.png


Multi-hierarchical columns and indices
---------------------------------------

Rendering dataframes with multi-hierarchical columns or indices are very similar to rendering the simpler dataframes. The `data_value_func` and `data_style_func` work the same way. The functions that handle `index` cell rendering and `column` header rendering can access the `IndexNode` object that is passed to those functions to determine the value and level that is currently being rendered. This becomes clearer with an example.

We demonstrate this by setting a variety of colors to each cell that holds one of the values of the hierarchical columns or indices.

Note that the `IndexNode` argument passed to the callback function has a `node.key` field that unique identifies each cell with a name that is built appending the value of each item in the index or column hierarchy.

.. literalinclude:: basic_usage.py
   :linenos:
   :language: python
   :start-after: start_imports
   :end-before: end_imports

.. literalinclude:: basic_usage.py
   :linenos:
   :language: python
   :start-after: start_basic_example_3
   :end-before: end_basic_example_3
   :emphasize-lines: 11-30

The above function gives us the `xlsx` file shown below. Note the colors used to render the indices and columns and review how the two functions, namely, `index_style_function` and `header_style_function` provide the colors based on the `IndexNode` attributes. You will notice the use of `node.key` in these functions to identify each cell uniquely.

.. image:: _static/xlsx_basic_example3.png
