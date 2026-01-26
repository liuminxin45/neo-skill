"""诊断与 trace"""

from typing import Optional
from .models import SearchQuery, SearchResult
from .registry import Registry
from .matcher import Matcher
from .install_record import InstallRecordManager


class Doctor:
    """诊断工具 - 提供匹配 trace 和安装记录分析"""
    
    def __init__(self, registry: Optional[Registry] = None, 
                 record_manager: Optional[InstallRecordManager] = None):
        if registry is None:
            registry = Registry()
        if record_manager is None:
            record_manager = InstallRecordManager()
        
        self.registry = registry
        self.matcher = Matcher(registry)
        self.record_manager = record_manager
    
    def trace_match(self, query: SearchQuery) -> str:
        """输出匹配 trace"""
        output = ["=== skill-finder Doctor Trace ===\n"]
        
        output.append("【匹配 Trace】")
        output.append(f"- Query: goal=\"{query.goal}\", tags={query.tags}, ide=\"{query.ide}\"")
        
        candidates = self.matcher._coarse_filter(query)
        output.append(f"- 粗筛命中: {len(candidates)} 个候选")
        
        if candidates:
            for tag in (query.tags or []):
                units = self.registry.search_by_tag(tag)
                if units:
                    output.append(f"  - Tag '{tag}': {len(units)} 个 unit")
        
        result = self.matcher.match(query)
        
        if result.matches:
            output.append("- 精排结果:")
            for i, match in enumerate(result.matches[:3], 1):
                output.append(f"  {i}. {match.unit.unit_id} (score={match.score:.2f})")
                output.append(f"     - {', '.join(match.reasons)}")
            output.append(f"- 最终返回: Top {len(result.matches)}")
        else:
            output.append(f"- 拒绝原因: {result.rejection_reason}")
            output.append(f"- 拒绝分类: {result.rejection_category}")
        
        return "\n".join(output)
    
    def show_install_records(self, n: int = 5) -> str:
        """显示最近的安装记录"""
        output = ["\n【安装记录（最近 {} 条）】".format(n)]
        
        records = self.record_manager.get_recent(n)
        
        if not records:
            output.append("- 暂无安装记录")
            return "\n".join(output)
        
        for i, record in enumerate(records, 1):
            status_icon = "✓" if record.result == "success" else "✗" if record.result == "failed" else "○"
            output.append(f"{i}. {record.timestamp[:10]} {record.timestamp[11:19]} | {record.unit_id} | {record.install_mode} | {status_icon} {record.result}")
            
            if record.result == "failed" and record.error_summary:
                error_preview = record.error_summary[:100].replace("\n", " ")
                output.append(f"   错误: {error_preview}...")
        
        return "\n".join(output)
    
    def suggest_fix(self, package_id: str) -> str:
        """针对安装失败提供修复建议"""
        output = ["\n【冲突/异常建议】"]
        
        records = self.record_manager.filter_by_package(package_id)
        failed = [r for r in records if r.result == "failed"]
        
        if not failed:
            output.append(f"- Package {package_id} 无失败记录")
            return "\n".join(output)
        
        last_failed = failed[-1]
        
        package = self.registry.get_package(package_id)
        if package and package.install.uninstall_cmd:
            output.append(f"- 若安装失败，尝试重装:")
            output.append(f"  {package.install.uninstall_cmd} && {package.install.auto_install_cmd}")
        else:
            output.append(f"- 建议手动检查错误信息并重试安装")
        
        if last_failed.error_summary:
            output.append(f"\n最近错误摘要:")
            output.append(f"  {last_failed.error_summary[:200]}")
        
        return "\n".join(output)
    
    def full_report(self, query: SearchQuery) -> str:
        """完整诊断报告"""
        output = []
        output.append(self.trace_match(query))
        output.append(self.show_install_records())
        return "\n".join(output)
