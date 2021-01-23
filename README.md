# jupyfmt

[![PyPI](https://img.shields.io/pypi/v/jupyfmt.svg?style=flat)](https://pypi.python.org/pypi/jupyfmt)
[![Tests](https://github.com/kpj/jupyfmt/workflows/Tests/badge.svg)](https://github.com/kpj/jupyfmt/actions)

Format code in Jupyter notebooks.

[jupyter-black](https://github.com/drillan/jupyter-black) and [nb_black](https://github.com/dnanhkhoa/nb_black) are fabulous Jupyter extensions for formatting your code in the editor.
`jupyfmt` allows you to assert properly formatted Jupyter notebook cells in your CI.


## Installation

```python
$ pip install jupyfmt
```


## Usage

```bash
$ jupyfmt Notebook.ipynb
--- Cell 1 ---
--- original
+++ new
@@ -1,2 +1,2 @@
-def foo (*args):
+def foo(*args):
     return sum(args)


--- Cell 2 ---
--- original
+++ new
@@ -1 +1 @@
-foo(1, 2,3)
+foo(1, 2, 3)
```
