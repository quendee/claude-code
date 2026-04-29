"""
STEP 2: Tool Registry with Metadata
====================================

Goal: Make tools into objects with metadata instead of raw functions.

Key Concepts:
  - Tools are now OBJECTS with structure (like Tool interface in Tool.ts)
  - Tools have: name, description, aliases, enabled flag
  - ToolRegistry manages all tools
  - Lookup supports both primary name AND aliases
  - We can iterate over tools and describe them

This matches the Tool interface and basic registry pattern in Claude Code.
"""

from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class Tool:
    """
    Represents a tool available to the AI model.
    
    Maps to the Tool interface in src/Tool.ts with:
    - name: primary identifier
    - description: what the tool does
    - callable: the actual implementation
    - aliases: alternative names (for backwards compatibility)
    - enabled: whether this tool is currently active
    """
    name: str
    description: str
    callable: Callable
    aliases: Optional[List[str]] = None
    enabled: bool = True


# Create tool instances with metadata
# These now have descriptions the model can see!

BASH = Tool(
    name="bash",
    description="Execute shell commands in the terminal",
    callable=lambda cmd: f"[Bash] {cmd}",
    aliases=["shell", "terminal", "exec"],
    enabled=True,
)

FILE_READ = Tool(
    name="file_read",
    description="Read the contents of a file",
    callable=lambda path: f"[FileRead] {path}",
    aliases=["read", "get_file"],
    enabled=True,
)

FILE_EDIT = Tool(
    name="file_edit",
    description="Create or modify a file",
    callable=lambda path, content: f"[FileEdit] {path}",
    aliases=["write", "edit", "create_file"],
    enabled=True,
)

WEB_FETCH = Tool(
    name="web_fetch",
    description="Fetch and retrieve content from web URLs",
    callable=lambda url: f"[WebFetch] {url}",
    aliases=["fetch", "http_get"],
    enabled=True,
)

WEB_SEARCH = Tool(
    name="web_search",
    description="Search the web for information",
    callable=lambda query: f"[WebSearch] {query}",
    aliases=["search"],
    enabled=True,
)

# A disabled tool won't be offered to the model
DEPRECATED_TOOL = Tool(
    name="deprecated_tool",
    description="This tool is no longer available",
    callable=lambda: "N/A",
    enabled=False,
)


class ToolRegistry:
    """
    Manages tool registration and lookup.
    
    Similar to how src/tools.ts manages tools through:
    - getAllBaseTools() - register all tools
    - getTools() - get available tools
    - findToolByName() - lookup by name or alias
    
    The registry is THE SOURCE OF TRUTH for tools.
    """
    
    def __init__(self):
        self.tools: List[Tool] = []
    
    def register(self, tool: Tool) -> None:
        """Add a tool to the registry"""
        self.tools.append(tool)
    
    def get_all_tools(self) -> List[Tool]:
        """
        Get ALL tools, even disabled ones.
        Maps to: getAllBaseTools() in tools.ts
        """
        return self.tools
    
    def get_enabled_tools(self) -> List[Tool]:
        """
        Get only ENABLED tools.
        Maps to filtering step in getTools()
        """
        return [tool for tool in self.tools if tool.enabled]
    
    def find_tool_by_name(self, name: str) -> Optional[Tool]:
        """
        Find a tool by its primary name OR alias.
        Maps to: findToolByName() and toolMatchesName() in Tool.ts
        
        This enables:
        - Primary lookup: "bash" -> bash tool
        - Alias lookup: "shell" -> bash tool (backwards compatibility!)
        """
        for tool in self.tools:
            # Check primary name
            if tool.name == name:
                return tool
            # Check aliases
            if tool.aliases and name in tool.aliases:
                return tool
        return None
    
    def list_tools(self, include_disabled: bool = False) -> List[Tool]:
        """Get tools for display/description to the model"""
        tools = self.get_all_tools() if include_disabled else self.get_enabled_tools()
        return sorted(tools, key=lambda t: t.name)


def main():
    print("=" * 60)
    print("STEP 2: Tool Registry with Metadata")
    print("=" * 60)
    print()
    
    # Create and populate registry
    registry = ToolRegistry()
    
    # Register tools
    registry.register(BASH)
    registry.register(FILE_READ)
    registry.register(FILE_EDIT)
    registry.register(WEB_FETCH)
    registry.register(WEB_SEARCH)
    registry.register(DEPRECATED_TOOL)
    
    print(f"Total tools registered: {len(registry.get_all_tools())}")
    print(f"Enabled tools: {len(registry.get_enabled_tools())}")
    print()
    
    # Example 1: List all tools with descriptions
    print("All Tools (with descriptions):")
    for tool in registry.list_tools(include_disabled=True):
        status = "✓ ENABLED" if tool.enabled else "✗ DISABLED"
        aliases = f" (aliases: {', '.join(tool.aliases)})" if tool.aliases else ""
        print(f"  [{status}] {tool.name}: {tool.description}{aliases}")
    print()
    
    # Example 2: Get only enabled tools
    print("Enabled Tools Only:")
    for tool in registry.get_enabled_tools():
        print(f"  ✓ {tool.name}")
    print()
    
    # Example 3: Find by primary name
    print("Lookup by PRIMARY NAME:")
    tool = registry.find_tool_by_name("bash")
    print(f"  find_tool_by_name('bash') -> {tool.name if tool else 'Not found'}")
    print()
    
    # Example 4: Find by alias (backwards compatibility)
    print("Lookup by ALIAS (backwards compatibility!):")
    tool = registry.find_tool_by_name("read")  # Alias for file_read
    print(f"  find_tool_by_name('read') -> {tool.name if tool else 'Not found'}")
    
    tool = registry.find_tool_by_name("exec")  # Alias for bash
    print(f"  find_tool_by_name('exec') -> {tool.name if tool else 'Not found'}")
    print()
    
    # Example 5: Call a tool using the registry
    print("Call tools via registry lookup:")
    tool = registry.find_tool_by_name("file_read")
    if tool:
        result = tool.callable("example.txt")
        print(f"  Read file: {result}")
    
    tool = registry.find_tool_by_name("search")  # Using alias
    if tool:
        result = tool.callable("Python decorators")
        print(f"  Search: {result}")
    print()
    
    # Example 6: What happens with non-existent tool?
    print("Lookup for non-existent tool:")
    tool = registry.find_tool_by_name("nonexistent")
    print(f"  find_tool_by_name('nonexistent') -> {tool}")
    print()
    
    print("=" * 60)
    print("KEY INSIGHTS FROM STEP 2:")
    print("=" * 60)
    print("""
1. Tools are now OBJECTS with metadata (description, aliases)
2. The model can see what each tool does via descriptions
3. Aliases enable backwards compatibility when renaming tools
4. Registry is the single source of truth (maps to getAllBaseTools)
5. We can filter by enabled/disabled status
6. Lookup supports both primary name and aliases

Comparison to Original:
  - Tool interface: ✓ (name, description, callable, aliases, enabled)
  - findToolByName(): ✓ (primary + alias lookup)
  - toolMatchesName(): ✓ (name or alias match)
  - getEnabledTools(): ✓ (filtering step)

Next: We need to add PERMISSIONS to control which tools users can access!
    """)


if __name__ == "__main__":
    main()
