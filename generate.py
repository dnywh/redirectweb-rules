#!/usr/bin/env python3
"""Generate rules.redirectweb for RedirectWeb import."""

from __future__ import annotations

import json
from pathlib import Path

KILL = "https://example.com/"
BUNDLE = "io.github.mshibanami.RedirectWebForSafari"
OUT = Path(__file__).with_name("rules.redirectweb")


def esc(host: str) -> str:
    return host.replace(".", r"\.")


def rule(*, title: str, pattern: str, dest: str, examples: list[str], comments: str = "") -> dict:
    return {
        "kind": "Redirect",
        "type": "declarativeNetRequestRedirect",
        "title": title,
        "isEnabled": True,
        "sourceURLPattern": {"type": "regularExpression", "value": pattern},
        "destinationURLPattern": dest,
        "resourceTypes": ["main_frame"],
        "exampleURLs": examples,
        "excludeURLPatterns": [],
        "captureGroupProcesses": [],
        "comments": comments,
        "commentsOptions": {"format": "markdown"},
        "targetBrowserOptions": {"browsers": [], "selectionType": "including"},
    }


def kill_root(label: str, host: str, examples: list[str]) -> dict:
    return rule(
        title=f"Kill {label} root",
        pattern=rf"^https://(?:www\.)?{esc(host)}/?([\?#].*)?$",
        dest=KILL,
        examples=examples,
        comments=(
            "Matches with and without www. Safari DNR cannot use `|`, "
            "so different hosts stay as separate rules."
        ),
    )


def kill_path(label: str, host: str, path: str, examples: list[str]) -> dict:
    path = path.strip("/")
    return rule(
        title=f"Kill {label} /{path}",
        pattern=rf"^https://(?:www\.)?{esc(host)}/{path}/?([\?#].*)?$",
        dest=KILL,
        examples=examples,
    )


def rewrite(label: str, host: str, dest_host: str, examples: list[str]) -> dict:
    return rule(
        title=f"{label} to {dest_host}",
        pattern=rf"^https://(?:www\.)?{esc(host)}/(.*)$",
        dest=f"https://{dest_host}/$1",
        examples=examples,
        comments=(
            "`(?:www.)?` is non-capturing, so `$1` is the path. "
            "Do not use `(www.)?` or `$1` becomes `www.`."
        ),
    )


def kill_host(label: str, host: str, examples: list[str]) -> dict:
    return rule(
        title=f"Kill {label}",
        pattern=rf"^https://(?:www\.)?{esc(host)}/.*$",
        dest=KILL,
        examples=examples,
        comments="Whole-site kill. Add more hosts like this for Instagram, TikTok, and so on.",
    )


def main() -> None:
    redirects = [
        kill_root("X", "x.com", ["https://x.com/", "https://www.x.com", "https://x.com/?lang=en"]),
        kill_root("Twitter", "twitter.com", ["https://twitter.com/", "https://www.twitter.com"]),
        kill_path("X", "x.com", "home", ["https://x.com/home", "https://www.x.com/home"]),
        kill_path("Twitter", "twitter.com", "home", ["https://twitter.com/home"]),
        kill_path("X", "x.com", "explore", ["https://x.com/explore"]),
        kill_path("Twitter", "twitter.com", "explore", ["https://twitter.com/explore"]),
        kill_root("xcancel", "xcancel.com", ["https://xcancel.com/"]),
        kill_path("xcancel", "xcancel.com", "home", ["https://xcancel.com/home"]),
        kill_path("xcancel", "xcancel.com", "explore", ["https://xcancel.com/explore"]),
        kill_root("Reddit", "reddit.com", ["https://www.reddit.com/", "https://reddit.com"]),
        kill_path("Reddit", "reddit.com", "r/all", ["https://www.reddit.com/r/all"]),
        kill_path("Reddit", "reddit.com", "r/popular", ["https://www.reddit.com/r/popular"]),
        kill_root("Safereddit", "safereddit.com", ["https://safereddit.com/"]),
        kill_path("Safereddit", "safereddit.com", "r/all", ["https://safereddit.com/r/all"]),
        kill_path("Safereddit", "safereddit.com", "r/popular", ["https://safereddit.com/r/popular"]),
        rewrite(
            "X",
            "x.com",
            "xcancel.com",
            ["https://x.com/user/status/123", "https://www.x.com/user/status/123"],
        ),
        rewrite(
            "Twitter",
            "twitter.com",
            "xcancel.com",
            ["https://twitter.com/search?q=hi", "https://www.twitter.com/search?q=hi"],
        ),
        rewrite(
            "Reddit",
            "reddit.com",
            "safereddit.com",
            ["https://www.reddit.com/r/apple/comments/abc", "https://reddit.com/r/apple"],
        ),
        rewrite("old Reddit", "old.reddit.com", "safereddit.com", ["https://old.reddit.com/r/apple"]),
        rewrite("new Reddit", "new.reddit.com", "safereddit.com", ["https://new.reddit.com/r/apple"]),
        kill_host(
            "Threads",
            "threads.net",
            ["https://www.threads.net/", "https://threads.net/@someone"],
        ),
        kill_host(
            "threads.com",
            "threads.com",
            ["https://www.threads.com/", "https://threads.com/@someone"],
        ),
    ]
    payload = {
        "kind": "RedirectList",
        "bundleID": BUNDLE,
        "formatVersion": "5",
        "redirects": redirects,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT} ({len(redirects)} rules)")


if __name__ == "__main__":
    main()
