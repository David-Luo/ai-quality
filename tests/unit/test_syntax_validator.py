# tests/unit/test_syntax_validator.py

import pytest
from qoder.validators.syntax_validator import SyntaxValidator


def test_valid_python_code():
    """测试有效的 Python 代码"""
    code = """
def test_example():
    x = 1 + 2
    assert x == 3
"""
    is_valid, error = SyntaxValidator.check(code)
    assert is_valid is True
    assert error == ""


def test_invalid_syntax():
    """测试语法错误"""
    code = """
def test_example(
    # Missing closing parenthesis
"""
    is_valid, error = SyntaxValidator.check(code)
    assert is_valid is False
    assert "SyntaxError" in error


def test_indentation_error():
    """测试缩进错误"""
    code = """
def test_example():
if True:
pass
"""
    is_valid, error = SyntaxValidator.check(code)
    assert is_valid is False
    assert "SyntaxError" in error
