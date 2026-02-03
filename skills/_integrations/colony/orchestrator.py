"""
Orchestrator for Starknet Intelligence Colony
==============================================
Main coordinator that manages agent lifecycle, scheduling, and communication.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Use absolute imports to support both module and standalone execution
from shared_state import shared_state, MessageType
from config import AGENTS, REPORTS, LOGGING

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent lifecycle states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class AgentInfo:
    """Information about a running agent"""
    name: str
    state: AgentState
    last_run: Optional[str] = None
    last_error: Optional[str] = None
    run_count: int = 0
    next_run: Optional[str] = None


class Orchestrator:
    """
    Main orchestrator for the Colony.
    
    Responsibilities:
    - Agent lifecycle management
    - Scheduling and coordination
    - Error handling and recovery
    - Resource management
    - Report generation coordination
    """
    
    def __init__(self):
        self._agents: Dict[str, Any] = {}  # Agent name -> agent instance
        self._agent_tasks: Dict[str, asyncio.Task] = {}
        self._agent_info: Dict[str, AgentInfo] = {}
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        # Report scheduling
        self._report_tasks: List[asyncio.Task] = []
        
        # Configuration
        self._check_interval = 10  # seconds between status checks
    
    # =========================================================================
    # Agent Registration
    # =========================================================================
    
    def register_agent(self, name: str, agent: Any):
        """Register an agent with the orchestrator"""
        if name in self._agents:
            logger.warning(f"Agent {name} already registered, overwriting")
        
        self._agents[name] = agent
        self._agent_info[name] = AgentInfo(
            name=name,
            state=AgentState.STOPPED
        )
        logger.info(f"Agent registered: {name}")
    
    def unregister_agent(self, name: str):
        """Unregister an agent"""
        if name in self._agents:
            del self._agents[name]
            if name in self._agent_info:
                del self._agent_info[name]
            logger.info(f"Agent unregistered: {name}")
    
    # =========================================================================
    # Agent Lifecycle
    # =========================================================================
    
    async def start_agent(self, name: str) -> bool:
        """Start a specific agent"""
        if name not in self._agents:
            logger.error(f"Agent not found: {name}")
            return False
        
        if name in self._agent_tasks and not self._agent_tasks[name].done():
            logger.warning(f"Agent {name} is already running")
            return False
        
        agent = self._agents[name]
        self._agent_info[name].state = AgentState.STARTING
        
        # Create task for agent
        task = asyncio.create_task(self._run_agent(name, agent))
        self._agent_tasks[name] = task
        
        logger.info(f"Agent starting: {name}")
        return True
    
    async def start_all_agents(self) -> None:
        """Start all registered agents"""
        for name in self._agents:
            await self.start_agent(name)
    
    async def stop_agent(self, name: str) -> bool:
        """Stop a specific agent"""
        if name not in self._agent_tasks:
            return False
        
        task = self._agent_tasks[name]
        self._agent_info[name].state = AgentState.STOPPING
        
        # Give agent time to cleanup
        try:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error stopping agent {name}: {e}")
        
        self._agent_info[name].state = AgentState.STOPPED
        del self._agent_tasks[name]
        logger.info(f"Agent stopped: {name}")
        return True
    
    async def stop_all_agents(self) -> None:
        """Stop all running agents"""
        for name in list(self._agent_tasks.keys()):
            await self.stop_agent(name)
    
    async def pause_agent(self, name: str) -> bool:
        """Pause a running agent"""
        if name not in self._agent_tasks:
            return False
        
        task = self._agent_tasks[name]
        task.cancel()
        
        self._agent_info[name].state = AgentState.PAUSED
        logger.info(f"Agent paused: {name}")
        return True
    
    async def resume_agent(self, name: str) -> bool:
        """Resume a paused agent"""
        if name not in self._agents:
            return False
        
        # Create new task
        agent = self._agents[name]
        task = asyncio.create_task(self._run_agent(name, agent))
        self._agent_tasks[name] = task
        
        self._agent_info[name].state = AgentState.RUNNING
        logger.info(f"Agent resumed: {name}")
        return True
    
    async def _run_agent(self, name: str, agent: Any) -> None:
        """Internal method to run an agent"""
        self._agent_info[name].state = AgentState.RUNNING
        self._agent_info[name].run_count += 1
        
        try:
            if hasattr(agent, 'run'):
                await agent.run()
            elif hasattr(agent, 'start'):
                await agent.start()
            else:
                logger.error(f"Agent {name} has no run() or start() method")
        except asyncio.CancelledError:
            logger.info(f"Agent {name} cancelled")
        except Exception as e:
            logger.error(f"Agent {name} error: {e}")
            self._agent_info[name].last_error = str(e)
            self._agent_info[name].state = AgentState.ERROR
            await shared_state.add_alert("agent_error", f"Agent {name} failed: {e}", "error")
        finally:
            if name in self._agent_tasks:
                del self._agent_tasks[name]
    
    # =========================================================================
    # Agent Status
    # =========================================================================
    
    def get_agent_status(self, name: str) -> Optional[AgentInfo]:
        """Get status of a specific agent"""
        return self._agent_info.get(name)
    
    def get_all_status(self) -> Dict[str, AgentInfo]:
        """Get status of all agents"""
        return dict(self._agent_info)
    
    async def wait_for_agents(self, timeout: Optional[float] = None) -> bool:
        """Wait for all agent tasks to complete"""
        if not self._agent_tasks:
            return True
        
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._agent_tasks.values(), return_exceptions=True),
                timeout=timeout
            )
            return True
        except asyncio.TimeoutError:
            return False
    
    # =========================================================================
    # Report Scheduling
    # =========================================================================
    
    async def schedule_report(self, report_type: str, interval_seconds: int):
        """Schedule a recurring report"""
        async def report_loop():
            while not self._shutdown_event.is_set():
                try:
                    # Generate report based on type
                    await self._generate_report(report_type)
                    await asyncio.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Report error ({report_type}): {e}")
        
        task = asyncio.create_task(report_loop())
        self._report_tasks.append(task)
        logger.info(f"Scheduled {report_type} report every {interval_seconds}s")
    
    async def _generate_report(self, report_type: str):
        """Generate a report of the specified type"""
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime(REPORTS.DATE_FORMAT)
        report_filename = REPORTS.OUTPUT_DIR / f"{report_type}_{timestamp}.json"
        
        report_data = {
            "type": report_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        if report_type == "market":
            market_data = await shared_state.get_market_data()
            arbitrage = await shared_state.get_arbitrage_opportunities()
            report_data["data"] = {
                "prices": market_data.to_dict() if market_data else {},
                "arbitrage": [a.to_dict() for a in arbitrage[:10]]
            }
        elif report_type == "whale":
            whales = await shared_state.get_whale_movements()
            report_data["data"] = {
                "movements": [w.to_dict() for w in whales[:20]]
            }
        elif report_type == "research":
            reports = await shared_state.get_research_reports(limit=5)
            report_data["data"] = {
                "reports": [r.to_dict() for r in reports]
            }
        elif report_type == "content":
            content = await shared_state.get_content(limit=10)
            report_data["data"] = {
                "content": [c.to_dict() for c in content]
            }
        
        # Save report
        import json
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Report generated: {report_filename}")
    
    # =========================================================================
    # Main Loop
    # =========================================================================
    
    async def run(self, run_forever: bool = True):
        """
        Run the orchestrator.
        
        Args:
            run_forever: If True, runs until shutdown. If False, runs once and returns.
        """
        self._running = True
        logger.info("Orchestrator starting")
        
        try:
            # Load persisted state
            await shared_state.load_state()
            
            # Start all agents
            await self.start_all_agents()
            
            # Schedule periodic reports
            await self.schedule_report("market", AGENTS.REPORT_INTERVAL)
            await self.schedule_report("whale", AGENTS.REPORT_INTERVAL)
            await self.schedule_report("content", AGENTS.REPORT_INTERVAL)
            
            # Start daily research report
            await self.schedule_report("research", 86400)  # 24 hours
            
            if run_forever:
                # Main loop for monitoring
                while self._running:
                    await self._monitor_loop()
                    await asyncio.sleep(self._check_interval)
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            await shared_state.add_alert("orchestrator_error", str(e), "critical")
        finally:
            await self.shutdown()
    
    async def _monitor_loop(self):
        """Periodic monitoring tasks"""
        # Update agent status
        for name, info in self._agent_info.items():
            if name in self._agent_tasks:
                task = self._agent_tasks[name]
                if task.done():
                    if info.state == AgentState.RUNNING:
                        info.state = AgentState.STOPPED
                    # Check for exceptions
                    try:
                        exc = task.exception()
                        if exc:
                            info.last_error = str(exc)
                            info.state = AgentState.ERROR
                    except asyncio.InvalidStateError:
                        pass
        
        # Update shared state with agent statuses
        status_data = {
            name: {
                "state": info.state.value,
                "last_run": info.last_run,
                "run_count": info.run_count
            }
            for name, info in self._agent_info.items()
        }
        await shared_state.update_agent_status("orchestrator", "running")
        
        # Periodic state save
        await shared_state.save_state()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Orchestrator shutting down")
        self._running = False
        self._shutdown_event.set()
        
        # Stop all agents
        await self.stop_all_agents()
        
        # Cancel report tasks
        for task in self._report_tasks:
            task.cancel()
        
        # Final state save
        await shared_state.save_state()
        
        logger.info("Orchestrator shutdown complete")
    
    async def restart(self):
        """Restart the orchestrator"""
        await self.shutdown()
        self._running = True
        self._shutdown_event = asyncio.Event()
        await self.run()
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    async def get_colony_status(self) -> Dict[str, Any]:
        """Get full colony status"""
        snapshot = await shared_state.get_snapshot()
        snapshot["orchestrator"] = {
            "running": self._running,
            "agents": {name: info.__dict__ for name, info in self._agent_info.items()},
            "active_tasks": len(self._agent_tasks)
        }
        return snapshot
    
    async def send_message(self, target_agent: str, message_type: str, payload: Any):
        """Send a message to a specific agent"""
        # Store message in shared state for agent to pick up
        await shared_state.add_alert(message_type, payload, "info")
        logger.info(f"Message sent to {target_agent}: {message_type}")


# Global orchestrator instance
orchestrator = Orchestrator()
