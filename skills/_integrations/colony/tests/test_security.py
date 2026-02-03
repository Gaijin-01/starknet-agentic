"""
Tests for Security Analysis Agent
"""

import pytest
from pathlib import Path
import sys
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestSecurityAgent:
    """Tests for Security Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create security agent instance"""
        from colony.agents.security_agent import SecurityAgent
        return SecurityAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent creates properly"""
        assert agent.name == "security_agent"
        assert agent._running is False
        assert len(agent._monitored_protocols) > 0
    
    @pytest.mark.asyncio
    async def test_vulnerability_severity_levels(self, agent):
        """Test vulnerability severity classification"""
        from colony.agents.security_agent import Severity, Vulnerability
        
        vuln = Vulnerability(
            id="test-123",
            protocol="test",
            type=agent._vulnerability_patterns.keys().__iter__().__next__(),
            severity=Severity.CRITICAL,
            title="Test Vulnerability",
            description="Test description",
            evidence="Test evidence",
            impact="Test impact",
            recommendation="Test recommendation",
            score=95
        )
        
        assert vuln.severity == Severity.CRITICAL
        assert vuln.score == 95
    
    @pytest.mark.asyncio
    async def test_risk_score_calculation(self, agent):
        """Test overall risk score calculation"""
        from colony.agents.security_agent import Vulnerability, Severity, VulnerabilityType
        
        # Create test vulnerabilities
        vulnerabilities = [
            Vulnerability(
                id="test-1",
                protocol="test",
                type=VulnerabilityType.REENTRANCY,
                severity=Severity.CRITICAL,
                title="Critical",
                description="",
                evidence="",
                impact="",
                recommendation="",
                score=95
            ),
            Vulnerability(
                id="test-2",
                protocol="test",
                type=VulnerabilityType.ACCESS_CONTROL,
                severity=Severity.HIGH,
                title="High",
                description="",
                evidence="",
                impact="",
                recommendation="",
                score=75
            )
        ]
        
        audit_findings = []
        liquidity_risks = []
        
        score = agent._calculate_risk_score(vulnerabilities, audit_findings, liquidity_risks)
        
        # Should be 100 - 20 (critical) - 10 (high) = 70
        assert score == 70
    
    @pytest.mark.asyncio
    async def test_risk_level_mapping(self, agent):
        """Test score to risk level conversion"""
        assert agent._get_risk_level(95) == "Minimal"
        assert agent._get_risk_level(75) == "Low"
        assert agent._get_risk_level(55) == "Medium"
        assert agent._get_risk_level(35) == "High"
        assert agent._get_risk_level(15) == "Critical"
    
    @pytest.mark.asyncio
    async def test_protocol_scan(self, agent):
        """Test security scan of a protocol"""
        report = await agent.scan_protocol("ekubo")
        
        assert report.protocol == "ekubo"
        assert report.overall_score >= 0
        assert report.risk_level in ["Minimal", "Low", "Medium", "High", "Critical"]
        assert len(report.vulnerabilities) >= 0
        assert report.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_security_report_generation(self, agent):
        """Test security report structure"""
        report = await agent.scan_protocol("jediswap")
        
        assert hasattr(report, "id")
        assert hasattr(report, "protocol")
        assert hasattr(report, "overall_score")
        assert hasattr(report, "risk_level")
        assert hasattr(report, "vulnerabilities")
        assert hasattr(report, "audit_findings")
        assert hasattr(report, "recommendations")
        assert hasattr(report, "summary")
    
    @pytest.mark.asyncio
    async def test_audit_finding_creation(self, agent):
        """Test audit finding data structure"""
        from colony.agents.security_agent import AuditFinding, Severity
        
        finding = AuditFinding(
            id="audit-123",
            auditor="OpenZeppelin",
            protocol="test",
            title="Test Finding",
            severity=Severity.HIGH,
            category="Access Control",
            description="Test description",
            recommendation="Fix it"
        )
        
        assert finding.auditor == "OpenZeppelin"
        assert finding.severity == Severity.HIGH
        assert finding.status == "unresolved"
    
    @pytest.mark.asyncio
    async def test_recommendation_generation(self, agent):
        """Test recommendation generation from vulnerabilities"""
        from colony.agents.security_agent import Vulnerability, Severity, VulnerabilityType
        
        vulnerabilities = [
            Vulnerability(
                id="test-1",
                protocol="test",
                type=VulnerabilityType.REENTRANCY,
                severity=Severity.HIGH,
                title="Reentrancy",
                description="",
                evidence="",
                impact="",
                recommendation="",
                score=80
            )
        ]
        
        audit_findings = []
        recommendations = agent._generate_recommendations(vulnerabilities, audit_findings)
        
        assert len(recommendations) > 0
        assert any("reentrancy" in r.lower() for r in recommendations)
    
    @pytest.mark.asyncio
    async def test_summary_generation(self, agent):
        """Test security summary generation"""
        summary = agent._generate_summary("TestProtocol", 75, "Low", 3)
        
        assert "TestProtocol" in summary
        assert "75/100" in summary
        assert "Low Risk" in summary
    
    @pytest.mark.asyncio
    async def test_vulnerability_to_dict(self, agent):
        """Test vulnerability serialization"""
        from colony.agents.security_agent import Vulnerability, Severity, VulnerabilityType
        
        vuln = Vulnerability(
            id="test-123",
            protocol="test",
            type=VulnerabilityType.REENTRANCY,
            severity=Severity.MEDIUM,
            title="Test",
            description="Desc",
            evidence="Ev",
            impact="Imp",
            recommendation="Rec",
            score=50
        )
        
        data = vuln.to_dict()
        
        assert data["id"] == "test-123"
        assert data["type"] == "reentrancy"
        assert data["severity"] == "medium"
        assert data["score"] == 50
    
    @pytest.mark.asyncio
    async def test_audit_status_check(self, agent):
        """Test audit status checking"""
        status = await agent.check_audit_status("ekubo")
        
        assert "has_audit" in status
        assert "last_audit_date" in status
        assert "auditor" in status
        assert status["has_audit"] is True
    
    @pytest.mark.asyncio
    async def test_security_dashboard(self, agent):
        """Test security dashboard data"""
        dashboard = await agent.get_security_dashboard()
        
        assert "protocols_monitored" in dashboard
        assert "average_score" in dashboard
        assert "protocol_status" in dashboard
        assert dashboard["protocols_monitored"] > 0
    
    @pytest.mark.asyncio
    async def test_liquidity_risk_analysis(self, agent):
        """Test liquidity risk analysis"""
        risks = await agent._analyze_liquidity_risk("ekubo")
        
        assert len(risks) > 0
        for risk in risks:
            assert "type" in risk
            assert "severity" in risk
            assert "description" in risk
    
    @pytest.mark.asyncio
    async def test_vulnerability_types(self, agent):
        """Test all vulnerability types are available"""
        from colony.agents.security_agent import VulnerabilityType
        
        expected_types = [
            VulnerabilityType.REENTRANCY,
            VulnerabilityType.UNSAFE_EXTERNAL_CALL,
            VulnerabilityType.PROXY_UPGRADE_RISK,
            VulnerabilityType.ACCESS_CONTROL,
            VulnerabilityType.OVERFLOW_UNDERFLOW,
            VulnerabilityType.FRONT_RUNNING,
            VulnerabilityType.ORACLE_MANIPULATION,
            VulnerabilityType.CONCENTRATION_RISK,
            VulnerabilityType.TVL_DROP,
            VulnerabilityType.ORACLE_DEVIATION
        ]
        
        for vtype in expected_types:
            assert vtype in VulnerabilityType


class TestResearchIntegration:
    """Tests for Research + Security integration"""
    
    @pytest.mark.asyncio
    async def test_combined_report_generation(self):
        """Test combined research + security report"""
        from colony.agents.research_agent import ResearchAgent
        
        agent = ResearchAgent()
        report = await agent.generate_combined_report("ekubo")
        
        assert report["protocol"] == "ekubo"
        assert "research" in report
        assert "security" in report
        assert "overall_assessment" in report
        assert "recommendations" in report
    
    @pytest.mark.asyncio
    async def test_combined_report_assessment(self):
        """Test combined assessment calculation"""
        from colony.agents.research_agent import ResearchAgent
        
        agent = ResearchAgent()
        
        assessment = agent._assess_protocol(
            research_score=0.85,
            security_score=80,
            opportunities=["Yield farming", "Liquidity provision"],
            risks=["Smart contract risk", "Impermanent loss"]
        )
        
        assert "overall_score" in assessment
        assert "assessment" in assessment
        assert "risk_rating" in assessment


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
