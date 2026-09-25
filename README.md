# Kobo Bulk Share

A small command-line tool for bulk-sharing a [KoboToolbox](https://www.kobotoolbox.org/) project with many user accounts at once, using the KoboToolbox API's `permission-assignments/bulk/` endpoint.

Useful when you need to grant dozens (or hundreds) of users access to submit, view, or manage data on a project — the KoboToolbox web UI becomes slow and unresponsive when sharing with large numbers of users manually, one at a time.

## Features

- Reads usernames and their permissions from a CSV file
- Supports **different permissions per user** in the same run
- Prompts interactively for your API token, project UID, and CSV path — nothing to hardcode or edit in the script
- Works as a plain Python script or as a packaged standalone `.exe` (see [Packaging as an .exe](#packaging-as-an-exe))

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/)
- A KoboToolbox account with permission to manage sharing on the target project
- Your KoboToolbox API token (get it at `https://<your-domain>/token/`, e.g. `https://kf.kobotoolbox.org/token/`)
- The project's asset UID (found in the project's URL in the Kobo dashboard)

## Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

Or just install the one dependency directly:

```bash
pip install requests
```

## Usage

Prepare a CSV file with a `username` column and a `permissions` column. Multiple permissions for the same user are separated by `|`:

```csv
username,permissions
user1,add_submissions
user2,add_submissions|view_submissions
user3,view_submissions|change_submissions|validate_submissions
```

Run the script:

```bash
python kobo_bulk_share.py
```

You'll be prompted for:

| Prompt | Description |
|---|---|
| Kobo domain | Defaults to `kf.kobotoolbox.org`; change if self-hosted |
| API token | From your KoboToolbox account |
| Project (asset) UID | The project you're sharing |
| Path to CSV file | Defaults to `users.csv` in the current folder |

The script then bulk-assigns the listed permissions to each user and prints a success or failure message.

## Valid permission slugs

| Slug | Description |
|---|---|
| `view_asset` | Preview the form |
| `add_submissions` | Submit data (auto-grants `view_asset`) |
| `view_submissions` | View submitted data |
| `change_submissions` | Edit submitted data |
| `validate_submissions` | Approve/reject submissions |
| `delete_submissions` | Delete submissions |
| `change_asset` | Edit the form itself |
| `manage_asset` | Full project control (includes all of the above) |

Granting a higher-level permission automatically includes the ones it depends on — e.g. you don't need to list `view_asset` alongside `add_submissions`.

## Package .exe

To distribute this as a standalone Windows executable (no Python required on the recipient's machine):

```bash
pip install pyinstaller
pyinstaller --onefile --console kobo_bulk_share.py
```

The executable will be created at `dist/kobo_bulk_share.exe`.

> **Note:** PyInstaller does not cross-compile — build on Windows (or a Windows CI runner) to produce a Windows `.exe`.

Each recipient supplies their own API token when the tool runs, so no credentials are baked into the executable.

## Security notes

- Your API token grants access to your KoboToolbox account — don't share it or commit it to version control.
- This tool never stores your token; it's used only for the duration of the script run.

## Contributing

Issues and pull requests are welcome.
