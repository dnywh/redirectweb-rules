# RedirectWeb rules

Kill homepages and feeds, rewrite X tweet links to Twitter Web Viewer, rewrite Reddit to Safereddit, block Threads. Blocked pages land on `https://example.com/`.

RedirectWeb walks the list top to bottom. The first matching rule wins. All rules use **Original** type (not DNR). Safari DNR is unreliable for regex redirects and rejects `|` in patterns.

## Import

1. Download or generate [`rules.redirectweb`](./rules.redirectweb).
2. **Mac:** drag it onto the RedirectWeb window, or File → Import Rules.
3. **iPhone:** save it in Files, share the file, choose RedirectWeb.

After import:

- Turn off overlapping redirects in StopTheMadness Pro.
- In Safari, allow RedirectWeb on All Websites, including Private Browsing.

## Updating

Import **adds** rules. It does not replace or merge by title. Re-importing on top of an existing set creates duplicates.

1. Turn off iCloud Sync in RedirectWeb (optional, but stops old rules syncing back).
2. Delete all rules in My Rules.
3. Download the latest `rules.redirectweb` (or run `python3 generate.py` locally).
4. Import once.
5. Turn iCloud Sync back on if you use it.

Regenerate locally:

```sh
python3 generate.py
```

## Rules

| Site | Behaviour |
|------|-----------|
| X / Twitter | Rewrite status URLs to Twitter Web Viewer; kill `/`, `/home`, `/explore` |
| Twitter Web Viewer | Kill bare homepage only (`/` with no query) |
| Facebook / Instagram | Kill homepage and feed tabs; allow direct post/profile links |
| Reddit | Kill roots and feeds; rewrite deep links to Safereddit |
| Threads | Block entire site |

There is no catch-all kill for X/Twitter. Profiles, search, and other paths still load.

To block another whole site, copy a Threads rule in `generate.py` (`kill_host(...)`).

## Pattern notes

**www:** patterns use `(?:www.)?` (non-capturing). Do not use `(www.)?` or `$1` will capture `www.` and break rewrites.

**Query strings:** tweet patterns end with `(?:[\?#].*)?$` because RedirectWeb full-matches URLs. Links like `?s=20` need this suffix.

**Viewer homepage:** the kill rule matches `twitterwebviewer.com/` exactly. `/?tweet=ID` must not match, or tweet redirects get killed on arrival.
