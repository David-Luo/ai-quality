# L1-07：知识库管理模块需求

**文档版本**：v1.0  
**所属模块**：M7 - 知识库管理  
**依赖模块**：M1（CLI Test Agent）、M2（测试用例管理）  
**最后更新**：2026-04-12

---

## 1. 模块定位

知识库管理模块为 AI 生成测试用例和测试脚本提供上下文增强（RAG），知识来源为**Git 工程内的 `.md` 文件**，无需单独维护。

**核心职责**：
- 自动索引工程内 `.md` 文件，构建向量知识库
- 为 CLI Test Agent 提供语义检索接口，补充 AI 上下文
- 在平台侧提供知识库浏览和搜索功能
- 管理知识库索引的增量更新

**设计原则**：
- **零额外维护**：知识来源就是工程内的 `.md` 文档，写文档即维护知识库
- **本地优先**：知识库索引可在本地构建，CLI 离线可用
- **增量更新**：仅重新索引变更的文件，不全量重建

**知识库覆盖范围**（工程内 `.md` 文件类型）：

| 文件类型 | 典型位置 | 提供的知识 |
|---------|---------|---------|
| 需求文档 | `docs/requirements/` | 功能需求、业务规则 |
| API 文档 | `docs/api/` | 接口定义、参数约束 |
| 页面结构文档 | `docs/ui/` | 页面元素、交互逻辑 |
| 已有测试用例 | `tests/cases/` | 测试模式、历史用例 |
| README/架构文档 | 根目录/docs | 系统概述、模块划分 |

---

## 2. 功能清单

| 编号 | 功能 | 优先级 | 版本 |
|------|------|--------|------|
| F7.1 | 知识库索引构建 | P0 | V1.0 |
| F7.2 | 知识库语义检索（CLI） | P0 | V1.0 |
| F7.3 | 增量索引更新 | P0 | V1.0 |
| F7.4 | 知识库浏览（平台） | P1 | V1.5 |
| F7.5 | 知识条目评分与反馈 | P2 | V2.0 |

---

## 3. F7.1 知识库索引构建

### 3.1 索引构建命令

```bash
# 初始化并构建完整索引
qoder kb index

# 构建指定目录的索引
qoder kb index --path docs/

# 查看索引状态
qoder kb status
```

`qoder kb index` 输出示例：

```
🔍 扫描工程 Markdown 文件...
  找到 47 个 .md 文件

📚 构建知识库索引...
  ████████████████████████ 47/47

✓ 知识库索引完成
  文件数：47
  块数：312
  向量维度：768
  存储路径：tests/.qoder/kb/
  耗时：8.3s
```

### 3.2 文档分块（Chunking）策略

| 分块策略 | 适用场景 | 块大小 |
|---------|---------|-------|
| Markdown 标题分割 | 长文档（>500 行） | 按 H2/H3 章节分割 |
| 固定大小分割 | 短文档或无结构文档 | 512 tokens，重叠 64 tokens |
| 段落分割 | 中等文档 | 按空行分割，最大 256 tokens |

**分块算法优先级**：
1. 识别 Markdown 结构（标题层级）
2. 若单章节 > 512 tokens，递归按子标题分割
3. 若无标题结构，使用固定大小分割

### 3.3 块元数据

每个向量块附带元数据：

```json
{
  "chunk_id": "docs/api/users.md#section-2",
  "file_path": "docs/api/users.md",
  "section_title": "GET /api/users/{id}",
  "file_mtime": 1744444800,
  "content_hash": "sha256:abc123...",
  "token_count": 284,
  "chunk_index": 2,
  "total_chunks": 5
}
```

### 3.4 向量嵌入配置

```toml
# tests/.qoder/config.toml
[kb]
enabled = true
index_paths = [
    "docs/",
    "tests/cases/",
    "README.md",
]
exclude_patterns = [
    "*.draft.md",
    "tests/reports/**",
    ".qoder/**",
]

[kb.embedding]
# 本地模式（无需网络，推荐 CI 环境）
provider = "local"
model = "BAAI/bge-small-zh-v1.5"   # 中文优化嵌入模型
device = "cpu"                       # cpu | cuda | mps

# 云端模式（可选，需要 API Key）
# provider = "openai"
# model = "text-embedding-3-small"

[kb.storage]
type = "qdrant_local"                # qdrant_local | qdrant_server
path = "tests/.qoder/kb/"           # 本地存储路径
collection_name = "test_knowledge"
```

### 3.5 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 向量数据库 | Qdrant（本地模式） | 零依赖，数据文件存在工程内 |
| 嵌入模型（本地） | BAAI/bge-small-zh-v1.5 | 中文优化，256MB，CPU 可用 |
| 嵌入框架 | FastEmbed | 轻量级，无需 PyTorch |
| Markdown 解析 | python-markdown-it | 准确解析 Markdown 结构 |

### 3.6 索引存储位置

```
tests/.qoder/kb/
├── collection/            # Qdrant 本地集合文件
│   ├── vectors/
│   └── payload/
├── index_manifest.json    # 索引文件清单（路径、hash、更新时间）
└── config.json            # 知识库配置快照
```

> `.qoder/kb/` 目录应加入 `.gitignore`，不提交到版本库（按需本地构建）

---

## 4. F7.2 知识库语义检索（CLI）

### 4.1 检索集成到 AI 生成工作流

知识库检索不作为独立命令暴露给用户，而是在 CLI Test Agent 的 AI 生成步骤中**自动触发**：

```
qoder test generate（生成测试用例）
  ↓
Planner 节点：分析需求文本
  ↓
KnowledgeRetriever 节点（自动触发）
  ├─ 查询1：{需求关键词} 相关的已有测试用例
  ├─ 查询2：{功能模块} 相关的 API/页面文档
  └─ 查询3：{业务规则} 相关的需求说明
  ↓
将检索结果注入 LLM 上下文
  ↓
Generator 节点：生成测试用例（带知识库上下文）
```

### 4.2 检索参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| top_k | 5 | 每个查询返回的最相关块数 |
| score_threshold | 0.6 | 相似度阈值，低于此值不使用 |
| max_context_tokens | 2000 | 注入 LLM 的最大 Token 数 |
| query_count | 3 | 并行查询数（每次生成） |

### 4.3 检索查询构造

KnowledgeRetriever 节点基于当前任务自动构造检索查询：

```python
def build_retrieval_queries(task: GenerationTask) -> list[str]:
    """基于生成任务构造检索查询。"""
    queries = []
    
    # 查询1：直接需求文本
    if task.requirement_text:
        queries.append(task.requirement_text[:200])
    
    # 查询2：模块/功能关键词
    if task.module_name:
        queries.append(f"{task.module_name} 功能 测试 接口")
    
    # 查询3：相似历史用例
    if task.case_title:
        queries.append(f"测试用例 {task.case_title}")
    
    return queries[:3]  # 最多 3 个查询
```

### 4.4 上下文注入格式

将检索到的知识注入 LLM Prompt：

```
---知识库上下文（自动检索）---

[来源: docs/api/users.md > GET /api/users/{id}]
GET /api/users/{id} 返回指定用户的完整信息...
响应字段：id, username, email, created_at, role

[来源: tests/cases/auth/TC-001_valid_login.md > 测试步骤]
1. 打开登录页 /login
2. 输入用户名 testuser@example.com
3. 输入密码 Test@123456
...

[来源: docs/requirements/user-management.md > 密码规则]
密码必须满足：至少 8 位，包含大写字母、数字和特殊字符...

---知识库上下文结束---
```

### 4.5 手动查询命令（调试用）

```bash
# 手动查询知识库（用于调试/验证）
qoder kb query "用户登录失败的处理逻辑"

# 输出
检索结果（相似度降序）：

1. [0.92] docs/requirements/auth.md > 登录错误处理
   连续登录失败 5 次后账户锁定 30 分钟...

2. [0.87] tests/cases/auth/TC-005_invalid_password.md > 测试步骤
   1. 输入错误密码 3 次
   2. 验证显示"密码错误，还有 2 次机会"...

3. [0.81] docs/api/auth.md > POST /api/auth/login
   错误响应：{"error": "invalid_credentials", "remaining_attempts": 2}
```

---

## 5. F7.3 增量索引更新

### 5.1 触发时机

| 触发方式 | 说明 |
|---------|------|
| `qoder kb index` 手动触发 | 全量扫描，仅更新变更文件 |
| `qoder test generate` 前自动触发 | 检测变更文件，增量更新 |
| Git Pre-commit Hook（可选） | 提交前自动更新已修改的 `.md` 文件 |

### 5.2 变更检测算法

```python
def detect_changed_files(manifest: IndexManifest, scan_paths: list[str]) -> list[str]:
    """
    检测需要重新索引的文件。
    返回新增、修改的文件路径列表（删除的文件从索引中移除）。
    """
    changed = []
    current_files = {}
    
    # 扫描当前文件
    for path in scan_paths:
        for md_file in glob(f"{path}/**/*.md", recursive=True):
            stat = os.stat(md_file)
            content_hash = compute_file_hash(md_file)
            current_files[md_file] = {
                "mtime": stat.st_mtime,
                "content_hash": content_hash,
            }
    
    # 对比清单：找出新增和修改的文件
    for file_path, meta in current_files.items():
        if file_path not in manifest.files:
            changed.append(file_path)  # 新增文件
        elif manifest.files[file_path]["content_hash"] != meta["content_hash"]:
            changed.append(file_path)  # 内容变更
    
    # 删除不再存在的文件的索引
    for file_path in list(manifest.files.keys()):
        if file_path not in current_files:
            manifest.remove_file(file_path)
    
    return changed
```

### 5.3 增量更新输出

```
🔍 检查知识库更新...
  发现 3 个变更文件

📚 增量更新知识库...
  ✓ docs/api/users.md（已更新）
  ✓ docs/requirements/auth.md（新增）
  ✗ tests/cases/TC-099_draft.md（跳过：排除模式 *.draft.md）

✓ 知识库已更新（+2 文件，总计 314 块）
```

---

## 6. F7.4 知识库浏览（平台，V1.5）

### 6.1 功能描述

平台 Web UI 提供只读的知识库浏览界面，方便团队成员查看已索引的知识内容。

### 6.2 页面功能

**知识库概览页**：
- 索引文件总数、块总数
- 最近更新时间
- 文件类型分布（需求/API文档/测试用例/其他）

**知识文件列表**：
- 按目录树形展示
- 显示文件名、最后更新时间、块数
- 搜索框（语义检索）

**知识文件详情**：
- Markdown 渲染展示
- 对应的向量块分割展示（调试用）
- 关联用例列表（哪些用例引用了此文件的知识）

### 6.3 API 规范

```
GET /api/kb/files             → 知识文件列表（支持分页、搜索）
GET /api/kb/files/{id}        → 知识文件详情
GET /api/kb/search?q={query}  → 语义搜索（返回相关块）
GET /api/kb/stats             → 知识库统计
POST /api/kb/reindex          → 触发重新索引（管理员权限）
```

---

## 7. 与其他模块的接口规范

### 7.1 → M1（CLI Test Agent）

| 接口 | 方向 | 说明 |
|------|------|------|
| 知识库语义检索 API | CLI 调用 | KnowledgeRetriever 节点调用 |
| 增量索引更新 | CLI 触发 | 生成前自动更新 |
| `config.toml` 中的知识库配置 | CLI 读取 | 索引路径、嵌入模型配置 |

### 7.2 → M2（测试用例管理）

| 接口 | 方向 | 说明 |
|------|------|------|
| 测试用例 Markdown 文件 | 知识库索引 | `tests/cases/` 目录自动纳入索引 |
| 用例知识检索 | 知识库提供 | 生成新用例时参考历史用例模式 |

### 7.3 → M8（平台门户）

| 接口 | 方向 | 说明 |
|------|------|------|
| 知识库搜索 API | 平台调用 | 提供 Web 知识库搜索页面 |
| 知识文件元数据 | 平台展示 | 知识库浏览功能 |
| 重新索引触发 | 平台调用 | 管理员手动触发全量重建 |

---

## 8. 技术实现要点

### 8.1 依赖清单

```toml
[project.optional-dependencies]
kb = [
    "qdrant-client>=1.11.0",       # 向量数据库客户端
    "fastembed>=0.3.0",             # 轻量级嵌入框架
    "markdown-it-py>=3.0.0",        # Markdown 解析
    "python-frontmatter>=1.1.0",    # Front Matter 解析
    "tiktoken>=0.7.0",              # Token 计数
]
```

### 8.2 FastEmbed 初始化

```python
from fastembed import TextEmbedding

# 首次使用自动下载模型（~256MB，缓存在 ~/.cache/fastembed/）
embedding_model = TextEmbedding(
    model_name="BAAI/bge-small-zh-v1.5",
    max_length=512,
)

def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = list(embedding_model.embed(texts))
    return [e.tolist() for e in embeddings]
```

### 8.3 Qdrant 本地客户端

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

COLLECTION_NAME = "test_knowledge"
VECTOR_DIM = 384  # bge-small-zh-v1.5 的向量维度


def get_qdrant_client(storage_path: str) -> QdrantClient:
    return QdrantClient(path=storage_path)


def init_collection(client: QdrantClient):
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_DIM,
                distance=Distance.COSINE,
            ),
        )


def search(client: QdrantClient, query: str, top_k: int = 5) -> list[dict]:
    query_vector = embed_texts([query])[0]
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        score_threshold=0.6,
        with_payload=True,
    )
    return [
        {
            "score": hit.score,
            "text": hit.payload["text"],
            "source": hit.payload["chunk_id"],
            "section_title": hit.payload.get("section_title", ""),
        }
        for hit in results
    ]
```

### 8.4 Markdown 分块实现

```python
from markdown_it import MarkdownIt
import re


def split_markdown_by_headings(content: str) -> list[dict]:
    """按 H2/H3 标题分割 Markdown 文档。"""
    md = MarkdownIt()
    tokens = md.parse(content)

    sections = []
    current_section = {"title": "前言", "content": [], "level": 0}

    for token in tokens:
        if token.type == "heading_open":
            level = int(token.tag[1])  # h1=1, h2=2, h3=3
            if level <= 3 and current_section["content"]:
                sections.append(current_section)
                current_section = {"title": "", "content": [], "level": level}
        elif token.type == "inline" and current_section.get("awaiting_title"):
            current_section["title"] = token.content
            current_section["awaiting_title"] = False
        elif token.type == "heading_open":
            current_section["awaiting_title"] = True
        else:
            current_section["content"].append(token.content or "")

    if current_section["content"]:
        sections.append(current_section)

    return [
        {
            "title": s["title"],
            "text": "\n".join(filter(None, s["content"])),
        }
        for s in sections
        if "".join(filter(None, s["content"])).strip()
    ]
```

### 8.5 模型下载优化

首次运行 `qoder kb index` 时，若本地模型未缓存，自动下载：

```
首次使用知识库功能需要下载嵌入模型
模型：BAAI/bge-small-zh-v1.5（~256MB）
下载源：Hugging Face Hub

是否继续下载？[Y/n]：
```

企业环境可配置离线模型路径：

```toml
[kb.embedding]
provider = "local"
model = "BAAI/bge-small-zh-v1.5"
model_cache_dir = "/shared/models/"   # 企业内网共享模型目录
```

---

## 9. 验收标准汇总

### MVP（V1.0）必须满足

- [ ] `qoder kb index` 能扫描工程内所有 `.md` 文件并构建向量索引
- [ ] `qoder test generate` 自动触发知识库检索并注入 AI 上下文
- [ ] 增量更新：仅重新索引内容变更的文件
- [ ] 索引数据存储在 `tests/.qoder/kb/` 目录，不提交 Git
- [ ] 知识库为空时（未执行 `qoder kb index`），AI 生成仍可正常运行（降级处理）
- [ ] `qoder kb query <text>` 能返回相关文档片段（调试命令）

### V1.5 满足

- [ ] 平台 Web UI 提供知识库浏览页面
- [ ] 平台提供语义搜索接口（`GET /api/kb/search`）
- [ ] 管理员可通过平台触发重新索引

### V2.0 满足

- [ ] 知识条目评分：用户标记"有用/无用"，影响检索权重
- [ ] 支持云端共享知识库（多人协作时共享索引）

---

## 10. 附录：知识库效果示例

### 场景：生成登录相关测试用例

**用户命令**：
```bash
qoder test generate --requirement "用户使用邮件和密码登录系统"
```

**知识库检索结果**（自动检索，不显示给用户）：

```
检索到 5 个相关知识块：

1. [0.95] docs/requirements/auth.md > 登录规则
   - 密码至少 8 位，含大写+数字+特殊字符
   - 连续 5 次失败锁定 30 分钟
   - 支持"记住我"功能（7天有效期）

2. [0.89] docs/api/auth.md > POST /api/auth/login
   请求体：{"email": string, "password": string, "remember_me": boolean}
   成功响应：{"access_token": string, "expires_in": 3600}
   错误响应：{"error": "invalid_credentials", "remaining_attempts": number}

3. [0.84] tests/cases/auth/TC-001_valid_login.md
   已有登录成功用例（避免重复生成）

4. [0.82] docs/ui/login-page.md > 页面元素
   - 邮箱输入框：role="textbox", name="邮箱"
   - 密码输入框：role="textbox", name="密码"（type=password）
   - 登录按钮：role="button", name="登录"
```

**AI 生成结果**（基于知识库上下文，比无知识库更准确）：

生成的测试用例包含：
- TC-001：有效邮件+密码登录成功（跳过，已存在）
- TC-002：无效密码登录失败（含"剩余次数"验证）
- TC-003：连续5次失败锁定（知识库提供了"5次"这个规则）
- TC-004：记住我功能（7天有效期验证）
- TC-005：邮箱格式不合法（前端验证）
