from __future__ import annotations

import sys

import pydantic

from ._utils import Colors, organization_info
from .._exceptions import APIError, OpenAIError


class CLIError(OpenAIError):
    ...


class SilentCLIError(CLIError):
    ...


def display_error(err: CLIError | APIError | pydantic.ValidationError) -> None:
    if isinstance(err, SilentCLIError):
        return

    sys.stderr.write(
        f"{organization_info()}{Colors.FAIL}Error:{Colors.ENDC} {err}\n"
    )
