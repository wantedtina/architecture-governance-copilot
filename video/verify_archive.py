"""Check archived bytes without executing production tools or modifying media."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        choices=("all", "tracked"),
        default="all",
        help="Check all local archive files, or only entries tracked in the Git index.",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    selected = None
    if args.scope == "tracked":
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", "video/"],
            cwd=root.parent,
            check=True,
            capture_output=True,
        )
        selected = {
            name.decode().removeprefix("video/") for name in result.stdout.split(b"\0") if name
        }
    manifest = json.loads((root / "ARCHIVE_MANIFEST.json").read_text())
    errors = []
    checked = 0
    skipped = 0
    for item in manifest["files"]:
        if selected is not None and item["file"] not in selected:
            skipped += 1
            continue
        path = root / item["file"]
        checked += 1
        if not path.is_file():
            errors.append(f"Missing file: {item['file']}")
        elif (
            path.stat().st_size != item["bytes"]
            or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]
        ):
            errors.append(f"Content mismatch: {item['file']}")
    if not checked:
        errors.append("No manifest entries selected; stage or restore the archive first.")
    recordings = json.loads((root / "v2/narration/RECORDINGS.json").read_text())
    if args.scope == "all":
        if len(recordings["files"]) != 12:
            errors.append("Expected twelve original recordings.")
        for item in recordings["files"]:
            path = root / "v2/narration/raw" / item["filename"]
            if (
                not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]
            ):
                errors.append(f"Recording mismatch: {item['filename']}")
    for name in ["v2/narration/NARRATION.md", "v2/narration/SUBTITLES.srt"]:
        if "That's our response to the feedback." in (root / name).read_text():
            errors.append(f"Removed sentence found in {name}")
    if errors:
        raise SystemExit(
            "\n".join(errors) + "\nA checkout omits ignored local media; "
            "use --scope tracked or restore the full archive."
        )
    print(
        f"PASS: {checked} manifest entries checked, {skipped} skipped; "
        f"final script/captions preserved. Scope: {args.scope}. No rendering performed."
    )


if __name__ == "__main__":
    main()
