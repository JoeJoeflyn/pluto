"""
Local sync — push or pull the SQLite file to a shared folder.

Last-write-wins, no conflict resolution. Intended for the CLI/web app
running on the same machine, or pointed at a Dropbox/OneDrive/USB folder.
"""
from __future__ import annotations

import os
import shutil


def sync_database(folder: str, direction: str, db_path: str) -> dict:
    """
    `direction` is 'push', 'pull', or 'auto':
      - push: copy local db_path -> folder/expenses.db
      - pull: copy folder/expenses.db -> local db_path
      - auto: pull if remote is newer, otherwise push
    """
    folder = os.path.abspath(os.path.expanduser(folder))
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    db_path = os.path.abspath(db_path)
    if not os.path.exists(db_path):
        raise FileNotFoundError("Local database file is missing")

    target = os.path.join(folder, "expenses.db")

    if direction == "push":
        shutil.copy2(db_path, target)
        return {
            "action": "push",
            "folder": folder,
            "detail": f"Copied to {target}",
        }

    if direction == "pull":
        if not os.path.exists(target):
            raise FileNotFoundError(f"No database found at {target}")
        shutil.copy2(target, db_path)
        return {
            "action": "pull",
            "folder": folder,
            "detail": f"Restored from {target}",
        }

    if os.path.exists(target) and os.path.getmtime(target) > os.path.getmtime(db_path):
        shutil.copy2(target, db_path)
        return {
            "action": "auto-pull",
            "folder": folder,
            "detail": "Remote was newer; pulled.",
        }
    shutil.copy2(db_path, target)
    return {
        "action": "auto-push",
        "folder": folder,
        "detail": "Local was newer; pushed.",
    }
