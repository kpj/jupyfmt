import re
import json
import subprocess

import black

from typing import Optional


SKIPPABLE_MAGIC_CODES = [
    # non-python languages
    'bash',
    'html',
    'javascript',
    'js',
    'latex',
    'markdown',
    'perl',
    'ruby',
    'sh',
    'svg',
    # extra functionality
    'writefile',
]


class FormattingException(Exception):
    pass


def format_python(orig_source: str, **kwargs) -> str:
    """Format Python code using Black.

    https://github.com/psf/black
    """
    try:
        fmted_source = black.format_str(orig_source, **kwargs)
    except black.InvalidInput as e:
        raise FormattingException from e

    return fmted_source


def format_r(orig_source: str, **kwargs) -> str:
    """Format R code using styler.

    https://github.com/r-lib/styler
    """
    proc = subprocess.run(
        ["Rscript", "-e", f"styler::style_text({json.dumps(orig_source)})"],
        capture_output=True,
    )

    if proc.returncode != 0:
        raise FormattingException(proc.stderr.decode())

    return re.sub('# %#jupylint#', '#%#jupylint#', proc.stdout.decode(), flags=re.M)


def get_formatter(source: str) -> str:
    """Detect language of code cell by parsing cell magic."""
    first_nonempty_line = next(line for line in source.splitlines() if line)

    if any(
        first_nonempty_line.startswith(f'%%{magic}') for magic in SKIPPABLE_MAGIC_CODES
    ):
        return None

    # detect language
    marker = first_nonempty_line.split()[0][2:]  # "%%<lang> other"
    return {"R": format_r}.get(marker, format_python)


def format_code(orig_source: str, **kwargs) -> Optional[str]:
    """Detect language and format code."""
    formatter = get_formatter(orig_source)

    if formatter is None:
        return None

    # some formatters expect empty line at end of non-empty file
    # for notebook cells, this does not make sense
    if len(orig_source) > 0:
        orig_source += '\n'

    # Jupyter cell magic can mess up black
    # TODO: this is a bad hack
    orig_source = re.sub('^%', '#%#jupylint#', orig_source, flags=re.M)
    orig_source = re.sub('^!', '#!#jupylint#', orig_source, flags=re.M)

    fmted_source = formatter(orig_source, **kwargs)

    fmted_source = re.sub('^#%#jupylint#', '%', fmted_source, flags=re.M)
    fmted_source = re.sub('^#!#jupylint#', '!', fmted_source, flags=re.M)

    # remove added newline if needed
    if fmted_source.endswith("\n"):
        fmted_source = fmted_source[:-1]

    return fmted_source
