import requests

BASE = "http://127.0.0.1:5002"

endpoints = ["/status", "/graph", "/events"]

for e in endpoints:
    try:
        r = requests.get(BASE + e)
        print(e, r.status_code, r.text[:80])
    except Exception as ex:
        print(e, "ERROR", ex)
