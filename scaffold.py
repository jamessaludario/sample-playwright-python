"""
scaffold.py — create a test project for YOUR web app
====================================================
Run it from the starter kit folder:

    python scaffold.py

It asks two questions (project name, app URL) and creates a fresh,
independent test project NEXT TO the kit folder:

    ../<project-name>-tests/

The new folder has the full structure (pages/, helpers/, tests/, ...),
a smoke test that should pass immediately, the AI prompts, and a .env
already filled in with your answers. The starter kit itself is never
modified — scaffold as many projects as you like.

Non-interactive use:

    python scaffold.py --name my-app --url https://my-app.example.com
    python scaffold.py --name my-app --url http://localhost:3000 --dest C:/work/my-app-tests

Adding tests to an EXISTING repository (e.g. an e2e/ folder inside your
app's repo)? Point --dest at it and add --into-existing: files you
already have are left untouched, only missing ones are added.

Prefer not to clone the kit at all? Create your repo straight from the
GitHub template instead:
https://github.com/jamessaludario/qa-test-template-python
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).parent
TEMPLATE = KIT / "template"
PROMPTS = KIT / "prompts"


def ask(question, default=None):
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"  {question}{suffix}: ").strip()
    except EOFError:
        answer = ""
    return answer or default or ""


def copy_tree(sources, dest, skip_existing):
    """
    Copy every file from the source trees into dest, returning the list
    of files skipped because they already existed (only possible with
    skip_existing — otherwise we only ever write into a fresh folder).
    """
    skipped = []
    for src_root, prefix in sources:
        for src in src_root.rglob("*"):
            if not src.is_file():
                continue
            target = dest / prefix / src.relative_to(src_root)
            if target.exists():
                if skip_existing:
                    skipped.append(target)
                    continue
                sys.exit(f"\n  Refusing to overwrite existing file: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    return skipped


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new test project")
    parser.add_argument("--name", help="short project name, e.g. my-app")
    parser.add_argument("--url", help="the app's address, e.g. https://my-app.example.com")
    parser.add_argument("--dest", help="where to create the project (default: ../<name>-tests)")
    parser.add_argument(
        "--into-existing", action="store_true",
        help="allow a non-empty destination; existing files are kept, missing ones added",
    )
    options = parser.parse_args()

    print()
    print("  QA STARTER KIT - scaffold a test project for your web app")
    print()

    name = options.name or ask("Project name (short, no spaces)", "my-app")
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or "my-app"

    url = options.url or ask("Your app's URL", "http://localhost:3000")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    dest = Path(options.dest) if options.dest else KIT.parent / f"{name}-tests"
    if dest.exists() and any(dest.iterdir()) and not options.into_existing:
        sys.exit(
            f"\n  {dest} already exists and is not empty - not touching it.\n"
            "  (Adding tests to an existing repo? Re-run with --into-existing.)"
        )
    dest.mkdir(parents=True, exist_ok=True)

    # 1. Copy the template (the project skeleton) and the AI prompts.
    skipped = copy_tree(
        [(TEMPLATE, Path("")), (PROMPTS, Path("prompts"))],
        dest,
        skip_existing=options.into_existing,
    )

    # 2. Write the .env with the answers (the template's .env.example
    #    stays too, as documentation).
    env_file = dest / ".env"
    if env_file.exists():
        skipped.append(env_file)
    else:
        env_file.write_text(
            f"PROJECT_NAME={name}\nBASE_URL={url}\n", encoding="utf-8"
        )

    # 3. Personalize the README (only if it came from the template).
    readme = dest / "README.md"
    if readme.exists() and readme not in skipped:
        readme.write_text(
            readme.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", name),
            encoding="utf-8",
        )

    print(f"\n  Created: {dest}")
    if skipped:
        print(f"\n  Kept your {len(skipped)} existing file(s) untouched:")
        for path in skipped:
            print(f"    - {path.relative_to(dest)}")
    print(f"""
  Next steps:

    cd {dest}
    pip install -r requirements.txt   (skip if already installed)
    playwright install chromium       (skip if already installed)
    pytest tests/test_smoke.py        <- should pass immediately

  Then grow the suite:

    - With an AI agent: open the folder in your agent and feed it
      prompts/00-quick-start.md  (conventions live in CLAUDE.md)
    - By hand: copy pages/example_page.py.template and go

  Happy testing!""")


if __name__ == "__main__":
    main()
