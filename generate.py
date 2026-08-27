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


def tweet_to_viewer(label: str, host: str, examples: list[str]) -> dict:
    return rule(
        title=f"{label} status to Twitter Web Viewer",
        pattern=(
            rf"^https://(?:www\.)?{esc(host)}/"
            rf"(?:[^/]+/status/|i/status/|i/web/status/)(\d+)(?:[\?#].*)?$"
        ),
        dest="https://twitterwebviewer.com/?tweet=$1",
        examples=examples,
        comments=(
            "Extracts the numeric tweet id from status URLs. "
            "Query strings like `?s=20` are dropped on purpose."
        ),
    )


def kill_remaining(label: str, host: str, examples: list[str]) -> dict:
    return rule(
        title=f"Kill other {label} URLs",
        pattern=rf"^https://(?:www\.)?{esc(host)}/.*$",
        dest=KILL,
        examples=examples,
        comments="Profiles, search, and other non-status X URLs. Put this after the status rewrite.",
    )


def kill_host(label: str, host: str, examples: list[str]) -> dict:
    return rule(
        title=f"Kill {label}",
        pattern=rf"^https://(?:www\.)?{esc(host)}/.*$",
        dest=KILL,
        examples=examples,
        comments="Whole-site kill. Add more hosts like this for TikTok and so on.",
    )


def main() -> None:
    redirects = [
        kill_root("X", "x.com", ["https://x.com/", "https://www.x.com", "https://x.com/?lang=en"]),
        kill_root("Twitter", "twitter.com", ["https://twitter.com/", "https://www.twitter.com"]),
        kill_path("X", "x.com", "home", ["https://x.com/home", "https://www.x.com/home"]),
        kill_path("Twitter", "twitter.com", "home", ["https://twitter.com/home"]),
        kill_path("X", "x.com", "explore", ["https://x.com/explore"]),
        kill_path("Twitter", "twitter.com", "explore", ["https://twitter.com/explore"]),
        tweet_to_viewer(
            "X",
            "x.com",
            [
                "https://x.com/resend/status/2091897900800635319?s=20",
                "https://www.x.com/user/status/123",
                "https://x.com/i/status/123",
            ],
        ),
        tweet_to_viewer(
            "Twitter",
            "twitter.com",
            [
                "https://twitter.com/resend/status/2091897900800635319?s=20",
                "https://www.twitter.com/user/status/123",
            ],
        ),
        kill_remaining("X", "x.com", ["https://x.com/resend", "https://x.com/search?q=hi"]),
        kill_remaining(
            "Twitter",
            "twitter.com",
            ["https://twitter.com/resend", "https://twitter.com/search?q=hi"],
        ),
        kill_root(
            "Twitter Web Viewer",
            "twitterwebviewer.com",
            ["https://twitterwebviewer.com/", "https://www.twitterwebviewer.com/"],
        ),
        kill_root("Facebook", "facebook.com", ["https://www.facebook.com/", "https://facebook.com/"]),
        kill_path("Facebook", "facebook.com", "home", ["https://www.facebook.com/home"]),
        kill_root("Facebook mobile", "m.facebook.com", ["https://m.facebook.com/"]),
        kill_path("Facebook mobile", "m.facebook.com", "home", ["https://m.facebook.com/home"]),
        kill_root("Instagram", "instagram.com", ["https://www.instagram.com/", "https://instagram.com/"]),
        kill_path("Instagram", "instagram.com", "explore", ["https://www.instagram.com/explore/"]),
        kill_path("Instagram", "instagram.com", "reels", ["https://www.instagram.com/reels/"]),
        kill_root("Instagram mobile", "m.instagram.com", ["https://m.instagram.com/"]),
        kill_root("Reddit", "reddit.com", ["https://www.reddit.com/", "https://reddit.com"]),
        kill_path("Reddit", "reddit.com", "r/all", ["https://www.reddit.com/r/all"]),
        kill_path("Reddit", "reddit.com", "r/popular", ["https://www.reddit.com/r/popular"]),
        kill_root("Safereddit", "safereddit.com", ["https://safereddit.com/"]),
        kill_path("Safereddit", "safereddit.com", "r/all", ["https://safereddit.com/r/all"]),
        kill_path("Safereddit", "safereddit.com", "r/popular", ["https://safereddit.com/r/popular"]),
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
