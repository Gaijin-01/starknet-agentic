"""
Opportunity Tracker - Log and analyze arbitrage opportunities
Stores data in JSON lines format for later parsing
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field


TRACKING_LOG = Path(__file__).parent / "tracking.log"


@dataclass
class TrackedOpportunity:
    """Tracked arbitrage opportunity"""
    id: str  # Unique ID: dex_from-dex_to-token_path
    pair: str  # "STRK→USDC"
    dex_from: str
    dex_to: str
    token_path: List[str]
    estimated_profit: float
    profit_percent: float
    first_seen: str  # ISO timestamp
    last_seen: str  # ISO timestamp
    scanned_at: str  # HH:MM:SS
    executed_at: Optional[str] = None
    actual_profit: Optional[float] = None
    gas_used: Optional[float] = None
    slippage: Optional[float] = None
    status: str = "scanned"  # scanned, executed, expired, null

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.first_seen,
            "pair": self.pair,
            "dex_from": self.dex_from,
            "dex_to": self.dex_to,
            "token_path": self.token_path,
            "estimated_profit": self.estimated_profit,
            "profit_percent": self.profit_percent,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "scanned_at": self.scanned_at,
            "executed_at": self.executed_at,
            "actual_profit": self.actual_profit,
            "gas_used": self.gas_used,
            "slippage": self.slippage,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrackedOpportunity":
        return cls(
            id=data.get("id", ""),
            pair=data.get("pair", ""),
            dex_from=data.get("dex_from", ""),
            dex_to=data.get("dex_to", ""),
            token_path=data.get("token_path", []),
            estimated_profit=data.get("estimated_profit", 0),
            profit_percent=data.get("profit_percent", 0),
            first_seen=data.get("first_seen", ""),
            last_seen=data.get("last_seen", ""),
            scanned_at=data.get("scanned_at", ""),
            executed_at=data.get("executed_at"),
            actual_profit=data.get("actual_profit"),
            gas_used=data.get("gas_used"),
            slippage=data.get("slippage"),
            status=data.get("status", "scanned")
        )


class OpportunityTracker:
    """Track arbitrage opportunities over time"""

    def __init__(self, log_file: Path = TRACKING_LOG):
        self.log_file = log_file
        self._memory_cache: Dict[str, TrackedOpportunity] = {}

    def _generate_id(self, opp) -> str:
        """Generate unique ID for opportunity"""
        path = "-".join(opp.token_path)
        return f"{opp.dex_from}-{opp.dex_to}-{path}"

    def _get_time_now(self) -> tuple:
        """Get current time as ISO and HH:MM:SS"""
        now = datetime.utcnow()
        return now.isoformat() + "Z", now.strftime("%H:%M:%S")

    def log_opportunity(self, opp) -> TrackedOpportunity:
        """Log a new or update existing opportunity"""
        opp_id = self._generate_id(opp)
        iso_time, time_str = self._get_time_now()

        # Check if exists in cache
        if opp_id in self._memory_cache:
            tracked = self._memory_cache[opp_id]
            tracked.last_seen = iso_time
            tracked.estimated_profit = opp.estimated_profit
            tracked.profit_percent = opp.profit_percent
        else:
            pair = "→".join(opp.token_path)
            tracked = TrackedOpportunity(
                id=opp_id,
                pair=pair,
                dex_from=opp.dex_from,
                dex_to=opp.dex_to,
                token_path=opp.token_path,
                estimated_profit=opp.estimated_profit,
                profit_percent=opp.profit_percent,
                first_seen=iso_time,
                last_seen=iso_time,
                scanned_at=time_str
            )
            self._memory_cache[opp_id] = tracked

        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(tracked.to_dict()) + "\n")

        return tracked

    def mark_executed(self, opp_id: str, actual_profit: float, gas_used: float, slippage: float = 0):
        """Mark opportunity as executed with real metrics"""
        if opp_id in self._memory_cache:
            tracked = self._memory_cache[opp_id]
            tracked.executed_at = datetime.utcnow().isoformat() + "Z"
            tracked.actual_profit = actual_profit
            tracked.gas_used = gas_used
            tracked.slippage = slippage
            tracked.status = "executed"

            # Update log
            with open(self.log_file, "a") as f:
                f.write(json.dumps(tracked.to_dict()) + "\n")

    def mark_expired(self, opp_id: str):
        """Mark opportunity as expired"""
        if opp_id in self._memory_cache:
            tracked = self._memory_cache[opp_id]
            tracked.status = "expired"
            tracked.last_seen = datetime.utcnow().isoformat() + "Z"

    def load_history(self) -> List[TrackedOpportunity]:
        """Load all tracked opportunities from log"""
        opportunities = []

        if not self.log_file.exists():
            return opportunities

        with open(self.log_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        opp = TrackedOpportunity.from_dict(data)
                        opportunities.append(opp)
                        self._memory_cache[opp.id] = opp
                    except json.JSONDecodeError:
                        continue

        return opportunities

    def get_stats(self) -> Dict:
        """Get tracking statistics - counts from log file"""
        entries = []

        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and line != "{}":
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

        if not entries:
            return {
                "total": 0,
                "executed": 0,
                "avg_variance": None,
                "avg_gas": None,
                "avg_opportunity_lifespan_min": None
            }

        executed = [e for e in entries if e.get("status") == "executed"]

        # Calculate variance (estimated vs actual)
        variances = []
        gas_costs = []

        for e in executed:
            estimated = e.get("estimated_profit", 0)
            actual = e.get("actual_profit", 0)
            if estimated and actual:
                variance = ((actual - estimated) / estimated) * 100
                variances.append(variance)

            gas = e.get("gas_used")
            if gas:
                gas_costs.append(gas)

        return {
            "total": len(entries),
            "executed": len(executed),
            "scanned": len([e for e in entries if e.get("status") == "scanned"]),
            "avg_variance": sum(variances) / len(variances) if variances else None,
            "avg_gas": sum(gas_costs) / len(gas_costs) if gas_costs else None,
            "avg_opportunity_lifespan_min": None  # Will be calculated per-pair
        }

    def analyze_by_pair(self) -> Dict[str, Dict]:
        """Analyze opportunities by trading pair - counts ALL historical observations"""
        by_pair = {}

        # Read all entries from log file for accurate counts
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    pair = data.get("pair", "unknown")
                    if pair not in by_pair:
                        by_pair[pair] = {
                            "count": 0,
                            "total_estimated": 0,
                            "total_actual": 0,
                            "total_profit_percent": 0,
                            "executed": 0,
                            "lifespans": []
                        }

                    by_pair[pair]["count"] += 1
                    by_pair[pair]["total_estimated"] += data.get("estimated_profit", 0)
                    by_pair[pair]["total_profit_percent"] += data.get("profit_percent", 0)

                    if data.get("status") == "executed" and data.get("actual_profit"):
                        by_pair[pair]["total_actual"] += data["actual_profit"]
                        by_pair[pair]["executed"] += 1

        # Calculate averages
        for pair_data in by_pair.values():
            if pair_data["count"] > 0:
                pair_data["avg_profit_percent"] = pair_data["total_profit_percent"] / pair_data["count"]
                pair_data["avg_estimated"] = pair_data["total_estimated"] / pair_data["count"]

        return by_pair


# Convenience function
def get_tracker() -> OpportunityTracker:
    """Get the global tracker instance"""
    return OpportunityTracker()
