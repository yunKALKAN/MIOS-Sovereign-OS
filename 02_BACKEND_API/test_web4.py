import requests

BASE = "http://127.0.0.1:5002"

print(requests.get(BASE + "/health").json())
print(requests.get(BASE + "/graph").json())
print(requests.get(BASE + "/radar").json())
print(requests.get(BASE + "/funding").json())
