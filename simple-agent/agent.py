"""
Minimal agentic loop over the Anthropic Messages API.

Supports two tool types:
  - Server-side tools (e.g. web_search): declared in the tools list; Anthropic's
    infrastructure executes them transparently within a single API call.
  - Client-side tools (e.g. calculator): your code runs them when the response
    contains a `tool_use` block, then sends a `tool_result` back to continue.
"""

import anthropic
from tools import CalculatorTool, WEB_SEARCH_DEFINITION
from tools.base import Tool

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096


def build_registry(*tools: Tool) -> dict[str, Tool]:
    return {t.name: t for t in tools}


def run(prompt: str, model: str = DEFAULT_MODEL, verbose: bool = False) -> str:
    client = anthropic.Anthropic()

    # --- Client-side tools --------------------------------------------------
    calculator = CalculatorTool()
    registry = build_registry(calculator)

    # --- Tool declarations sent to the API ----------------------------------
    # Server-side tools use their own dict format (include "type").
    # Client-side tools use Tool.definition() which returns name/description/input_schema.
    tools = [
        WEB_SEARCH_DEFINITION,
        calculator.definition(),
    ]

    messages: list[dict] = [{"role": "user", "content": prompt}]

    # --- Agentic loop -------------------------------------------------------
    while True:
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            tools=tools,
            messages=messages,
        )

        if verbose:
            for block in response.content:
                block_type = getattr(block, "type", "unknown")
                if block_type == "server_tool_use":
                    print(f"[server_tool_use] {block.name}({block.input})")
                elif block_type == "web_search_tool_result":
                    count = len(getattr(block, "content", []))
                    print(f"[web_search_tool_result] {count} result(s) returned")
                elif block_type == "tool_use":
                    print(f"[tool_use] {block.name}({block.input})")

        # Append assistant turn (required so the conversation stays coherent)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Collect all text blocks into the final answer
            return "\n".join(
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            )

        if response.stop_reason == "tool_use":
            # Handle every client-side tool_use block in the response
            tool_results = []
            for block in response.content:
                if getattr(block, "type", None) != "tool_use":
                    continue
                tool = registry.get(block.name)
                if tool is None:
                    result = f"Error: unknown tool '{block.name}'"
                else:
                    result = tool.run(**block.input)
                    if verbose:
                        print(f"[tool_result] {block.name} → {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})
            # Loop — send results back and let Claude continue

        # stop_reason == "max_tokens" or unexpected: just return what we have
        if response.stop_reason not in ("end_turn", "tool_use"):
            return "\n".join(
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            )
