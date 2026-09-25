"""
KoboToolbox — Bulk share a project with many user accounts via the API.

Reads (username, permissions) pairs from a CSV and grants each user those
permissions on a project, using the bulk permission-assignments endpoint
(recommended for many users — the web UI gets slow/unresponsive beyond a
handful of users).

Run it directly and it will prompt for the token, project UID, and CSV path,
so this also works when packaged as a standalone .exe.

Docs: https://community.kobotoolbox.org/t/assign-permissions-to-lots-of-users-with-the-api/24303
"""

import csv
import sys
import requests

DEFAULT_KOBO_DOMAIN = "kf.kobotoolbox.org"   # change if self-hosted / other server
USERNAME_COLUMN = "username"
PERMISSIONS_COLUMN = "permissions"
PERMISSIONS_DELIMITER = "|"


def read_users_from_csv(csv_path, username_column, permissions_column, delimiter):
    """
    Read (username, [permissions]) pairs from a CSV file.

    Returns a list of dicts: [{"username": "user1", "permissions": ["add_submissions", ...]}, ...]
    Rows with an empty username or empty permissions are skipped.
    """
    users = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for col in (username_column, permissions_column):
            if col not in fieldnames:
                raise ValueError(
                    f"Column '{col}' not found in {csv_path}. "
                    f"Available columns: {fieldnames}"
                )

        for row in reader:
            username = (row.get(username_column) or "").strip()
            raw_permissions = (row.get(permissions_column) or "").strip()

            if not username or not raw_permissions:
                continue

            permissions = [
                p.strip() for p in raw_permissions.split(delimiter) if p.strip()
            ]
            if permissions:
                users.append({"username": username, "permissions": permissions})

    return users


def build_payload(users, base_url):
    """Build the JSON array expected by the bulk permission-assignments endpoint."""
    payload = []
    for user in users:
        for perm in user["permissions"]:
            payload.append(
                {
                    "user": f"{base_url}/users/{user['username']}/",
                    "permission": f"{base_url}/permissions/{perm}/",
                }
            )
    return payload


def share_project(asset_uid, users, token, base_url):
    url = f"{base_url}/assets/{asset_uid}/permission-assignments/bulk/"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }
    payload = build_payload(users, base_url)

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code in (200, 201):
        print(f"Success: shared project with {len(users)} user(s).")
    else:
        print(f"Failed (status {response.status_code}):")
        print(response.text)

    return response


def prompt(text, default=None):
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or default


def main():
    print("=== KoboToolbox Bulk Project Sharing ===\n")

    domain = prompt("Kobo domain", DEFAULT_KOBO_DOMAIN)
    base_url = f"https://{domain}/api/v2"

    token = prompt("API token (from https://%s/token/)" % domain)
    if not token:
        sys.exit("An API token is required.")

    asset_uid = prompt("Project (asset) UID")
    if not asset_uid:
        sys.exit("A project UID is required.")

    csv_path = prompt("Path to CSV file", "users.csv")

    try:
        users = read_users_from_csv(
            csv_path, USERNAME_COLUMN, PERMISSIONS_COLUMN, PERMISSIONS_DELIMITER
        )
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"Error reading CSV: {e}")

    print(f"\nLoaded {len(users)} user(s) from {csv_path}.")
    if not users:
        sys.exit("No valid users found in the CSV — nothing to do.")

    share_project(asset_uid, users, token, base_url)
    input("\nDone. Press Enter to exit.")


if __name__ == "__main__":
    main()