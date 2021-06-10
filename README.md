# jupyfmt

[![PyPI](https://img.shields.io/pypi/v/jupyfmt.svg?style=flat)](https://pypi.python.org/pypi/jupyfmt)
[![Tests](https://github.com/kpj/jupyfmt/workflows/Tests/badge.svg)](https://github.com/kpj/jupyfmt/actions)

The uncompromising Jupyter notebook formatter.

`jupyfmt` allows you to format notebooks in-place from the commandline as well as assert properly formatted Jupyter notebook cells in your CI.
Inspired by [snakefmt](https://github.com/snakemake/snakefmt/). Uses [black](https://github.com/psf/black/) under the hood.


## Installation

Install the latest release from PyPI:

```python
$ pip install jupyfmt
```


## Usage

`jupyfmt` can be used to format notebooks in-place or report diffs and summary statistics.

Overview of commandline parameters:
```
$ jupyfmt --help
Usage: jupyfmt [OPTIONS] [PATH_LIST]...

  The uncompromising Jupyter notebook formatter.

  PATH_LIST specifies notebooks and directories to search for notebooks in. By
  default, all notebooks will be formatted in-place. Use `--check`, `--diff`
  (or `--compact-diff`) to print summary reports instead.

Options:
  -l, --line-length INT           How many characters per line to allow.
  -S, --skip-string-normalization
                                  Don't normalize string quotes or prefixes.
  --check                         Don't write files back, just return status
                                  and print summary.
  -d, --diff                      Don't write files back, just output a diff
                                  for each file to stdout.
  --compact-diff                  Same as --diff but only show lines that
                                  would change plus a few lines of context.
  --assert-consistent-execution   Assert that all cells have been executed in
                                  correct order.
  --exclude PATTERN               Regular expression to match paths which
                                  should be exluded when searching
                                  directories.  [default: (/.git/|/.ipynb_chec
                                  kpoints/|/build/|/dist/)]
  --accepted-languages PATTERN    Only format Jupyter notebooks in these
                                  languages.  [default: python]
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

Report formatting suggestions for a given notebook (this is particularly useful for CI workflows):
```bash
$ jupyfmt --check --compact-diff Notebook.ipynb
--- notebook_dir/Notebook.ipynb - Cell 1 (original)
+++ notebook_dir/Notebook.ipynb - Cell 1 (formatted)
@@ -1,2 +1,2 @@
-def foo (*args):
+def foo(*args):
     return sum(args)

--- notebook_dir/Notebook.ipynb - Cell 2 (original)
+++ notebook_dir/Notebook.ipynb - Cell 2 (formatted)
@@ -1 +1 @@
-foo(1, 2,3)
+foo(1, 2, 3)

2 cell(s) would be changed 😬
1 cell(s) would be left unchanged 🎉

1 file(s) would be changed 😬
```

## Mega-Linter Integration

`jupyfmt` can be run as part of [Mega-Linter](https://github.com/nvuillam/mega-linter) by adding the following to `.mega-linter.yml`:

```yaml
PLUGINS:
  - https://raw.githubusercontent.com/kpj/jupyfmt/master/mega-linter-plugin-jupyfmt/jupyfmt.megalinter-descriptor.yml

ENABLE_LINTERS:
  - JUPYTER_JUPYFMT
```
