"""主动搜索入口 - CLI 接口"""

import sys
from typing import Optional
from .interview import Interview
from .registry import Registry
from .matcher import Matcher
from .installer import Installer
from .doctor import Doctor


class SkillFinderCLI:
    """skill-finder CLI 主入口"""
    
    def __init__(self):
        self.registry = Registry()
        self.matcher = Matcher(self.registry)
        self.installer = Installer()
        self.doctor = Doctor(self.registry)
    
    def run(self):
        """主流程"""
        print("=== skill-finder ===")
        print("发现/匹配/安装第三方 skill 库\n")
        
        interview = Interview()
        query = interview.collect()
        
        print("\n=== 匹配结果 ===")
        result = self.matcher.match(query)
        
        if not result.matches:
            print(f"✗ 未找到匹配的第三方能力\n")
            print(f"拒绝原因: {result.rejection_reason}")
            print(f"建议: 尝试使用 skill-creator 创建自研 skill")
            return
        
        print(f"找到 {len(result.matches)} 个匹配的能力：\n")
        
        for i, match in enumerate(result.matches, 1):
            print(f"【{i}】{match.unit.name} ({match.package.name})")
            print(f"- 描述: {match.unit.description}")
            print(f"- 匹配原因: {'; '.join(match.reasons)}")
            print(f"- 置信度: {match.score:.2f}")
            print(f"- README: {match.package.docs.readme}")
            
            if match.warnings:
                print(f"- ⚠ 警告: {'; '.join(match.warnings)}")
            print()
        
        choice = input("选择要安装的能力 [1]: ").strip() or "1"
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(result.matches):
                print("无效选择")
                return
        except ValueError:
            print("无效选择")
            return
        
        selected = result.matches[idx]
        
        print("\n=== 安装方式 ===")
        print("[1] 自动安装（默认）")
        print("[2] 手动安装（仅输出命令）")
        
        mode_choice = input("选择 [1]: ").strip() or "1"
        mode = "manual" if mode_choice == "2" else "auto"
        
        record = self.installer.install(selected, mode=mode)
        
        if record.result == "success" or record.result == "skipped":
            print("\n=== 使用方式 ===")
            for ep in selected.unit.entrypoints:
                print(f"命令: {ep.command}")
                if ep.args:
                    print(f"参数: {ep.args}")
                if ep.cwd:
                    print(f"工作目录: {ep.cwd}")
                if ep.examples:
                    print("示例:")
                    for example in ep.examples:
                        print(f"  {example}")
                print()
            
            print(f"详细文档: {selected.package.docs.readme}")
            
            if selected.unit.usage_notes:
                print(f"\n使用说明:\n{selected.unit.usage_notes}")


def main():
    """CLI 入口"""
    if len(sys.argv) > 1 and sys.argv[1] == "doctor":
        from .models import SearchQuery
        doctor = Doctor()
        query = SearchQuery(goal="测试", ide="windsurf")
        print(doctor.show_install_records())
    else:
        cli = SkillFinderCLI()
        cli.run()


if __name__ == "__main__":
    main()
