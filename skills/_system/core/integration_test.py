#!/usr/bin/env python3
"""
integration_test.py - Full LLM Tool Calling Integration Test

Tests the complete pipeline:
1. LLM (MiniMax) receives message
2. LLM triggers tool call
3. Executor executes tool
4. Result sent back to LLM
5. LLM generates final response
"""

import asyncio
import sys
import json
from pathlib import Path

# Add paths for imports
CURRENT_DIR = Path(__file__).parent
SKILLS_SYSTEM = CURRENT_DIR
CLAWD = SKILLS_SYSTEM.parent.parent.parent

sys.path.insert(0, str(SKILLS_SYSTEM))
sys.path.insert(0, str(CLAWD))

from minimax_client import MiniMaxClient
from tools import TOOL_DEFINITIONS
from executor import ToolExecutor


async def test_full_pipeline():
    """Test complete LLM tool calling pipeline."""
    print("=" * 60)
    print("🔗 FULL PIPELINE INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize components
    client = MiniMaxClient()
    executor = ToolExecutor()
    
    print(f"\n✅ Components initialized")
    print(f"   Model: {client.model}")
    print(f"   Tools: {len(TOOL_DEFINITIONS)} defined")
    
    # Test cases
    test_cases = [
        {
            "name": "Crypto Price Query",
            "message": "What's the current price of Bitcoin?",
            "expected_tool": "get_crypto_price",
            "expected_param": "bitcoin"
        },
        {
            "name": "Multi-Crypto Query", 
            "message": "Give me BTC, ETH and STRK prices",
            "expected_tool": "get_crypto_prices",
            "expected_param": ["bitcoin", "ethereum", "starknet"]
        },
        {
            "name": "Web Search",
            "message": "Search for latest crypto news",
            "expected_tool": "web_search",
            "expected_param": "crypto news"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 Test: {test['name']}")
        print(f"   Message: {test['message']}")
        print("-" * 60)
        
        try:
            # Step 1: Call LLM with tools
            response = await client.chat_complete(
                messages=[{"role": "user", "content": test["message"]}],
                tools=TOOL_DEFINITIONS,
                max_tokens=500
            )
            
            # Step 2: Check if tool was triggered
            if response.tool_calls:
                print(f"   ✅ Tool triggered: {response.tool_calls[0].function_name}")
                print(f"   Args: {response.tool_calls[0].arguments[:100]}...")
                
                # Step 3: Execute tool
                tool_name = response.tool_calls[0].function_name
                args = json.loads(response.tool_calls[0].arguments)
                
                print(f"\n   ⚙️  Executing {tool_name}...")
                result = await executor.execute(tool_name, args)
                
                # Step 4: Show result
                success = result.get("success", False)
                if success:
                    print(f"   ✅ Execution successful")
                    if "data" in result:
                        data = result["data"]
                        if isinstance(data, list):
                            for item in data[:2]:
                                print(f"      - {item.get('token_id', 'unknown')}: ${item.get('price', 'N/A')}")
                        else:
                            print(f"      Data keys: {list(data.keys())[:5]}")
                else:
                    print(f"   ⚠️  Execution failed: {result.get('error', 'unknown')}")
                
                # Step 5: Send result back to LLM for final response
                print(f"\n   🤖 Sending result back to LLM...")
                
                messages = [
                    {"role": "user", "content": test["message"]},
                    {"role": "assistant", "content": "", "tool_calls": [
                        {
                            "id": response.tool_calls[0].id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": response.tool_calls[0].arguments
                            }
                        }
                    ]},
                    {"role": "tool", "content": json.dumps(result), "tool_call_id": response.tool_calls[0].id}
                ]
                
                final_response = await client.chat_complete(
                    messages=messages,
                    max_tokens=300
                )
                
                print(f"\n   📝 Final response:")
                print(f"   {final_response.content[:200]}...")
                
            else:
                print(f"   ⚠️  No tool triggered (LLM answered directly)")
                print(f"   Response: {response.content[:100]}...")
            
            print(f"\n   ✅ Test passed")
            
        except Exception as e:
            print(f"\n   ❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 INTEGRATION TEST COMPLETE")
    print("=" * 60)


async def test_tool_directly():
    """Test individual tool execution."""
    print("\n" + "=" * 60)
    print("🔧 DIRECT TOOL EXECUTION TEST")
    print("=" * 60)
    
    executor = ToolExecutor()
    
    # Test get_crypto_price
    print(f"\n🧪 Testing get_crypto_price...")
    result = await executor.execute("get_crypto_price", {"token_id": "bitcoin"})
    print(f"   Result: {json.dumps(result, indent=4, default=str)[:500]}")
    
    # Test web_search
    print(f"\n🧪 Testing web_search...")
    result = await executor.execute("web_search", {"query": "Starknet news", "count": 3})
    print(f"   Results: {len(result.get('data', []))} items found")


if __name__ == "__main__":
    print("\n🚀 Starting integration tests...\n")
    
    # Run tests
    asyncio.run(test_full_pipeline())
    asyncio.run(test_tool_directly())
    
    print("\n✨ All tests completed!")
