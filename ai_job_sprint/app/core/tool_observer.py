import logging
import time

logger = logging.getLogger(__name__)


async def observe_tool(
    tool_name,
    function,
    **arguments,
):

    start = time.perf_counter()

    try:

        result = await function(**arguments)

        latency = time.perf_counter() - start

        logger.info(
            "tool=%s " "input=%s " "output=%s " "latency=%.2f " "error=None",
            tool_name,
            arguments,
            result,
            latency,
        )

        return result

    except Exception as exc:

        latency = time.perf_counter() - start

        logger.exception(
            "tool=%s " "input=%s " "latency=%.2f " "error=%s",
            tool_name,
            arguments,
            latency,
            str(exc),
        )

        raise
