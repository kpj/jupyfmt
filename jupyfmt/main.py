import difflib
from pathlib import Path

from typing import Union, List

import black
import nbformat as nbf

import click


PathLike = Union[Path, str]


def format_file(notebook_path: PathLike, mode: black.FileMode):
    with open(notebook_path) as fd:
        nb = nbf.read(fd, as_version=4)

    cells_changed = 0
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue

        orig_source = cell['source']

        # black expects empty line at end of file
        # for notebook cells, this does not make sense
        orig_source += '\n'

        try:
            fmted_source = black.format_str(orig_source, mode=mode)
        except black.InvalidInput as e:
            print(f'Error "{str(e)}" while formatting code with black.')

        if orig_source != fmted_source:
            print(f'--- Cell {i} ---')

            # diff = difflib.ndiff(orig_source.split('\n'), fmted_source.split('\n'))
            diff = difflib.unified_diff(
                orig_source.splitlines(keepends=True),
                fmted_source.splitlines(keepends=True),
                fromfile='original',
                tofile='new',
            )

            diff_str = ''.join(diff)

            print(diff_str)
            print('')

            cells_changed += 1

    return cells_changed


def get_notebooks_in_dir(path):
    for child in path.iterdir():
        if child.is_dir():
            yield from get_notebooks_in_dir(child)
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
    path_list: List[PathLike],
):
    files_to_format = set()
    for path in path_list:
        path = Path(path)

        if path.is_file():
            files_to_format.add(path)
        elif path.is_dir():
            files_to_format.update(get_notebooks_in_dir(path))

    mode = black.FileMode(
        line_length=line_length, string_normalization=not skip_string_normalization
    )

    files_changed = 0
    for notebook_fname in files_to_format:
        if format_file(notebook_fname, mode):
            files_changed += 1

    if files_changed:
        ctx.exit(1)


if __name__ == '__main__':
    main()
