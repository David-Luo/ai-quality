# src/qoder/models/case_models.py

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TestStep:
    """单个测试步骤"""
    step_number: int
    action: str                       # 操作描述
    expected_result: str              # 预期结果
    request: Optional[str] = None     # API 请求(API 用例专用)


@dataclass
class ParsedCase:
    """解析后的测试用例"""
    id: str                           # TC_001
    title: str                        # 用例标题
    module: str                       # 所属模块
    priority: str                     # P0-P3
    type: str                         # functional/api/ui/boundary/exception/security
    tags: list[str] = field(default_factory=list)
    status: str = "draft"             # draft/approved/deprecated
    preconditions: list[str] = field(default_factory=list)
    steps: list[TestStep] = field(default_factory=list)
    test_data: dict[str, str] = field(default_factory=dict)
    notes: str = ""
    source_path: str = ""             # 源 Markdown 文件路径
    frontmatter: dict = field(default_factory=dict)  # 完整 Frontmatter(用于回写)

    @property
    def is_api(self) -> bool:
        """判断是否为 API 测试用例"""
        return self.type == "api"

    @property
    def slug(self) -> str:
        """生成 URL/文件名安全的 slug"""
        import re
        slug = self.title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '_', slug).strip('_')
        # 中文转拼音(可选依赖 pypinyin)
        return slug or f"case_{self.id}"


@dataclass
class GeneratedScript:
    """生成的测试脚本"""
    case_id: str                      # 关联用例 ID
    framework: str                    # playwright | pytest
    code: str                         # Python 源代码
    output_path: str                  # 输出文件路径
    validation_status: str = "pending"  # passed/failed/needs_review/pending
    validation_errors: list[str] = field(default_factory=list)


@dataclass
class GenerationSummary:
    """生成结果汇总"""
    total: int = 0
    generated: int = 0
    skipped: int = 0
    ui_count: int = 0
    api_count: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class GenerationResult:
    """Agent execute() 的返回值"""
    scripts: list[GeneratedScript] = field(default_factory=list)
    summary: GenerationSummary = field(default_factory=GenerationSummary)
    status: str = "success"           # success/partial/failed
