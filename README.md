# multi-wind-calc
Generator of multiple aeroelastic simulations for wind turbines

## Status

Some parts of this repo have become obsolete since it changed to Luigi (`run_generator` and `batch` now obsolete).

Needs one extra function for just executing runs perhaps that calls the `luigi.build` function.

## Run Specification

The explicit run list specification has the following approximate structure:

```
+-- baseline file inputs
+-- simulation executables
+-- load cases (call this a group?) [
    +-- name / folder
    +-- runs [
        +-- list field key / value pairs to edit from baseline
    ]
]
```
The `TaskSpawner` then uses this run list to generate new luigi tasks (simulations) by using an `InputEditor` to edit the baseline file inputs. Each run is given a new folder in the load case directory.

This format should be extended to allow children in the runs list so that you can make some editions and then make a set of new runs based on a new baseline with the aforementioned editions.

The idea is that this explicit run list can be generated from a more condensed format using the `combinators`, which support actions such as `zip` and `grid` on co-existing lists of variables. This effectively fills the prupose of the maps in Bladed's multiple calculation setup.

## CLI

Multi Wind Calc provides a CLI. Currently the only available function is specfile inspection.

```
Usage: spawn [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level [error|warning|info|debug]
  --log-console
  --help                          Show this message and exit.

Commands:
  inspect
```

### `inspect` command

```
Usage: spawn inspect [OPTIONS] SPECFILE

Options:
  --help  Show this message and exit.
```