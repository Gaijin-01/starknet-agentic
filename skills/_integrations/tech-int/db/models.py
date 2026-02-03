#!/usr/bin/env python3
"""
Tech-Int Data Models
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json


@dataclass
class Technology:
    """Detected technology"""
    name: str
    type: str  # cms, server, framework, js, iot, language
    confidence: float = 0.8
    version: Optional[str] = None
    cves: List[str] = field(default_factory=list)
    cvss: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "confidence": self.confidence,
            "version": self.version,
            "cves": self.cves,
            "cvss": self.cvss
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Technology":
        return cls(
            name=data["name"],
            type=data["type"],
            confidence=data.get("confidence", 0.8),
            version=data.get("version"),
            cves=data.get("cves", []),
            cvss=data.get("cvss")
        )


@dataclass
class Target:
    """Scan target result"""
    domain: str
    url: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    technologies: List[Technology] = field(default_factory=list)
    cves: List[str] = field(default_factory=list)
    iot_device: Optional[str] = None
    error: Optional[str] = None
    
    def get_tech_stack_str(self) -> str:
        return ", ".join([t.name for t in self.technologies])
    
    def get_max_cvss(self) -> Optional[float]:
        if not self.technologies:
            return None
        cvss_values = [t.cvss for t in self.technologies if t.cvss]
        return max(cvss_values) if cvss_values else None
    
    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "url": self.url,
            "status_code": self.status_code,
            "headers": self.headers,
            "technologies": [t.to_dict() for t in self.technologies],
            "cves": self.cves,
            "iot_device": self.iot_device,
            "error": self.error
        }
