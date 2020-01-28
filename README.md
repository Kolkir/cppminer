# cppminer
C++ code miner which produces a code2seq compatible datasets.

Basically, an extractor for code2seq should be able to output for each directory containing source files:

* A single text file, where each row is an example.
* Each example is a space-delimited list of fields, where:

    1. The first field is the target label, internally delimited by the "|" character (for example: compare|ignore|case)
    2. Each of the following field are contexts, where each context has three components separated by commas (","). None of these components can include spaces nor commas.

We refer to these three components as a token, a path, and another token, but in general other types of ternary contexts can be considered.

Each "token" component is a token in the code, split to subtokens using the "|" character.

Each path is a path between two tokens, split to path nodes (or other kinds of building blocks) using the "|" character. Example for a context:

my|key,StringExression|MethodCall|Name,get|value

Here my|key and get|value are tokens, and StringExression|MethodCall|Name is the syntactic path that connects them.
