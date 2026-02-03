#!/usr/bin/env python3
"""
minimax_client.py - MiniMax API Client with Tool Calling Support

This module provides MiniMax API integration with OpenAI-compatible tool calling.
Supports: Chat completions, streaming, function calling.
"""

import json
import logging
import os
import asyncio
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional
from pathlib import Path

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('minimax-client')


@dataclass
class ToolCall:
    """Represents a tool call from LLM."""
    id: str
    function_name: str
    arguments: str


@dataclass
class ChatMessage:
    """Chat message for completions."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


@dataclass
class CompletionResponse:
    """Response from chat completion."""
    content: str
    model: str
    tool_calls: Optional[List[ToolCall]] = None
    usage: Optional[Dict] = None


class MiniMaxClient:
    """
    MiniMax API client with tool calling support.
    
    Compatible with OpenAI-style tool calling format.
    """
    
    # Correct API endpoints (OpenAI-compatible)
    BASE_URL = "https://api.minimax.io/v1"
    CHAT_COMPLETIONS = "/chat/completions"
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "MiniMax-M2.1"
    ):
        self.api_key = api_key or os.environ.get("MINIMAX_API_KEY", "")
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def chat_complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False
    ) -> CompletionResponse:
        """
        Send chat completion request with optional tool calling.
        
        Args:
            messages: List of message dicts
            tools: OpenAI-style tool definitions
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-2)
            stream: Whether to stream response
            
        Returns:
            CompletionResponse with content and optional tool calls
        """
        session = await self._get_session()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if tools:
            payload["tools"] = tools
        
        if stream:
            return await self._stream_complete(session, payload)
        
        # Non-streaming request
        try:
            async with session.post(
                f"{self.base_url}{self.CHAT_COMPLETIONS}",
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"MiniMax API error: {response.status} - {error_text}")
                    raise Exception(f"API error: {response.status}")
                
                data = await response.json()
                return self._parse_response(data)
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise
    
    async def _stream_complete(
        self,
        session: aiohttp.ClientSession,
        payload: Dict
    ) -> CompletionResponse:
        """Handle streaming completion."""
        # For now, return non-streaming
        # Full streaming implementation would parse SSE
        async with session.post(
            f"{self.base_url}{self.CHAT_COMPLETIONS}",
            json=payload
        ) as response:
            data = await response.json()
            return self._parse_response(data)
    
    def _parse_response(self, data: Dict) -> CompletionResponse:
        """Parse API response into CompletionResponse."""
        # Extract content from OpenAI-compatible format
        content = ""
        tool_calls = None
        
        # OpenAI/MiniMax format
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            # Extract tool calls
            if "tool_calls" in message:
                tool_calls = [
                    ToolCall(
                        id=tc.get("id", ""),
                        function_name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", "")
                    )
                    for tc in message["tool_calls"]
                ]
        
        # Usage stats
        usage = data.get("usage", {})
        
        return CompletionResponse(
            content=content,
            model=data.get("model", self.model),
            tool_calls=tool_calls,
            usage=usage
        )
    
    async def call_with_tools(
        self,
        messages: List[ChatMessage],
        tools: List[Dict],
        tool_executor=None,
        max_iterations: int = 5
    ) -> str:
        """
        Execute chat with tool calling loop.
        
        This method handles the complete tool calling flow:
        1. Send message with tool definitions
        2. If LLM requests tool, execute it
        3. Send result back to LLM
        4. Repeat until no more tool calls
        
        Args:
            messages: List of ChatMessage objects
            tools: Tool definitions
            tool_executor: Function to execute tools (name, args) -> result
            max_iterations: Maximum tool call iterations
            
        Returns:
            Final text response from LLM
        """
        # Convert messages to dict format
        msg_dicts = []
        for msg in messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function_name,
                            "arguments": tc.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            msg_dicts.append(msg_dict)
        
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Get response
            response = await self.chat_complete(
                messages=msg_dicts,
                tools=tools,
                max_tokens=4096
            )
            
            # If no tool calls, return content
            if not response.tool_calls:
                return response.content
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                logger.info(f"Tool call: {tool_call.function_name}")
                
                # Execute tool if executor provided
                if tool_executor:
                    try:
                        args = json.loads(tool_call.arguments) if tool_call.arguments else {}
                        result = await tool_executor(tool_call.function_name, args)
                        result_json = json.dumps(result)
                    except Exception as e:
                        result_json = json.dumps({"error": str(e)})
                else:
                    result_json = json.dumps({"message": "Tool executor not configured"})
                
                # Add tool result to messages
                msg_dicts.append({
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function_name,
                            "arguments": tool_call.arguments
                        }
                    }]
                })
                
                msg_dicts.append({
                    "role": "tool",
                    "content": result_json,
                    "tool_call_id": tool_call.id
                })
        
        return "Max iterations reached"


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

async def get_minimax_client(
    api_key: str = None,
    model: str = "MiniMax-M2.1"
) -> MiniMaxClient:
    """Get configured MiniMax client."""
    return MiniMaxClient(
        api_key=api_key,
        model=model
    )


async def quick_complete(
    prompt: str,
    api_key: str = None,
    model: str = "MiniMax-M2.1"
) -> str:
    """Quick text completion without tool calling."""
    async with MiniMaxClient(api_key=api_key, model=model) as client:
        response = await client.chat_complete(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048
        )
        return response.content


# ============================================
# MAIN (for testing)
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MiniMax client test")
    parser.add_argument("--prompt", "-p", default="Hello, how are you?")
    parser.add_argument("--model", "-m", default="MiniMax-M2.1")
    
    args = parser.parse_args()
    
    async def test():
        print(f"Model: {args.model}")
        print(f"Prompt: {args.prompt}")
        print("---")
        
        result = await quick_complete(args.prompt, model=args.model)
        print(f"Response: {result}")
    
    asyncio.run(test())
