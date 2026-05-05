# Web search is a server-side tool: Anthropic's infrastructure executes it.
# No `run()` needed — just declare it in the `tools` array and the API handles the rest.
# The response will transparently include `server_tool_use` and `web_search_tool_result`
# blocks, and Claude's final answer will already incorporate the search results.

WEB_SEARCH_DEFINITION = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,
}
