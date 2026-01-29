#!/usr/bin/env python3
"""
llm_client.py - Universal LLM client with fallback support
Supports: MiniMax, OpenAI, Anthropic, Ollama (local)
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Generator
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('llm-client')


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    latency_ms: float = 0
    success: bool = True
    error: str = None


class LLMProvider(ABC):
    """Abstract base for LLM providers."""
    
    @abstractmethod
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass


class MiniMaxProvider(LLMProvider):
    """MiniMax API provider (configured in Clawdbot)."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = self.config.get('model', 'MiniMax-M2.1')
        self.api_key = os.environ.get('MINIMAX_API_KEY', '')
        self.base_url = self.config.get('base_url', 'https://api.minimax.chat/v1')
        
    def is_available(self) -> bool:
        # MiniMax is default in Clawdbot, assume available
        return True
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Use clawdbot message for MiniMax."""
        import subprocess
        
        start = time.time()
        
        # Format messages into single prompt
        prompt = self._format_messages(messages)
        
        try:
            # Use clawdbot's configured model
            result = subprocess.run(
                ['clawdbot', 'message', '--raw', prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            latency = (time.time() - start) * 1000
            
            if result.returncode == 0:
                return LLMResponse(
                    content=result.stdout.strip(),
                    model=self.model,
                    provider='minimax',
                    latency_ms=latency
                )
            else:
                return LLMResponse(
                    content='',
                    model=self.model,
                    provider='minimax',
                    success=False,
                    error=result.stderr
                )
                
        except Exception as e:
            return LLMResponse(
                content='',
                model=self.model,
                provider='minimax',
                success=False,
                error=str(e)
            )
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format messages for single prompt."""
        parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                parts.append(f"[System Instructions]\n{content}\n")
            elif role == 'assistant':
                parts.append(f"[Previous Response]\n{content}\n")
            else:
                parts.append(f"[User]\n{content}\n")
        return '\n'.join(parts)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = self.config.get('model', 'gpt-4o-mini')
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.base_url = 'https://api.openai.com/v1/chat/completions'
        
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                content='', model=self.model, provider='openai',
                success=False, error='No API key'
            )
        
        start = time.time()
        
        payload = {
            'model': self.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', 4096),
            'temperature': kwargs.get('temperature', 0.7)
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode('utf-8'))
            
            latency = (time.time() - start) * 1000
            content = result['choices'][0]['message']['content']
            tokens = result.get('usage', {}).get('total_tokens', 0)
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider='openai',
                tokens_used=tokens,
                latency_ms=latency
            )
            
        except Exception as e:
            return LLMResponse(
                content='', model=self.model, provider='openai',
                success=False, error=str(e)
            )


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = self.config.get('model', 'llama3.1:8b')
        self.base_url = self.config.get('base_url', 'http://localhost:11434')
        
    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f'{self.base_url}/api/tags')
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except:
            return False
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        start = time.time()
        
        # Convert to Ollama format
        prompt = self._format_messages(messages)
        
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': kwargs.get('temperature', 0.7),
                'num_predict': kwargs.get('max_tokens', 4096)
            }
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f'{self.base_url}/api/generate',
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read().decode('utf-8'))
            
            latency = (time.time() - start) * 1000
            
            return LLMResponse(
                content=result.get('response', ''),
                model=self.model,
                provider='ollama',
                latency_ms=latency
            )
            
        except Exception as e:
            return LLMResponse(
                content='', model=self.model, provider='ollama',
                success=False, error=str(e)
            )
    
    def _format_messages(self, messages: List[Dict]) -> str:
        parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                parts.append(f"<|system|>\n{content}</s>")
            elif role == 'assistant':
                parts.append(f"<|assistant|>\n{content}</s>")
            else:
                parts.append(f"<|user|>\n{content}</s>")
        parts.append("<|assistant|>")
        return '\n'.join(parts)


class AnthropicProvider(LLMProvider):
    """Anthropic API provider (when available)."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = self.config.get('model', 'claude-sonnet-4-20250514')
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.base_url = 'https://api.anthropic.com/v1/messages'
        
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def complete(self, messages: List[Dict], **kwargs) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                content='', model=self.model, provider='anthropic',
                success=False, error='No API key'
            )
        
        start = time.time()
        
        # Separate system message
        system = ''
        chat_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                system = msg['content']
            else:
                chat_messages.append(msg)
        
        payload = {
            'model': self.model,
            'max_tokens': kwargs.get('max_tokens', 4096),
            'messages': chat_messages
        }
        if system:
            payload['system'] = system
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.base_url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01'
                }
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode('utf-8'))
            
            latency = (time.time() - start) * 1000
            content = result['content'][0]['text']
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider='anthropic',
                latency_ms=latency
            )
            
        except Exception as e:
            return LLMResponse(
                content='', model=self.model, provider='anthropic',
                success=False, error=str(e)
            )


class LLMClient:
    """Universal LLM client with fallback chain."""
    
    PROVIDERS = {
        'minimax': MiniMaxProvider,
        'openai': OpenAIProvider,
        'ollama': OllamaProvider,
        'anthropic': AnthropicProvider
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.providers = self._init_providers()
        self.stats = {
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'by_provider': {}
        }
        
    def _default_config(self) -> Dict:
        return {
            'primary': 'minimax',
            'fallback': ['openai', 'ollama'],
            'max_retries': 3,
            'retry_delay': 2
        }
    
    def _init_providers(self) -> Dict[str, LLMProvider]:
        providers = {}
        provider_config = self.config.get('providers', {})
        
        for name, cls in self.PROVIDERS.items():
            providers[name] = cls(provider_config.get(name, {}))
        
        return providers
    
    def complete(self, 
                 messages: List[Dict],
                 system: str = None,
                 **kwargs) -> LLMResponse:
        """Complete with automatic fallback."""
        
        # Prepend system message if provided
        if system:
            messages = [{'role': 'system', 'content': system}] + messages
        
        self.stats['requests'] += 1
        
        # Try primary provider first
        primary = self.config.get('primary', 'minimax')
        response = self._try_provider(primary, messages, **kwargs)
        
        if response.success:
            self.stats['successes'] += 1
            return response
        
        # Try fallback chain
        fallbacks = self.config.get('fallback', [])
        for provider_name in fallbacks:
            logger.info(f"Trying fallback: {provider_name}")
            response = self._try_provider(provider_name, messages, **kwargs)
            
            if response.success:
                self.stats['successes'] += 1
                return response
        
        # All failed
        self.stats['failures'] += 1
        return LLMResponse(
            content='',
            model='none',
            provider='none',
            success=False,
            error='All providers failed'
        )
    
    def _try_provider(self, 
                      name: str, 
                      messages: List[Dict],
                      **kwargs) -> LLMResponse:
        """Try a single provider with retries."""
        provider = self.providers.get(name)
        
        if not provider:
            return LLMResponse(
                content='', model='none', provider=name,
                success=False, error=f'Unknown provider: {name}'
            )
        
        if not provider.is_available():
            return LLMResponse(
                content='', model='none', provider=name,
                success=False, error=f'Provider not available: {name}'
            )
        
        max_retries = self.config.get('max_retries', 3)
        retry_delay = self.config.get('retry_delay', 2)
        
        for attempt in range(max_retries):
            response = provider.complete(messages, **kwargs)
            
            if response.success:
                # Update stats
                if name not in self.stats['by_provider']:
                    self.stats['by_provider'][name] = {'success': 0, 'fail': 0}
                self.stats['by_provider'][name]['success'] += 1
                return response
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
        
        if name not in self.stats['by_provider']:
            self.stats['by_provider'][name] = {'success': 0, 'fail': 0}
        self.stats['by_provider'][name]['fail'] += 1
        
        return response
    
    def get_stats(self) -> Dict:
        """Get usage statistics."""
        return self.stats
    
    def check_providers(self) -> Dict[str, bool]:
        """Check availability of all providers."""
        return {
            name: provider.is_available()
            for name, provider in self.providers.items()
        }


# Convenience function
def ask(prompt: str, system: str = None, **kwargs) -> str:
    """Simple interface to ask LLM."""
    client = LLMClient()
    messages = [{'role': 'user', 'content': prompt}]
    response = client.complete(messages, system=system, **kwargs)
    return response.content if response.success else f"Error: {response.error}"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='LLM Client')
    parser.add_argument('--check', action='store_true', help='Check providers')
    parser.add_argument('--ask', help='Ask a question')
    parser.add_argument('--provider', help='Specific provider')
    
    args = parser.parse_args()
    
    client = LLMClient()
    
    if args.check:
        print(json.dumps(client.check_providers(), indent=2))
    elif args.ask:
        if args.provider:
            client.config['primary'] = args.provider
            client.config['fallback'] = []
        response = client.complete([{'role': 'user', 'content': args.ask}])
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"Latency: {response.latency_ms:.0f}ms")
        print(f"\n{response.content}")
