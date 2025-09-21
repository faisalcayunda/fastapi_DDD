import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        loop=settings.LOOP,
        http=settings.HTTP,
        log_level=settings.LOG_LEVEL,
        reload=settings.DEBUG,
        limit_concurrency=settings.LIMIT_CONCURRENCY,
        backlog=settings.BACKLOG,
        limit_max_requests=settings.LIMIT_MAX_REQUESTS,
        timeout_keep_alive=settings.TIMEOUT_KEEP_ALIVE,
        access_log=settings.ACCESS_LOG,
        h11_max_incomplete_event_size=settings.H11_MAX_INCOMPLETE_EVENT_SIZE,
        server_header=settings.SERVER_HEADER,
        date_header=settings.DATE_HEADER,
        forwarded_allow_ips=settings.FORWARDED_ALLOW_IPS,
    )
