from arq.connections import RedisSettings
from app.config import settings

async def startup(ctx):
    ctx["service"] = "nexo-worker"

async def heartbeat(ctx):
    return {"service": ctx["service"], "status": "ok"}

class WorkerSettings:
    functions = [heartbeat]
    on_startup = startup
    redis_settings = RedisSettings.from_dsn(settings().redis_url)
    max_jobs = 4
    job_timeout = 120
    max_tries = 3
