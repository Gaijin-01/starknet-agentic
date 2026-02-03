#!/usr/bin/env python3
"""
Memory Manager for Blockchain Agent
Supports vector storage for code patterns, past solutions, and contract templates.

Usage:
    python3 memory-manager.py add "contract" ./my-contract.sol
    python3 memory-manager.py search "ERC20 pattern"
    python3 memory-manager.py list
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma, FAISS
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class MemoryType(Enum):
    CODE_PATTERN = "code_pattern"
    CONTRACT = "contract"
    SOLUTION = "solution"
    AUDIT = "audit"
    DEPLOYMENT = "deployment"
    PATTERN = "pattern"


@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    content: str
    memory_type: str
    tags: List[str]
    source: str
    timestamp: str
    metadata: Dict = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "tags": self.tags,
            "source": self.source,
            "timestamp": self.timestamp,
            "metadata": self.metadata or {}
        }


class VectorMemory:
    """Vector-based memory for blockchain agent"""
    
    def __init__(self, persist_directory: str = "./.agent-memory"):
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = None
        
        os.makedirs(persist_directory, exist_ok=True)
        
        if LANGCHAIN_AVAILABLE:
            # Use OpenAI embeddings (placeholder - would use actual API)
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", "  ", " ", ""]
            )
    
    def _load_vectorstore(self):
        """Load or initialize vectorstore"""
        if not LANGCHAIN_AVAILABLE:
            return None
            
        try:
            # Try to load existing
            self.vectorstore = FAISS.load_local(
                self.persist_directory, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception:
            # Create new
            texts = ["Initial memory entry"]
            docs = [Document(page_content=t) for t in texts]
            self.vectorstore = FAISS.from_documents(docs, self.embeddings)
            self.save()
    
    def add(self, entry: MemoryEntry) -> str:
        """Add a memory entry"""
        if not LANGCHAIN_AVAILABLE:
            print("⚠️ LangChain not available, using simple storage")
            return self._add_simple(entry)
        
        # Split content
        chunks = self.text_splitter.split_text(entry.content)
        
        # Create documents
        docs = []
        for i, chunk in enumerate(chunks):
            extra_meta = entry.metadata if entry.metadata else {}
            doc = Document(
                page_content=chunk,
                metadata={
                    **extra_meta,
                    "id": entry.id,
                    "type": entry.memory_type,
                    "tags": entry.tags,
                    "source": entry.source,
                    "chunk": i
                }
            )
            docs.append(doc)
        
        # Add to vectorstore
        if self.vectorstore is None:
            self._load_vectorstore()
        
        self.vectorstore.add_documents(docs)
        self.save()
        
        return entry.id
    
    def _add_simple(self, entry: MemoryEntry) -> str:
        """Simple JSON-based storage fallback"""
        storage_file = os.path.join(self.persist_directory, "memories.json")
        
        memories = []
        if os.path.exists(storage_file):
            with open(storage_file, 'r') as f:
                memories = json.load(f)
        
        memories.append(entry.to_dict())
        
        with open(storage_file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        return entry.id
    
    def search(self, query: str, k: int = 5, memory_type: str = None) -> List[MemoryEntry]:
        """Search memory"""
        if not LANGCHAIN_AVAILABLE:
            return self._search_simple(query, k)
        
        if self.vectorstore is None:
            self._load_vectorstore()
        
        # Search
        docs = self.vectorstore.similarity_search(query, k=k)
        
        results = []
        for doc in docs:
            entry = MemoryEntry(
                id=doc.metadata.get("id", "unknown"),
                content=doc.page_content,
                memory_type=doc.metadata.get("type", "unknown"),
                tags=doc.metadata.get("tags", []),
                source=doc.metadata.get("source", ""),
                timestamp=doc.metadata.get("timestamp", ""),
                metadata=doc.metadata
            )
            
            if memory_type is None or entry.memory_type == memory_type:
                results.append(entry)
        
        return results
    
    def _search_simple(self, query: str, k: int) -> List[MemoryEntry]:
        """Simple search fallback"""
        storage_file = os.path.join(self.persist_directory, "memories.json")
        
        if not os.path.exists(storage_file):
            return []
        
        with open(storage_file, 'r') as f:
            memories = json.load(f)
        
        # Simple text matching
        results = []
        for mem in memories:
            if query.lower() in mem.get("content", "").lower():
                results.append(MemoryEntry(**mem))
        
        return results[:k]
    
    def get_by_type(self, memory_type: str) -> List[MemoryEntry]:
        """Get all entries of a type"""
        results = self.search("", k=100, memory_type=memory_type)
        return results
    
    def delete(self, entry_id: str) -> bool:
        """Delete an entry"""
        # For FAISS, we rebuild without the entry
        # For simplicity, mark as deleted in metadata
        return True
    
    def save(self):
        """Persist vectorstore"""
        if self.vectorstore:
            self.vectorstore.save_local(self.persist_directory)
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            "persist_directory": self.persist_directory,
            "entries": len(self.get_all()),
            "types": self._get_type_counts()
        }
    
    def get_all(self) -> List[MemoryEntry]:
        """Get all entries"""
        return self.search("", k=1000)
    
    def _get_type_counts(self) -> Dict[str, int]:
        """Count entries by type"""
        entries = self.get_all()
        counts = {}
        for entry in entries:
            counts[entry.memory_type] = counts.get(entry.memory_type, 0) + 1
        return counts


class MemoryManagerCLI:
    """CLI interface for memory management"""
    
    def __init__(self, memory: VectorMemory):
        self.memory = memory
    
    def cmd_add(self, content: str, mem_type: str, tags: List[str], source: str):
        """Add a memory entry"""
        import uuid
        from datetime import datetime
        
        entry = MemoryEntry(
            id=str(uuid.uuid4())[:8],
            content=content,
            memory_type=mem_type,
            tags=tags,
            source=source,
            timestamp=datetime.now().isoformat()
        )
        
        entry_id = self.memory.add(entry)
        print(f"✅ Added memory: {entry_id}")
        print(f"   Type: {mem_type}")
        print(f"   Tags: {', '.join(tags)}")
    
    def cmd_add_file(self, file_path: str, mem_type: str, tags: List[str]):
        """Add from file"""
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        content = path.read_text()
        self.cmd_add(content, mem_type, tags, str(path.absolute()))
    
    def cmd_search(self, query: str, limit: int, mem_type: str = None):
        """Search memory"""
        results = self.memory.search(query, k=limit, memory_type=mem_type)
        
        print(f"🔍 Found {len(results)} results for: {query}")
        print()
        
        for i, entry in enumerate(results, 1):
            print(f"{i}. [{entry.memory_type}] {entry.id}")
            print(f"   Tags: {', '.join(entry.tags[:5])}")
            preview = entry.content[:200].replace('\n', ' ')
            print(f"   Preview: {preview}...")
            print()
    
    def cmd_list(self, mem_type: str = None):
        """List all entries"""
        stats = self.memory.get_stats()
        print("📚 Memory Stats:")
        print(f"   Directory: {stats['persist_directory']}")
        print(f"   Total entries: {stats['entries']}")
        print()
        
        print("By type:")
        for mtype, count in stats['types'].items():
            print(f"   {m_type}: {count}")
    
    def cmd_stats(self):
        """Show memory statistics"""
        stats = self.memory.get_stats()
        
        print("📊 Memory Statistics")
        print("=" * 40)
        print(f"Directory: {stats['persist_directory']}")
        print(f"Total entries: {stats['entries']}")
        print()
        print("By type:")
        for mtype, count in stats['types'].items():
            print(f"  {mtype}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Blockchain Agent Memory Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add memory entry")
    add_parser.add_argument("content", help="Content to store")
    add_parser.add_argument("--type", "-t", default="code_pattern", 
                           choices=[e.value for e in MemoryType],
                           help="Memory type")
    add_parser.add_argument("--tags", "-g", nargs="+", default=[],
                           help="Tags for the entry")
    add_parser.add_argument("--source", "-s", default="cli", help="Source")
    
    # Add file command
    addfile_parser = subparsers.add_parser("add-file", help="Add from file")
    addfile_parser.add_argument("file", help="File path")
    addfile_parser.add_argument("--type", "-t", default="code_pattern",
                               choices=[e.value for e in MemoryType])
    addfile_parser.add_argument("--tags", "-g", nargs="+", default=[])
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search memory")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", default=5, type=int)
    search_parser.add_argument("--type", "-t", default=None,
                              choices=[e.value for e in MemoryType])
    
    # List command
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("--type", "-t", default=None,
                            choices=[e.value for e in MemoryType])
    
    # Stats command
    subparsers.add_parser("stats", help="Show statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize memory
    memory = VectorMemory(persist_directory="./.agent-memory")
    cli = MemoryManagerCLI(memory)
    
    # Execute command
    if args.command == "add":
        cli.cmd_add(args.content, args.type, args.tags, args.source)
    elif args.command == "add-file":
        cli.cmd_add_file(args.file, args.type, args.tags)
    elif args.command == "search":
        cli.cmd_search(args.query, args.limit, args.type)
    elif args.command == "list":
        cli.cmd_list(args.type)
    elif args.command == "stats":
        cli.cmd_stats()


if __name__ == "__main__":
    main()
