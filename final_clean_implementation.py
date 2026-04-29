"""
FINAL CLEAN IMPLEMENTATION: Claude Code Tool Selection (Simplified)
===================================================================

This is a clean, simplified implementation of Claude Code's tool selection system
that closely follows the original architecture but removes REPL/VM complexity.

Key Features:
- ✅ Tool registration and metadata
- ✅ Mode-based filtering (NORMAL, SIMPLE, COORDINATOR)
- ✅ MCP tool integration
- ✅ Tool pool assembly and deduplication
- ✅ Tool search for large tool sets
- ❌ No REPL/VM execution (kept simple)
- ❌ No permission system (removed for clarity)

Architecture Overview:
1. ToolPool - Central registry and filtering
2. ExecutionContext - Defines execution mode
3. Tool assembly - Merges built-in + MCP tools
4. Runtime lookup - findToolByName for execution

This matches the core flow from src/tools.ts but simplified.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Set, Dict
from abc import ABC, abstractmethod


@dataclass
class Tool:
    """Tool interface matching src/Tool.ts"""
    name: str
    description: str
    callable: Callable
    search_hint: str = ""           # For tool search
    aliases: Optional[List[str]] = None
    enabled: bool = True
    is_mcp: bool = False            # Is this from MCP server?
    mcp_server: Optional[str] = None


class ExecutionMode(Enum):
    """Execution modes from src/tools.ts"""
    NORMAL = "normal"              # Full tool set
    SIMPLE = "simple"              # Minimal tools only
    COORDINATOR = "coordinator"    # Orchestration mode


@dataclass
class ExecutionContext:
    """Execution context - simplified, no permissions"""
    mode: ExecutionMode
    enable_coordinator: bool = False


class ToolPool:
    """
    The complete tool selection system.

    This implements the core architecture from src/tools.ts:
    - getAllBaseTools() → builtin_tools
    - getTools() → mode filtering
    - assembleToolPool() → merge + deduplicate
    - getMergedTools() → for token counting
    - findToolByName() → runtime lookup
    """

    def __init__(self):
        self.builtin_tools: List[Tool] = []
        self.mcp_tools: List[Tool] = []
        self.simple_mode_tools: Set[str] = {"bash", "file_read", "file_edit"}

    # ========== REGISTRATION ==========

    def register_builtin_tool(self, tool: Tool) -> None:
        """Register a built-in tool (like getAllBaseTools)"""
        tool.is_mcp = False
        self.builtin_tools.append(tool)

    def register_mcp_tool(self, tool: Tool, server: str) -> None:
        """Register an MCP tool from a server"""
        tool.is_mcp = True
        tool.mcp_server = server
        self.mcp_tools.append(tool)

    # ========== MODE FILTERING ==========

    def apply_mode_filtering(
        self, tools: List[Tool], context: ExecutionContext
    ) -> List[Tool]:
        """
        Apply mode-specific filtering (from getTools in tools.ts)
        """

        if context.mode == ExecutionMode.SIMPLE:
            # Simple mode: minimal tool set
            tools = [
                t for t in tools
                if t.name in self.simple_mode_tools
            ]

            # Add coordinator tools if enabled
            if context.enable_coordinator:
                for name in ["agent", "task_stop"]:
                    tool = next((
                        t for t in self.builtin_tools
                        if t.name == name
                    ), None)
                    if tool:
                        tools.append(tool)

        elif context.mode == ExecutionMode.COORDINATOR:
            # Coordinator mode: specialized set
            tools = [
                t for t in tools
                if t.name in {"agent", "task_stop"}
            ]

        # NORMAL mode: no additional filtering
        return tools

    # ========== MAIN FILTERING FUNCTION ==========

    def get_tools(self, context: ExecutionContext) -> List[Tool]:
        """
        Get filtered built-in tools (like getTools in tools.ts)

        Order: enabled tools → mode filtering
        """
        # Start with enabled tools
        tools = [t for t in self.builtin_tools if t.enabled]

        # Apply mode filtering
        tools = self.apply_mode_filtering(tools, context)

        return tools

    def get_mcp_tools_filtered(self) -> List[Tool]:
        """Get enabled MCP tools (simplified, no permission filtering)"""
        return [t for t in self.mcp_tools if t.enabled]

    # ========== TOOL POOL ASSEMBLY ==========

    def assemble_tool_pool(self, context: ExecutionContext) -> List[Tool]:
        """
        Assemble final tool pool for model (like assembleToolPool in tools.ts)

        Rules:
        1. Get filtered built-in tools
        2. Get filtered MCP tools
        3. Deduplicate by name (built-ins win)
        4. Sort for cache stability
        """
        builtin = self.get_tools(context)
        mcp = self.get_mcp_tools_filtered()

        # Deduplicate: built-in tools take precedence
        builtin_names = {t.name for t in builtin}
        mcp_unique = [t for t in mcp if t.name not in builtin_names]

        # Combine and sort
        combined = builtin + mcp_unique
        combined.sort(key=lambda t: t.name)

        return combined

    def get_merged_tools(self, context: ExecutionContext) -> List[Tool]:
        """
        Get ALL tools for token counting (like getMergedTools)
        Used to determine if tool deferral needed
        """
        builtin = self.get_tools(context)
        mcp = self.get_mcp_tools_filtered()
        return builtin + mcp

    # ========== RUNTIME TOOL LOOKUP ==========

    def find_tool_by_name(
        self, tools: List[Tool], name: str
    ) -> Optional[Tool]:
        """
        Find tool by name or alias (like findToolByName in Tool.ts)
        Called when model tries to use a tool
        """
        for tool in tools:
            if tool.name == name:
                return tool
            if tool.aliases and name in tool.aliases:
                return tool
        return None

    # ========== TOOL SEARCH ==========

    def search_tools(
        self, tools: List[Tool], query: str
    ) -> List[Tool]:
        """
        Search tools by keyword (like ToolSearchTool)
        Used when there are too many tools for system prompt
        """
        query_lower = query.lower()
        results = []

        for tool in tools:
            # Match on name, description, search_hint, or aliases
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower() or
                query_lower in tool.search_hint.lower()):
                results.append(tool)
            elif tool.aliases:
                for alias in tool.aliases:
                    if query_lower in alias.lower():
                        results.append(tool)
                        break

        return results

    # ========== STATISTICS ==========

    def should_defer_tools(self, context: ExecutionContext) -> bool:
        """
        Check if tools should be deferred (use tool search instead)
        Based on token count estimation
        """
        merged = self.get_merged_tools(context)
        return len(merged) > 50  # Arbitrary threshold

    def get_stats(self, context: ExecutionContext) -> Dict:
        """Get tool pool statistics"""
        builtin = self.get_tools(context)
        mcp = self.get_mcp_tools_filtered()
        merged = self.get_merged_tools(context)

        return {
            "builtin_tools": len(builtin),
            "mcp_tools": len(mcp),
            "total_merged": len(merged),
            "should_defer": self.should_defer_tools(context),
        }


def create_sample_tools() -> ToolPool:
    """
    Create a sample tool pool with realistic tools
    This demonstrates the registration process
    """
    pool = ToolPool()

    # Built-in tools (like getAllBaseTools returns)
    builtin_tools = [
        Tool("bash", "Execute shell commands", lambda cmd: f"[Bash] {cmd}",
             "shell terminal command execute", ["shell", "exec"]),
        Tool("file_read", "Read file contents", lambda path: f"[FileRead] {path}",
             "read view get file content", ["read", "cat"]),
        Tool("file_edit", "Edit or create files", lambda path, content: f"[FileEdit] {path}",
             "write edit create modify file", ["write", "edit"]),
        Tool("web_fetch", "Fetch web content", lambda url: f"[WebFetch] {url}",
             "http get retrieve url web", ["fetch", "http"]),
        Tool("web_search", "Search the web", lambda query: f"[WebSearch] {query}",
             "search find google query web", ["search"]),
        Tool("task_output", "Get task output", lambda: "[TaskOutput]",
             "output result task status", ["result"]),
        Tool("agent", "Call sub-agents", lambda: "[Agent]",
             "delegate spawn subagent help", []),
        Tool("task_stop", "Stop task execution", lambda: "[TaskStop]",
             "stop cancel abort terminate task", ["stop"]),
    ]

    for tool in builtin_tools:
        pool.register_builtin_tool(tool)

    # MCP tools (from external servers)
    mcp_tools = [
        ("git_commit", "Git operations", "git version control commit", "git_server"),
        ("sql_query", "Execute SQL queries", "database query sql execute", "database_server"),
        ("slack_message", "Send Slack messages", "slack message chat send", "slack_server"),
        ("aws_s3", "Access AWS S3", "aws cloud storage s3 bucket", "aws_server"),
    ]

    for name, desc, hint, server in mcp_tools:
        pool.register_mcp_tool(
            Tool(name, desc, lambda: f"[{name.upper()}]", hint),
            server
        )

    return pool


def demonstrate_tool_selection():
    """
    Demonstrate the complete tool selection flow
    """
    print("=" * 80)
    print("FINAL CLEAN IMPLEMENTATION: Claude Code Tool Selection")
    print("=" * 80)
    print()

    # Create tool pool
    pool = create_sample_tools()
    print(f"✓ Created tool pool with {len(pool.builtin_tools)} built-in + {len(pool.mcp_tools)} MCP tools")
    print()

    # Test different execution contexts
    contexts = [
        ("NORMAL Mode", ExecutionContext(ExecutionMode.NORMAL)),
        ("SIMPLE Mode", ExecutionContext(ExecutionMode.SIMPLE)),
        ("COORDINATOR Mode", ExecutionContext(ExecutionMode.COORDINATOR)),
        ("SIMPLE + Coordinator", ExecutionContext(ExecutionMode.SIMPLE, enable_coordinator=True)),
    ]

    for title, context in contexts:
        print("-" * 80)
        print(f"🧪 {title}")
        print("-" * 80)

        # Get final tool pool
        tools = pool.assemble_tool_pool(context)
        stats = pool.get_stats(context)

        print(f"Available tools: {len(tools)}")
        print(f"Built-in: {stats['builtin_tools']}, MCP: {stats['mcp_tools']}")
        print(f"Should defer tools? {stats['should_defer']}")
        print()

        # Show tools by type
        builtin_tools = [t for t in tools if not t.is_mcp]
        mcp_tools = [t for t in tools if t.is_mcp]

        if builtin_tools:
            print("Built-in tools:")
            for tool in sorted(builtin_tools, key=lambda t: t.name):
                print(f"  • {tool.name}: {tool.description}")
            print()

        if mcp_tools:
            print("MCP tools:")
            for tool in sorted(mcp_tools, key=lambda t: t.name):
                print(f"  • {tool.name} ({tool.mcp_server}): {tool.description}")
            print()

    # Demonstrate tool lookup
    print("-" * 80)
    print("🔍 Tool Lookup Demonstration")
    print("-" * 80)

    normal_context = ExecutionContext(ExecutionMode.NORMAL)
    tools = pool.assemble_tool_pool(normal_context)

    lookups = ["bash", "shell", "read", "nonexistent"]
    for name in lookups:
        tool = pool.find_tool_by_name(tools, name)
        result = f"{tool.name} ({tool.description})" if tool else "Not found"
        print(f"find_tool_by_name('{name}') → {result}")

    print()

    # Demonstrate tool search
    print("-" * 80)
    print("🔎 Tool Search Demonstration")
    print("-" * 80)

    all_tools = pool.get_merged_tools(normal_context)
    search_queries = ["file", "web", "git", "database"]

    for query in search_queries:
        results = pool.search_tools(all_tools, query)
        print(f"Search '{query}': {len(results)} results")
        for tool in results[:3]:  # Show first 3
            print(f"  • {tool.name}: {tool.description}")
        if len(results) > 3:
            print(f"  ... and {len(results) - 3} more")
        print()

    print("=" * 80)
    print("🎯 ARCHITECTURE SUMMARY")
    print("=" * 80)
    print("""
This implementation closely follows Claude Code's tool selection:

1. REGISTRATION: Tools registered as built-in or MCP
2. FILTERING: Mode-based filtering (no permissions for simplicity)
3. ASSEMBLY: assembleToolPool() merges and deduplicates
4. LOOKUP: findToolByName() for runtime tool calls
5. SEARCH: ToolSearchTool behavior for large tool sets

Key differences from full Claude Code:
- ❌ No REPL/VM execution (kept simple)
- ❌ No permission system (removed for clarity)
- ✅ Core tool selection logic preserved
- ✅ MCP integration maintained
- ✅ Tool pool assembly matches original

The system is production-ready for understanding tool selection!
    """)


if __name__ == "__main__":
    demonstrate_tool_selection()
</content>
<parameter name="filePath">C:\Users\migue\Desktop\tool_selection_exercise\final_clean_implementation.py