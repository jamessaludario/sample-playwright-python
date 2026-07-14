"""
scaffold.py — create a test project for YOUR web app
====================================================
Run it from the starter kit folder:

    python scaffold.py

It asks a few questions (project name, app URL, which framework pieces
you want) and creates a fresh, independent test project NEXT TO the kit:

    ../<project-name>-tests/

The new folder gets the chosen structure, a smoke test that should pass
immediately, the AI prompts, and a .env already filled in with your
answers. The starter kit itself is never modified — scaffold as many
projects as you like.

Non-interactive use:

    python scaffold.py --name my-app --url https://my-app.example.com
    python scaffold.py --name my-app --url http://localhost:3000 --dest C:/work/my-app-tests
    python scaffold.py --name my-app --url https://... --include pages,constants
    python scaffold.py --name my-app --url https://... --include none

Adding tests to an EXISTING repository (e.g. an e2e/ folder inside your
app's repo)? Point --dest at it and add --into-existing: files you
already have are left untouched, only missing ones are added.

Prefer not to clone the kit at all? Click "Use this template" on the
kit's GitHub page to get your own copy of everything, then run this
script inside it.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).parent
TEMPLATE = KIT / "template"
PROMPTS = KIT / "prompts"

# ---------------------------------------------------------------------------
# The optional framework pieces
# ---------------------------------------------------------------------------
# Some pieces build on others, so choosing one pulls its needs in too:
#   helpers  use  pages   (journeys are built from page objects)
#   pages    use  constants (for BASE_URL)
#   fixtures use  constants (for the blocked-URL list)

COMPONENTS = ["pages", "helpers", "constants", "fixtures", "utils"]
DEPENDENCIES = {
    "helpers": {"pages"},
    "pages": {"constants"},
    "fixtures": {"constants"},
}

# Which template paths belong to which component. Everything not listed
# here is core and always copied.
COMPONENT_PATHS = {
    "pages": ["pages"],
    "helpers": ["helpers"],
    "constants": ["constants.py"],
    "fixtures": ["fixtures"],
    "utils": ["utils"],
}

# conftest.py and tests/test_smoke.py adapt to the chosen pieces, so
# they are generated rather than copied when anything is excluded.
GENERATED = {"conftest.py", "tests/test_smoke.py"}


def resolve(selection):
    """Add the dependencies of every chosen component. Returns the full
    set and the list that was auto-added (to tell the user)."""
    selected = set(selection)
    added = []
    changed = True
    while changed:
        changed = False
        for component in list(selected):
            for needed in DEPENDENCIES.get(component, ()):
                if needed not in selected:
                    selected.add(needed)
                    added.append(needed)
                    changed = True
    return selected, added


# ---------------------------------------------------------------------------
# Generated files (only used when some components are excluded)
# ---------------------------------------------------------------------------

CONFTEST_HEADER = '''\
"""
conftest.py
===========
pytest automatically loads this file before running any tests.
"""
'''

DOTENV_LOADER = '''
import os
from pathlib import Path


def _load_dotenv():
    """Read the .env file next to this script (if there is one) and put
    its KEY=value lines into the environment."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()
'''

FIXTURES_PLUGINS = '''
# Load the fixture modules (ad blocking, reports, screenshots).
pytest_plugins = [
    "fixtures.browser",
    "fixtures.reporting",
]
'''

SMOKE_DOC = '''\
"""
Your first test: the app loads.

This "smoke test" proves the whole toolchain works end to end — config,
browser, your app's URL — before you invest in real tests. It should
pass immediately after you fill in .env.
"""
'''

SMOKE_BODIES = {
    # what the test opens depends on which pieces exist
    "helpers": '''
from playwright.sync_api import Page, expect

from helpers.flows import open_app


def test_app_loads(page: Page):
    # Step 1: open the app's front page (BASE_URL from your .env)
    open_app(page)
''',
    "pages": '''
from playwright.sync_api import Page, expect

from pages import BasePage


def test_app_loads(page: Page):
    # Step 1: open the app's front page (BASE_URL from your .env)
    BasePage(page).open()
''',
    "constants": '''
from playwright.sync_api import Page, expect

from constants import BASE_URL


def test_app_loads(page: Page):
    # Step 1: open the app's front page (BASE_URL from your .env)
    page.goto(BASE_URL)
''',
    "bare": '''
import os

from playwright.sync_api import Page, expect


def test_app_loads(page: Page):
    # Step 1: open the app's front page (BASE_URL from your .env,
    # loaded by conftest.py)
    page.goto(os.environ["BASE_URL"])
''',
}

SMOKE_CHECKS = '''
    # Step 2: the page rendered something — it has a title...
    expect(page).not_to_have_title("")

    # ...and a visible body. Replace these generic checks with something
    # specific to YOUR app (its heading, its logo, its login button).
    expect(page.locator("body")).to_be_visible()
'''


def build_conftest(selected):
    parts = [CONFTEST_HEADER]
    if "constants" not in selected:
        parts.append(DOTENV_LOADER)  # someone has to load .env
    if "fixtures" in selected:
        parts.append(FIXTURES_PLUGINS)
    return "".join(parts)


def build_smoke_test(selected):
    for flavor in ("helpers", "pages", "constants"):
        if flavor in selected:
            return SMOKE_DOC + SMOKE_BODIES[flavor] + SMOKE_CHECKS
    return SMOKE_DOC + SMOKE_BODIES["bare"] + SMOKE_CHECKS


# ---------------------------------------------------------------------------
# The scaffolding itself
# ---------------------------------------------------------------------------

def ask(question, default=None):
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"  {question}{suffix}: ").strip()
    except EOFError:
        answer = ""
    return answer or default or ""


def choose_components(flag_value):
    """Turn the --include flag (or an interactive answer) into a set."""
    if flag_value is None:
        print("  Framework pieces: pages, helpers, constants, fixtures, utils")
        flag_value = ask(
            'Include which? ("all", "none", or a comma list)', "all"
        )
    value = flag_value.strip().lower()
    if value in ("", "all"):
        return set(COMPONENTS), []
    if value == "none":
        return resolve([])
    wanted = [part.strip() for part in value.split(",") if part.strip()]
    unknown = [part for part in wanted if part not in COMPONENTS]
    if unknown:
        sys.exit(f"\n  Unknown component(s): {', '.join(unknown)}. "
                 f"Choose from: {', '.join(COMPONENTS)}")
    return resolve(wanted)


def component_of(relative_path):
    """Which component a template file belongs to (None = core)."""
    for component, roots in COMPONENT_PATHS.items():
        for root in roots:
            if relative_path == root or relative_path.startswith(root + "/"):
                return component
    return None


def copy_tree(sources, dest, selected, skip_existing):
    """Copy the wanted files, returning (copied, skipped-existing)."""
    skipped = []
    for src_root, prefix in sources:
        for src in src_root.rglob("*"):
            if not src.is_file():
                continue
            relative = src.relative_to(src_root).as_posix()
            if prefix == "" and (
                relative in GENERATED and selected != set(COMPONENTS)
            ):
                continue  # generated variant will be written instead
            if prefix == "" and component_of(relative) not in (None, *selected):
                continue  # an excluded component's file
            target = dest / prefix / Path(relative)
            if target.exists():
                if skip_existing:
                    skipped.append(target)
                    continue
                sys.exit(f"\n  Refusing to overwrite existing file: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    return skipped


def write_if_missing(path, content, skipped):
    if path.exists():
        skipped.append(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new test project")
    parser.add_argument("--name", help="short project name, e.g. my-app")
    parser.add_argument("--url", help="the app's address, e.g. https://my-app.example.com")
    parser.add_argument("--dest", help="where to create the project (default: ../<name>-tests)")
    parser.add_argument(
        "--include",
        help='framework pieces: "all" (default), "none", or a comma list '
             f'from: {", ".join(COMPONENTS)}',
    )
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

    selected, auto_added = choose_components(options.include)
    if auto_added:
        print(f"  (Also including {', '.join(sorted(set(auto_added)))} - "
              "needed by your choices.)")

    dest = Path(options.dest) if options.dest else KIT.parent / f"{name}-tests"
    if dest.exists() and any(dest.iterdir()) and not options.into_existing:
        sys.exit(
            f"\n  {dest} already exists and is not empty - not touching it.\n"
            "  (Adding tests to an existing repo? Re-run with --into-existing.)"
        )
    dest.mkdir(parents=True, exist_ok=True)

    # 1. Copy the template (the project skeleton) and the AI prompts.
    skipped = copy_tree(
        [(TEMPLATE, ""), (PROMPTS, "prompts")],
        dest, selected, skip_existing=options.into_existing,
    )

    # 2. Files that adapt to the chosen pieces.
    if selected != set(COMPONENTS):
        write_if_missing(dest / "conftest.py", build_conftest(selected), skipped)
        write_if_missing(
            dest / "tests" / "test_smoke.py", build_smoke_test(selected), skipped
        )
        if "constants" not in selected:
            # run_tests.py reads the project name from constants.py —
            # point it at the environment instead.
            run_tests = dest / "run_tests.py"
            if run_tests.exists() and run_tests not in skipped:
                run_tests.write_text(
                    run_tests.read_text(encoding="utf-8").replace(
                        "from constants import PROJECT_NAME",
                        'import os\n\nPROJECT_NAME = os.environ.get("PROJECT_NAME", "My app")',
                    ),
                    encoding="utf-8",
                )

    # 3. Write the .env with the answers (the template's .env.example
    #    stays too, as documentation).
    env_file = dest / ".env"
    if env_file.exists():
        skipped.append(env_file)
    else:
        env_file.write_text(
            f"PROJECT_NAME={name}\nBASE_URL={url}\n", encoding="utf-8"
        )

    # 4. Personalize the README (only if it came from the template).
    readme = dest / "README.md"
    if readme.exists() and readme not in skipped:
        readme.write_text(
            readme.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", name),
            encoding="utf-8",
        )

    print(f"\n  Created: {dest}")
    print(f"  Included pieces: {', '.join(c for c in COMPONENTS if c in selected) or '(bare minimum)'}")
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
