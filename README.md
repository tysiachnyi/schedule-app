# Schedule App (Slack Duty Rotator)

This Python app rotates a weekly on‑duty developer list and posts to Slack. It uses:

- GitHub Gists (GitHub API) to store the list of developers
- Slack Incoming Webhook to notify the selected on‑duty developer(s)
- GitHub Actions to run the rotation automatically on a schedule

## Prerequisites

- Python 3.9+
- A Slack Incoming Webhook URL
- A GitHub Personal Access Token with `gist` scope
- A GitHub Gist containing the developers list (JSON array of strings), e.g.
  ```json
  ["dev1", "dev2", "dev3", "dev4", "dev5"]
  ```

## Environment Variables

Create a `.env.local` file at the project root (ignored by git):

```
AUTH_TOKEN=ghp_your_token_with_gist_scope
GIST_ID=your_gist_id
GIST_FILE_NAME=developers.json  # or the actual file name in your gist
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
```

Notes:

- `AUTH_TOKEN` must have `gist` permissions.
- `GIST_FILE_NAME` must match the file name inside the gist.

## Install & Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

## What the app does

- Loads `.env.local` with `python-dotenv`.
- Fetches the developers list from the configured Gist.
- Rotates the list so the first developer moves to the end.
- (Optionally) Posts a Slack message naming the new on‑duty developer(s).
- You can extend it to write the rotated list back to the Gist so the rotation persists.

## GitHub Actions (Scheduled Run)

Create `.github/workflows/schedule.yml`:

```yaml
name: Weekly duty rotation

on:
  schedule:
    - cron: "0 8 * * 1" # Every Monday at 08:00 UTC
  workflow_dispatch: {}

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run rotation
        env:
          AUTH_TOKEN: ${{ secrets.AUTH_TOKEN }}
          GIST_ID: ${{ secrets.GIST_ID }}
          GIST_FILE_NAME: ${{ secrets.GIST_FILE_NAME }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python main.py
```

Set the required secrets in your repository settings.
