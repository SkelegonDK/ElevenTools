import re


def detect_string_variables(text: str):
    """
    Detects string variables in a given text
    """
    return re.findall(r"\{([^}]+)\}", text)


def detect_phonetic_variables(text: str):
    """
    Detect string variables in double square brackets.
    """
    return re.findall(r"\[\[([^]]+)\]\]", text)


def detect_phonetic_conversion(script: str):
    """
    Detect phonetic conversion string format [[language:word]], and returns a list of tuples with language and word.
    Example: [("english", "hello"), ("french", "bonjour")]
    """
    return re.findall(r"\[\[([^:]+):([^]]+)\]\]", script)
