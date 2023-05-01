from backoff import backoff
from redis import Redis

from async_api.tests.functional.settings import config


@backoff
def redis_connect():
    redis_client = Redis(
        f"{config.redis_host}",
        encoding="utf8",
        decode_responses=True,
    )

    if not redis_client.ping():
        raise Exception


if __name__ == "__main__":
    redis_connect()
