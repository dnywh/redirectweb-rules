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


def rule(
    *,
    title: str,
    dest: str,
    examples: list[str],
    comments: str = "",
    rule_type: str = "declarativeNetRequestRedirect",
    pattern: str | None = None,
    pattern_type: str = "regularExpression",
    exclude_patterns: list[dict[str, str]] | None = None,
    capture_group_processes: list[dict] | None = None,
) -> dict:
    if pattern is None:
        raise ValueError("pattern is required")

    payload: dict = {
        "kind": "Redirect",
        "type": rule_type,
        "title": title,
        "isEnabled": True,
        "sourceURLPattern": {"type": pattern_type, "value": pattern},
        "destinationURLPattern": dest,
        "exampleURLs": examples,
        "excludeURLPatterns": exclude_patterns or [],
        "captureGroupProcesses": capture_group_processes or [],
        "comments": comments,
        "commentsOptions": {"format": "markdown"},
        "targetBrowserOptions": {"browsers": [], "selectionType": "including"},
    }
    if rule_type == "declarativeNetRequestRedirect":
        payload["resourceTypes"] = ["main_frame"]
    return payload


def strip_query_suffix(group_index: int) -> dict:
    return {
        "groupIndex": group_index,
        "process": {
            "id": "replaceOccurrences",
            "matchingPattern": {"type": "regularExpression", "value": "\\?.*"},
            "replacement": "",
        },
    }


def status_exclude_patterns(host: str) -> list[dict[str, str]]:
    return [
        {
            "type": "regularExpression",
            "value": rf"^https://(?:www\.)?{esc(host)}/[^/]+/status/\d+(?:[\?#].*)?$",
        },
        {
            "type": "regularExpression",
            "value": rf"^https://(?:www\.)?{esc(host)}/i/status/\d+(?:[\?#].*)?$",
        },
        {
            "type": "regularExpression",
            "value": rf"^https://(?:www\.)?{esc(host)}/i/web/status/\d+(?:[\?#].*)?$",
        },
        {"type": "wildcard", "value": f"https://{host}/*/status/*"},
        {"type": "wildcard", "value": f"https://www.{host}/*/status/*"},
        {"type": "wildcard", "value": f"https://{host}/i/status/*"},
        {"type": "wildcard", "value": f"https://www.{host}/i/status/*"},
        {"type": "wildcard", "value": f"https://{host}/i/web/status/*"},
        {"type": "wildcard", "value": f"https://www.{host}/i/web/status/*"},
    ]


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


def tweet_to_viewer_rules(label: str, host: str) -> list[dict]:
    """Wildcard rules: RedirectWeb regex Examples failed on status URLs with ?s=20."""
    status_example = (
        "https://x.com/resend/status/2091897900800635319?s=20"
        if host == "x.com"
        else "https://twitter.com/resend/status/2091897900800635319?s=20"
    )
    shapes = [
        (
            f"{label} user status",
            f"https://{host}/*/status/*",
            2,
            status_example,
        ),
        (
            f"{label} user status (www)",
            f"https://www.{host}/*/status/*",
            2,
            f"https://www.{host}/resend/status/2091897900800635319?s=20",
        ),
        (
            f"{label} i/status",
            f"https://{host}/i/status/*",
            1,
            f"https://{host}/i/status/123?s=20",
        ),
        (
            f"{label} i/web/status",
            f"https://{host}/i/web/status/*",
            1,
            f"https://{host}/i/web/status/123",
        ),
    ]
    return [
        rule(
            title=f"{title} to Twitter Web Viewer",
            pattern=pattern,
            pattern_type="wildcard",
            dest="https://twitterwebviewer.com/?tweet=$" + str(group_index),
            examples=[example],
            rule_type="originalRedirect",
            capture_group_processes=[strip_query_suffix(group_index)],
            comments=(
                "Wildcard + Original type. Strips `?s=20` style query strings from the tweet id. "
                "Put these above Kill other URLs."
            ),
        )
        for title, pattern, group_index, example in shapes
    ]


def kill_remaining(label: str, host: str, examples: list[str]) -> dict:
    return rule(
        title=f"Kill other {label} URLs",
        pattern=rf"^https://(?:www\.)?{esc(host)}/.*$",
        dest=KILL,
        examples=examples,
        rule_type="originalRedirect",
        exclude_patterns=status_exclude_patterns(host),
        comments=(
            "Excludes must allow `?s=20` on status URLs. Without that, this catch-all "
            "was sending tweet links to example.com."
        ),
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
        *tweet_to_viewer_rules("X", "x.com"),
        *tweet_to_viewer_rules("Twitter", "twitter.com"),
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
