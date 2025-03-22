import os
from dotenv import load_dotenv

from taskiq import TaskiqScheduler
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend, RedisScheduleSource

from features import update_advert_stat_statistics, get_all_active_advert_stats

load_dotenv()

DEVELOPMENT_MODE = bool(int(os.getenv("DEVELOPMENT_MODE")))

REDIS = os.getenv("REDIS")
CRON_SETTING = os.getenv("CRON_SETTING")

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = os.getenv("REDIS_DB")

REDIS_HOST = "redis"
REDIS_PORT = 6379

if DEVELOPMENT_MODE:
    REDIS_HOST = "localhost"
    REDIS_PORT = int(os.getenv("REDIS_PORT"))

redis_async_result = RedisAsyncResultBackend(
    redis_url=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
)

broker = ListQueueBroker(
    url=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0",
).with_result_backend(redis_async_result)

schedule_source = RedisScheduleSource(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[schedule_source],
)

@broker.task("update_video_statistics")
async def update_video_statistics(advert_stat_id):
    await update_advert_stat_statistics(advert_stat_id)

@broker.task("update_all_statistics")
async def update_all_statistics():
    active_advert_stats = get_all_active_advert_stats()

    for advert_stat in active_advert_stats:
        await update_video_statistics.kiq(advert_stat.id)

async def schedule():
    task = await update_all_statistics.schedule_by_cron(schedule_source, CRON_SETTING)

    return task.schedule_id
