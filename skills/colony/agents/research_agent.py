"""
Research Agent for Starknet Intelligence Colony
================================================
Deep protocol analysis, security audits, competitive research.
Integrates with Security Agent for comprehensive analysis.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import uuid

from ..shared_state import shared_state, ResearchReport
from ..orchestrator import orchestrator
from ..config import AGENTS

# Use global web tools (will be set by Moltbot when available)
web_search = None
web_fetch = None

logger = logging.getLogger(__name__)


@dataclass
class ProtocolAnalysis:
    """Deep protocol analysis"""
    name: str
    category: str  # DEX, Lending, Yield, etc.
    tvl: float
    tvl_change_24h: float
    volume_24h: float
    apr: float
    audit_status: str
    security_score: float
    risks: List[str]
    opportunities: List[str]
    competitors: List[str]
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "tvl": self.tvl,
            "tvl_change_24h": self.tvl_change_24h,
            "volume_24h": self.volume_24h,
            "apr": self.apr,
            "audit_status": self.audit_status,
            "security_score": self.security_score,
            "risks": self.risks,
            "opportunities": self.opportunities,
            "competitors": self.competitors
        }


class ResearchAgent:
    """
    Research Agent for deep protocol analysis.
    
    Responsibilities:
    - Deep protocol analysis
    - Security audit review
    - Token metrics analysis
    - Competitive analysis
    - Investment thesis generation
    """
    
    def __init__(self):
        self.name = "research_agent"
        self._running = False
        self._last_research = None
        self._research_queue: List[str] = []
    
    async def start(self):
        """Start the research agent"""
        logger.info("Research Agent starting")
        await shared_state.update_agent_status(self.name, "starting")
        self._running = True
        
        # Initialize research queue with default topics
        self._research_queue = list(AGENTS.RESEARCH_TOPICS)
        
        await shared_state.update_agent_status(self.name, "running")
        
        try:
            await self._run_loop()
        except asyncio.CancelledError:
            logger.info("Research Agent cancelled")
        finally:
            self._running = False
            await shared_state.update_agent_status(self.name, "stopped")
    
    async def _run_loop(self):
        """Main agent loop - runs less frequently than market agent"""
        while self._running:
            try:
                if self._research_queue:
                    topic = self._research_queue.pop(0)
                    await self._research_topic(topic)
                
                # Wait before next research cycle (6 hours)
                await asyncio.sleep(21600)
                
            except Exception as e:
                logger.error(f"Research Agent error: {e}")
                await shared_state.add_alert("research_agent_error", str(e), "error")
                await asyncio.sleep(3600)  # 1 hour on error
    
    # =========================================================================
    # Research Methods
    # =========================================================================
    
    async def _research_topic(self, topic: str):
        """Conduct research on a specific topic"""
        logger.info(f"Researching: {topic}")
        await shared_state.update_agent_status(self.name, f"researching: {topic}")
        
        # Search for recent information
        search_results = await self._search_topic(topic)
        
        # Fetch detailed information
        findings = []
        sources = []
        
        for result in search_results[:AGENTS.MAX_RESEARCH_DEPTH]:
            try:
                content = await self._fetch_content(result["url"])
                if content:
                    findings.extend(self._extract_findings(content))
                    sources.append({
                        "title": result["title"],
                        "url": result["url"]
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch {result['url']}: {e}")
        
        # Generate research report
        report = ResearchReport(
            id=str(uuid.uuid4())[:8],
            topic=topic,
            title=f"Research Brief: {topic}",
            summary=await self._generate_summary(topic, findings),
            findings=findings[:10],  # Limit findings
            risks=await self._identify_risks(topic, findings),
            opportunities=await self._identify_opportunities(topic, findings),
            sources=sources,
            timestamp=datetime.utcnow().isoformat(),
            sentiment=await self._analyze_sentiment(findings),
            confidence=min(0.9, 0.5 + len(findings) * 0.05)
        )
        
        # Store report
        await shared_state.add_research_report(report)
        self._last_research = datetime.utcnow()
        
        logger.info(f"Research complete: {topic}")
    
    async def _search_topic(self, topic: str) -> List[Dict[str, str]]:
        """Search for information on a topic"""
        # Use web search if available
        if web_search is not None:
            try:
                results = await web_search(
                    query=f"{topic} Starknet DeFi 2024",
                    count=10
                )
                
                if results:
                    return [
                        {
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "snippet": r.get("snippet", "")
                        }
                        for r in results
                    ]
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        # Return sample data if search not available or failed
        return [
            {
                "title": f"{topic} - Overview",
                "url": f"https://example.com/{topic.lower().replace(' ', '-')}",
                "snippet": f"Research findings for {topic}"
            }
        ]
    
    async def _fetch_content(self, url: str) -> str:
        """Fetch and extract readable content from URL"""
        if web_fetch is None:
            return ""
        
        try:
            content = await web_fetch(
                url=url,
                extractMode="markdown"
            )
            return content
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return ""
    
    def _extract_findings(self, content: str) -> List[str]:
        """Extract key findings from content"""
        # Simple extraction - in production, use NLP
        findings = []
        
        # Look for key sentences
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 50 and len(line) < 300:
                # Filter for meaningful content
                if any(keyword in line.lower() for keyword in [
                    'protocol', 'defi', 'starknet', 'tvl', 'volume',
                    'audit', 'security', 'risk', 'opportunity', 'yield'
                ]):
                    findings.append(line)
        
        return findings[:5]  # Limit findings per source
    
    async def _generate_summary(self, topic: str, findings: List[str]) -> str:
        """Generate research summary"""
        if not findings:
            return f"Research on {topic} - limited data available."
        
        summary = f"Research Brief: {topic}\n\n"
        summary += f"Analysis Date: {datetime.utcnow().strftime('%Y-%m-%d')}\n"
        summary += f"Findings: {len(findings)} key points identified.\n\n"
        
        if findings:
            summary += "Key Findings:\n"
            for i, finding in enumerate(findings[:5], 1):
                summary += f"{i}. {finding[:200]}...\n"
        
        return summary
    
    async def _identify_risks(self, topic: str, findings: List[str]) -> List[str]:
        """Identify potential risks from findings"""
        risk_keywords = [
            'hack', 'vulnerability', 'exploit', 'risk', 'warning',
            'audit', 'issue', 'problem', 'concern', 'attack'
        ]
        
        risks = []
        for finding in findings:
            if any(keyword in finding.lower() for keyword in risk_keywords):
                risks.append(finding[:200])
        
        # Add generic risks based on topic
        if 'defi' in topic.lower():
            risks.append("Smart contract risk - always audit before investing")
            risks.append("Impermanent loss for liquidity providers")
            risks.append("Oracle dependency risks")
        
        return list(set(risks))[:5]  # Deduplicate
    
    async def _identify_opportunities(self, topic: str, findings: List[str]) -> List[str]:
        """Identify opportunities from findings"""
        opp_keywords = [
            'growth', 'opportunity', 'yield', 'earning', 'profit',
            'launch', 'airdrop', 'incentive', 'reward', 'increase'
        ]
        
        opportunities = []
        for finding in findings:
            if any(keyword in finding.lower() for keyword in opp_keywords):
                opportunities.append(finding[:200])
        
        # Add generic opportunities
        if 'starknet' in topic.lower():
            opportunities.append("Early ecosystem participation potential")
            opportunities.append("STRK token incentives")
            opportunities.append("Low gas fees for DeFi strategies")
        
        return list(set(opportunities))[:5]
    
    async def _analyze_sentiment(self, findings: List[str]) -> str:
        """Analyze sentiment of findings"""
        positive = sum(1 for f in findings if any(
            word in f.lower() for word in ['growth', 'opportunity', 'profit', 'good', 'strong']
        ))
        negative = sum(1 for f in findings if any(
            word in f.lower() for word in ['risk', 'hack', 'warning', 'problem', 'bad']
        ))
        
        if positive > negative * 2:
            return "positive"
        elif negative > positive * 2:
            return "negative"
        else:
            return "neutral"
    
    # =========================================================================
    # Protocol Analysis
    # =========================================================================
    
    async def analyze_protocol(self, protocol_name: str) -> ProtocolAnalysis:
        """Deep analysis of a specific protocol"""
        # Sample analysis - in production, fetch real data
        analysis = ProtocolAnalysis(
            name=protocol_name,
            category="DEX",
            tvl=10_000_000,
            tvl_change_24h=5.2,
            volume_24h=1_500_000,
            apr=12.5,
            audit_status="Audited",
            security_score=0.85,
            risks=["Smart contract risk", "Liquidity risk"],
            opportunities=["High yield farming", "Early adoption rewards"],
            competitors=["jediswap", "myswap", "avnu"]
        )
        
        return analysis
    
    async def get_competitive_analysis(self) -> Dict[str, Any]:
        """Get competitive analysis of Starknet DeFi landscape"""
        return {
            "protocols": {
                "ekubo": {
                    "tvl": 15000000,
                    "volume_24h": 2300000,
                    "市场份额": "35%",
                    "优势": ["Concentrated liquidity", "Low fees"],
                    "劣势": ["New platform risk"]
                },
                "jediswap": {
                    "tvl": 8000000,
                    "volume_24h": 1200000,
                    "市场份额": "20%",
                    "优势": ["First mover", "Established brand"],
                    "劣势": ["Higher fees", "Lower efficiency"]
                },
                "myswap": {
                    "tvl": 5000000,
                    "volume_24h": 800000,
                    "市场份额": "12%",
                    "优势": ["Stablecoin focus"],
                    "劣势": ["Limited token pairs"]
                }
            },
            "market_share_by_category": {
                "DEX": {"ekubo": "35%", "jediswap": "20%", "myswap": "12%", "其他": "33%"},
                "Lending": {"nostra": "45%", "other": "55%"},
                "Yield": {"yearn": "30%", "beefy": "25%", "other": "45%"}
            },
            "emerging_trends": [
                "Concentrated liquidity becoming standard",
                "Real yield models replacing token incentives",
                "Cross-chain integrations growing",
                "Institutional interest increasing"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    async def queue_research(self, topic: str):
        """Queue a topic for research"""
        self._research_queue.append(topic)
    
    async def get_latest_research(self, topic: str) -> Optional[ResearchReport]:
        """Get latest research report for a topic"""
        return await shared_state.get_latest_research(topic)
    
    async def run_research_once(self, topic: str) -> ResearchReport:
        """Run research on a topic immediately (for testing)"""
        await self._research_topic(topic)
        return await shared_state.get_latest_research(topic)
    
    async def generate_investment_thesis(self, protocol_name: str) -> Dict[str, Any]:
        """Generate investment thesis for a protocol"""
        analysis = await self.analyze_protocol(protocol_name)
        
        return {
            "protocol": protocol_name,
            "thesis": f"""
Investment Thesis for {protocol_name}

Bull Case:
- TVL growing at {analysis.tvl_change_24h}% daily
- Strong security score of {analysis.security_score}
- Competitive APR of {analysis.apr}%
- Multiple yield opportunities

Risks:
- {', '.join(analysis.risks[:2])}

Recommendation: Monitor for entry opportunity
            """.strip(),
            "score": analysis.security_score * analysis.apr / 10,
            "confidence": 0.75,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # =========================================================================
    # Combined Research + Security Reports
    # =========================================================================
    
    async def generate_combined_report(self, protocol_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive report combining research and security analysis.
        
        This integrates the Research Agent with Security Agent for full analysis.
        """
        logger.info(f"Generating combined report for: {protocol_name}")
        
        # Run research analysis
        research_data = await self.analyze_protocol(protocol_name)
        
        # Run security analysis (import here to avoid circular dependency)
        try:
            from .security_agent import security_agent
            security_report = await security_agent.scan_protocol(protocol_name)
            security_data = security_report.to_dict()
        except ImportError:
            logger.warning("Security agent not available")
            security_data = {"error": "Security analysis unavailable"}
        
        # Generate combined report
        combined_report = {
            "protocol": protocol_name,
            "generated_at": datetime.utcnow().isoformat(),
            "research": {
                "category": research_data.category,
                "tvl": research_data.tvl,
                "tvl_change_24h": research_data.tvl_change_24h,
                "volume_24h": research_data.volume_24h,
                "apr": research_data.apr,
                "audit_status": research_data.audit_status,
                "security_score": research_data.security_score,
                "risks": research_data.risks,
                "opportunities": research_data.opportunities,
                "competitors": research_data.competitors
            },
            "security": security_data,
            "overall_assessment": self._assess_protocol(
                research_data.security_score,
                security_data.get("overall_score", 50),
                research_data.opportunities,
                research_data.risks
            ),
            "recommendations": await self._generate_combined_recommendations(
                research_data, security_data
            )
        }
        
        # Store as content
        from ..shared_state import ContentPiece
        content = ContentPiece(
            id=str(uuid.uuid4())[:8],
            type="combined_report",
            platform="internal",
            title=f"Combined Analysis: {protocol_name}",
            content=self._format_combined_report(combined_report),
            tags=["research", "security", protocol_name.lower()]
        )
        await shared_state.add_content(content)
        
        return combined_report
    
    def _assess_protocol(self,
                         research_score: float,
                         security_score: int,
                         opportunities: List[str],
                         risks: List[str]) -> Dict[str, Any]:
        """Generate overall protocol assessment"""
        # Weighted combination
        overall_score = (research_score * 0.4 + security_score * 0.6)
        
        if overall_score >= 80:
            assessment = "Strong Buy"
            risk_rating = "Low"
        elif overall_score >= 60:
            assessment = "Buy with Caution"
            risk_rating = "Medium"
        elif overall_score >= 40:
            assessment = "Hold"
            risk_rating = "High"
        else:
            assessment = "Avoid"
            risk_rating = "Critical"
        
        return {
            "overall_score": overall_score,
            "assessment": assessment,
            "risk_rating": risk_rating,
            "opportunity_count": len(opportunities),
            "risk_count": len(risks)
        }
    
    async def _generate_combined_recommendations(self,
                                                  research: ProtocolAnalysis,
                                                  security: Dict) -> List[str]:
        """Generate combined research + security recommendations"""
        recommendations = []
        
        # Research-based recommendations
        if research.opportunities:
            recommendations.append(f"Explore yield opportunities in {research.category}")
        
        if research.audit_status != "Audited":
            recommendations.append("Priority: Complete third-party security audit")
        
        # Security-based recommendations
        if isinstance(security, dict) and "recommendations" in security:
            recommendations.extend(security["recommendations"][:3])
        
        return recommendations[:10]
    
    def _format_combined_report(self, report: Dict) -> str:
        """Format combined report as readable text"""
        lines = [
            f"# Combined Analysis: {report['protocol']}",
            f"Generated: {report['generated_at']}",
            "",
            "## Research Summary",
            f"- Category: {report['research']['category']}",
            f"- TVL: ${report['research']['tvl']:,.0f}",
            f"- 24h Change: {report['research']['tvl_change_24h']:+.1f}%",
            f"- APR: {report['research']['apr']:.1f}%",
            f"- Security Score: {report['research']['security_score']:.2f}",
            "",
            "## Security Assessment",
            f"- Overall Score: {report['security'].get('overall_score', 'N/A')}/100",
            f"- Risk Level: {report['security'].get('risk_level', 'Unknown')}",
            f"- Vulnerabilities: {len(report['security'].get('vulnerabilities', []))}",
            "",
        ]
        
        # Add assessment section
        assessment = report['overall_assessment']
        lines.extend([
            "## Overall Assessment",
            f"- Score: {assessment['overall_score']:.1f}/100",
            f"- Rating: {assessment['assessment']}",
            f"- Risk: {assessment['risk_rating']}",
            "",
            "## Recommendations"
        ])
        
        for i, rec in enumerate(report['recommendations'], 1):
            lines.append(f"{i}. {rec}")
        
        return "\n".join(lines)


# Create agent instance
research_agent = ResearchAgent()
