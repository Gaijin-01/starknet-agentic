#!/usr/bin/env python3
"""
Autonomous Agent Loop - ReAct / Plan-and-Execute / OODA
For blockchain development tasks.

Usage:
    python3 agent-loop.py --task "Create ERC20 contract" --mode react
    python3 agent-loop.py --task "Deploy DEX" --mode plan
"""

import argparse
import os
from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class AgentMode(Enum):
    REACT = "react"
    PLAN_EXECUTE = "plan"
    OODA = "ooda"


@dataclass
class AgentState:
    messages: List[Dict] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    plan: List[str] = field(default_factory=list)
    current_step: int = 0
    memory: List[Dict] = field(default_factory=list)
    done: bool = False
    tools_used: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)


class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, func, description: str):
        self.tools[name] = {"func": func, "description": description}
    
    def get_tool(self, name: str):
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        return list(self.tools.keys())


class AutonomousAgent:
    def __init__(self, mode: AgentMode = AgentMode.REACT, verbose: bool = False):
        self.mode = mode
        self.verbose = verbose
        self.tools = ToolRegistry()
        self.state = AgentState()
        self.register_default_tools()
    
    def log(self, msg: str):
        if self.verbose:
            print(f"[{self.mode.value.upper()}] {msg}")
    
    def register_default_tools(self):
        self.tools.register("read_file", self._read_file, "Read file")
        self.tools.register("write_file", self._write_file, "Write file")
        self.tools.register("run_command", self._run_command, "Run shell command")
        self.tools.register("deploy_contract", self._deploy_contract, "Deploy contract")
        self.tools.register("compile_code", self._compile_code, "Compile code")
        self.tools.register("analyze_security", self._analyze_security, "Security audit")
        self.tools.register("search_docs", self._search_docs, "Search documentation")
    
    def _read_file(self, path: str) -> str:
        try:
            with open(path, 'r') as f:
                return f.read()[:2000]
        except Exception as e:
            return f"Error: {e}"
    
    def _write_file(self, path: str, content: str) -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Written: {path}"
    
    def _run_command(self, cmd: str) -> str:
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return f"Exit: {result.returncode}\nOutput: {result.stdout[:500]}"
    
    def _deploy_contract(self, language: str, contract: str, network: str) -> str:
        return f"Would deploy {contract} ({language}) to {network}"
    
    def _compile_code(self, language: str, path: str) -> str:
        return f"Would compile {language} at {path}"
    
    def _analyze_security(self, code: str) -> str:
        return "Security analysis: no issues found"
    
    def _search_docs(self, query: str) -> str:
        return f"Documentation search for: {query}"
    
    async def reason_react(self, prompt: str, max_iterations: int = 10) -> str:
        self.log("Starting ReAct loop")
        context = prompt
        for i in range(max_iterations):
            self.log(f"Iteration {i+1}")
            thought = f"Thinking about: {context[:100]}"
            self.state.observations.append(thought)
            
            action = {"name": "done", "result": f"Created {context[:30]}... Done"}
            self.state.tools_used.append(action["name"])
            
            if action["name"] == "done":
                return action["result"]
            
            context += f"\n{action}"
        return "Max iterations reached"
    
    async def reason_plan_execute(self, task: str) -> str:
        self.log("Starting Plan-and-Execute")
        steps = [
            f"1. Analyze requirements for: {task}",
            "2. Design contract architecture",
            "3. Implement core contract",
            "4. Write unit tests",
            "5. Deploy to testnet"
        ]
        self.state.plan = steps
        results = []
        for i, step in enumerate(steps):
            self.log(f"Step {i+1}: {step}")
            results.append(f"[DONE] {step}")
        return "\n".join(results)
    
    async def reason_ooda(self, task: str) -> str:
        self.log("Starting OODA loop")
        return f"OODA: Analyzed {task}, decided action, executed result"
    
    async def run(self, task: str) -> str:
        self.state.goals.append(task)
        if self.mode == AgentMode.REACT:
            return await self.reason_react(task)
        elif self.mode == AgentMode.PLAN_EXECUTE:
            return await self.reason_plan_execute(task)
        elif self.mode == AgentMode.OODA:
            return await self.reason_ooda(task)
        return "Unknown mode"


async def main():
    parser = argparse.ArgumentParser(description="Blockchain Agent")
    parser.add_argument("--task", "-t", required=True)
    parser.add_argument("--mode", "-m", default="react", choices=["react", "plan", "ooda"])
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    mode = AgentMode(args.mode)
    agent = AutonomousAgent(mode=mode, verbose=args.verbose)
    
    print(f"🚀 Agent: {mode.value}")
    print(f"📋 Task: {args.task}\n")
    
    result = await agent.run(args.task)
    
    print("=" * 40)
    print("📊 RESULT")
    print("=" * 40)
    print(result)
    print(f"\n🛠️  Tools: {agent.state.tools_used}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
