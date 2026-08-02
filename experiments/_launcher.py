"""Shared launcher for the run scripts in this folder.

Every script here is a thin CONFIG block plus a call to :func:`train` or :func:`play`.
The real work still happens in ``scripts/rsl_rl/train.py`` and ``scripts/rsl_rl/play.py``;
this module just synthesizes the command line they expect and hands off.

Why hand off instead of importing them: both scripts parse arguments, launch Isaac Sim,
and bind the Hydra task name at *module scope*, so there is no importable entry point to
call with parameters. ``runpy`` executes them exactly as ``python scripts/rsl_rl/train.py``
would, but in this process -- so Ctrl-C in the terminal takes the simulator down with it,
and breakpoints in the env/reward code are hit when you launch with F5.
"""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts" / "rsl_rl"

# argparse dest -> flag, for the few flags that are not just --<key>
FLAG_NAMES = {"real_time": "--real-time"}


def config_to_argv(config: dict) -> list[str]:
    """Turn a CONFIG dict into command-line arguments.

    ``None`` and ``False`` entries are dropped so the underlying script keeps its own
    default, ``True`` becomes a bare flag, anything else becomes ``--key value``.
    """
    argv = []
    for key, value in config.items():
        if value is None or value is False:
            continue
        flag = FLAG_NAMES.get(key, f"--{key}")
        if value is True:
            argv.append(flag)
        else:
            argv.extend([flag, str(value)])
    return argv


def run_script(script_name: str, argv: list[str]) -> None:
    """Execute ``scripts/rsl_rl/<script_name>`` with ``argv`` as its command line."""
    script = SCRIPTS_DIR / script_name

    # train.py/play.py build their log paths from a relative "logs/rsl_rl/...", so they
    # must run from the repo root. The VS Code play button already uses the workspace
    # root, but this keeps the scripts correct from any working directory.
    os.chdir(REPO_ROOT)

    # both scripts do a bare `import cli_args`, which only resolves because Python puts
    # the script's own directory on sys.path when it is invoked directly.
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))

    sys.argv = [str(script), *argv]
    print(f"[experiments] {script_name} {' '.join(argv)}\n")

    try:
        runpy.run_path(str(script), run_name="__main__")
    except KeyboardInterrupt:
        print("\n[experiments] interrupted")
        raise SystemExit(130)


def train(config: dict, overrides: list[str] | None = None) -> None:
    """Launch training. ``overrides`` are Hydra dotted overrides (see the run scripts)."""
    run_script("train.py", config_to_argv(config) + list(overrides or []))


def play(config: dict) -> None:
    """Launch inference on a trained checkpoint.

    No Hydra overrides here: play.py uses ``parse_args`` rather than ``parse_known_args``,
    so any extra argument is a hard error.
    """
    run_script("play.py", config_to_argv(config))
