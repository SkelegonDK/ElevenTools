import pytest
from functions import detect_string_variables, detect_phonetic_variables, detect_phonetic_conversion

def test_detect_string_variables():
    text = "Hello {name}, welcome to {place}!"
    result = detect_string_variables(text)
    assert result == ["name", "place"]

def test_detect_string_variables_no_variables():
    text = "Hello, welcome to our place!"
    result = detect_string_variables(text)
    assert result == []

def test_detect_phonetic_variables():
    text = "The pronunciation of [[word]] is important."
    result = detect_phonetic_variables(text)
    assert result == ["word"]

def test_detect_phonetic_variables_no_variables():
    text = "The pronunciation is important."
    result = detect_phonetic_variables(text)
    assert result == []

def test_detect_phonetic_conversion():
    script = "Say [[english:hello]] and [[french:bonjour]]"
    result = detect_phonetic_conversion(script)
    assert result == [("english", "hello"), ("french", "bonjour")]

def test_detect_phonetic_conversion_no_conversion():
    script = "Say hello and bonjour"
    result = detect_phonetic_conversion(script)
    assert result == []
