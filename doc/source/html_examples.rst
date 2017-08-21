HTML Examples
=============


This page provides a list of examples that demonstrate rendering html
tables from the given dataframe. Each example is self-contained inside
a class. We have some helper functions to provide the data we need for
this examples

Helper Functions (Data loading routines)
----------------------------------------

.. literalinclude:: html_usage.py
   :linenos:
   :language: python
   :start-after: start_imports
   :end-before: end_imports

.. literalinclude:: html_usage.py
   :linenos:
   :language: python
   :start-after: start_data_routine
   :end-before: end_data_routine


Example 1 - DataFrame with default styles
------------------------------------------------

Demonstrates converting dataframe into html format with default
styles.

.. literalinclude:: html_usage.py
   :linenos:
   :language: python
   :start-after: start_HTMLExample1
   :end-before: end_HTMLExample1


.. image:: _static/html_example1.png

Example 2 - DataFrame with custom styles
----------------------------------------------

In this example, we format the different components of dataframe with
various styling attributes

.. literalinclude:: html_usage.py
   :linenos:
   :language: python
   :start-after: start_HTMLExample2
   :end-before: end_HTMLExample2

.. image:: _static/html_example2.png

Example 3 - Simple DataFrame with Layouts
------------------------------------------------------------------

Demonstrates rendering dataframes with multi-hierarchical indices
and mult-hierarchical columns

.. literalinclude:: html_usage.py
   :linenos:
   :language: python
   :start-after: start_HTMLExample3
   :end-before: end_HTMLExample3

.. image:: _static/html_example3.png


Example 4 - DataFrames with Multi-hierarchical columns and indices
------------------------------------------------------------------

Demonstrates rendering dataframes with multi-hierarchical indices
and mult-hierarchical columns

.. literalinclude:: html_usage.py
   :linenos:
   :language: python
   :start-after: start_HTMLExample4
   :end-before: end_HTMLExample4

.. image:: _static/html_example4.png
