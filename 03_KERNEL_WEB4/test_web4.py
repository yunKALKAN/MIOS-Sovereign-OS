import requests

BASE = "http://127.0.0.1:5002"

print(requests.get(BASE + "/api/v1/health").json())
print(requests.get(BASE + "/api/v1/graph").json())
print(requests.get(BASE + "/api/v1/radar").json())
print(requests.get(BASE + "/api/v1/funding").json())
