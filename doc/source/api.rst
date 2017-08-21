API
===


Building the presentation model
--------------------------------

.. autofunction:: package.public.table_compositor.table_compositor.table_compositor.build_presentation_model


Rendering to XLSX
------------------

.. autoclass:: package.public.table_compositor.table_compositor.xlsx_writer.XLSXWriter
   :members: to_xlsx, to_xlsx_worksheet


Rendering to HTML
------------------

.. autoclass:: package.public.table_compositor.table_compositor.html_writer.HTMLWriter
   :members: to_html

Helper XLSX Styles
-------------------

.. autoclass:: package.public.table_compositor.table_compositor.xlsx_styles.OpenPyxlStyleHelper
   :members:

.. autoclass:: package.public.table_compositor.table_compositor.xlsx_styles.XLSXWriterDefaults
   :members:

Helper HTML Styles
-------------------

.. autoclass:: package.public.table_compositor.table_compositor.html_styles.HTMLWriterDefaults
   :members:
