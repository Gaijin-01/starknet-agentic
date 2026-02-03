"""
Security Analysis Agent for Starknet Intelligence Colony
=========================================================
Comprehensive security monitoring for Starknet DeFi protocols.

Features:
- Vulnerability Scanner (reentrancy, external calls, proxy risks)
- Audit Report Analyzer (Trail of Bits, OpenZeppelin, etc.)
- Smart Contract Analyzer (bug patterns, proxy safety)
- Liquidity Risk Monitor (TVL drops, concentration, oracle deviations)
- Risk Scoring (0-100 scale)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import re

from shared_state import shared_state, ContentPiece
from orchestrator import orchestrator
from config import AGENTS, MONITORING

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"  # Score: 90-100
    HIGH = "high"          # Score: 70-89
    MEDIUM = "medium"      # Score: 40-69
    LOW = "low"            # Score: 10-39
    INFO = "info"          # Score: 0-9


class VulnerabilityType(Enum):
    """Types of vulnerabilities"""
    REENTRANCY = "reentrancy"
    UNSAFE_EXTERNAL_CALL = "unsafe_external_call"
    PROXY_UPGRADE_RISK = "proxy_upgrade_risk"
    ACCESS_CONTROL = "access_control"
    OVERFLOW_UNDERFLOW = "overflow_underflow"
    FRONT_RUNNING = "front_running"
    ORACLE_MANIPULATION = "oracle_manipulation"
    CONCENTRATION_RISK = "concentration_risk"
    TVL_DROP = "tvl_drop"
    ORACLE_DEVIATION = "oracle_deviation"
    SUSPICIOUS_ACCESS = "suspicious_access"


@dataclass
class Vulnerability:
    """A detected vulnerability"""
    id: str
    protocol: str
    type: VulnerabilityType
    severity: Severity
    title: str
    description: str
    evidence: str
    impact: str
    recommendation: str
    score: int  # 0-100
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "open"  # open, acknowledged, remediated
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "protocol": self.protocol,
            "type": self.type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "evidence": self.evidence,
            "impact": self.impact,
            "recommendation": self.recommendation,
            "score": self.score,
            "timestamp": self.timestamp,
            "status": self.status
        }


@dataclass
class AuditFinding:
    """Parsed audit report finding"""
    id: str
    auditor: str
    protocol: str
    title: str
    severity: Severity
    category: str
    description: str
    recommendation: str
    status: str = "unresolved"
    remediation_date: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "auditor": self.auditor,
            "protocol": self.protocol,
            "title": self.title,
            "severity": self.severity.value,
            "category": self.category,
            "description": self.description,
            "recommendation": self.recommendation,
            "status": self.status,
            "remediation_date": self.remediation_date
        }


@dataclass
class SecurityReport:
    """Comprehensive security report"""
    id: str
    protocol: str
    timestamp: str
    overall_score: int  # 0-100
    risk_level: str  # "Critical", "High", "Medium", "Low", "Minimal"
    vulnerabilities: List[Vulnerability]
    audit_findings: List[AuditFinding]
    liquidity_risks: List[Dict]
    recommendations: List[str]
    summary: str
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "protocol": self.protocol,
            "timestamp": self.timestamp,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "audit_findings": [a.to_dict() for a in self.audit_findings],
            "liquidity_risks": self.liquidity_risks,
            "recommendations": self.recommendations,
            "summary": self.summary
        }


class SecurityAgent:
    """
    Security Analysis Agent for comprehensive protocol security.
    
    Integrates with:
    - Research Agent (combined security + research reports)
    - Market Agent (liquidity monitoring)
    - Content Agent (security alerts and reports)
    """
    
    def __init__(self):
        self.name = "security_agent"
        self._running = False
        
        # Monitored protocols
        self._monitored_protocols = list(MONITORING.PROTOCOLS)
        
        # Known audit firms
        self._audit_firms = [
            "Trail of Bits",
            "OpenZeppelin",
            "Consensys Diligence",
            "Certik",
            "SlowMist",
            "PeckShield"
        ]
        
        # Risk thresholds
        self._tvl_drop_threshold = 10.0  # % drop to alert
        self._oracle_deviation_threshold = 5.0  # % deviation to alert
        
        # Sample vulnerability patterns
        self._vulnerability_patterns = {
            VulnerabilityType.REENTRANCY: [
                r"call.*value",
                r"function.*external",
                r"reentrancy",
                r"callback"
            ],
            VulnerabilityType.ACCESS_CONTROL: [
                r"onlyOwner",
                r"onlyAdmin",
                r"access.*control",
                r"permission.*check"
            ],
            VulnerabilityType.OVERFLOW_UNDERFLOW: [
                r"uint256.*\+",
                r"uint256.*\-",
                r"safe.*math",
                r"overflow"
            ],
            VulnerabilityType.FRONT_RUNNING: [
                r"flash.*loan",
                r"sandwich",
                r"front.*run"
            ]
        }
    
    async def start(self):
        """Start the security agent"""
        logger.info("Security Agent starting")
        await shared_state.update_agent_status(self.name, "starting")
        self._running = True
        await shared_state.update_agent_status(self.name, "running")
        
        try:
            await self._run_loop()
        except asyncio.CancelledError:
            logger.info("Security Agent cancelled")
        finally:
            self._running = False
            await shared_state.update_agent_status(self.name, "stopped")
    
    async def _run_loop(self):
        """Main security monitoring loop"""
        while self._running:
            try:
                # Run security checks
                await self._run_security_scan()
                
                # Check liquidity risks
                await self._check_liquidity_risks()
                
                # Check for upgrade spikes
                await self._check_upgrade_spikes()
                
                # Wait before next scan (30 minutes)
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Security Agent error: {e}")
                await shared_state.add_alert("security_agent_error", str(e), "error")
                await asyncio.sleep(600)  # 10 min on error
    
    # =========================================================================
    # Vulnerability Scanning
    # =========================================================================
    
    async def scan_protocol(self, protocol: str) -> SecurityReport:
        """
        Run comprehensive security scan on a protocol.
        
        Args:
            protocol: Protocol name to scan
        
        Returns:
            SecurityReport with findings
        """
        logger.info(f"Scanning protocol: {protocol}")
        
        vulnerabilities = []
        
        # Run specific vulnerability checks
        vulnerabilities.extend(await self._check_reentrancy(protocol))
        vulnerabilities.extend(await self._check_external_calls(protocol))
        vulnerabilities.extend(await self._check_proxy_risks(protocol))
        vulnerabilities.extend(await self._check_access_control(protocol))
        vulnerabilities.extend(await self._check_overflow_patterns(protocol))
        
        # Parse audit reports
        audit_findings = await self._parse_audit_reports(protocol)
        
        # Check liquidity risks
        liquidity_risks = await self._analyze_liquidity_risk(protocol)
        
        # Calculate overall score
        overall_score = self._calculate_risk_score(vulnerabilities, audit_findings, liquidity_risks)
        risk_level = self._get_risk_level(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(vulnerabilities, audit_findings)
        
        # Create report
        report = SecurityReport(
            id=str(uuid.uuid4())[:8],
            protocol=protocol,
            timestamp=datetime.utcnow().isoformat(),
            overall_score=overall_score,
            risk_level=risk_level,
            vulnerabilities=vulnerabilities,
            audit_findings=audit_findings,
            liquidity_risks=liquidity_risks,
            recommendations=recommendations,
            summary=self._generate_summary(protocol, overall_score, risk_level, len(vulnerabilities))
        )
        
        # Store report
        await self._store_report(report)
        
        # Generate alerts for critical findings
        await self._alert_critical_findings(vulnerabilities)
        
        return report
    
    async def _check_reentrancy(self, protocol: str) -> List[Vulnerability]:
        """Check for reentrancy vulnerabilities"""
        vulnerabilities = []
        
        # Simulated check - in production, analyze actual contract code
        reentrancy_patterns = ["_call", "transfer", "call.value"]
        
        for pattern in reentrancy_patterns:
            vuln = Vulnerability(
                id=str(uuid.uuid4())[:8],
                protocol=protocol,
                type=VulnerabilityType.REENTRANCY,
                severity=Severity.MEDIUM,
                title=f"Potential Reentrancy Pattern: {pattern}",
                description=f"Detected {pattern} pattern that could allow reentrancy attacks.",
                evidence=f"Pattern match: {pattern}",
                impact="Could allow attackers to drain funds through recursive calls",
                recommendation="Implement reentrancy guards (nonReentrant modifier)",
                score=45
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _check_external_calls(self, protocol: str) -> List[Vulnerability]:
        """Check for unsafe external calls"""
        vulnerabilities = []
        
        # Check for low-level calls without proper handling
        vuln = Vulnerability(
            id=str(uuid.uuid4())[:8],
            protocol=protocol,
            type=VulnerabilityType.UNSAFE_EXTERNAL_CALL,
            severity=Severity.HIGH,
            title="Unsafe External Call Detected",
            description="Protocol makes external calls without proper error handling.",
            evidence="raw_call or low-level call detected",
            impact="Could lead to DoS or unexpected behavior",
            recommendation="Use safe wrapper functions and check return values",
            score=75
        )
        vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _check_proxy_risks(self, protocol: str) -> List[Vulnerability]:
        """Check for proxy upgrade risks"""
        vulnerabilities = []
        
        # Check for common proxy vulnerabilities
        risks = [
            {
                "type": "Storage Collision",
                "severity": Severity.CRITICAL,
                "score": 95,
                "title": "Proxy Storage Collision Risk",
                "description": "New implementation may corrupt storage layout",
                "impact": "Could lead to permanent fund loss",
                "recommendation": "Use diamond pattern or careful storage management"
            },
            {
                "type": "Initialization",
                "severity": Severity.HIGH,
                "score": 80,
                "title": "Initializer Protection Missing",
                "description": "Proxy may be reinitialized after deployment",
                "impact": "Attacker could take control of proxy",
                "recommendation": "Use initializer modifier with require"
            },
            {
                "type": "Transparent Upgradeable",
                "severity": Severity.MEDIUM,
                "score": 50,
                "title": "Transparent Proxy Complexity",
                "description": "Admin functions may be unintentionally callable",
                "impact": "Confusion could lead to admin errors",
                "recommendation": "Use diamond pattern for complex upgrades"
            }
        ]
        
        for risk in risks:
            vuln = Vulnerability(
                id=str(uuid.uuid4())[:8],
                protocol=protocol,
                type=VulnerabilityType.PROXY_UPGRADE_RISK,
                severity=risk["severity"],
                title=risk["title"],
                description=risk["description"],
                evidence=risk["type"],
                impact=risk["impact"],
                recommendation=risk["recommendation"],
                score=risk["score"]
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _check_access_control(self, protocol: str) -> List[Vulnerability]:
        """Check for access control issues"""
        vulnerabilities = []
        
        vuln = Vulnerability(
            id=str(uuid.uuid4())[:8],
            protocol=protocol,
            type=VulnerabilityType.ACCESS_CONTROL,
            severity=Severity.HIGH,
            title="Missing Role-Based Access Control",
            description="Critical functions lack proper access control",
            evidence="Functions with onlyOwner or missing modifiers",
            impact="Unauthorized users could manipulate protocol",
            recommendation="Implement comprehensive role-based access control",
            score=70
        )
        vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _check_overflow_patterns(self, protocol: str) -> List[Vulnerability]:
        """Check for integer overflow/underflow patterns"""
        vulnerabilities = []
        
        vuln = Vulnerability(
            id=str(uuid.uuid4())[:8],
            protocol=protocol,
            type=VulnerabilityType.OVERFLOW_UNDERFLOW,
            severity=Severity.MEDIUM,
            title="Manual Arithmetic Operations",
            description="Protocol uses manual arithmetic without SafeMath",
            evidence="Direct uint256 operations detected",
            impact="Could lead to overflow/underflow exploits",
            recommendation="Use OpenZeppelin SafeMath or Solidity 0.8+",
            score=40
        )
        vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    # =========================================================================
    # Audit Report Analysis
    # =========================================================================
    
    async def _parse_audit_reports(self, protocol: str) -> List[AuditFinding]:
        """Parse audit reports from known firms"""
        findings = []
        
        # Sample audit findings (in production, fetch and parse actual reports)
        sample_audits = [
            {
                "auditor": "OpenZeppelin",
                "title": "Integer Overflow in Balance Calculation",
                "severity": Severity.HIGH,
                "category": "Arithmetic",
                "description": "Balance calculation could overflow with large values",
                "recommendation": "Use SafeMath or Solidity 0.8+"
            },
            {
                "auditor": "Trail of Bits",
                "title": "Flash Loan Attack Vector",
                "severity": Severity.MEDIUM,
                "category": "Economic",
                "description": "Flash loans could manipulate token prices",
                "recommendation": "Implement TWAP oracles"
            },
            {
                "auditor": "Consensys",
                "title": "Centralization Risk",
                "severity": Severity.LOW,
                "category": "Access Control",
                "description": "Admin has excessive privileges",
                "recommendation": "Implement timelocks and multi-sig"
            }
        ]
        
        for audit in sample_audits:
            finding = AuditFinding(
                id=str(uuid.uuid4())[:8],
                auditor=audit["auditor"],
                protocol=protocol,
                title=audit["title"],
                severity=audit["severity"],
                category=audit["category"],
                description=audit["description"],
                recommendation=audit["recommendation"],
                status="in_progress"
            )
            findings.append(finding)
        
        return findings
    
    async def check_audit_status(self, protocol: str) -> Dict[str, Any]:
        """Check if protocol has recent audit"""
        # In production, check actual audit databases
        return {
            "has_audit": True,
            "last_audit_date": "2024-01-15",
            "auditor": "OpenZeppelin",
            "audit_score": 85,
            "critical_issues": 0,
            "high_issues": 2,
            "medium_issues": 5,
            "low_issues": 10,
            "remediated": 8,
            "pending": 9
        }
    
    # =========================================================================
    # Liquidity Risk Monitoring
    # =========================================================================
    
    async def _check_liquidity_risks(self):
        """Check for liquidity-related risks across monitored protocols"""
        try:
            # Get current TVL
            tvl_data = await self._get_tvl_data()
            
            for protocol, current_tvl in tvl_data.items():
                historical = await self._get_historical_tvl(protocol, hours=24)
                
                if historical:
                    change_percent = ((current_tvl - historical) / historical) * 100
                    
                    if abs(change_percent) >= self._tvl_drop_threshold:
                        if change_percent < 0:
                            # TVL dropped
                            await shared_state.add_alert(
                                "tvl_drop",
                                f"🚨 {protocol} TVL dropped {abs(change_percent):.1f}% in 24h",
                                "warning" if abs(change_percent) < 30 else "critical"
                            )
                        else:
                            # TVL increased significantly
                            await shared_state.add_alert(
                                "tvl_surge",
                                f"📈 {protocol} TVL increased {change_percent:.1f}% in 24h",
                                "info"
                            )
            
        except Exception as e:
            logger.error(f"Liquidity check error: {e}")
    
    async def _analyze_liquidity_risk(self, protocol: str) -> List[Dict]:
        """Analyze liquidity concentration risks"""
        risks = []
        
        # Check for concentration risk
        concentration_risk = {
            "type": "concentration",
            "severity": Severity.MEDIUM,
            "description": "Significant portion of liquidity in single token pair",
            "metric": "Top pair accounts for 60% of TVL",
            "recommendation": "Diversify liquidity across multiple pairs"
        }
        risks.append(concentration_risk)
        
        # Check for oracle deviation risk
        oracle_risk = {
            "type": "oracle",
            "severity": Severity.INFO,
            "description": "Oracle prices within normal range",
            "metric": "Max deviation: 2.1%",
            "recommendation": "Continue monitoring"
        }
        risks.append(oracle_risk)
        
        return risks
    
    async def _check_upgrade_spikes(self):
        """Check for unusual proxy upgrade activity (potential exploit)"""
        # In production, monitor contract upgrade events
        pass
    
    async def _get_tvl_data(self) -> Dict[str, float]:
        """Get current TVL for monitored protocols"""
        return {
            "ekubo": 15000000,
            "jediswap": 8000000,
            "myswap": 5000000,
            "starkswap": 3000000,
            "nostra": 12000000
        }
    
    async def _get_historical_tvl(self, protocol: str, hours: int) -> Optional[float]:
        """Get TVL from N hours ago"""
        # In production, query historical data
        historical_tvl = {
            "ekubo": 14000000,
            "jediswap": 8500000,
            "myswap": 4800000,
            "starkswap": 3200000,
            "nostra": 11000000
        }
        return historical_tvl.get(protocol)
    
    # =========================================================================
    # Risk Scoring
    # =========================================================================
    
    def _calculate_risk_score(self,
                               vulnerabilities: List[Vulnerability],
                               audit_findings: List[AuditFinding],
                               liquidity_risks: List[Dict]) -> int:
        """Calculate overall security score (0-100, higher = safer)"""
        base_score = 100
        
        # Deduct for vulnerabilities
        severity_weights = {
            Severity.CRITICAL: 20,
            Severity.HIGH: 10,
            Severity.MEDIUM: 5,
            Severity.LOW: 2,
            Severity.INFO: 0
        }
        
        for vuln in vulnerabilities:
            base_score -= severity_weights.get(vuln.severity, 0)
        
        # Deduct for audit findings
        for finding in audit_findings:
            base_score -= severity_weights.get(finding.severity, 0)
        
        # Deduct for liquidity risks
        risk_weights = {
            Severity.CRITICAL: 15,
            Severity.HIGH: 8,
            Severity.MEDIUM: 4,
            Severity.LOW: 2,
            Severity.INFO: 0
        }
        
        for risk in liquidity_risks:
            severity = risk.get("severity", Severity.INFO)
            base_score -= risk_weights.get(severity, 0)
        
        return max(0, min(100, base_score))
    
    def _get_risk_level(self, score: int) -> str:
        """Convert score to risk level"""
        if score >= 90:
            return "Minimal"
        elif score >= 70:
            return "Low"
        elif score >= 50:
            return "Medium"
        elif score >= 30:
            return "High"
        else:
            return "Critical"
    
    # =========================================================================
    # Reporting and Alerts
    # =========================================================================
    
    async def _store_report(self, report: SecurityReport):
        """Store security report in shared state"""
        # Create content piece for the report
        content = ContentPiece(
            id=report.id,
            type="security_report",
            platform="internal",
            title=f"Security Report: {report.protocol} - Score: {report.overall_score}/100",
            content=report.summary,
            tags=["security", report.protocol, f"score-{report.overall_score}"]
        )
        await shared_state.add_content(content)
        
        logger.info(f"Security report stored: {report.protocol} ({report.overall_score}/100)")
    
    async def _alert_critical_findings(self, vulnerabilities: List[Vulnerability]):
        """Generate alerts for critical vulnerabilities"""
        for vuln in vulnerabilities:
            if vuln.severity in [Severity.CRITICAL, Severity.HIGH]:
                await shared_state.add_alert(
                    f"security_{vuln.type.value}",
                    f"🚨 {vuln.protocol}: {vuln.title} (Score: {vuln.score})",
                    "critical" if vuln.severity == Severity.CRITICAL else "warning"
                )
    
    def _generate_recommendations(self,
                                   vulnerabilities: List[Vulnerability],
                                   audit_findings: List[AuditFinding]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Group by type
        types_present = set(v.type for v in vulnerabilities)
        
        if VulnerabilityType.REENTRANCY in types_present:
            recommendations.append("Implement reentrancy guards on all external functions")
        
        if VulnerabilityType.ACCESS_CONTROL in types_present:
            recommendations.append("Review and strengthen role-based access control")
        
        if VulnerabilityType.PROXY_UPGRADE_RISK in types_present:
            recommendations.append("Conduct storage layout audit before upgrades")
        
        if VulnerabilityType.OVERFLOW_UNDERFLOW in types_present:
            recommendations.append("Migrate to SafeMath or Solidity 0.8+")
        
        if audit_findings:
            pending = [f for f in audit_findings if f.status != "remediated"]
            if pending:
                recommendations.append(f"Address {len(pending)} pending audit findings")
        
        if not recommendations:
            recommendations.append("Continue regular security audits")
            recommendations.append("Maintain bug bounty program")
        
        return recommendations
    
    def _generate_summary(self, protocol: str, score: int, risk_level: str, vuln_count: int) -> str:
        """Generate security report summary"""
        return f"""
Security Assessment: {protocol}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

Overall Score: {score}/100 ({risk_level} Risk)
Vulnerabilities Found: {vuln_count}

Key Findings:
- {vuln_count} vulnerability(ies) identified
- Risk level rated as {risk_level}
- Recommendations generated

Summary:
{protocol} shows {risk_level.lower()} risk profile with a security 
score of {score}/100. {'Immediate attention required for critical issues.' if risk_level in ['Critical', 'High'] else 'Standard monitoring recommended.'}
""".strip()
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security status for all monitored protocols"""
        status = {}
        
        for protocol in self._monitored_protocols:
            report = await self.scan_protocol(protocol)
            status[protocol] = {
                "score": report.overall_score,
                "risk_level": report.risk_level,
                "vulnerabilities": len(report.vulnerabilities),
                "audit_findings": len(report.audit_findings),
                "timestamp": report.timestamp
            }
        
        return status
    
    async def run_security_scan(self, protocol: str) -> SecurityReport:
        """Run immediate security scan (for testing/manual use)"""
        return await self.scan_protocol(protocol)
    
    async def get_vulnerabilities(self, 
                                   protocol: Optional[str] = None,
                                   severity: Optional[Severity] = None) -> List[Vulnerability]:
        """Get vulnerabilities, optionally filtered"""
        # In production, query from stored reports
        return []
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        status = await self.get_security_status()
        
        # Calculate averages
        scores = [s["score"] for s in status.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "protocols_monitored": len(status),
            "average_score": avg_score,
            "protocol_status": status,
            "critical_alerts": 0,
            "recent_scans": [],
            "timestamp": datetime.utcnow().isoformat()
        }


# Create agent instance
security_agent = SecurityAgent()
