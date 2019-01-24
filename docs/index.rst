.. spawn documentation master file, created by
   sphinx-quickstart on Fri Nov  2 11:40:25 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: https://raw.githubusercontent.com/Simmovation/spawn/master/spawn_logo.png
   :height: 100px
   :alt: Spawn Logo
   :align: center

Spawn is a python package that allows users to concisely specify and execute a large number of tasks with complex and co-dependent input parameter variations. It is used particularly in engineering where frequently thousands of similar simulations with input parameter variations are run for design and certification purposes. Spawn allows the specification of such large task sets to be formulated in a concise and readable input file.

A typical Spawn process is:
1. Write an input specification file in JSON that specifies the parameters and their values.
2. Inspect the fully expanded specification tree with the `inspect` command.
3. Execute all tasks with the `run` command. This uses a back-end "spawner" to create the tasks, which can be fully customised for individual use cases.

If you are interested in using Spawn for executing wind turbine aeroelastic simulation using NREL's FAST, please see the `spawn-wind page
<https://github.com/Simmovation/spawn-wind>`_.

Get Started with Spawn
======================

Read :ref:`Spawn Input File Definition` to discover how to build your first Spawn spec file.

If you're using the command line interface, take a look at :ref:`Spawn Command Line Interface`.

A full :ref:`API Reference` is also provided.

.. toctree::
   :name: user_guide
   :caption: User Guide
   :hidden:

   user_guide/input-file-definition
   api/spawn.cli
   user_guide/glossary

.. toctree::
    :name: api
    :caption: API Reference
    :glob:
    :hidden:

    api/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
