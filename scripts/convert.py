"""
Run from the root directory:
python scripts/convert.py
"""

import csv
import os
import string
import subprocess

FILE_PATH = "tech_radar.csv"
RADAR_PATH = "radar"

QUADRANTS_MAP = {
    "Languages & Frameworks": "languages-and-frameworks",
    "Techniques": "techniques",
    "Platforms": "platforms",
    "Tools": "tools",
}

RINGS_MAP = {
    "Adopt": "adopt",
    "Trial": "trial",
    "Assess": "assess",
    "Hold": "hold",
}


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


def get_revision_headers(content: str) -> list[str]:
    """
    Get the headers of the revision.
    """
    return [
        header.strip()
        for header in content.strip("\ufeff").split("\n")[0].strip().split(",")
    ]


def parse_revision_content(content: str, headers: list[str]) -> list[tuple[str, str]]:
    """
    Parse the content of the revision.
    """
    reader = csv.DictReader(content.split("\n"), fieldnames=headers)
    next(reader)  # Skip the header row
    return [row for row in reader]


def get_file_name(row: dict) -> str:
    """
    Get the file name for an entry in the tech radar.
    """
    name = row["name"].lower()
    name = "".join(c for c in name if c in string.ascii_lowercase or c in string.digits or c == " ")    
    name = name.strip()
    name = name.replace(" ", "-")
    return f"{name}.md"


def get_file_template(row: dict) -> str:
    """
    Get the Markdown template for an entry in the tech radar.
    """
    quadrant = QUADRANTS_MAP[row["quadrant"]]
    ring = RINGS_MAP[row["ring"]]
    return f"""---
title: {row["name"]}
ring: {ring}
quadrant: {quadrant}
tags: []
---

{row["description"]}
"""


def has_state_changed(previous_state: dict | None, new_state: dict) -> bool:
    if previous_state is None:
        return True
    for k, v in previous_state.items():
        if k == "isNew":
            continue
        if v != new_state[k]:
            return True
    return False


def main():
    os.makedirs(RADAR_PATH, exist_ok=True)

    previous_states = {}

    for date_str, revision in get_revision_and_dates():
        os.makedirs(os.path.join(RADAR_PATH, date_str), exist_ok=True)
        content = get_revision_content(revision)
        headers = get_revision_headers(content)
        for row in parse_revision_content(content, headers):
            previous_state = previous_states.get(row["name"])
            if has_state_changed(previous_state, row):
                with open(
                    os.path.join(RADAR_PATH, date_str, get_file_name(row)), "w"
                ) as f:
                    f.write(get_file_template(row))
            previous_states[row["name"]] = row


if __name__ == "__main__":
    main()
