# src/qoder/validators/syntax_validator.py

import ast
import py_compile
import tempfile
import os


class SyntaxValidator:
    """Python 语法验证"""
    
    @staticmethod
    def check(code: str) -> tuple[bool, str]:
        """检查 Python 代码语法
        
        Returns:
            (is_valid, error_message)
        """
        # L1: AST 解析
        try:
            ast.parse(code)
        except SyntaxError as e:
            return False, f"SyntaxError: {e.msg} (line {e.lineno})"
        
        # L2: 编译检查
        try:
            with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
                f.write(code)
                f.flush()
                py_compile.compile(f.name, doraise=True)
        except py_compile.PyCompileError as e:
            return False, f"CompileError: {e}"
        finally:
            if 'f' in locals():
                os.unlink(f.name)
        
        return True, ""
