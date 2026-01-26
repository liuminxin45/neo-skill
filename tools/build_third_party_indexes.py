"""Registry 索引构建工具 - 从 packages 和 units 生成倒排索引"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

class IndexBuilder:
    def __init__(self, registry_root: Path):
        self.registry_root = registry_root
        self.packages_dir = registry_root / "packages"
        self.units_dir = registry_root / "units"
        self.indexes_dir = registry_root / "indexes"
        
    def build(self):
        """构建所有索引"""
        print("=== Registry Index Builder ===\n")
        
        self.indexes_dir.mkdir(parents=True, exist_ok=True)
        
        packages = self._load_packages()
        units = self._load_units()
        
        self._build_units_by_tag(units)
        self._build_units_by_keyword(units)
        self._build_units_by_ide(units)
        self._build_packages_all(packages)
        self._build_units_all(units)
        
        print("\n✓ 索引构建完成")
    
    def _load_packages(self) -> Dict[str, dict]:
        """加载所有 packages"""
        packages = {}
        for file in self.packages_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                packages[data["package_id"]] = data
        print(f"✓ 加载 {len(packages)} 个 packages")
        return packages
    
    def _load_units(self) -> Dict[str, dict]:
        """加载所有 units"""
        units = {}
        for file in self.units_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                units[data["unit_id"]] = data
        print(f"✓ 加载 {len(units)} 个 units")
        return units
    
    def _build_units_by_tag(self, units: Dict[str, dict]):
        """构建 tag 倒排索引"""
        index = defaultdict(list)
        
        for unit_id, unit in units.items():
            for tag in unit.get("capability_tags", []):
                tag_lower = tag.lower()
                if unit_id not in index[tag_lower]:
                    index[tag_lower].append(unit_id)
        
        output = dict(sorted(index.items()))
        self._save_index("units.by_tag.json", output)
        print(f"✓ 构建 units.by_tag.json ({len(output)} 个标签)")
    
    def _build_units_by_keyword(self, units: Dict[str, dict]):
        """构建 keyword 倒排索引"""
        index = defaultdict(list)
        
        for unit_id, unit in units.items():
            for keyword in unit.get("keywords", []):
                kw_lower = keyword.lower()
                if unit_id not in index[kw_lower]:
                    index[kw_lower].append(unit_id)
        
        output = dict(sorted(index.items()))
        self._save_index("units.by_keyword.json", output)
        print(f"✓ 构建 units.by_keyword.json ({len(output)} 个关键词)")
    
    def _build_units_by_ide(self, units: Dict[str, dict]):
        """构建 IDE 倒排索引"""
        index = defaultdict(list)
        
        for unit_id, unit in units.items():
            for ide in unit.get("ide_support", []):
                ide_lower = ide.lower()
                if unit_id not in index[ide_lower]:
                    index[ide_lower].append(unit_id)
        
        output = dict(sorted(index.items()))
        self._save_index("units.by_ide.json", output)
        print(f"✓ 构建 units.by_ide.json ({len(output)} 个 IDE)")
    
    def _build_packages_all(self, packages: Dict[str, dict]):
        """构建 packages 全量列表"""
        output = list(packages.keys())
        self._save_index("packages.all.json", output)
        print(f"✓ 构建 packages.all.json ({len(output)} 个 packages)")
    
    def _build_units_all(self, units: Dict[str, dict]):
        """构建 units 全量列表"""
        output = list(units.keys())
        self._save_index("units.all.json", output)
        print(f"✓ 构建 units.all.json ({len(output)} 个 units)")
    
    def _save_index(self, filename: str, data):
        """保存索引文件"""
        output_path = self.indexes_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) > 1:
        registry_root = Path(sys.argv[1])
    else:
        registry_root = Path(__file__).parent.parent / "data" / "third_party"
    
    builder = IndexBuilder(registry_root)
    builder.build()

if __name__ == "__main__":
    main()
