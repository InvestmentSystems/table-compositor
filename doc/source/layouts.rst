Layouts
=======

Apart from providing styling and formatting facilities, the table compositor library
also provides a powerful way to layout multiple tables on one
sheet. In this section we will look at some examples.

We will use the same presentation model from `basic_example2()`. We
will layout the presentation models with different layouts.

.. literalinclude:: basic_usage.py
   :linenos:
   :language: python
   :start-after: start_imports
   :end-before: end_imports

.. literalinclude:: basic_usage.py
   :linenos:
   :language: python
   :start-after: start_layout_example_1
   :end-before: end_layout_example_1
   :emphasize-lines: 27-36

In the preceding example, we create two layouts. On line 28, we have a
layout defined and then rendered to two files with different `orientations`.

When the orientation is `vertical`, then each item
(presentation_model) in the list is layed out vertically. The
orientation flips between `vertical` and `horizontal` for every nested
listed that is encountered. In this example, you will notice that
since the second item in the outer list is a list, the two
presentation models in the inner list are  rendered side-by-side
(i.e. with horizontal orientation)

.. image:: _static/layout_example1_1.png


When the value of orientation argument is changed to `horizontal`, the
renderer renders the outerlist horizontally and flips the orientation
of inner lists to vertical. The second output is show below.

.. image:: _static/layout_example1_2.png
