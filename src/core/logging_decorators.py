import functools
import inspect
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar, cast, overload

from fastapi import Request

P = ParamSpec("P")
R = TypeVar("R")


def _extract_request(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Request | None:
    for value in args:
        if isinstance(value, Request):
            return value
    for value in kwargs.values():
        if isinstance(value, Request):
            return value
    return None


def _duration_seconds(start_time: float) -> float:
    return round(time.monotonic() - start_time, 2)


def _format_endpoint_message(
    base_message: str,
    func_name: str,
) -> str:
    return f"{base_message} {func_name}"


@overload
def log_endpoint(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]: ...


@overload
def log_endpoint(func: Callable[P, R]) -> Callable[P, R]: ...


def log_endpoint(func: Callable[P, Any]) -> Callable[P, Any]:
    logger = logging.getLogger("app.endpoint")
    func_name = f"{func.__module__}.{func.__qualname__}"
    endpoint_name = func_name

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            start_time = time.monotonic()
            request = _extract_request(args, kwargs)
            extra = {"event": "endpoint_start", "endpoint": func_name}
            if request:
                extra.update(
                    {
                        "method": request.method,
                        "path": request.url.path,
                    }
                )
            logger.info(
                _format_endpoint_message("Endpoint call started", endpoint_name),
                extra=extra,
            )
            try:
                result = await func(*args, **kwargs)
            except Exception:
                logger.exception(
                    _format_endpoint_message("Endpoint call failed", endpoint_name),
                    extra={
                        **extra,
                        "event": "endpoint_error",
                        "duration_seconds": _duration_seconds(start_time),
                    },
                )
                raise
            duration_seconds = _duration_seconds(start_time)
            logger.info(
                f"{_format_endpoint_message('Endpoint call completed', endpoint_name)} "
                f"({duration_seconds:.2f} s)",
                extra={
                    **extra,
                    "event": "endpoint_ok",
                    "duration_seconds": duration_seconds,
                },
            )
            return result

        return cast(Callable[P, Awaitable[R]], async_wrapper)

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        start_time = time.monotonic()
        request = _extract_request(args, kwargs)
        extra = {"event": "endpoint_start", "endpoint": func_name}
        if request:
            extra.update(
                {
                    "method": request.method,
                    "path": request.url.path,
                }
            )
        logger.info(
            _format_endpoint_message("Endpoint call started", endpoint_name),
            extra=extra,
        )
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.exception(
                _format_endpoint_message("Endpoint call failed", endpoint_name),
                extra={
                    **extra,
                    "event": "endpoint_error",
                    "duration_seconds": _duration_seconds(start_time),
                },
            )
            raise
        duration_seconds = _duration_seconds(start_time)
        logger.info(
            f"{_format_endpoint_message('Endpoint call completed', endpoint_name)} "
            f"({duration_seconds:.2f} s)",
            extra={
                **extra,
                "event": "endpoint_ok",
                "duration_seconds": duration_seconds,
            },
        )
        return result

    return cast(Callable[P, R], sync_wrapper)


@overload
def log_service(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]: ...


@overload
def log_service(func: Callable[P, R]) -> Callable[P, R]: ...


def log_service(func: Callable[P, Any]) -> Callable[P, Any]:
    logger = logging.getLogger("app.service")
    func_name = f"{func.__module__}.{func.__qualname__}"

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            start_time = time.monotonic()
            logger.info(
                f"Service call started {func_name}",
                extra={"event": "service_start", "service": func_name},
            )
            try:
                result = await func(*args, **kwargs)
            except Exception:
                logger.exception(
                    f"Service call failed {func_name}",
                    extra={
                        "event": "service_error",
                        "service": func_name,
                        "duration_seconds": _duration_seconds(start_time),
                    },
                )
                raise
            duration_seconds = _duration_seconds(start_time)
            logger.info(
                f"Service call completed {func_name} ({duration_seconds:.2f} s)",
                extra={
                    "event": "service_ok",
                    "service": func_name,
                    "duration_seconds": duration_seconds,
                },
            )
            return result

        return cast(Callable[P, Awaitable[R]], async_wrapper)

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        start_time = time.monotonic()
        logger.info(
            f"Service call started {func_name}",
            extra={"event": "service_start", "service": func_name},
        )
        try:
            result = func(*args, **kwargs)
        except Exception:
            logger.exception(
                f"Service call failed {func_name}",
                extra={
                    "event": "service_error",
                    "service": func_name,
                    "duration_seconds": _duration_seconds(start_time),
                },
            )
            raise
        duration_seconds = _duration_seconds(start_time)
        logger.info(
            f"Service call completed {func_name} ({duration_seconds:.2f} s)",
            extra={
                "event": "service_ok",
                "service": func_name,
                "duration_seconds": duration_seconds,
            },
        )
        return result

    return cast(Callable[P, R], sync_wrapper)
