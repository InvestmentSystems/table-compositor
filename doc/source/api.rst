API
===


Building the presentation model
--------------------------------

.. autofunction:: table_compositor.table_compositor.build_presentation_model


Rendering to XLSX
------------------

.. autoclass:: table_compositor.xlsx_writer.XLSXWriter
   :members: to_xlsx, to_xlsx_worksheet


Rendering to HTML
------------------

.. autoclass:: table_compositor.html_writer.HTMLWriter
   :members: to_html

Helper XLSX Styles
-------------------

.. autoclass:: table_compositor.xlsx_styles.OpenPyxlStyleHelper
   :members:

.. autoclass:: table_compositor.xlsx_styles.XLSXWriterDefaults
   :members:

Helper HTML Styles
-------------------

.. autoclass:: table_compositor.html_styles.HTMLWriterDefaults
   :members:
