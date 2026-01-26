"""Registry 校验工具 - 检查 packages 和 units 的完整性与一致性"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Set

class RegistryLinter:
    def __init__(self, registry_root: Path):
        self.registry_root = registry_root
        self.packages_dir = registry_root / "packages"
        self.units_dir = registry_root / "units"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def lint(self) -> bool:
        """执行所有校验，返回是否通过"""
        print("=== Registry Linter ===\n")
        
        packages = self._load_packages()
        units = self._load_units()
        
        self._validate_package_fields(packages)
        self._validate_unit_fields(units)
        self._validate_references(packages, units)
        self._validate_formats(packages, units)
        
        self._print_results()
        return len(self.errors) == 0
    
    def _load_packages(self) -> Dict[str, dict]:
        """加载所有 packages"""
        packages = {}
        if not self.packages_dir.exists():
            self.errors.append(f"Packages 目录不存在: {self.packages_dir}")
            return packages
            
        for file in self.packages_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    packages[data.get("package_id", file.stem)] = data
            except Exception as e:
                self.errors.append(f"无法加载 package {file.name}: {e}")
        
        print(f"✓ 加载 {len(packages)} 个 packages")
        return packages
    
    def _load_units(self) -> Dict[str, dict]:
        """加载所有 units"""
        units = {}
        if not self.units_dir.exists():
            self.errors.append(f"Units 目录不存在: {self.units_dir}")
            return units
            
        for file in self.units_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    units[data.get("unit_id", file.stem)] = data
            except Exception as e:
                self.errors.append(f"无法加载 unit {file.name}: {e}")
        
        print(f"✓ 加载 {len(units)} 个 units\n")
        return units
    
    def _validate_package_fields(self, packages: Dict[str, dict]):
        """校验 package 字段完整性"""
        required_fields = ["package_id", "name", "description", "source", "docs", 
                          "supported_ides", "install", "units"]
        install_fields = ["method", "auto_install_cmd", "manual_install_cmd"]
        docs_fields = ["readme"]
        
        for pkg_id, pkg in packages.items():
            for field in required_fields:
                if field not in pkg:
                    self.errors.append(f"Package {pkg_id}: 缺少必填字段 '{field}'")
            
            if "install" in pkg:
                for field in install_fields:
                    if field not in pkg["install"]:
                        self.errors.append(f"Package {pkg_id}: install 缺少字段 '{field}'")
            
            if "docs" in pkg:
                for field in docs_fields:
                    if field not in pkg["docs"]:
                        self.errors.append(f"Package {pkg_id}: docs 缺少字段 '{field}'")
            
            if "trust_level" in pkg:
                if pkg["trust_level"] not in ["trusted", "experimental", "deprecated"]:
                    self.errors.append(f"Package {pkg_id}: trust_level 值非法 '{pkg['trust_level']}'")
    
    def _validate_unit_fields(self, units: Dict[str, dict]):
        """校验 unit 字段完整性"""
        required_fields = ["unit_id", "package_id", "name", "description", 
                          "capability_tags", "keywords", "ide_support", "entrypoints"]
        
        for unit_id, unit in units.items():
            for field in required_fields:
                if field not in unit:
                    self.errors.append(f"Unit {unit_id}: 缺少必填字段 '{field}'")
            
            if "entrypoints" in unit and isinstance(unit["entrypoints"], list):
                for i, ep in enumerate(unit["entrypoints"]):
                    if "command" not in ep or not ep["command"]:
                        self.errors.append(f"Unit {unit_id}: entrypoints[{i}].command 为空")
    
    def _validate_references(self, packages: Dict[str, dict], units: Dict[str, dict]):
        """校验引用一致性"""
        package_ids = set(packages.keys())
        unit_ids = set(units.keys())
        
        for pkg_id, pkg in packages.items():
            if "units" in pkg:
                for unit_id in pkg["units"]:
                    if unit_id not in unit_ids:
                        self.errors.append(f"Package {pkg_id}: 引用的 unit '{unit_id}' 不存在")
        
        for unit_id, unit in units.items():
            if "package_id" in unit:
                if unit["package_id"] not in package_ids:
                    self.errors.append(f"Unit {unit_id}: 引用的 package '{unit['package_id']}' 不存在")
    
    def _validate_formats(self, packages: Dict[str, dict], units: Dict[str, dict]):
        """校验格式规范"""
        for pkg_id, pkg in packages.items():
            if not self._is_valid_package_id(pkg_id):
                self.errors.append(f"Package ID 格式错误: {pkg_id} (应为 gh:owner/repo | pip:pkg | npm:pkg)")
            
            if "docs" in pkg and "readme" in pkg["docs"]:
                if not pkg["docs"]["readme"].startswith(("http://", "https://")):
                    self.errors.append(f"Package {pkg_id}: README 链接格式错误")
        
        for unit_id, unit in units.items():
            if "#" not in unit_id:
                self.errors.append(f"Unit ID 格式错误: {unit_id} (应为 <package_id>#<unit-name>)")
            else:
                pkg_prefix = unit_id.split("#")[0]
                if "package_id" in unit and unit["package_id"] != pkg_prefix:
                    self.warnings.append(f"Unit {unit_id}: unit_id 前缀与 package_id 不一致")
    
    def _is_valid_package_id(self, pkg_id: str) -> bool:
        """检查 package_id 格式"""
        if pkg_id.startswith("gh:"):
            parts = pkg_id[3:].split("/")
            return len(parts) == 2 and all(parts)
        elif pkg_id.startswith(("pip:", "npm:")):
            return len(pkg_id) > 4
        return False
    
    def _print_results(self):
        """打印校验结果"""
        print("\n=== 校验结果 ===\n")
        
        if self.errors:
            print(f"✗ 发现 {len(self.errors)} 个错误:\n")
            for err in self.errors:
                print(f"  - {err}")
        else:
            print("✓ 所有必填项校验通过")
        
        if self.warnings:
            print(f"\n⚠ {len(self.warnings)} 个警告:\n")
            for warn in self.warnings:
                print(f"  - {warn}")
        
        print()

def main():
    if len(sys.argv) > 1:
        registry_root = Path(sys.argv[1])
    else:
        registry_root = Path(__file__).parent.parent / "data" / "third_party"
    
    linter = RegistryLinter(registry_root)
    success = linter.lint()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
