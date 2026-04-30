# Tool Selection System - Progressive Learning Exercise

This folder contains a step-by-step Python implementation of Claude Code's tool selection system, starting from a minimal prototype and building up to match the original design.

## Files Overview

### 1. **step1_minimal.py** - Minimal Tool Selection
- Simple function-based tools
- Basic dictionary lookup
- No metadata, no filtering
- **Purpose**: Understand the absolute basics

### 2. **step2_registry.py** - Tool Registry with Metadata
- Tools as objects with name, description, aliases
- ToolRegistry class for management
- Name and alias-based lookup
- **Purpose**: Add structure and metadata tracking

### 4. **step4_modes.py** - Mode-Based Tool Selection
- Simple Mode (only core tools)
- REPL Mode (virtualized tools)
- Coordinator Mode (specialized tools)
- Conditional tool inclusion based on environment
- **Purpose**: Handle different execution contexts
- **Note**: Simplified version without permission management

### 5. **step5_full_system.py** - Complete System with MCP Integration
- Full implementation matching original architecture
- MCP (Model Context Protocol) tools support
- Tool search and deferred loading
- Comprehensive state management
- **Purpose**: See the complete picture

## How to Use

Run each file sequentially to understand the progression:

```bash
python step1_minimal.py
python step2_registry.py
python step3_permissions.py
python step4_modes.py
python step5_full_system.py
```

Each file builds on concepts from the previous one. Read the code comments to understand:
- What's new in each step
- How it maps to the original Claude Code
- The design rationale

## Key Concepts

- **Tool**: An executable operation with metadata (name, description, aliases)
- **Registry**: Central place to register and lookup tools
- **Permission Context**: Describes what tools a user is allowed to use
- **Filtering**: Removing tools based on permissions, mode, or feature flags
- **Mode**: Different execution contexts require different tool sets
- **MCP Tools**: Dynamically loaded tools from Model Context Protocol servers
- **Deferred Loading**: Tools are only loaded when needed to save token count

## Mapping to Original Code

| Step | Original Files | Key Functions |
|------|---|---|
| 1 | - | N/A |
| 2 | `Tool.ts`, `tools.ts` | `Tool` interface, `ToolRegistry` |
| 3 | `permissions/permissions.ts` | `getDenyRuleForTool()`, `filterToolsByDenyRules()` |
| 4 | `tools.ts` | `getTools()`, mode-based filtering |
| 5 | `tools.ts`, `services/tools/` | `assembleToolPool()`, `getMergedTools()` |

## Understanding the Original Code

After working through these steps, you can understand:
- How `getAllBaseTools()` registers all available tools
- Why `getTools(permissionContext)` exists separately
- How permissions are applied with deny rules
- Why MCP tools are merged separately with `assembleToolPool()`
- The purpose of `findToolByName()` and `toolMatchesName()`
