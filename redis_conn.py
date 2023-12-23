import redis

# Connect to Redis server
redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0)
