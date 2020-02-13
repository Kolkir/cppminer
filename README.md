# cppminer
cppminer produces a code2seq compatible datasets from C++ code bases.

It has following command line interface:
~~~
usage: miner.py [-h] [-c number] [-l length] [-p number] path out

positional arguments:
  path                  the path sources directory
  out                   the output path

optional arguments:
  -h, --help            show this help message and exit
  -c number, --max_contexts_num number
                        maximum number of contexts per sample
  -l length, --max_path_len length
                        maximum path length (0 - no limit)
  -p number, --processes_num number
                        number of parallel processes
~~~

The input path is traversed recursively and all files with following extensions `c, cc, cpp` are parsed. 
It is recommended to use the [c++ compilation database](https://clang.llvm.org/docs/JSONCompilationDatabase.html) which provides all required compilation flags for project files.
The application produces following three files `train.c2s`, `test.c2s` and `validation.c2s` into the output directory.  

These files have following format:

* Each row is an example.
* Each example is a space-delimited list of fields, where:

    1. The first field is the target label, internally delimited by the "|" character (for example: compare|ignore|case)
    2. Each of the following field are contexts, where each context has three components separated by commas (","). None of these components can include spaces nor commas.

Context's components are a token, a path, and another token.

Each `token` component is a token in the code, split to subtokens using the "|" character.

Each `path` is a path between two tokens, split to path nodes using the "|" character. Example for a context:
```
my|key,StringExression|MethodCall|Name,get|value
```
Here `my|key` and `get|value` are tokens, and `StringExression|MethodCall|Name` is the syntactic path that connects them.
