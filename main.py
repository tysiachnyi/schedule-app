import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import List

IS_GITHUB = os.getenv("GITHUB_ACTIONS") == True  # or: os.getenv("CI") == "true"

if not IS_GITHUB:
    load_dotenv(
        dotenv_path=Path(__file__).resolve().parent / ".env.local", override=False
    )


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


def update_gist(data: List[str]) -> None:
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    payload = {
        "files": {
            GIST_FILE_NAME: {
                "content": json.dumps(data, indent=2),
            }
        }
    }
    r = requests.patch(url, headers=headers, json=payload, timeout=15)
    r.raise_for_status()


def slack_message(developers):
    message = "👨‍💻 Weekly Dev Schedule\n\n" + "\n".join(f"- {d}" for d in developers)
    print(message)
    r = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=15,
    )
    r.raise_for_status()


def main():
    developers = get_developers()
    new_developers = rotate(developers)
    update_gist(new_developers)
    slack_message(new_developers)


if __name__ == "__main__":
    main()
