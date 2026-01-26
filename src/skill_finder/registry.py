"""Registry 加载与索引查询"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from .models import SkillPackage, SkillUnit


class Registry:
    """Registry 管理器 - 加载 packages/units 和索引"""
    
    def __init__(self, registry_root: Optional[Path] = None):
        if registry_root is None:
            registry_root = Path(__file__).parent.parent.parent / "data" / "third_party"
        
        self.registry_root = Path(registry_root)
        self.packages_dir = self.registry_root / "packages"
        self.units_dir = self.registry_root / "units"
        self.indexes_dir = self.registry_root / "indexes"
        
        self._packages_cache: Dict[str, SkillPackage] = {}
        self._units_cache: Dict[str, SkillUnit] = {}
        self.indexes: Dict[str, dict] = {}
        
        self._load_indexes()
    
    def _load_indexes(self):
        """加载所有索引文件"""
        if not self.indexes_dir.exists():
            raise FileNotFoundError(f"索引目录不存在: {self.indexes_dir}")
        
        index_files = {
            "by_tag": "units.by_tag.json",
            "by_keyword": "units.by_keyword.json",
            "by_ide": "units.by_ide.json",
            "packages_all": "packages.all.json",
            "units_all": "units.all.json",
        }
        
        for key, filename in index_files.items():
            index_path = self.indexes_dir / filename
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    self.indexes[key] = json.load(f)
            else:
                self.indexes[key] = {} if key != "packages_all" and key != "units_all" else []
    
    def get_package(self, package_id: str) -> Optional[SkillPackage]:
        """获取 package（带缓存）"""
        if package_id in self._packages_cache:
            return self._packages_cache[package_id]
        
        sanitized_id = package_id.replace(":", "_").replace("/", "_")
        package_path = self.packages_dir / f"{sanitized_id}.json"
        
        if not package_path.exists():
            return None
        
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                package = SkillPackage(**data)
                self._packages_cache[package_id] = package
                return package
        except Exception as e:
            print(f"加载 package {package_id} 失败: {e}")
            return None
    
    def get_unit(self, unit_id: str) -> Optional[SkillUnit]:
        """获取 unit（带缓存）"""
        if unit_id in self._units_cache:
            return self._units_cache[unit_id]
        
        sanitized_id = unit_id.replace(":", "_").replace("/", "_")
        unit_path = self.units_dir / f"{sanitized_id}.json"
        
        if not unit_path.exists():
            return None
        
        try:
            with open(unit_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                unit = SkillUnit(**data)
                self._units_cache[unit_id] = unit
                return unit
        except Exception as e:
            print(f"加载 unit {unit_id} 失败: {e}")
            return None
    
    def search_by_tag(self, tag: str) -> List[str]:
        """通过 tag 搜索 unit_id 列表"""
        return self.indexes.get("by_tag", {}).get(tag.lower(), [])
    
    def search_by_keyword(self, keyword: str) -> List[str]:
        """通过 keyword 搜索 unit_id 列表"""
        return self.indexes.get("by_keyword", {}).get(keyword.lower(), [])
    
    def search_by_ide(self, ide: str) -> List[str]:
        """通过 IDE 搜索 unit_id 列表"""
        return self.indexes.get("by_ide", {}).get(ide.lower(), [])
    
    def get_all_packages(self) -> List[str]:
        """获取所有 package_id"""
        return self.indexes.get("packages_all", [])
    
    def get_all_units(self) -> List[str]:
        """获取所有 unit_id"""
        return self.indexes.get("units_all", [])
