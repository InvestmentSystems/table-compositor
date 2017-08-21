Example of XLSX Styles
======================

In the preceding examples, we have used the functions provided by
`xslx_styles.OpenPyxlStyleHelper` to return the required style
dictionary.  Some examples of style dictionaries that can be returned by
functions returning styles are provided below for reference. For
details on how to build style attributes refer to the `openpyxl`
documentation.

Style with background color
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from openpyxl.styles import PatternFill
   from openpyxl.styles import fills

   fill = PatternFill(fgColor=Color('4f81BD'), patternType=fills.FILL_SOLID)

   # note that we return a dict, whose key = `fill` which is an
   # attrbute of  `cell` object in `openpyxl`
   style = dict(fill=fill)


Style with percentage formatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   number_format = '0.00%'

   fill = PatternFill(fgColor=Color('4f81BD'), patternType=fills.FILL_SOLID)

   # note that we return a dict, whose key = `number_format` which is an
   # attrbute of  `cell` object in `openpyxl`
   style = dict(number_format=number_format)


Style with alignment and fonts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from openpyxl.styles import Alignment
   from openpyxl.styles import Font
   font=Font(bold=True, color='FFFFFF')

   # note that we return a dict, whose key = `number_format` which is an
   # attrbute of  `cell` object in `openpyxl`
   style = dict(alignment=Alignment(horizontal=center, font=font)
