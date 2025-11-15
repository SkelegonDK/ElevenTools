import re


def detect_string_variables(text: str) -> list[str]:
    """Detects string variables in a given text enclosed in curly braces.

    Args:
        text (str): The input text to search for variables.

    Returns:
        List[str]: A list of variable names found in the text (without curly braces).
            For example, for text "Hello {name}", returns ["name"].
    """
    return re.findall(r"\{([^}]+)\}", text)


def detect_phonetic_variables(text: str) -> list[str]:
    """Detects phonetic variables in a given text enclosed in double square brackets.

    Args:
        text (str): The input text to search for phonetic variables.

    Returns:
        List[str]: A list of phonetic variable names found in the text (without brackets).
            For example, for text "The [[word]]", returns ["word"].
    """
    return re.findall(r"\[\[([^]]+)\]\]", text)


def detect_phonetic_conversion(script: str) -> list[tuple[str, str]]:
    """Detects phonetic conversion strings in the format [[language:word]].

    Args:
        script (str): The input text to search for phonetic conversion strings.

    Returns:
        List[Tuple[str, str]]: A list of tuples containing (language, word) pairs.
            For example, for text "[[english:hello]]", returns [("english", "hello")].
    """
    return re.findall(r"\[\[([^:]+):([^]]+)\]\]", script)
