from mcp.server.fastmcp import FastMCP

mcp = FastMCP("safe-tools")


@mcp.tool()
def safe_add(a: int, b: int) -> int:
    """安全地计算两个整数相加。"""
    return a + b


if __name__ == "__main__":
    mcp.run()
