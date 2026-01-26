"""测试 UI/UX Pro Max Skill 的匹配"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from skill_finder.models import SearchQuery
from skill_finder.registry import Registry
from skill_finder.matcher import Matcher


def test_uiux_skill():
    """测试 UI/UX Pro Max Skill 匹配"""
    print("=== 测试 UI/UX Pro Max Skill ===\n")
    
    registry = Registry()
    matcher = Matcher(registry)
    
    # 测试 1: UI 设计需求
    print("【测试 1: UI 设计需求】")
    query1 = SearchQuery(
        goal="设计一个 SaaS 产品的落地页",
        tags=["ui-design", "web-design"],
        ide="windsurf"
    )
    
    result1 = matcher.match(query1)
    
    if result1.matches:
        print(f"✓ 匹配成功: {len(result1.matches)} 个结果")
        for match in result1.matches:
            print(f"  - {match.unit.name} (score={match.score:.2f})")
            print(f"    原因: {'; '.join(match.reasons)}")
    else:
        print(f"✗ 未匹配: {result1.rejection_reason}")
    
    print()
    
    # 测试 2: 设计系统生成
    print("【测试 2: 设计系统生成】")
    query2 = SearchQuery(
        goal="生成医疗应用的设计系统",
        tags=["design-system"],
        keywords=["design system", "style guide"],
        ide="cursor"
    )
    
    result2 = matcher.match(query2)
    
    if result2.matches:
        print(f"✓ 匹配成功: {len(result2.matches)} 个结果")
        for match in result2.matches:
            print(f"  - {match.unit.name} (score={match.score:.2f})")
            print(f"    原因: {'; '.join(match.reasons)}")
    else:
        print(f"✗ 未匹配: {result2.rejection_reason}")
    
    print()
    
    # 测试 3: 验证 package 加载
    print("【测试 3: Package 加载】")
    package = registry.get_package("gh:nextlevelbuilder/ui-ux-pro-max-skill")
    if package:
        print(f"✓ Package 加载成功: {package.name}")
        print(f"  - 包含 {len(package.units)} 个 units")
        print(f"  - 支持 {len(package.supported_ides)} 个 IDE")
    else:
        print("✗ Package 加载失败")
    
    print()
    
    # 测试 4: 验证索引
    print("【测试 4: 索引查询】")
    ui_design_units = registry.search_by_tag("ui-design")
    print(f"✓ Tag 'ui-design': {len(ui_design_units)} 个 units")
    
    design_system_units = registry.search_by_tag("design-system")
    print(f"✓ Tag 'design-system': {len(design_system_units)} 个 units")
    
    windsurf_units = registry.search_by_ide("windsurf")
    print(f"✓ IDE 'windsurf': {len(windsurf_units)} 个 units")
    
    print("\n" + "=" * 50)
    print("✓ UI/UX Pro Max Skill 测试通过")
    print("=" * 50)


if __name__ == "__main__":
    test_uiux_skill()
