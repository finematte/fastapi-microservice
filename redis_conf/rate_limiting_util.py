import redis
from datetime import timedelta


class RateLimiter:
    def __init__(
        self,
        redis_client: redis.Redis,
        threshold: int,
        reset_interval: timedelta,
    ):
        self.redis_client = redis_client
        self.threshold = threshold
        self.reset_interval = reset_interval

    def _get_redis_key(self, ip: str):
        return f"failed_attempts:{ip}"

    def is_rate_limited(self, ip: str):
        key = self._get_redis_key(ip)
        failed_attempts = self.redis_client.get(key)

        if failed_attempts and int(failed_attempts) >= self.threshold:
            return True
        return False

    def record_failure(self, ip: str):
        key = self._get_redis_key(ip)
        self.redis_client.incr(key)
        self.redis_client.expire(key, int(self.reset_interval.total_seconds()))

    def reset_failures(self, ip: str):
        key = self._get_redis_key(ip)
        self.redis_client.delete(key)
