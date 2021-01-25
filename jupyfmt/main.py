import re
import difflib
from pathlib import Path

from typing import Union, List

import black
import nbformat as nbf

import click


PathLike = Union[Path, str]


def format_file(
    notebook_path: PathLike,
    mode: black.FileMode,
    check: bool,
    diff: bool,
    compact_diff: bool,
):
    with open(notebook_path) as fd:
        nb = nbf.read(fd, as_version=4)

    cells_errored = 0
    cells_changed = 0
    cells_unchanged = 0
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue

        orig_source = cell['source']

        # black expects empty line at end of file
        # for notebook cells, this does not make sense
        orig_source += '\n'

        # Jupyter cell magic can mess up black
        # TODO: this is a bad hack
        orig_source = re.sub('^%', '#%#jupylint#', orig_source, flags=re.M)

        try:
            fmted_source = black.format_str(orig_source, mode=mode)
        except black.InvalidInput as e:
            if check:
                print(f'Error while formatting cell {i}: {e}')
                cells_errored += 1
                continue
            else:
                raise e

        if orig_source != fmted_source:
            fmted_source = re.sub('^#%#jupylint#', '%', fmted_source, flags=re.M)

            header = f'{notebook_path} - Cell {i} '

            if compact_diff:
                diff_result = difflib.unified_diff(
                    orig_source.splitlines(keepends=True),
                    fmted_source.splitlines(keepends=True),
                    fromfile=header,
                    tofile=header,
                )
            elif diff:
                diff_result = difflib.ndiff(
                    orig_source.splitlines(keepends=True),
                    fmted_source.splitlines(keepends=True),
                )

            if compact_diff or diff:
                diff_str = ''.join(diff_result)
                print(diff_str)

            if fmted_source.endswith('\n'):
                # remove dummy newline we added earlier
                fmted_source = fmted_source[:-1]
            fmted_cell = nbf.v4.new_code_cell(fmted_source)
            nb['cells'][i] = fmted_cell

            cells_changed += 1
        else:
            cells_unchanged += 1

    if cells_errored == 0 and not check and not compact_diff and not diff:
        with open(notebook_path, 'w') as fd:
            nbf.write(nb, fd)

    if check:
        if not diff and not compact_diff:
            print(notebook_path)

        if cells_errored > 0:
            print(f'{cells_errored} cell(s) raised parsing errors 🤕')
        if cells_changed > 0:
            print(f'{cells_changed} cell(s) would be changed 😬')
        if cells_unchanged > 0:
            print(f'{cells_unchanged} cell(s) would be left unchanged 🎉')
        print()

    return cells_errored, cells_changed, cells_unchanged


def get_notebooks_in_dir(path, exclude_regex):
    for child in path.iterdir():
        exclude_match = exclude_regex.search(str(child.resolve().as_posix()))
        if exclude_match and exclude_match.group(0):
            continue

        if child.is_dir():
            yield from get_notebooks_in_dir(child, exclude_regex)
        elif child.is_file() and child.suffix == '.ipynb':
            yield child


@click.command()
@click.option(
    '-l',
    '--line-length',
    default=88,
    type=int,
    help='How many characters per line to allow.',
    metavar='INT',
)
@click.option(
    '-S',
    '--skip-string-normalization',
    is_flag=True,
    default=False,
    help='Don\'t normalize string quotes or prefixes.',
)
@click.option(
    '--check',
    is_flag=True,
    help=('Don\'t write files back, just return status and print summary.'),
)
@click.option(
    '-d',
    '--diff',
    is_flag=True,
    help='Don\'t write files back, just output a diff for each file to stdout.',
)
@click.option(
    '--compact-diff',
    is_flag=True,
    help=(
        'Same as --diff but only show lines that would change plus a few lines of context.'
    ),
)
@click.option(
    '--exclude',
    type=str,
    metavar='PATTERN',
    default=r'(.git|.ipynb_checkpoints|build|dist)',
    help=(
        'Regular expression to match paths which should be exluded when searching directories.'
    ),
    show_default=True,
)
@click.argument(
    'path_list',
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, allow_dash=False
    ),
)
@click.pass_context
def main(
    ctx: click.Context,
    line_length: int,
    skip_string_normalization: bool,
    check: bool,
    diff: bool,
    compact_diff: bool,
    exclude: str,
    path_list: List[PathLike],
):
    """The uncompromising Jupyter notebook formatter.

    PATH_LIST specifies notebooks and directories to search for notebooks in. By default, all notebooks will be formatted in-place. Use `--check`, `--diff` (or `--compact-diff`) to print summary reports instead.
    """

    # gather files to format
    exclude_regex = re.compile(exclude)
    files_to_format = set()
    for path in path_list:
        path = Path(path)

        if path.is_file():
            files_to_format.add(path)
        elif path.is_dir():
            files_to_format.update(get_notebooks_in_dir(path, exclude_regex))

    # format files
    mode = black.FileMode(
        line_length=line_length, string_normalization=not skip_string_normalization
    )

    files_errored = 0
    files_changed = 0
    files_unchanged = 0
    for notebook_fname in files_to_format:
        try:
            cells_errored, cells_changed, cells_unchanged = format_file(
                notebook_fname, mode, check, diff, compact_diff
            )
        except Exception as e:
            if check:
                print(f'Error while formatting file "{notebook_fname}": {e}')
                files_errored += 1
                continue
            else:
                raise e

        if cells_errored > 0:
            files_errored += 1
        elif cells_changed > 0:
            files_changed += 1
        else:
            files_unchanged += 1

    # report
    if check:
        if files_errored > 0:
            print(f'{files_errored} file(s) raised parsing errors 🤕')
        if files_changed > 0:
            print(f'{files_changed} file(s) would be changed 😬')
        if files_unchanged > 0:
            print(f'{files_unchanged} file(s) would be left unchanged 🎉')

    # return appropriate exit code
    exit_code = 0

    if check:
        if files_errored > 0:
            exit_code = 2
        elif files_changed > 0:
            exit_code = 1

    ctx.exit(exit_code)


if __name__ == '__main__':
    main()
