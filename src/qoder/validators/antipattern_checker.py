# src/qoder/validators/antipattern_checker.py

import re
import ast


class AntipatternChecker:
    """反模式检查"""
    
    UI_RULES = [
        ("UI-001", r'locator\s*\(\s*["\']//', "XPath selector detected"),
        ("UI-001", r'xpath\s*=', "XPath selector detected"),
        ("UI-002", r'wait_for_timeout\s*\(', "Fixed wait detected (wait_for_timeout)"),
        ("UI-004", r'page\.goto\s*\(\s*["\']https?://', "Hardcoded URL detected"),
    ]
    
    API_RULES = [
        ("API-001", r'import\s+requests\b', "Use httpx, not requests"),
        ("API-004", r'httpx\.\w+\(\s*["\']https?://', "Hardcoded Base URL detected"),
    ]
    
    COMMON_RULES = [
        ("COMMON-001", r'(?i)(password|token|api_key|secret)\s*=\s*["\'][^"\']{8,}', "Hardcoded secret detected"),
    ]
    
    @classmethod
    def check(cls, code: str, framework: str) -> list[str]:
        """检查反模式
        
        Returns:
            List of violation descriptions
        """
        violations = []
        
        # Common rules
        for rule_id, pattern, desc in cls.COMMON_RULES:
            if re.search(pattern, code):
                violations.append(f"{rule_id}: {desc}")
        
        # Framework-specific rules
        rules = cls.UI_RULES if framework == "playwright" else cls.API_RULES
        for rule_id, pattern, desc in rules:
            if re.search(pattern, code):
                violations.append(f"{rule_id}: {desc}")
        
        return violations
