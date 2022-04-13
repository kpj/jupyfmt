import re
import json
import subprocess

import black

from typing import Optional


SKIPPABLE_MAGIC_CODES = [
    # non-python languages
    "bash",
    "html",
    "javascript",
    "js",
    "latex",
    "markdown",
    "perl",
    "ruby",
    "sh",
    "svg",
    # extra functionality
    "writefile",
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
        raise FormattingException(e)

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

    return re.sub("# %#jupylint#", "#%#jupylint#", proc.stdout.decode(), flags=re.M)


NONPYTHON_FORMATTERS = {"R": format_r}


def get_formatter(source: str, exclude_nonkernel_languages: bool) -> str:
    """Detect language of code cell by parsing cell magic."""
    # empty cells need no formatter
    if len(source) == 0:
        return None

    # detect formatter based on cell magic in forst non-empty line
    first_nonempty_line = next(line for line in source.splitlines() if line)

    # decide whether to skip cell
    if exclude_nonkernel_languages:
        skip_codes = SKIPPABLE_MAGIC_CODES + list(NONPYTHON_FORMATTERS.keys())
    else:
        skip_codes = SKIPPABLE_MAGIC_CODES

    if any(first_nonempty_line.startswith(f"%%{magic}") for magic in skip_codes):
        return None

    # detect language
    marker = first_nonempty_line.split()[0][2:]  # "%%<lang> other"

    # return formatter associated with language
    return NONPYTHON_FORMATTERS.get(marker, format_python)


def format_code(
    orig_source: str, exclude_nonkernel_languages: bool, **kwargs
) -> Optional[str]:
    """Detect language and format code."""
    formatter = get_formatter(orig_source, exclude_nonkernel_languages)

    if formatter is None:
        return None

    # some formatters expect empty line at end of non-empty file
    # for notebook cells, this does not make sense
    if len(orig_source) > 0:
        orig_source += "\n"

    # Jupyter cell magic can mess up black
    # TODO: this is a bad hack
    orig_source = re.sub("^%", "#%#jupylint#", orig_source, flags=re.M)
    orig_source = re.sub("^!", "#!#jupylint#", orig_source, flags=re.M)

    fmted_source = formatter(orig_source, **kwargs)

    fmted_source = re.sub("^#%#jupylint#", "%", fmted_source, flags=re.M)
    fmted_source = re.sub("^#!#jupylint#", "!", fmted_source, flags=re.M)

    # remove added newline if needed
    if fmted_source.endswith("\n"):
        fmted_source = fmted_source[:-1]

    return fmted_source
