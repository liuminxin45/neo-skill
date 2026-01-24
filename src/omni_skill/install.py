"""
Install module: 依赖闭包解析、物化拷贝、manifest 生成

遵循架构规则：
- Source Space vs Install Space 严格分离
- 最小闭包原则
- 禁止 source path 泄漏
"""
from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class FileMapping:
    """文件映射：Source -> Install"""
    source: Path
    target: Path
    hash: str = ""
    
    def to_dict(self) -> dict:
        return {
            "source": str(self.source),
            "target": str(self.target),
            "hash": self.hash
        }


@dataclass
class InstallManifest:
    """安装清单"""
    version: str = "1.0"
    skill_id: str = ""
    install_root: str = ""
    installed_at: str = ""
    files: List[FileMapping] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "skill_id": self.skill_id,
            "install_root": self.install_root,
            "installed_at": self.installed_at,
            "files": [f.to_dict() for f in self.files],
            "dependencies": self.dependencies
        }
    
    def save(self, path: Path) -> None:
        """保存 manifest 到文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class DependencyClosureResolver:
    """依赖闭包解析器"""
    
    def __init__(self, source_root: Path):
        self.source_root = source_root
        self.visited: Set[Path] = set()
        self.closure: Set[Path] = set()
    
    def resolve(self, skill_dir: Path) -> Set[Path]:
        """
        解析 skill 的依赖闭包
        
        Args:
            skill_dir: skill 源目录（Source Space）
        
        Returns:
            依赖闭包文件集合
        """
        self.visited.clear()
        self.closure.clear()
        
        # 1. 添加 skill 主要文件
        self._add_skill_files(skill_dir)
        
        # 2. 解析 skillspec.json 中的引用
        skillspec = skill_dir / "skillspec.json"
        if skillspec.exists():
            self._resolve_skillspec(skillspec)
        
        # 3. 添加必需不变量
        self._add_universal_invariants()
        
        return self.closure
    
    def _add_skill_files(self, skill_dir: Path) -> None:
        """添加 skill 的主要文件"""
        # skillspec.json
        skillspec = skill_dir / "skillspec.json"
        if skillspec.exists():
            self.closure.add(skillspec)
        
        # references/
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in refs_dir.rglob("*"):
                if ref_file.is_file():
                    self.closure.add(ref_file)
        
        # scripts/
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.rglob("*"):
                if script_file.is_file():
                    self.closure.add(script_file)
        
        # assets/
        assets_dir = skill_dir / "assets"
        if assets_dir.exists():
            for asset_file in assets_dir.rglob("*"):
                if asset_file.is_file():
                    self.closure.add(asset_file)
    
    def _resolve_skillspec(self, skillspec: Path) -> None:
        """解析 skillspec.json 中的引用"""
        if skillspec in self.visited:
            return
        self.visited.add(skillspec)
        
        try:
            with open(skillspec, 'r', encoding='utf-8') as f:
                spec = json.load(f)
            
            # 解析 references
            for ref in spec.get("references", []):
                ref_path = skillspec.parent / ref
                if ref_path.exists():
                    self.closure.add(ref_path)
            
            # 解析 scripts
            for script in spec.get("scripts", []):
                script_path = skillspec.parent / script
                if script_path.exists():
                    self.closure.add(script_path)
            
            # 解析 assets
            for asset in spec.get("assets", []):
                asset_path = skillspec.parent / asset
                if asset_path.exists():
                    self.closure.add(asset_path)
            
            # 解析 libraries（如果有）
            libraries = spec.get("libraries", [])
            if libraries:
                # 生成 requirements.txt
                self._generate_requirements(skillspec.parent, libraries)
        
        except Exception as e:
            print(f"Warning: Failed to parse {skillspec}: {e}")
    
    def _generate_requirements(self, skill_dir: Path, libraries: List) -> None:
        """生成 requirements.txt"""
        req_file = skill_dir / "requirements.txt"
        
        lines = []
        for lib in libraries:
            if isinstance(lib, dict):
                name = lib.get('name', '')
                version = lib.get('version', '')
                if version:
                    lines.append(f"{name}{version}")
                else:
                    lines.append(name)
            else:
                lines.append(str(lib))
        
        if lines:
            with open(req_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
            self.closure.add(req_file)
    
    def _add_universal_invariants(self) -> None:
        """添加必需不变量"""
        shared_dir = self.source_root / ".shared" / "skill-creator" / "data_packs"
        
        # universal/
        universal_dir = shared_dir / "universal"
        if universal_dir.exists():
            # schema
            schema = universal_dir / "schema.skill.json"
            if schema.exists():
                self.closure.add(schema)
            
            # output_packs/
            output_packs_dir = universal_dir / "output_packs"
            if output_packs_dir.exists():
                for pack_file in output_packs_dir.rglob("*.json"):
                    self.closure.add(pack_file)
            
            # minimal_checklists/
            checklists_dir = universal_dir / "minimal_checklists"
            if checklists_dir.exists():
                for checklist_file in checklists_dir.rglob("*.json"):
                    self.closure.add(checklist_file)


class SkillInstaller:
    """Skill 安装器：物化拷贝到 Install Space"""
    
    def __init__(self, source_root: Path, install_root: Path):
        self.source_root = source_root
        self.install_root = install_root
        self.resolver = DependencyClosureResolver(source_root)
    
    def install(self, skill_id: str, target: str = "windsurf") -> InstallManifest:
        """
        安装 skill 到 Install Space
        
        Args:
            skill_id: skill ID
            target: 目标 AI 助手 (windsurf/claude/cursor/github)
        
        Returns:
            InstallManifest
        """
        skill_dir = self.source_root / "skills" / skill_id
        if not skill_dir.exists():
            raise FileNotFoundError(f"Skill not found: {skill_dir}")
        
        # 1. 解析依赖闭包
        closure = self.resolver.resolve(skill_dir)
        print(f"Resolved {len(closure)} files in dependency closure")
        
        # 2. 确定 install 目标目录
        install_target_root = self._get_install_target_root(target, skill_id)
        
        # 3. 物化拷贝
        manifest = InstallManifest(
            skill_id=skill_id,
            install_root=str(install_target_root.relative_to(self.install_root)),
            installed_at=datetime.utcnow().isoformat() + "Z"
        )
        
        for source_file in closure:
            target_file = self._map_to_install_space(source_file, skill_id, target)
            self._copy_file(source_file, target_file)
            
            # 计算哈希
            file_hash = self._compute_hash(target_file)
            
            mapping = FileMapping(
                source=source_file.relative_to(self.source_root),
                target=target_file.relative_to(self.install_root),
                hash=file_hash
            )
            manifest.files.append(mapping)
        
        # 4. 收集依赖信息
        manifest.dependencies = self._collect_dependencies(skill_dir)
        
        # 5. 保存 manifest
        manifest_path = install_target_root / ".install_manifest.json"
        manifest.save(manifest_path)
        
        print(f"Installed {skill_id} to {install_target_root}")
        print(f"Manifest saved to {manifest_path}")
        
        return manifest
    
    def _get_install_target_root(self, target: str, skill_id: str) -> Path:
        """获取 install 目标根目录"""
        if target == "windsurf":
            return self.install_root / ".windsurf" / "workflows" / "data" / skill_id
        elif target == "claude":
            return self.install_root / ".claude" / "skills" / skill_id / "resources"
        elif target == "cursor":
            return self.install_root / ".cursor" / "commands" / "data" / skill_id
        elif target == "github":
            return self.install_root / ".github" / "skills" / skill_id
        else:
            raise ValueError(f"Unknown target: {target}")
    
    def _map_to_install_space(self, source_file: Path, skill_id: str, target: str) -> Path:
        """映射 Source Space 路径到 Install Space 路径"""
        install_target_root = self._get_install_target_root(target, skill_id)
        
        # 计算相对路径
        try:
            # 尝试相对于 skills/{skill_id}
            rel_path = source_file.relative_to(self.source_root / "skills" / skill_id)
            return install_target_root / rel_path
        except ValueError:
            pass
        
        try:
            # 尝试相对于 .shared/skill-creator/data_packs
            rel_path = source_file.relative_to(self.source_root / ".shared" / "skill-creator" / "data_packs")
            return install_target_root / "data_packs" / rel_path
        except ValueError:
            pass
        
        # 兜底：使用文件名
        return install_target_root / source_file.name
    
    def _copy_file(self, source: Path, target: Path) -> None:
        """拷贝文件"""
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    
    def _compute_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return f"sha256:{sha256.hexdigest()}"
    
    def _collect_dependencies(self, skill_dir: Path) -> Dict[str, List[str]]:
        """收集依赖信息"""
        deps = {
            "libraries": [],
            "data_packs": []
        }
        
        # 读取 skillspec.json
        skillspec = skill_dir / "skillspec.json"
        if skillspec.exists():
            try:
                with open(skillspec, 'r', encoding='utf-8') as f:
                    spec = json.load(f)
                
                # 收集 libraries
                libraries = spec.get("libraries", [])
                for lib in libraries:
                    if isinstance(lib, dict):
                        name = lib.get('name', '')
                        if name:
                            deps["libraries"].append(name)
                    else:
                        deps["libraries"].append(str(lib))
            
            except Exception as e:
                print(f"Warning: Failed to parse {skillspec}: {e}")
        
        # 收集 data_packs（固定的必需不变量）
        deps["data_packs"] = [
            "universal/output_packs",
            "universal/minimal_checklists",
            "universal/schema"
        ]
        
        return deps
