"""
STEP 1: Minimal Tool Selection
==============================

Goal: Start with the simplest possible tool selection system.

Key Concepts:
  - Tools are just functions
  - Selection is based on simple name lookup
  - No metadata, no filtering
  - Just direct dictionary lookup and execution

This is the absolute foundation.
"""


def bash_tool(command: str) -> str:
    """Execute a bash command"""
    return f"[Bash] Executed: {command}"


def file_read_tool(path: str) -> str:
    """Read a file"""
    return f"[FileRead] Content of: {path}"


def file_edit_tool(path: str, content: str) -> str:
    """Edit or create a file"""
    return f"[FileEdit] Updated: {path}"


def web_fetch_tool(url: str) -> str:
    """Fetch content from the web"""
    return f"[WebFetch] Retrieved from: {url}"


# Store available tools in a simple dictionary
# Key = tool name, Value = callable
TOOLS = {
    "bash": bash_tool,
    "file_read": file_read_tool,
    "file_edit": file_edit_tool,
    "web_fetch": web_fetch_tool,
}


def select_tool(tool_name: str):
    """
    Find a tool by name.
    
    Returns the tool callable if found, None otherwise.
    This is basically what findToolByName() does in the original.
    """
    return TOOLS.get(tool_name)


def call_tool(tool_name: str, *args, **kwargs):
    """
    Find and call a tool.
    
    This combines:
    1. findToolByName() - look up the tool
    2. Tool execution - call it with arguments
    """
    tool = select_tool(tool_name)
    if tool is None:
        return f"ERROR: Tool '{tool_name}' not found"
    
    try:
        return tool(*args, **kwargs)
    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    print("=" * 60)
    print("STEP 1: Minimal Tool Selection")
    print("=" * 60)
    print()
    
    print("Available tools:")
    for name in TOOLS.keys():
        print(f"  - {name}")
    print()
    
    # Example 1: Direct lookup
    print("Example 1: Direct tool lookup")
    tool = select_tool("bash")
    print(f"  select_tool('bash') -> {tool.__name__ if tool else 'None'}")
    print()
    
    # Example 2: Tool that doesn't exist
    print("Example 2: Tool lookup for non-existent tool")
    tool = select_tool("nonexistent")
    print(f"  select_tool('nonexistent') -> {tool}")
    print()
    
    # Example 3: Call a tool
    print("Example 3: Call a tool")
    result = call_tool("bash", "ls -la")
    print(f"  call_tool('bash', 'ls -la') -> {result}")
    print()
    
    # Example 4: Call another tool
    print("Example 4: Call file_read tool")
    result = call_tool("file_read", "README.md")
    print(f"  call_tool('file_read', 'README.md') -> {result}")
    print()
    
    # Example 5: Try to call non-existent tool
    print("Example 5: Call non-existent tool")
    result = call_tool("unknown_tool")
    print(f"  call_tool('unknown_tool') -> {result}")
    print()
    
    print("=" * 60)
    print("KEY INSIGHTS FROM STEP 1:")
    print("=" * 60)
    print("""
1. Tools are just callables (functions) stored in a dictionary
2. Lookup is straightforward: TOOLS.get(name)
3. No metadata means we can't describe tools to the model
4. No filtering means all tools available to everyone
5. No aliases means tool names are hardcoded

Next: We need to add METADATA and STRUCTURE to tools!
    """)


if __name__ == "__main__":
    main()
