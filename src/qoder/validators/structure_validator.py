# src/qoder/validators/structure_validator.py

import ast


class StructureValidator:
    """脚本结构验证"""
    
    @staticmethod
    def check(code: str, framework: str) -> tuple[bool, str]:
        """检查脚本结构
        
        Returns:
            (is_valid, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False, "Invalid Python syntax"
        
        # 检查是否存在 test_ 函数
        test_functions = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        
        if len(test_functions) != 1:
            return False, f"Expected exactly 1 test function, found {len(test_functions)}"
        
        # 检查参数签名
        func = test_functions[0]
        args = [arg.arg for arg in func.args.args]
        
        if framework == "playwright":
            if "page" not in args:
                return False, "UI test function missing 'page' parameter"
        elif framework == "pytest":
            if "api_client" not in args:
                return False, "API test function missing 'api_client' parameter"
        
        # 检查包含 docstring
        if not (func.body and isinstance(func.body[0], ast.Expr) and isinstance(func.body[0].value, ast.Constant)):
            return False, "Test function missing docstring"
        
        # 检查至少有一个断言
        has_assertion = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                has_assertion = True
                break
            # Playwright: expect() 函数调用
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "expect":
                    has_assertion = True
                    break
                # 或者 expect().method() 链式调用
                if isinstance(node.func, ast.Attribute) and node.func.attr == "expect":
                    has_assertion = True
                    break
        
        if not has_assertion:
            return False, "Test function has no assertions"
        
        return True, ""
