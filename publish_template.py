"""
publish_template.py — sync the GitHub template repo (maintainer tool)
=====================================================================
The kit offers a "Use this template" repository so people can start a
test repo for their app WITHOUT cloning the kit:

    https://github.com/jamessaludario/qa-test-template-python

That repo's content is generated from this kit's template/ and prompts/
folders. After changing either, run:

    python publish_template.py

It clones the template repo, replaces its content with a fresh build,
and pushes one sync commit. (Needs push access — you, the maintainer.)
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).parent
TEMPLATE_REPO = "https://github.com/jamessaludario/qa-test-template-python.git"


def run(args, cwd=None):
    print(">>", " ".join(args))
    subprocess.run(args, cwd=cwd, check=True)


def main():
    workdir = Path(tempfile.mkdtemp(prefix="qa-template-publish-"))
    clone = workdir / "repo"
    run(["git", "clone", TEMPLATE_REPO, str(clone)])

    # Wipe everything except git's own bookkeeping...
    for item in clone.iterdir():
        if item.name == ".git":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()

    # ...and rebuild from the kit: template/ is the project skeleton,
    # prompts/ rides along in a prompts/ subfolder.
    shutil.copytree(KIT / "template", clone, dirs_exist_ok=True)
    shutil.copytree(KIT / "prompts", clone / "prompts", dirs_exist_ok=True)

    # The scaffolder personalizes {{PROJECT_NAME}}; template users get a
    # neutral name until they edit it.
    readme = clone / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", "My app"),
        encoding="utf-8",
    )

    # One commit per sync, traceable back to the kit commit it came from.
    kit_sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=KIT, capture_output=True, text=True,
    ).stdout.strip() or "unknown"

    run(["git", "add", "--all"], cwd=clone)
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=clone,
        capture_output=True, text=True,
    ).stdout.strip()
    if not status:
        print("\nTemplate repo is already up to date - nothing to publish.")
        return

    run(["git", "commit", "-m", f"sync from qa-starter-kit-python@{kit_sha}"],
        cwd=clone)
    run(["git", "push"], cwd=clone)
    print("\nPublished. https://github.com/jamessaludario/qa-test-template-python")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(f"\nCommand failed with exit code {error.returncode}.")
