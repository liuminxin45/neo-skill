"""skill-finder 核心数据结构定义"""

from typing import Literal, Optional, List, Dict
from pydantic import BaseModel, Field


class InstallerSpec(BaseModel):
    """安装器规范"""
    method: Literal["git", "pip", "npm", "release_asset"]
    auto_install_cmd: str = Field(..., description="自动安装执行的命令（可多行）")
    manual_install_cmd: str = Field(..., description="手动安装给用户的命令（可多行）")
    uninstall_cmd: Optional[str] = Field(None, description="卸载命令（可选）")
    notes: Optional[str] = Field(None, description="安装注意事项")


class SourceSpec(BaseModel):
    """源信息"""
    type: Literal["git", "pip", "npm", "release_asset"]
    repo: Optional[str] = None
    url: Optional[str] = None
    package: Optional[str] = None
    ref: Optional[str] = None
    tag: Optional[str] = None
    commit: Optional[str] = None
    version: Optional[str] = None


class DocsSpec(BaseModel):
    """文档链接"""
    readme: str = Field(..., description="README 链接（必须）")
    homepage: Optional[str] = None
    issues: Optional[str] = None


class SkillPackage(BaseModel):
    """Package 定义（安装载体）"""
    package_id: str = Field(..., description="唯一标识：gh:owner/repo | pip:pkg | npm:pkg")
    name: str
    description: str
    source: SourceSpec
    docs: DocsSpec
    supported_ides: List[str] = Field(..., description="包级 IDE 支持")
    install: InstallerSpec
    units: List[str] = Field(..., description="包含的 unit_id 列表")
    trust_level: Optional[Literal["trusted", "experimental", "deprecated"]] = "trusted"
    notes: Optional[str] = None


class EntrypointSpec(BaseModel):
    """使用入口"""
    command: str = Field(..., description="原生命令")
    args: Optional[str] = Field(None, description="参数说明")
    cwd: Optional[str] = Field(None, description="工作目录要求")
    examples: Optional[List[str]] = Field(None, description="使用示例")


class SkillUnit(BaseModel):
    """Unit 定义（能力单元，匹配维度）"""
    unit_id: str = Field(..., description="唯一标识：gh:owner/repo#skill-a")
    package_id: str = Field(..., description="所属 package")
    name: str
    description: str
    capability_tags: List[str] = Field(..., description="能力标签")
    keywords: List[str] = Field(..., description="关键词")
    ide_support: List[str] = Field(..., description="IDE 支持列表")
    entrypoints: List[EntrypointSpec] = Field(..., description="使用入口")
    docs_override: Optional[DocsSpec] = None
    usage_notes: Optional[str] = Field(None, description="10-20 行微摘要")
    conflicts: Optional[str] = Field(None, description="已知冲突/注意事项")


class SearchQuery(BaseModel):
    """搜索查询"""
    goal: str
    input_type: Optional[str] = None
    output_type: Optional[str] = None
    env: Optional[str] = None
    ide: Optional[str] = None
    constraints: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None


class MatchResult(BaseModel):
    """匹配结果"""
    unit: SkillUnit
    package: SkillPackage
    score: float
    reasons: List[str] = Field(..., description="匹配原因")
    warnings: Optional[List[str]] = None


class SearchResult(BaseModel):
    """搜索结果"""
    query: SearchQuery
    matches: List[MatchResult]
    rejection_reason: Optional[str] = None
    rejection_category: Optional[Literal[
        "no_candidates_by_tag",
        "candidates_but_no_ide_support",
        "candidates_but_incompatible_env",
        "insufficient_info"
    ]] = None


class InstallRecord(BaseModel):
    """安装记录"""
    timestamp: str
    unit_id: str
    package_id: str
    install_mode: Literal["auto", "manual"]
    executed: bool
    method: str
    commands: str
    result: Literal["success", "failed", "skipped"]
    error_summary: Optional[str] = None
    docs_links: DocsSpec
