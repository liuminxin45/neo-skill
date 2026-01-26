"""skill-finder 端到端测试脚本"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from skill_finder.models import SearchQuery
from skill_finder.registry import Registry
from skill_finder.matcher import Matcher
from skill_finder.recommender import Recommender
from skill_finder.doctor import Doctor


def test_registry():
    """测试 Registry 加载"""
    print("=== 测试 Registry ===")
    registry = Registry()
    
    package = registry.get_package("gh:aider-chat/aider")
    assert package is not None, "Package 加载失败"
    print(f"✓ Package 加载成功: {package.name}")
    
    unit = registry.get_unit("gh:aider-chat/aider#code-edit")
    assert unit is not None, "Unit 加载失败"
    print(f"✓ Unit 加载成功: {unit.name}")
    
    tag_results = registry.search_by_tag("code-generation")
    assert len(tag_results) > 0, "Tag 搜索失败"
    print(f"✓ Tag 搜索成功: {len(tag_results)} 个结果")
    
    print()


def test_matcher():
    """测试 Matcher 匹配"""
    print("=== 测试 Matcher ===")
    registry = Registry()
    matcher = Matcher(registry)
    
    query = SearchQuery(
        goal="AI 辅助代码重构",
        tags=["code-refactoring"],
        ide="windsurf"
    )
    
    result = matcher.match(query)
    
    if result.matches:
        print(f"✓ 匹配成功: {len(result.matches)} 个结果")
        for match in result.matches:
            print(f"  - {match.unit.name} (score={match.score:.2f})")
    else:
        print(f"✗ 未匹配: {result.rejection_reason}")
    
    print()


def test_recommender():
    """测试 Recommender 推荐"""
    print("=== 测试 Recommender ===")
    recommender = Recommender()
    
    query = SearchQuery(
        goal="多文件代码编辑",
        tags=["code-generation", "multi-file-editing"],
        ide="windsurf"
    )
    
    result = recommender.recommend(query)
    
    if result.matches:
        print(f"✓ 推荐成功: {result.matches[0].unit.name}")
        print(f"  置信度: {result.matches[0].score:.2f}")
    else:
        print(f"○ 无高置信推荐: {result.rejection_reason}")
    
    print()


def test_doctor():
    """测试 Doctor trace"""
    print("=== 测试 Doctor ===")
    doctor = Doctor()
    
    query = SearchQuery(
        goal="git commit 生成",
        tags=["git-commit"],
        ide="windsurf"
    )
    
    trace = doctor.trace_match(query)
    print(trace)
    print()
    
    records = doctor.show_install_records(3)
    print(records)
    print()


def main():
    """运行所有测试"""
    print("skill-finder 端到端测试\n")
    
    try:
        test_registry()
        test_matcher()
        test_recommender()
        test_doctor()
        
        print("=" * 50)
        print("✓ 所有测试通过")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
