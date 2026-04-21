# src/qoder/agents/script_generator/nodes/validator.py

import ast
import py_compile
import tempfile
import os

from qoder.validators.syntax_validator import SyntaxValidator
from qoder.validators.structure_validator import StructureValidator
from qoder.validators.antipattern_checker import AntipatternChecker


def validator_node(state: dict) -> dict:
    """验证生成的脚本"""
    validation_results = []
    retry_scripts = []
    
    for script in state.get("generated_scripts", []):
        if script.get("validation_status") == "pending":
            errors = []
            
            # L1: 语法检查
            syntax_ok, syntax_err = SyntaxValidator.check(script["code"])
            if not syntax_ok:
                errors.append(f"Syntax: {syntax_err}")
            
            # L2: 结构检查
            structure_ok, structure_err = StructureValidator.check(
                script["code"], script["framework"]
            )
            if not structure_ok:
                errors.append(f"Structure: {structure_err}")
            
            # L3: 反模式检查
            antipatterns = AntipatternChecker.check(script["code"], script["framework"])
            errors.extend(f"Anti-pattern: {a}" for a in antipatterns)
            
            if errors:
                script["validation_status"] = "failed"
                script["validation_errors"] = errors
                if state.get("retry_count", 0) < 3:
                    retry_scripts.append(script)
                else:
                    script["validation_status"] = "needs_review"
                    script["code"] = f"# TODO: NEEDS MANUAL REVIEW\n\n{script['code']}"
            else:
                script["validation_status"] = "passed"
            
            validation_results.append({
                "case_id": script["case_id"],
                "status": script["validation_status"],
                "errors": errors,
            })
    
    return {
        "generated_scripts": state["generated_scripts"],
        "validation_results": validation_results,
        "retry_scripts": retry_scripts,
        "retry_count": state.get("retry_count", 0) + 1 if retry_scripts else state.get("retry_count", 0),
    }
