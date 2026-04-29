"""
STEP 4: Mode-Based Tool Selection
==================================

Goal: Different execution modes require different tool sets.

Key Concepts:
  - SIMPLE_MODE: Only core tools (bash, file_read, file_edit)
  - REPL_MODE: Virtual machine mode, primitives wrapped by REPL tool
  - COORDINATOR_MODE: Special orchestration mode with Agent/Task tools
  - NORMAL_MODE: Full tool set
  
These modes fundamentally change which tools are available to the model.

This maps to in src/tools.ts:
- The isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE) checks
- isReplModeEnabled() checks  
- feature('COORDINATOR_MODE') checks
- The getTools() function implements mode selection
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional


@dataclass
class Tool:
    """Tool object with metadata"""
    name: str
    description: str
    callable: Callable
    aliases: Optional[List[str]] = None
    enabled: bool = True


class ExecutionMode(Enum):
    """Different execution contexts"""
    NORMAL = "normal"              # Full tool set
    SIMPLE = "simple"              # Minimal tools only
    REPL = "repl"                  # Virtual machine with wrapped tools
    COORDINATOR = "coordinator"    # Orchestration mode


@dataclass
class ExecutionContext:
    """
    Execution context describing how the code should run.
    
    Maps to various environment variables and feature flags in original:
    - process.env.CLAUDE_CODE_SIMPLE
    - process.env.REPL_MODE_ENABLED
    - feature('COORDINATOR_MODE')
    """
    mode: ExecutionMode
    has_repl: bool = False           # Is REPL tool available?
    enable_coordinator: bool = False  # Is Coordinator Mode enabled?


class ModeAwareRegistry:
    """
    Tool Registry that changes tool availability based on execution mode.
    
    In the original, this logic lives in the getTools() function.
    """
    
    def __init__(self):
        self.all_tools: List[Tool] = []
        self.simple_mode_tools: Set[str] = {"bash", "file_read", "file_edit"}
        self.repl_only_hidden_tools: Set[str] = {"bash", "file_read", "file_edit"}
        
    def register(self, tool: Tool) -> None:
        """Register a tool"""
        self.all_tools.append(tool)
    
    def get_all_enabled_tools(self) -> List[Tool]:
        """Get all enabled tools"""
        return [t for t in self.all_tools if t.enabled]
    
    def find_tool_by_name(self, name: str) -> Optional[Tool]:
        """Find tool by name or alias"""
        for tool in self.all_tools:
            if tool.name == name:
                return tool
            if tool.aliases and name in tool.aliases:
                return tool
        return None
    
    def get_tools_for_context(
        self, context: ExecutionContext
    ) -> List[Tool]:
        """
        Get tools appropriate for the execution context.
        
        This is THE KEY FUNCTION that incorporates mode-based logic.
        Maps to: getTools() in tools.ts
        
        Order of operations matches the original:
        1. Check execution mode
        2. Apply mode-specific filtering
        3. Remove REPL-only-hidden-tools if REPL is enabled
        """
        
        # SIMPLE MODE: Very restricted tool set
        if context.mode == ExecutionMode.SIMPLE:
            tools = [
                t for t in self.get_all_enabled_tools()
                if t.name in self.simple_mode_tools
            ]
            
            # If REPL is available in simple mode, use REPL instead of raw tools
            if context.has_repl:
                # User asked for simple mode AND repl: return just REPL tool
                repl_tool = self.find_tool_by_name("repl")
                if repl_tool:
                    tools = [repl_tool]
            
            # Add coordinator tools if in coordinator mode too
            if context.enable_coordinator:
                # Coordinator needs Task and Agent tools
                for name in ["agent", "task_stop"]:
                    tool = self.find_tool_by_name(name)
                    if tool:
                        tools.append(tool)
            
            return tools
        
        # REPL MODE: Standard tools hidden, wrapped by REPL
        elif context.mode == ExecutionMode.REPL:
            # Get all enabled tools to start
            tools = self.get_all_enabled_tools()
            
            # Remove primitive tools that are wrapped by REPL
            # (user accesses them INSIDE the REPL VM)
            tools = [
                t for t in tools
                if t.name not in self.repl_only_hidden_tools
            ]
            
            return tools
        
        # COORDINATOR MODE: Special orchestration tool set
        elif context.mode == ExecutionMode.COORDINATOR:
            # Coordinator primarily needs Agent and Task tools
            coordinator_tools = {"agent", "task_stop"}
            
            tools = [
                t for t in self.get_all_enabled_tools()
                if t.name in coordinator_tools
            ]
            
            return tools
        
        # NORMAL MODE (default): Full tool set minus special internal tools
        else:  # ExecutionMode.NORMAL
            tools = self.get_all_enabled_tools()
            return tools


def main():
    print("=" * 60)
    print("STEP 4: Mode-Based Tool Selection")
    print("=" * 60)
    print()
    
    # Create registry and register tools
    registry = ModeAwareRegistry()
    
    # Core tools
    registry.register(Tool("bash", "Execute shell commands", lambda: "[Bash]"))
    registry.register(Tool("file_read", "Read files", lambda: "[FileRead]"))
    registry.register(Tool("file_edit", "Edit files", lambda: "[FileEdit]"))
    
    # Extended tools
    registry.register(Tool("web_fetch", "Fetch from web", lambda: "[WebFetch]"))
    registry.register(Tool("web_search", "Search web", lambda: "[WebSearch]"))
    registry.register(Tool("task_output", "Get task output", lambda: "[TaskOutput]"))
    
    # Special tools
    registry.register(Tool("agent", "Call sub-agents", lambda: "[Agent]"))
    registry.register(Tool("task_stop", "Stop a task", lambda: "[TaskStop]"))
    registry.register(Tool("repl", "Virtual machine REPL", lambda: "[REPL]"))
    
    print(f"Total tools registered: {len(registry.all_tools)}")
    print()
    
    # Helper function
    def show_tools(title, context):
        tools = registry.get_tools_for_context(context)
        print(f"{title}:")
        print(f"  Mode: {context.mode.value}")
        print(f"  Tools available ({len(tools)}):")
        for tool in sorted(tools, key=lambda t: t.name):
            print(f"    - {tool.name}")
        print()
    
    # Example 1: Normal mode
    print("-" * 60)
    print("EXAMPLE 1: Normal Mode (default)")
    print("-" * 60)
    
    normal_context = ExecutionContext(
        mode=ExecutionMode.NORMAL,
    )
    show_tools("Normal Mode", normal_context)
    
    # Example 2: Simple mode
    print("-" * 60)
    print("EXAMPLE 2: Simple Mode (--simple flag)")
    print("-" * 60)
    
    simple_context = ExecutionContext(
        mode=ExecutionMode.SIMPLE,
    )
    show_tools("Simple Mode", simple_context)
    
    print("Note: Only bash, file_read, file_edit available")
    print("      This is for constrained environments")
    print()
    
    # Example 3: Simple mode + REPL
    print("-" * 60)
    print("EXAMPLE 3: Simple Mode + REPL")
    print("-" * 60)
    
    simple_repl_context = ExecutionContext(
        mode=ExecutionMode.SIMPLE,
        has_repl=True,  # REPL tool is available
    )
    show_tools("Simple Mode + REPL", simple_repl_context)
    
    print("Note: Plain tools replaced with REPL")
    print("      User runs code inside the REPL VM")
    print()
    
    # Example 4: Normal mode + REPL
    print("-" * 60)
    print("EXAMPLE 4: Normal Mode + REPL")
    print("-" * 60)
    
    normal_repl_context = ExecutionContext(
        mode=ExecutionMode.REPL,
        has_repl=True,
    )
    show_tools("Normal Mode + REPL", normal_repl_context)
    
    print("Note: Primitive tools hidden (wrapped by REPL)")
    print("      But extended tools still available for use")
    print()
    
    # Example 5: Coordinator mode
    print("-" * 60)
    print("EXAMPLE 5: Coordinator Mode (orchestration)")
    print("-" * 60)
    
    coordinator_context = ExecutionContext(
        mode=ExecutionMode.COORDINATOR,
        enable_coordinator=True,
    )
    show_tools("Coordinator Mode", coordinator_context)
    
    print("Note: Specialized for multi-agent coordination")
    print("      Only Agent and Task tools available")
    print()
    
    # Example 6: Simple mode + coordinator
    print("-" * 60)
    print("EXAMPLE 6: Simple Mode + Coordinator Mode")
    print("-" * 60)
    
    simple_coordinator_context = ExecutionContext(
        mode=ExecutionMode.SIMPLE,
        enable_coordinator=True,
    )
    show_tools("Simple + Coordinator", simple_coordinator_context)
    
    print("Note: Simple mode tools + coordinator tools")
    print()
    
    print("=" * 60)
    print("KEY INSIGHTS FROM STEP 4:")
    print("=" * 60)
    print("""
1. Execution MODE fundamentally changes the tool set
2. SIMPLE_MODE: Minimal tools for constrained environments
3. REPL_MODE: Wraps primitives in Virtual Machine
4. COORDINATOR_MODE: Specialized for multi-agent work
5. Modes can COMBINE (simple + coordinator, normal + repl)

Tool Availability by Mode:
  Mode               Tool Set
  ----               --------
  NORMAL             All enabled tools
  SIMPLE             bash, file_read, file_edit
  REPL               All except {bash, file_read, file_edit}
  COORDINATOR        agent, task_stop

Comparison to Original:
  - ExecutionMode enum: ✓ (maps to various env checks)
  - Mode-based filtering: ✓ (the big if/elif in getTools())
  - Simple mode check: ✓ (CLAUDE_CODE_SIMPLE)
  - REPL mode check: ✓ (isReplModeEnabled())
  - Coordinator check: ✓ (feature('COORDINATOR_MODE'))
  - Mode combination: ✓ (multiple checks at once)

Next: We'll merge built-in tools with MCP tools and create the FULL SYSTEM!
    """)


if __name__ == "__main__":
    main()
