import asyncio
import logging
from inspect import iscoroutinefunction

import async_timeout
from requests import HTTPError

logger = logging.getLogger()


async def wait_is_healthy(health_check_method, *args, **kwargs):
    try:
        async with async_timeout.timeout(120):
            while True:
                try:
                    if iscoroutinefunction(health_check_method):
                        await health_check_method(*args, **kwargs)
                    else:
                        health_check_method(*args, **kwargs)
                    break
                except (HTTPError, Exception):
                    await asyncio.sleep(1)
    except asyncio.TimeoutError as exc:
        logger.error("Health-check failed: %s", exc)
        raise
