import nbformat as nbf

import pytest
from click.testing import CliRunner

import jupyfmt


@pytest.fixture
def valid_notebook(tmp_path):
    nb = nbf.v4.new_notebook()

    code = '1 + 1'
    nb['cells'] = [
        nbf.v4.new_code_cell(code)
    ]

    fname = tmp_path / 'notebook.ipynb'
    with open(fname, 'w') as fd:
        nbf.write(nb, fd)

    return fname


@pytest.fixture
def invalid_notebook(tmp_path):
    nb = nbf.v4.new_notebook()

    code = '1+1'
    nb['cells'] = [
        nbf.v4.new_code_cell(code)
    ]

    fname = tmp_path / 'notebook.ipynb'
    with open(fname, 'w') as fd:
        nbf.write(nb, fd)

    return fname


def test_valid_notebooks(valid_notebook):
    runner = CliRunner()

    result = runner.invoke(jupyfmt.main, [str(valid_notebook)])
    assert result.exit_code == 0


def test_invalid_notebooks(invalid_notebook):
    runner = CliRunner()

    result = runner.invoke(jupyfmt.main, [str(invalid_notebook)])
    assert result.exit_code == 1
