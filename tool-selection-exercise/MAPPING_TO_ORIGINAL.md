# Mapping Between Python Learning Code and Original Claude Code

This document shows exactly how each Python file maps to the original TypeScript source.

## File Organization

```
claude-code/src/
├── Tool.ts                           → Python: All steps (Tool interface, toolMatchesName, findToolByName)
├── tools.ts                          → Python: All steps (registration, filtering, assembly)
├── services/tools/
│   ├── toolOrchestration.ts         → Python: step5_full_system (runtime orchestration)
│   └── toolExecution.ts             → Python: step5_full_system (find and execute)
└── tools/
    ├── BashTool/
    ├── FileReadTool/
    ├── FileEditTool/
    ├── REPLTool/                     → Python: step4_modes (REPL wrapping)
    ├── AgentTool/                    → Python: step4_modes (coordinator)
    ├── TaskStopTool/                 → Python: step4_modes (coordinator)
    ├── ToolSearchTool/               → Python: step5_full_system (search_tools)
    └── ... 40+ more tools
```

## Step-by-Step Mapping

### STEP 1: Minimal Tool Selection
**Python:** `step1_minimal.py`
**Original concept:** Absolute basics of how tools work

| Python | TypeScript Original |
|--------|---------------------|
| `TOOLS` dict | Tool pool implicitly |
| `select_tool()` | Basic tool lookup |
| `call_tool()` | Tool execution |

**Why this step:** Shows the absolute minimum - just dictionaries and functions.

---

### STEP 2: Tool Registry with Metadata
**Python:** `step2_registry.py`
**Original files:** `src/Tool.ts`, start of `src/tools.ts`

| Python | TypeScript Original |
|--------|---------------------|
| `@dataclass Tool` | `export type Tool<...>` in Tool.ts |
| `Tool.name` | `tool.name` |
| `Tool.description` | Used in `description()` method |
| `Tool.aliases` | `aliases?: string[]` property |
| `Tool.enabled` | `isEnabled()` check |
| `ToolRegistry` | Implied in tools.ts structure |
| `get_all_tools()` | `getAllBaseTools()` in tools.ts:180 |
| `find_tool_by_name()` | `findToolByName()` in Tool.ts:358 |
| `toolMatchesName()` | `toolMatchesName()` in Tool.ts:348 |

**Key code locations:**
- `Tool.ts:348` - `toolMatchesName()` function
- `Tool.ts:358` - `findToolByName()` function
- `tools.ts:180` - `getAllBaseTools()` returns Tools array
- `tools.ts:175-215` - Tool registration with imports and features

**Why this step:** Introduces structure - tools are objects with metadata, not raw functions.

---

### STEP 3: Mode-Based Tool Selection
**Python:** `step4_modes.py`
**Original file:** `src/tools.ts` (large getTools function)

| Python | TypeScript Original |
|--------|---------------------|
| `ExecutionMode` enum | Environment checks |
| `SIMPLE` mode | `process.env.CLAUDE_CODE_SIMPLE` check at tools.ts:270 |
| `REPL` mode | `isReplModeEnabled()` check at tools.ts:314-318 |
| `COORDINATOR` mode | `feature('COORDINATOR_MODE')` at tools.ts:281+ |
| `NORMAL` mode | Default mode (no special env flags) |
| `simple_mode_tools` | `[BashTool, FileReadTool, FileEditTool]` at tools.ts:273 |
| `repl_only_hidden_tools` | `REPL_ONLY_TOOLS` constant |
| `apply_mode_filtering()` | Main if/elif block in `getTools()` |

**Key code locations:**
- `tools.ts:270-333` - The main `getTools(permissionContext)` function
- `tools.ts:164` - `REPL_ONLY_TOOLS` definition
- `tools.ts:270` - Simple mode check
- `tools.ts:281` - Coordinator mode check  
- `tools.ts:314` - REPL mode check
- `src/tools/REPLTool/constants.ts` - REPL configuration

**Why this step:** Different execution contexts need different tool sets.

**Important modes:**
- **SIMPLE**: Minimal environment, only 3 core tools
- **REPL**: Virtual machine mode, primitives wrapped
- **COORDINATOR**: Multi-agent orchestration
- **NORMAL**: Full set (default)

---

### STEP 4: Complete System with MCP Integration  
**Python:** `step5_full_system.py`
**Original files:** `src/tools.ts`, `src/services/tools/`

| Python | TypeScript Original |
|--------|---------------------|
| `builtin_tools` | `getAllBaseTools()` return value |
| `mcp_tools` | `mcpTools` parameter in functions |
| `get_tools()` | `getTools(permissionContext)` with mode |
| `get_mcp_tools_filtered()` | MCP filtering in `assembleToolPool()` |
| `assemble_tool_pool()` | `assembleToolPool()` at tools.ts:345-375 |
| `get_merged_tools()` | `getMergedTools()` at tools.ts:383-400 |
| `find_tool_by_name()` | `findToolByName()` at Tool.ts:358 |
| `search_tools()` | `ToolSearchTool` behavior |
| `should_defer_tools()` | `isToolSearchEnabled()` check |

**Key code locations:**
- `tools.ts:345-375` - `assembleToolPool()` function
- `tools.ts:383-400` - `getMergedTools()` function
- `tools.ts:1-100` - Tool registration
- `src/services/tools/toolOrchestration.ts` - Runtime coordination
- `src/services/tools/toolExecution.ts` - Tool execution + permission checks
- `src/tools/ToolSearchTool/ToolSearchTool.ts` - Tool search logic

**Why this step:** The complete picture - all layers working together.

**Flow:**
```
1. getAllBaseTools()           → All built-in tools
2. getTools(context)           → Filter by permissions + mode
3. get_mcp_tools_filtered()    → Filter MCP tools by permissions
4. assembleToolPool()          → Merge, deduplicate, sort
5. Tools in system prompt      → Model sees this list
6. Model calls tool by name    
7. findToolByName()            → Look up the tool
8. Permission check at runtime → Verify allowed to call
9. Execute tool
```

---

## Original File Structure Reference

### Core Tool Definition
```typescript
// src/Tool.ts:348-358
export function toolMatchesName(tool, name)
export function findToolByName(tools, name)
```

Tool interface at `src/Tool.ts:368-425`:
```typescript
export type Tool<...> = {
  aliases?: string[]
  searchHint?: string
  call()
  description()
  inputSchema
  outputSchema
  ...
}
```

### Tool Registration
```typescript
// src/tools.ts:180-250
export function getAllBaseTools(): Tools {
  return [
    AgentTool,
    TaskOutputTool,
    BashTool,
    // Conditional imports for feature-gated tools
    ...(SuggestBackgroundPRTool ? [SuggestBackgroundPRTool] : []),
    // 40+ tools total
  ]
}
```

### Mode-Based Tool Selection
```typescript
// src/tools.ts:270-340
export const getTools = (): Tools => {
  // Simple mode check
  if (isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)) {
    const simpleTools: Tool[] = [BashTool, FileReadTool, FileEditTool]
    return simpleTools
  }
  
  // REPL mode check
  if (isReplModeEnabled()) {
    allowedTools = allowedTools.filter(
      tool => !REPL_ONLY_TOOLS.has(tool.name)
    )
  }
  
  return allowedTools
}
```

### Tool Pool Assembly
```typescript
// src/tools.ts:345-375
export function assembleToolPool(
  mcpTools: Tools,
): Tools {
  const builtInTools = getTools()
  const allowedMcpTools = mcpTools
  
  return uniqBy(
    [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
    'name',
  )
}
```

### Runtime Tool Execution
```typescript
// src/services/tools/toolExecution.ts:345-351
let tool = findToolByName(toolUseContext.options.tools, toolName)
if (!tool) {
  const fallbackTool = findToolByName(getAllBaseTools(), toolName)
  tool = fallbackTool
}
```

---

## Key Design Patterns in the Original

### 1. **Layered Filtering**
Mode filtering → Tool pool assembly

### 2. **Separation of Concerns**
- Built-in tools ≠ MCP tools (merged at the end)
- Pool assembly ≠ Runtime execution

### 3. **Feature Flags**
Tools can be conditionally included based on:
- `process.env.USER_TYPE === 'ant'`
- `feature('COORDINATOR_MODE')`
- `process.env.CLAUDE_CODE_SIMPLE`
- And many more

### 4. **Backwards Compatibility**
Aliases allow renaming tools without breaking existing code.
Old name → New name still works.

### 5. **Token Efficiency**
Tool search (ToolSearchTool) enables handling 100+ tools.
Deferred loading saves tokens by loading schemas on-demand.

---

## How to Use This Reference

1. **I don't understand a concept** → Read the corresponding Python step
2. **I want to see TypeScript** → Use the code locations provided
3. **I want to understand the flow** → Follow the "Flow" sections
4. **I want to know why** → See "Why this step" explanations

Example:
- "How does permission filtering work?" 
  - Read: `step3_permissions.py`
  - Original: `tools.ts:253-264`

---

## Running the Examples

```bash
# Run individual step
python step2_registry.py

# Run all steps
python run_all_steps.py

# Or run directly in Python
python -i step5_full_system.py
>>> pool = ToolPool()
>>> pool.register_builtin_tool(...)
```

---

## Advanced: Extending the System

Once you understand the system, you can:

1. **Add a new tool**: Register it in `getAllBaseTools()`
2. **Create a new mode**: Add to `ExecutionMode` enum
3. **Handle MCP tools**: Use `register_mcp_tool()`
4. **Search tools**: Use `search_tools()` when too many available

---

## Common Questions

**Q: Why is mode filtering important?**
A: Different execution contexts need different tool sets. Simple mode constrains to core tools, REPL mode wraps primitives, coordinator mode enables orchestration.

**Q: Why merge MCP tools separately?**
A: MCP tools are DYNAMIC (servers can change), built-in tools are STATIC.
Kept separate for cache stability and clear precedence.

**Q: Why deduplicate (built-in wins)?**
A: If both have "bash", built-in is trusted. MCP might be user-provided.

**Q: When is tool deferral triggered?**
A: When token count would be too high with all schemas.
Uses ToolSearchTool instead - model searches instead of seeing all tools.

**Q: Is REPL mode safe?**
A: Yes! Primitives are wrapped in a REPL VM, preventing direct access.
Model code runs in controlled environment before returning results.

