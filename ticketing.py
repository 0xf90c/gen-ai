import os
import requests

def create_ticket(title, body):
    token = os.getenv("GITHUB_TOKEN")
    repo  = os.getenv("GITHUB_REPO")

    print("[ticket] repo =", repo)
    print("[ticket] token_present =", bool(token))

    if not token:
        raise ValueError("GITHUB_TOKEN is not set")
    if not repo or "/" not in repo:
        raise ValueError("GITHUB_REPO must be like username/repo")

    url = f"https://api.github.com/repos/{repo}/issues"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "data-insights-app"
    }

    payload = {
        "title": title,
        "body": body
    }

    r = requests.post(url, headers=headers, json=payload)

    print("[ticket] status:", r.status_code)
    data = r.json()
    print("[ticket] response:", data)

    if r.status_code >= 400:
        raise RuntimeError(data)

    return data["html_url"]