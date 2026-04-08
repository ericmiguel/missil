"""Internal helper for module-level deprecation warnings."""

from collections.abc import Callable
from typing import Any
import warnings


def make_deprecated_getattr(
    mapping: dict[str, str],
    module_globals: dict[str, Any],
    module_name: str,
) -> Callable[[str], object]:
    """
    Return a module-level ``__getattr__`` that emits ``DeprecationWarning``.

    Parameters
    ----------
    mapping : dict[str, str]
        Old name -> new name pairs.
    module_globals : dict[str, Any]
        The calling module's ``globals()`` dict.
    module_name : str
        The calling module's ``__name__``.

    Returns
    -------
    Callable[[str], object]
        A ``__getattr__`` function ready to be assigned at module level.

    Examples
    --------
    ```python
    from missil._deprecated import make_deprecated_getattr

    __getattr__ = make_deprecated_getattr(
        {"OldName": "NewName"},
        globals(),
        __name__,
    )
    ```
    """

    def __getattr__(name: str) -> object:
        if name in mapping:
            new_name = mapping[name]
            warnings.warn(
                f"'{name}' is deprecated and will be removed in a future version. "
                f"Use '{new_name}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return module_globals[new_name]
        raise AttributeError(f"module {module_name!r} has no attribute {name!r}")

    return __getattr__
