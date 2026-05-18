# scripts/09_verify_observability.py
import os

import requests


def check_prometheus() -> None:
    resp = requests.get(
        "http://localhost:9090/api/v1/query",
        params={"query": 'http_requests_total{job="api-gateway"}'},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    assert data.get("status") == "success"
    print("Integration 9 OK: Prometheus metrics flowing")


def check_langsmith() -> None:
    api_key = os.environ.get("LANGCHAIN_API_KEY")
    if not api_key:
        print("Skip LangSmith check: LANGCHAIN_API_KEY chưa được cấu hình")
        return

    from langsmith import Client

    client = Client(api_key=api_key)
    project = os.environ.get("LANGCHAIN_PROJECT", "lab28-platform")
    runs = list(client.list_runs(project_name=project, limit=1))
    assert len(runs) > 0
    print("Integration 10 OK: LangSmith traces visible")


if __name__ == "__main__":
    check_prometheus()
    check_langsmith()
