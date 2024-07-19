import os
from typing import Any, Dict, Optional

import requests

GITHUB_API_URL = "https://api.github.com/repos/bogdanfinn/tls-client/releases/latest"
LOCAL_VERSION_FILE = os.path.join(os.path.dirname(__file__), "dependencies/version.txt")
DOWNLOAD_DIR = os.path.dirname(LOCAL_VERSION_FILE)

dependency_filenames = {
    "tls-client-windows-32": "tls-client-32.dll",
    "tls-client-windows-64": "tls-client-64.dll",
    "tls-client-darwin-arm64": "tls-client-arm64.dylib",
    "tls-client-darwin-amd64": "tls-client-x86.dylib",
    "tls-client-linux-alpine-amd64": "tls-client-amd64.so",
    "tls-client-linux-ubuntu-amd64": "tls-client-x86.so",
    "tls-client-linux-arm64": "tls-client-arm64.so",
}


def get_latest_release(session: requests.Session) -> Optional[Dict[str, Any]]:
    response = session.get(GITHUB_API_URL)
    response.raise_for_status()
    latest_release = response.json()
    return latest_release


def read_local_version() -> Optional[str]:
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    return None


def save_local_version(version: str) -> None:
    with open(os.path.join(LOCAL_VERSION_FILE), "w") as f:
        f.write(version)


def download_file(session: requests.Session, url: str, dest_path: str) -> None:
    response = session.get(url)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(response.content)


def update_lib() -> None:
    session = requests.Session()

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    latest_release = get_latest_release(session)
    if latest_release is None:
        return

    latest_version = latest_release["tag_name"]
    local_version = read_local_version()

    if latest_version == local_version:
        return
    print(f"New version found: {latest_version}. Updating...")

    assets = latest_release["assets"]
    for asset in assets:
        asset_name = asset["name"].rsplit("-", 1)[0]
        if asset_name in dependency_filenames:
            download_url = asset["browser_download_url"]
            dest_filename = dependency_filenames[asset_name]
            dest_path = os.path.join(DOWNLOAD_DIR, dest_filename)
            download_file(session, download_url, dest_path)
            print(f"Downloaded {dest_filename} from {download_url}")

    save_local_version(latest_version)
    print(f"Updated to version {latest_version}")


if __name__ == "__main__":
    update_lib()
