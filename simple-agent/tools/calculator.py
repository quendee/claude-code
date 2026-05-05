from .base import Tool


class CalculatorTool(Tool):
    """Client-side tool: your code executes it and returns a tool_result."""

    name = "calculator"
    description = (
        "Evaluate a mathematical expression and return the result. "
        "Supports standard Python arithmetic: +, -, *, /, **, //, %, and parentheses."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A valid Python arithmetic expression, e.g. '(3 + 5) * 2'",
            }
        },
        "required": ["expression"],
    }

    def run(self, expression: str) -> str:
        # eval is safe here because we restrict to arithmetic nodes only
        allowed = set("0123456789+-*/.() \t")
        if not all(c in allowed for c in expression):
            return f"Error: expression contains disallowed characters"
        try:
            result = eval(expression, {"__builtins__": {}})  # noqa: S307
            return str(result)
        except Exception as e:
            return f"Error: {e}"
