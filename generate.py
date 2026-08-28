#!/usr/bin/env python3
"""Generate rules.redirectweb for RedirectWeb import."""

from __future__ import annotations

import json
from pathlib import Path

KILL = "https://example.com/"
BUNDLE = "io.github.mshibanami.RedirectWebForSafari"
OUT = Path(__file__).with_name("rules.redirectweb")

# Safari + RedirectWeb: DNR is unreliable (regex, pipes, ordering). Use Original only.


def esc(host: str) -> str:
    return host.replace(".", r"\.")


def original_rule(
    *,
    title: str,
    dest: str,
    examples: list[str],
    comments: str = "",
    pattern: str,
    pattern_type: str = "regularExpression",
    exclude_patterns: list[dict[str, str]] | None = None,
) -> dict:
    return {
        "kind": "Redirect",
        "title": title,
        "isEnabled": True,
        "sourceURLPattern": {"type": pattern_type, "value": pattern},
        "destinationURLPattern": dest,
        "exampleURLs": examples,
        "excludeURLPatterns": exclude_patterns or [],
        "captureGroupProcesses": [],
        "comments": comments,
        "commentsOptions": {"format": "markdown"},
        "targetBrowserOptions": {"browsers": [], "selectionType": "including"},
    }


def kill_root(label: str, host: str, examples: list[str]) -> dict:
    return original_rule(
        title=f"Kill {label} root",
        pattern=rf"^https://(?:www\.)?{esc(host)}/?([\?#].*)?$",
        dest=KILL,
        examples=examples,
    )


def kill_path(label: str, host: str, path: str, examples: list[str]) -> dict:
    path = path.strip("/")
    return original_rule(
        title=f"Kill {label} /{path}",
        pattern=rf"^https://(?:www\.)?{esc(host)}/{path}/?([\?#].*)?$",
        dest=KILL,
        examples=examples,
    )


def rewrite(label: str, host: str, dest_host: str, examples: list[str]) -> dict:
    return original_rule(
        title=f"{label} to {dest_host}",
        pattern=rf"^https://(?:www\.)?{esc(host)}/(.*)$",
        dest=f"https://{dest_host}/$1",
        examples=examples,
        comments="`(?:www.)?` is non-capturing, so `$1` is the path.",
    )


def tweet_status_rule(
    label: str, host: str, path_label: str, path_pattern: str, example: str
) -> dict:
    # RedirectWeb full-matches the URL. Trailing ?query / #fragment must be explicit.
    return original_rule(
        title=f"{label} {path_label} to Twitter Web Viewer",
        pattern=rf"^https://(?:www\.)?{esc(host)}/{path_pattern}(\d+)(?:[\?#].*)?$",
        dest="https://twitterwebviewer.com/?tweet=$1",
        examples=[example],
        comments="Original type only. `(?:[?#].*)?$` is required for links with ?s=20.",
    )


def kill_homepage_exact(label: str, host: str, examples: list[str]) -> dict:
    """Bare homepage only. No query string, or ?tweet= links get killed too."""
    return original_rule(
        title=f"Kill {label} homepage",
        pattern=rf"^https://(?:www\.)?{esc(host)}/?$",
        dest=KILL,
        examples=examples,
        comments="Exact `/` only. `/?tweet=ID` must not match.",
    )


def kill_host(label: str, host: str, examples: list[str]) -> dict:
    return original_rule(
        title=f"Kill {label}",
        pattern=rf"^https://(?:www\.)?{esc(host)}/.*$",
        dest=KILL,
        examples=examples,
    )


def x_twitter_block(host_label: str, host: str, status_example: str) -> list[dict]:
    return [
        tweet_status_rule(host_label, host, "status", r"[^/]+/status/", status_example),
        tweet_status_rule(
            host_label, host, "i/status", r"i/status/", f"https://{host}/i/status/123?s=20"
        ),
        tweet_status_rule(
            host_label, host, "i/web/status", r"i/web/status/", f"https://{host}/i/web/status/123"
        ),
        kill_root(host_label, host, [f"https://{host}/", f"https://www.{host}/"]),
        kill_path(host_label, host, "home", [f"https://{host}/home"]),
        kill_path(host_label, host, "explore", [f"https://{host}/explore"]),
    ]


def main() -> None:
    redirects = [
        # Tweet rules first for each host, then kills for that host.
        *x_twitter_block(
            "X",
            "x.com",
            "https://x.com/resend/status/2091897900800635319?s=20",
        ),
        *x_twitter_block(
            "Twitter",
            "twitter.com",
            "https://twitter.com/resend/status/2091897900800635319?s=20",
        ),
        kill_homepage_exact(
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
        kill_host("Threads", "threads.net", ["https://www.threads.net/", "https://threads.net/@someone"]),
        kill_host("threads.com", "threads.com", ["https://www.threads.com/", "https://threads.com/@someone"]),
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
