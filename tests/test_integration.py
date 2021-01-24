import nbformat as nbf

import pytest
from click.testing import CliRunner

import jupyfmt


@pytest.fixture
def valid_notebook(tmp_path):
    nb = nbf.v4.new_notebook()

    nb['cells'] = [
        nbf.v4.new_code_cell('1 + 1'),
        nbf.v4.new_code_cell('%time 1 + 1'),
        nbf.v4.new_code_cell('%%time\n1 + 1'),
    ]

    fname = tmp_path / 'notebook.ipynb'
    with open(fname, 'w') as fd:
        nbf.write(nb, fd)

    return fname


@pytest.fixture
def invalid_notebook(tmp_path):
    nb = nbf.v4.new_notebook()

    code = '1+1'
    nb['cells'] = [nbf.v4.new_code_cell(code)]

    fname = tmp_path / 'notebook.ipynb'
    with open(fname, 'w') as fd:
        nbf.write(nb, fd)

    return fname


def test_valid_notebooks(valid_notebook):
    runner = CliRunner()

    result = runner.invoke(jupyfmt.main, ['--check', str(valid_notebook)])
    assert result.exit_code == 0
    assert '3 cell(s) would be left unchanged' in result.output
    assert '1 file(s) would be left unchanged' in result.output


def test_invalid_notebooks(invalid_notebook):
    runner = CliRunner()

    result = runner.invoke(jupyfmt.main, ['--check', str(invalid_notebook)])
    assert result.exit_code == 1
    assert '1 cell(s) would be changed' in result.output
    assert '1 file(s) would be changed' in result.output
