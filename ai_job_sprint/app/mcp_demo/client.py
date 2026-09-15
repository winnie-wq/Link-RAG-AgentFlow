import asyncio
import sys

from mcp import (
    ClientSession,
    StdioServerParameters,
)

from mcp.client.stdio import (
    stdio_client,
)


async def main():

    params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp_demo.server",
        ],
    )

    async with stdio_client(params) as (
        read,
        write,
    ):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            print(
                "Tools:",
                tools,
            )

            result = await session.call_tool(
                "safe_add",
                {
                    "a": 18,
                    "b": 27,
                },
            )

            print(
                "Result:",
                result,
            )


if __name__ == "__main__":

    asyncio.run(main())
