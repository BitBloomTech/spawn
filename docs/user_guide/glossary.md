# Glossary

| Term | Definition |
|------|------------|
| **Combinator** | Functor that combines multiple parameter arrays e.g. Cartesian outer product and "zip". They are defined in the key string with the prefix `combine:` |
| **Evaluator** | Object that generates a value determinsiticly based on input arguments. In the input it is referenced by using a string value that is prefixed with `eval:` or `#`|
| **Generator** | Object that generates a (different) value each time it is referenced. In the input it is declared in a `generators` top-level section and referenced using a string value that is prefixed with `gen:` or `@` |
| **Macro** | Direct substitution of a value with another value defined in the `macro` top-level section. Referenced using a string value that is prefixed with `macro:` or `$` |
| **Spawner** | The object that is responsible for creating ("spawning") simulation or calculations based on a specification tree that is parsed from the input |
| **Specification Node** | A single node in the specification tree with any given number of parameters associated with it. Generally the spawner will interpret spawn one simulation for each specification node. |
