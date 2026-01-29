#!/usr/bin/env python3
"""
nodriver Executor for X/Twitter Automation
Works in 1 tab, persistent session, no extension clicks needed.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import nodriver as nd
except ImportError:
    print("Error: nodriver not installed")
    print("Run: pip install nodriver")
    sys.exit(1)

CONFIG_FILE = Path(__file__).parent / "config.json"
PROFILE_FILE = Path("/home/wner/clawdbot/skills/style-learner/data/profiles/style_profile.json")


class XExecutor:
    def __init__(self):
        self.browser = None
        self.tab = None
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
        return {
            "headless": False,
            "user_data_dir": "~/.config/chrome/default",
            "cookie_file": None
        }
    
    async def start(self):
        """Start browser and navigate to X"""
        print("🚀 Starting nodriver...")
        
        self.browser = await nd.start(
            headless=self.config.get("headless", False),
            user_data_dir=self.config.get("user_data_dir")
        )
        
        # Create new tab at X home
        self.tab = await self.browser.get("https://x.com/home")
        
        print("✓ Browser started. Tab ready at x.com")
        print("📝 Commands: reply <url> <text>, quote <url> <text>, like <url>, tweet <text>, quit")
        
        return self
    
    async def close(self):
        if self.browser:
            self.browser.stop()
            print("👋 Browser closed")
    
    async def wait_for_load(self, selector: str, timeout: int = 10):
        """Wait for element to load"""
        try:
            await asyncio.sleep(2)  # Let page settle
            return True
        except:
            return False
    
    async def reply(self, url: str, text: str):
        """Post a reply"""
        print(f"🔗 Opening: {url}")
        await self.tab.get(url)
        await asyncio.sleep(3)
        
        # Click reply button
        try:
            reply_btn = await self.tab.select('button[data-testid="reply"]')
            await reply_btn.click()
            await asyncio.sleep(1)
            
            # Type in textarea
            textarea = await self.tab.select('div[data-testid="tweetTextarea_0"]')
            await textarea.clear()
            await textarea.send_keys(text)
            await asyncio.sleep(1)
            
            # Click post
            post_btn = await self.tab.select('button[data-testid="tweetButton"]')
            await post_btn.click()
            
            print(f"✓ Reply posted: {text[:50]}...")
            return True
        except Exception as e:
            print(f"✗ Reply failed: {e}")
            return False
    
    async def quote(self, url: str, text: str):
        """Post a quote tweet"""
        print(f"🔗 Opening: {url}")
        await self.tab.get(url)
        await asyncio.sleep(3)
        
        try:
            # Click share/quote
            share_btn = await self.tab.select('button[data-testid="shareButton"]')
            await share_btn.click()
            await asyncio.sleep(1)
            
            quote_btn = await self.tab.select('div[role="menuitem"]', timeout=5)
            # Find quote option
            async for item in self.tab.query_selector_all('div[role="menuitem"]'):
                if "quote" in (await item.text).lower():
                    await item.click()
                    break
            await asyncio.sleep(1)
            
            # Type quote text
            textarea = await self.tab.select('div[data-testid="tweetTextarea_0"]')
            await textarea.clear()
            await textarea.send_keys(text)
            await asyncio.sleep(1)
            
            # Post
            post_btn = await self.tab.select('button[data-testid="tweetButton"]')
            await post_btn.click()
            
            print(f"✓ Quote posted: {text[:50]}...")
            return True
        except Exception as e:
            print(f"✗ Quote failed: {e}")
            return False
    
    async def like(self, url: str):
        """Like a tweet"""
        print(f"🔗 Opening: {url}")
        await self.tab.get(url)
        await asyncio.sleep(2)
        
        try:
            like_btn = await self.tab.select('button[data-testid="like"]')
            await like_btn.click()
            print("✓ Liked")
            return True
        except Exception as e:
            print(f"✗ Like failed: {e}")
            return False
    
    async def tweet(self, text: str):
        """Post original tweet"""
        try:
            # Click tweet box on home
            tweet_btn = await self.tab.select('div[data-testid="tweetTextarea_0"]')
            await tweet_btn.click()
            await asyncio.sleep(1)
            
            # Type
            await self.tab.send_keys(text)
            await asyncio.sleep(1)
            
            # Post
            post_btn = await self.tab.select('button[data-testid="tweetButton"]')
            await post_btn.click()
            
            print(f"✓ Tweet posted: {text[:50]}...")
            return True
        except Exception as e:
            print(f"✗ Tweet failed: {e}")
            return False


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="X/Twitter Automation via nodriver")
    parser.add_argument("command", choices=["reply", "quote", "like", "tweet"], 
                       help="Action to perform")
    parser.add_argument("--url", help="Tweet URL (for reply/quote/like)")
    parser.add_argument("--text", help="Text content")
    
    args = parser.parse_args()
    
    executor = await XExecutor().start()
    
    try:
        if args.command == "reply" and args.url and args.text:
            await executor.reply(args.url, args.text)
        elif args.command == "quote" and args.url and args.text:
            await executor.quote(args.url, args.text)
        elif args.command == "like" and args.url:
            await executor.like(args.url)
        elif args.command == "tweet" and args.text:
            await executor.tweet(args.text)
        else:
            print("Usage:")
            print("  python x_executor.py reply --url <tweet_url> --text <reply>")
            print("  python x_executor.py quote --url <tweet_url> --text <quote>")
            print("  python x_executor.py like --url <tweet_url>")
            print("  python x_executor.py tweet --text <content>")
            
            # Interactive mode
            print("\n" + "="*50)
            print("INTERACTIVE MODE")
            print("="*50)
            
            while True:
                cmd = input("\n> ").strip()
                if cmd in ["quit", "exit", "q"]:
                    break
                parts = cmd.split()
                if not parts:
                    continue
                
                if parts[0] == "reply" and len(parts) >= 3:
                    url = parts[1]
                    text = " ".join(parts[2:])
                    await executor.reply(url, text)
                elif parts[0] == "quote" and len(parts) >= 3:
                    url = parts[1]
                    text = " ".join(parts[2:])
                    await executor.quote(url, text)
                elif parts[0] == "like" and len(parts) >= 2:
                    await executor.like(parts[1])
                elif parts[0] == "tweet" and len(parts) >= 2:
                    await executor.tweet(" ".join(parts[1:]))
                else:
                    print("Commands: reply <url> <text>, quote <url> <text>, like <url>, tweet <text>, quit")
    finally:
        await executor.close()


if __name__ == "__main__":
    asyncio.run(main())
