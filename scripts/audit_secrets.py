"""Check non-ignored repository files without printing any candidate secret."""
import re
import subprocess
import sys
from pathlib import Path


def main():
    names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"]).decode().split("\0")
    pattern = re.compile(rb"sk-(?:ws-)?[A-Za-z0-9._-]{20,}")
    hits = []
    for name in names:
        if name and Path(name).is_file() and pattern.search(Path(name).read_bytes()):
            hits.append(name)
    if hits:
        print("Potential credential found in files (values withheld): " + ", ".join(hits))
        return 1
    print("PASS: no credential-shaped strings found in tracked/non-ignored files; ignored .env not scanned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
