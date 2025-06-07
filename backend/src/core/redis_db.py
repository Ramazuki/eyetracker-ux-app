from redis.asyncio import Redis

from src.settings import settings


__all__ = ['get_redis', 'redis_client', 'COIN_UPDATES', 'INCOME_UPDATES', 'COIN_BALANCE']


def make_redis() -> Redis:
    dsn = settings.redis_dsn
    db = dsn.path.split('/')[1] if dsn.path else 0
    port = dsn.port or 6379
    return Redis(host=dsn.host, db=db, port=port, health_check_interval=30)


redis_client: Redis | None = make_redis()


def get_redis() -> Redis:
    if redis_client:
        return redis_client
    raise RuntimeError("Redis wasn't initialized. Check app lifespan.")


COIN_BALANCE = 'user_coin_balance'
INCOME_AMMOUNT = 'coin_increment'
INCOME_MULTIPLIER = 'income_multiplier'

COIN_UPDATES = 'coin_balance_updates'
INCOME_UPDATES = 'passive_income_updates'