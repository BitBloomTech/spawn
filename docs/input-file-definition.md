# Spawn Input File Definition

Spawn is a declarative language based on JSON. The JSON standard is defined at <http://json.org>. Based on a specification in JSON, Spawn generates parameter sets, which we refer to as nodes.

[TOC]

## Getting Started

The specification is defined in an object named `"spec"`. Each name/value pair within this object is a parameter name and its value. The following generates a single specification node with one parameter, named "alpha" with a vlue of 4:

```JSON
{
    "spec": {
        "alpha": 4
    }
}
```

 Sister name/value pairs are simultaneous (i.e. orccur on the same node). The following generates a single node with *two* simulataneous parameters - "alpha" with a vlue of 4, and "beta" with a value of "tadpole":

```JSON
{
    "spec": {
        "alpha": 4,
        "beta": "tadpole"
    }
}
```

Separate nodes can be created by separating parameters into different JSON nodes. Parameters defined outside of the object are also applied on each node. The following creates two nodes, both with parameters named "alpha" and "beta", where the first node has parameter values of 4 and "tadpole" respectively and the second has values of 6 and "tadpole" respectively. The names of the sub-objects (`"blah"` and `"blo"`) are not used but must be present to conform to the JSON standard:

```JSON
{
    "spec": {
        "beta": "tadpole",
        "blah": { "alpha": 4},
        "blo": { "alpha": 6}
    }
}
```

An identical specifcation could be written (less concisely) as:
```JSON
{
    "spec": {
        "blah": { "alpha": 4, "beta": "tadpole"},
        "blo": { "alpha": 6, "beta": "tadpole"}
    }
}
```

Avoiding repetitive definition and enabling concise and readable but compex specifications is one of the key aims of Spawn.

## Arrays

Multiple specification nodes where one parameter is varied can be created by using the array property of JSON. The same specification as at the end of the last section (two nodes, both with parameter "beta" of "tadpole" and parameter "alpha with values of 4 and 6) can be created by:
```JSON
{
    "spec": {
        "alpha": [4, 6],
        "beta": "tadpole"
    }
}
```

### Cartesian Product

The automatic behaviour of multiple sister arrays is to create all the parameter combinations of them (i.e. apply [Cartesian Product](https://en.wikipedia.org/wiki/Cartesian_product)). The following will create 6 (3*2) nodes (2D product):
```JSON
{
    "spec": {
        "alpha": [3, 5, 8],
        "beta": ["tadpole", "frog"]
    }
}
```
Additional sister arrays will add additional dimensions to the Cartesian product, and there is no limit. In this manner, a very large number of nodes can be created with just a few lines.

### Zip

To apply a one-one mapping between, we apply the zip "combinator" on the two arrays. A "combinator" is a name/object pair where the name determines the combination to be performed. The name starts with a `#` to differentiate it from other name/object pairs. The following generates three nodes ((3, "egg"), (5, "tadpole"), (8, "frog")):
```JSON
{
    "spec": {
        "#zip": {
            "alpha": [3, 5, 8],
            "beta": ["egg", "tadpole", "frog"]
        }
    }
}
```
There is no limit to the number of sister arrays, but they *must* all have equal size.

## Value Proxies

The value of parameter/value pairs can be represented by a proxy. The proxy is a string that starts with either a type identifier followed by a colon (longhand) or a special character (shorthand) to determine which type of value proxy it is. The parser then replaces the proxy when the specification is resolved. The tpyes of value proxies are as follows:

| Type | Longhand | Shorthand | Description |
|------|----------|-----------|-------------|
| Macro | `macro:` | `$` | Direct substitution of a previously declared value |
| Generator | `gen:` | `@` | Generates a (in general different) value each time it is resolved |
| Evaluator | `eval:` | `#` | Evaluates a value based on a deterministic function which can take arguments |

### Macros

Macros are declared alongside the spec and can then be used repeatedly. The name of the name/value pairs in the `macros` object determines the name of the macro that can be used in the `spec` object (where it must be prefixed). They can be a single value, array or object:

```JSON
{
    "macros": {
        "Alphas": [3, 5, 8]
    },
    "spec": {
        "a": {
            "alpha": "macro:Alphas",
            "beta": "tadpole"
        },
        "b": {
            "alpha": "$Alphas",
            "gamma": 4.2
        }
    }
}
```

### Generators

Generators generate a value each time they are resolved in the specification. The main uses of generators is providing random variates and counters. Generators are declared in an object named `generators`. Each generator is a name/object pair, where the name specifies the name of the generator to be used in the `spec` object. Each generator object must specify its method and arguments to its constructor. These are the inbuilt constructors:

| `method` | Argument names (default value) | Description |
|--------|-----------------------|-------------|
| `IncrementalInt` | `start`(1), `step`(1) | An incrementing integer starting at `start` and incrementing by `step` each time it is resolved |
| `RandomInt` | `min`(1), `max`(999), `seed`(1) | A random integer between `min` and `max` each time it's resolved |

The following example generates a value of 4 for "alpha" via the "a" object and a value of 5 via the "b" node:
```JSON
{
    "generators": {
        "Counter": {
            "method": "IncrementalInt",
            "start": 4
        }
    },
    "spec": {
        "a": {
            "alpha": "@Counter",
            "beta": "tadpole"
        },
        "b": {
            "alpha": "gen:Counter",
            "gamma": 4.2
        }
    }
}
```

### Evaluators

Evaluators allow function-style syntax to evaluate expressions with arguments. Arithmetic operations are supported as well as inbuilt evaluators `range` (as per [python's range function](https://docs.python.org/3/library/stdtypes.html?highlight=range#range)) and `repeat`. Unlike macros and generators, evaluators do not need an object defined alongside the `spec`. Some examples:

| Example | Resolution |
|---------|------------|
| `"#3 + 5"` | `8` |
| `"#3 - 5"` | `-2` |
| `"#3 * 5"` | `15` |
| `"#3 / 5"` | `0.6` |
| `"#range(3, 8)"` | `[3, 4, 5, 6, 7]` |
| `"eval:repeat(5, 3)"` | `[5, 5, 5]` |

Evaluators can also take other parameters simultaneously present in the specification if they are prefixed by `!`. They do not need to be in the same object. The following resolves `"gamma"` into the list `[3, 4]`:
```JSON
{
    "spec": {
        "alpha": 3,
        "blah": {
            "beta": 5,
            "gamma": "#range(!alpha, !beta)"
        }
    }
}
```
