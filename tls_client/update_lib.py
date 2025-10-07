from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import requests

from .utils import get_dependency_filename

GITHUB_API_URL = "https://api.github.com/repos/bogdanfinn/tls-client/releases/latest"
LOCAL_VERSION_FILE = os.path.join(os.path.dirname(__file__), "dependencies/version.txt")
DOWNLOAD_DIR = os.path.dirname(LOCAL_VERSION_FILE)
CHECK_INTERVAL = timedelta(hours=24)

CURRENT_DEPENDENCY_FILENAME = get_dependency_filename()


def get_latest_release(session: requests.Session) -> tuple[Any, str | None] | None:
    headers = {}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    local_version_info = read_local_version()
    if local_version_info and 'Etag' in local_version_info:
        headers['If-None-Match'] = local_version_info['Etag']

    response = session.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 304:  # Not Modified
        return None

    response.raise_for_status()
    latest_release = response.json()
    return latest_release, response.headers.get('Etag')


def read_local_version() -> Optional[Dict[str, str]]:
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as f:
            lines = f.read().splitlines(False)
            if len(lines) >= 3:
                return {
                    'version': lines[0],
                    'last_modified': lines[1],
                    'last_check': lines[2]
                }
    return None


def save_local_version(version: str, last_modified: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(f"{version}\n{last_modified}\n{now}")


def download_file(session: requests.Session, url: str, dest_path: str) -> None:
    response = session.get(url)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(response.content)


def should_check_update() -> bool:
    local_version_info = read_local_version()
    if not local_version_info or 'last_check' not in local_version_info:
        return True
    last_check = datetime.fromisoformat(local_version_info['last_check'])
    return datetime.now(timezone.utc) - last_check > CHECK_INTERVAL


def update_lib() -> None:
    if not should_check_update():
        return

    session = requests.Session()

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    result = get_latest_release(session)
    if result is None:
        return

    latest_release, last_modified = result
    latest_version = latest_release["tag_name"]
    local_version_info = read_local_version()

    if local_version_info and latest_version == local_version_info['version']:
        return

    print(f"New version found: {latest_version}. Updating...")

    assets = latest_release["assets"]
    dependency = CURRENT_DEPENDENCY_FILENAME.rsplit(".", 1)[0]
    for asset in assets:
        if asset["name"].startswith(dependency):
            download_url = asset["browser_download_url"]
            dest_path = os.path.join(DOWNLOAD_DIR, CURRENT_DEPENDENCY_FILENAME)
            download_file(session, download_url, dest_path)
            print(f"Downloaded {CURRENT_DEPENDENCY_FILENAME} from {download_url}")
            break
    else:
        print(f"Could not find asset for {CURRENT_DEPENDENCY_FILENAME}")
        return

    save_local_version(latest_version, last_modified)
    print(f"Updated to version {latest_version}")


if __name__ == "__main__":
    update_lib()
