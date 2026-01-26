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
        self.indexes_available: bool = False
        
        self._load_indexes()
    
    def _load_indexes(self):
        """加载所有索引文件"""
        if not self.indexes_dir.exists():
            self.indexes_available = False
            self.indexes = {
                "by_tag": {},
                "by_keyword": {},
                "by_ide": {},
                "packages_all": [],
                "units_all": [],
            }
            return
        
        self.indexes_available = True
        
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

    def _load_all_units_from_disk(self) -> Dict[str, SkillUnit]:
        """从磁盘加载所有 units（用于索引缺失时的降级查询）"""
        if self._units_cache:
            return self._units_cache

        if not self.units_dir.exists():
            return self._units_cache

        for unit_path in self.units_dir.glob("*.json"):
            try:
                with open(unit_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    unit = SkillUnit(**data)
                    self._units_cache[unit.unit_id] = unit
            except Exception as e:
                print(f"加载 unit 文件 {unit_path} 失败: {e}")

        return self._units_cache

    def _load_all_packages_from_disk(self) -> Dict[str, SkillPackage]:
        """从磁盘加载所有 packages（用于索引缺失时的降级查询）"""
        if self._packages_cache:
            return self._packages_cache

        if not self.packages_dir.exists():
            return self._packages_cache

        for package_path in self.packages_dir.glob("*.json"):
            try:
                with open(package_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    package = SkillPackage(**data)
                    self._packages_cache[package.package_id] = package
            except Exception as e:
                print(f"加载 package 文件 {package_path} 失败: {e}")

        return self._packages_cache
    
    def get_package(self, package_id: str) -> Optional[SkillPackage]:
        """获取 package（带缓存）"""
        if package_id in self._packages_cache:
            return self._packages_cache[package_id]
        
        sanitized_id = package_id.replace(":", "_").replace("/", "_")
        package_path = self.packages_dir / f"{sanitized_id}.json"
        
        if not package_path.exists():
            self._load_all_packages_from_disk()
            return self._packages_cache.get(package_id)
        
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
            self._load_all_units_from_disk()
            return self._units_cache.get(unit_id)
        
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
        by_tag = self.indexes.get("by_tag", {})
        if by_tag:
            return by_tag.get(tag.lower(), [])

        tag_lower = tag.lower()
        unit_ids: List[str] = []
        for unit in self._load_all_units_from_disk().values():
            if tag_lower in [t.lower() for t in unit.capability_tags]:
                unit_ids.append(unit.unit_id)
        return unit_ids
    
    def search_by_keyword(self, keyword: str) -> List[str]:
        """通过 keyword 搜索 unit_id 列表"""
        by_keyword = self.indexes.get("by_keyword", {})
        if by_keyword:
            return by_keyword.get(keyword.lower(), [])

        kw_lower = keyword.lower()
        unit_ids: List[str] = []
        for unit in self._load_all_units_from_disk().values():
            if kw_lower in [k.lower() for k in unit.keywords]:
                unit_ids.append(unit.unit_id)
        return unit_ids
    
    def search_by_ide(self, ide: str) -> List[str]:
        """通过 IDE 搜索 unit_id 列表"""
        by_ide = self.indexes.get("by_ide", {})
        if by_ide:
            return by_ide.get(ide.lower(), [])

        ide_lower = ide.lower()
        unit_ids: List[str] = []
        for unit in self._load_all_units_from_disk().values():
            if ide_lower in [i.lower() for i in unit.ide_support]:
                unit_ids.append(unit.unit_id)
        return unit_ids
    
    def get_all_packages(self) -> List[str]:
        """获取所有 package_id"""
        packages_all = self.indexes.get("packages_all", [])
        if packages_all:
            return packages_all

        return list(self._load_all_packages_from_disk().keys())
    
    def get_all_units(self) -> List[str]:
        """获取所有 unit_id"""
        units_all = self.indexes.get("units_all", [])
        if units_all:
            return units_all

        return list(self._load_all_units_from_disk().keys())
