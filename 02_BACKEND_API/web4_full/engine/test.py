import requests

BASE = "http://127.0.0.1:5080"

c = requests.get(BASE + "/challenge/AJAN").json()
print("CHALLENGE:", c)

print("LOGIN ATTEMPT (needs real signature):")

r = requests.post(BASE + "/login", json={
    "wallet": "AJAN",
    "message": c["message"],
    "signature": "DEMO",
})

print("LOGIN:", r.json())

print("GRAPH:", requests.get(BASE + "/graph").json())
print("STATUS:", requests.get(BASE + "/status").json())
