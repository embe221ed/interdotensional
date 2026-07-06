"""Token substitution utilities.

Theme configs reference palette colors as ``$token$`` (e.g. ``$red$``,
``$bg_primary$``). Nested palette keys flatten to dotted tokens
(``$git.add$``). Substitution happens before Jinja2 rendering, so templates
only ever see fully resolved values.
"""

import re

TOKEN_PATTERN = re.compile(r"\$([a-zA-Z0-9_.]+)\$")


def substitute_tokens(data, tokens: dict[str, str]):
    """Recursively substitute ``$TOKEN$`` occurrences in a YAML-parsed structure.

    Unknown tokens are left as-is so :func:`find_unresolved_tokens` can report
    them with their location.
    """
    if isinstance(data, str):
        # str() guards against unquoted YAML palette values (ints, floats):
        # re.sub requires the replacer to return a string.
        return TOKEN_PATTERN.sub(
            lambda m: str(tokens.get(m.group(1), m.group(0))), data
        )
    if isinstance(data, dict):
        return {k: substitute_tokens(v, tokens) for k, v in data.items()}
    if isinstance(data, list):
        return [substitute_tokens(item, tokens) for item in data]
    return data


def find_unresolved_tokens(data, path: str = "") -> list[tuple[str, str]]:
    """Return ``(path, token)`` pairs for any ``$TOKEN$`` left after substitution."""
    unresolved = []
    if isinstance(data, str):
        for match in TOKEN_PATTERN.finditer(data):
            unresolved.append((path, match.group(0)))
    elif isinstance(data, dict):
        for k, v in data.items():
            unresolved.extend(
                find_unresolved_tokens(v, f"{path}.{k}" if path else str(k))
            )
    elif isinstance(data, list):
        for i, item in enumerate(data):
            unresolved.extend(find_unresolved_tokens(item, f"{path}[{i}]"))
    return unresolved


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten a nested dict: ``{'git': {'add': 'X'}}`` -> ``{'git.add': 'X'}``."""
    items: dict = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items
