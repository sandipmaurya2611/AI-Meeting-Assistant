import redis
try:
    r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
    r.ping()
    print("Connected to Redis on 6379")
except Exception as e:
    print(f"Could not connect: {e}")
