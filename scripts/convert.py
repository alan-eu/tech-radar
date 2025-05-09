"""
Run from the root directory:
python scripts/convert.py
"""

import subprocess

FILE_PATH = "tech_radar.csv"


def get_revision_and_dates() -> list[tuple[str, str]]:
    """
    Get the revision and dates from the tech_radar.csvfile.
    """
    revisions = []
    output = subprocess.check_output(
        ["git", "log", '--pretty=format:"%h %ad"', "--date=short", FILE_PATH]
    )
    for line in output.decode("utf-8").split("\n"):
        revision, date_str = line.strip('"').split(" ")
        revisions.append((date_str, revision))

    # Keep a single revision for each date
    unique_revisions = []
    previous_date = None
    for date_str, revision in reversed(revisions):
        if date_str != previous_date:
            previous_date = date_str
            unique_revisions.append((date_str, revision))

    unique_revisions.reverse()

    return unique_revisions


def get_revision_content(revision: str) -> str:
    """
    Get the content of the revision.
    """
    return subprocess.check_output(["git", "show", f"{revision}:{FILE_PATH}"]).decode(
        "utf-8"
    )


if __name__ == "__main__":
    for date_str, revision in get_revision_and_dates():
        content = get_revision_content(revision)
        print(content)
