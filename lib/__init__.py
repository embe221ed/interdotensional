import re

def substitute_tokens(data, tokens):
    """
    Recursively walk through the data structure (which can be nested dicts, lists, or strings)
    and substitute any occurrence of a token of the form $TOKEN$ with its corresponding value
    from the tokens dictionary.
    
    :param data: The YAML-parsed structure (dict, list, str, etc.)
    :param tokens: A dictionary mapping token names (without the $ signs) to their substitution values.
    :return: A new data structure with the tokens substituted.
    """
    if isinstance(data, str):
        # Replace tokens in strings using regex
        pattern = re.compile(r'\$([a-zA-Z0-9_.]+)\$')
        def replacer(match):
            token_name = match.group(1)
            return tokens.get(token_name, match.group(0))  # fallback to original if token not found
        return pattern.sub(replacer, data)
    elif isinstance(data, dict):
        # Recursively process dictionary values
        return { k: substitute_tokens(v, tokens) for k, v in data.items() }
    elif isinstance(data, list):
        # Recursively process list items
        return [ substitute_tokens(item, tokens) for item in data ]
    else:
        # For other data types, return as is
        return data

def flatten_dict(d, parent_key='', sep='.'):
    """
    Recursively flattens a nested dictionary.
    For example, {'git': {'add': 'X'}} becomes {'git.add': 'X'}.
    
    :param d: The dictionary to flatten.
    :param parent_key: The base key string (used in recursion).
    :param sep: The separator between keys.
    :return: A new flat dictionary.
    """
    items = {}

    for k, v in d.items():
        new_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v

    return items
