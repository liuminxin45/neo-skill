"""安装记录管理"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from .models import InstallRecord


class InstallRecordManager:
    """安装记录管理器"""
    
    def __init__(self, record_path: Optional[Path] = None):
        if record_path is None:
            record_path = Path.home() / ".omni-skill" / "install_records.json"
        
        self.record_path = Path(record_path)
        self.record_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.record_path.exists():
            self._save_records([])
    
    def add(self, record: InstallRecord):
        """添加安装记录"""
        records = self.load_all()
        records.append(record.dict())
        self._save_records(records)
    
    def load_all(self) -> List[dict]:
        """加载所有记录"""
        try:
            with open(self.record_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def get_recent(self, n: int = 10) -> List[InstallRecord]:
        """获取最近 N 条记录"""
        records = self.load_all()
        recent = records[-n:] if len(records) > n else records
        return [InstallRecord(**r) for r in reversed(recent)]
    
    def filter_by_package(self, package_id: str) -> List[InstallRecord]:
        """按 package_id 过滤"""
        records = self.load_all()
        filtered = [r for r in records if r.get("package_id") == package_id]
        return [InstallRecord(**r) for r in filtered]
    
    def filter_by_unit(self, unit_id: str) -> List[InstallRecord]:
        """按 unit_id 过滤"""
        records = self.load_all()
        filtered = [r for r in records if r.get("unit_id") == unit_id]
        return [InstallRecord(**r) for r in filtered]
    
    def _save_records(self, records: List[dict]):
        """保存记录"""
        with open(self.record_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
