.. _python-package:

**************
Python Package
**************

Index
=====

.. list-table::
    :class: longtable

    * - :py:func:`python_environments.get`
      - Get the bundled data for the specified image.

    * - :py:class:`python_environments.ImageData`
      - Type for image data.

    * - :py:mod:`python_environments.data`
      - Module containing the bundled data as resources.

    * - :py:mod:`python_environments.generate`
      - Generation of introespection data for the current environment.


:py:mod:`python_environments`
=============================

.. automodule:: python_environments

    Functions
    =========

    .. autofunction:: python_environments.get

    Types
    =====

    .. autoclass:: python_environments.ImageData
        :show-inheritance:
        :members:


:py:mod:`python_environments.data`
==================================

.. py:module:: python_environments.data

    Module containing the bundled data as resources (see :py:mod:`importlib.resources`).

    Example Usage
    -------------

    .. code-block:: python

        import importlib.resources

        import python_environments.data


        data = importlib.resources.files(python_environments.data)
        data.joinpath('debian:10.json').read_text()


:py:mod:`python_environments.generate`
======================================

.. automodule:: python_environments.generate
    :members:
