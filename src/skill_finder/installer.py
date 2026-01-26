"""安装执行器"""

import subprocess
from datetime import datetime
from typing import Literal, Optional
from .models import MatchResult, InstallRecord
from .install_record import InstallRecordManager


class Installer:
    """安装执行器 - 支持自动/手动两种模式"""
    
    def __init__(self, record_manager: Optional[InstallRecordManager] = None):
        if record_manager is None:
            record_manager = InstallRecordManager()
        self.record_manager = record_manager
    
    def install(self, match: MatchResult, mode: Literal["auto", "manual"] = "auto") -> InstallRecord:
        """执行安装"""
        package = match.package
        unit = match.unit
        
        if mode == "manual":
            return self._manual_install(package, unit)
        else:
            return self._auto_install(package, unit)
    
    def _manual_install(self, package, unit) -> InstallRecord:
        """手动安装模式 - 仅输出命令"""
        print(f"\n=== 手动安装 {package.name} ===")
        print(package.install.manual_install_cmd)
        
        if package.install.notes:
            print(f"\n注意事项：\n{package.install.notes}")
        
        print("\n已记录安装指令。请手动执行上述命令。")
        
        record = InstallRecord(
            timestamp=datetime.now().isoformat(),
            unit_id=unit.unit_id,
            package_id=package.package_id,
            install_mode="manual",
            executed=False,
            method=package.install.method,
            commands=package.install.manual_install_cmd,
            result="skipped",
            error_summary=None,
            docs_links=package.docs
        )
        
        self.record_manager.add(record)
        return record
    
    def _auto_install(self, package, unit) -> InstallRecord:
        """自动安装模式 - 执行命令"""
        print(f"\n=== 自动安装 {package.name} ===")
        
        if package.install.notes:
            print(f"注意事项: {package.install.notes}")
        
        print(f"\n执行命令：\n{package.install.auto_install_cmd}\n")
        
        try:
            result = subprocess.run(
                package.install.auto_install_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✓ 安装成功")
                record = InstallRecord(
                    timestamp=datetime.now().isoformat(),
                    unit_id=unit.unit_id,
                    package_id=package.package_id,
                    install_mode="auto",
                    executed=True,
                    method=package.install.method,
                    commands=package.install.auto_install_cmd,
                    result="success",
                    error_summary=None,
                    docs_links=package.docs
                )
            else:
                print(f"✗ 安装失败\n{result.stderr}")
                record = InstallRecord(
                    timestamp=datetime.now().isoformat(),
                    unit_id=unit.unit_id,
                    package_id=package.package_id,
                    install_mode="auto",
                    executed=True,
                    method=package.install.method,
                    commands=package.install.auto_install_cmd,
                    result="failed",
                    error_summary=result.stderr[:500] if result.stderr else None,
                    docs_links=package.docs
                )
        
        except Exception as e:
            print(f"✗ 安装异常：{e}")
            record = InstallRecord(
                timestamp=datetime.now().isoformat(),
                unit_id=unit.unit_id,
                package_id=package.package_id,
                install_mode="auto",
                executed=True,
                method=package.install.method,
                commands=package.install.auto_install_cmd,
                result="failed",
                error_summary=str(e)[:500],
                docs_links=package.docs
            )
        
        self.record_manager.add(record)
        return record
