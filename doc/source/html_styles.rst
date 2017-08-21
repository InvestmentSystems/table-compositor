Example of HTML Styles
===============================

In the Basic section, we only saw examples of how to render dataframes
to a xlsx format. The same setup can be used to render dataframes to
HTML using the `html_writer.HTMLWriter.to_html` function. The only
thing that has to be changed is the style attributes that are being
returned. We want our style providing functions to return style
attributes that can be inlined into the `style` attribute of a `<td>`
or `<th>` tag.

Some examples of style dictionaries that can be return by
functions returning styles are provided below for reference.

Style for headers
^^^^^^^^^^^^^^^^^

.. code-block:: python

   style = dict(
    text_align='center',
    background_color='#4F81BD',
    color='#FFFFFF',
    font_weight='bold',
    white_space='pre',
    padding='10px',
   border=1)



Style for cell holding numeric values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   numeric_style = dict(
                text_align='right',
                background_color='#FFFFFF',
                color='#000000',
                font_weight='normal',
                white_space='pre',
                padding='10px',
                border=None)


Style using the html_styles.td_style object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    style = td_style(
                text_align='center',
                background_color='#4F81BD',
                color='#FFFFFF',
                font_weight='bold',
                white_space='pre',
                padding='10px',
                border=1)
