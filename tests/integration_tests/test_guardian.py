import requests


def test_integration(service_url):
    resp = requests.get(f"{service_url}/management/health", timeout=60)
    assert resp.json()["status"] == "up"
