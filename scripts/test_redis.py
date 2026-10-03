import redis


client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


client.set("agentmesh:test", "Redis is working")

value = client.get("agentmesh:test")

print("Redis value:", value)

client.delete("agentmesh:test")

print("Redis connection successful!")