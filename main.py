from ast import List
import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env.local", override=False)
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
GIST_ID = os.getenv("GIST_ID")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GIST_FILE_NAME = os.getenv("GIST_FILE_NAME")

required = {
    "AUTH_TOKEN": AUTH_TOKEN,
    "GIST_ID": GIST_ID,
    "SLACK_WEBHOOK_URL": SLACK_WEBHOOK_URL,
    "GIST_FILE_NAME": GIST_FILE_NAME,
}
missing = [k for k, v in required.items() if not v]
if missing:
    raise RuntimeError(f"Missing env vars: {', '.join(missing)}")


def get_developers() -> List[str]:
    r = requests.get(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15,
    )

    r.raise_for_status()
    content = r.json()["files"][GIST_FILE_NAME]["content"]
    developers: List[str] = json.loads(content)
    return developers


def rotate(developers):
    return developers[1:] + developers[:1]


def main():
    developers = get_developers()
    new_developers = rotate(developers)


if __name__ == "__main__":
    main()
