![Spawn Logo](https://raw.githubusercontent.com/Simmovation/spawn/master/spawn_logo.png "Spawn Logo")

[![CircleCI](https://circleci.com/gh/Simmovation/spawn.svg?style=svg&circle-token=7b196f71c3a3f53004970c6bb798bab074d3bea6)](https://circleci.com/gh/Simmovation/spawn)

[![ReadTheDocs](https://readthedocs.org/projects/spawn/badge/?style=flat)](http://spawn.readthedocs.io/)

Spawn is a python package that allows users to concisely specify and execute a large number of tasks with complex and co-dependent input parameter variations. It is used particularly in engineering where frequently thousands of similar simulations with input parameter variations are run for design and certification purposes. Spawn allows the specification of such large task sets to be formulated in a concise and readable input file.

A typical Spawn process is:
1. Write an input specification file in JSON that specifies the parameters and their values.
2. Inspect the fully expanded specification tree with the `inspect` command.
3. Execute all tasks with the `run` command. This uses a back-end "spawner" to create the tasks, which can be fully customised for individual use cases.

Read the [full Spawn documentation](http://spawn.readthedocs.io/).

If you are interested in using Spawn for executing wind turbine aeroelastic simulation using NREL's FAST, please see the [spawn-wind page](https://github.com/Simmovation/spawn-wind).