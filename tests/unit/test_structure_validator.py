# tests/unit/test_structure_validator.py

import pytest
from qoder.validators.structure_validator import StructureValidator


def test_valid_ui_structure():
    """测试有效的 UI 测试结构"""
    code = """
def test_login(page):
    \"\"\"Test login functionality\"\"\"
    page.goto("/login")
    page.get_by_label("Username").fill("test")
    expect(page).to_have_url("/dashboard")
"""
    is_valid, error = StructureValidator.check(code, "playwright")
    assert is_valid is True


def test_valid_api_structure():
    """测试有效的 API 测试结构"""
    code = """
def test_get_user(api_client):
    \"\"\"Test GET user endpoint\"\"\"
    response = api_client.get("/users/1")
    assert response.status_code == 200
"""
    is_valid, error = StructureValidator.check(code, "pytest")
    assert is_valid is True


def test_missing_page_parameter():
    """测试缺少 page 参数"""
    code = """
def test_login():
    \"\"\"Test login\"\"\"
    pass
"""
    is_valid, error = StructureValidator.check(code, "playwright")
    assert is_valid is False
    assert "missing 'page' parameter" in error


def test_missing_api_client_parameter():
    """测试缺少 api_client 参数"""
    code = """
def test_get_user():
    \"\"\"Test get user\"\"\"
    pass
"""
    is_valid, error = StructureValidator.check(code, "pytest")
    assert is_valid is False
    assert "missing 'api_client' parameter" in error


def test_missing_docstring():
    """测试缺少 docstring"""
    code = """
def test_login(page):
    pass
"""
    is_valid, error = StructureValidator.check(code, "playwright")
    assert is_valid is False
    assert "missing docstring" in error


def test_missing_assertion():
    """测试缺少断言"""
    code = """
def test_login(page):
    \"\"\"Test login\"\"\"
    page.goto("/login")
"""
    is_valid, error = StructureValidator.check(code, "playwright")
    assert is_valid is False
    assert "no assertions" in error


def test_multiple_test_functions():
    """测试多个 test 函数"""
    code = """
def test_login(page):
    \"\"\"Test login\"\"\"
    pass

def test_logout(page):
    \"\"\"Test logout\"\"\"
    pass
"""
    is_valid, error = StructureValidator.check(code, "playwright")
    assert is_valid is False
    assert "Expected exactly 1 test function" in error
