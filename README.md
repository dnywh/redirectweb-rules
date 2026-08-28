# RedirectWeb rules

Kill homepages and feeds, rewrite X tweet links to Twitter Web Viewer, rewrite Reddit to Safereddit, block Threads. Landing pad is `https://example.com/` (a reserved, boring page).

RedirectWeb matches **top of the list first**. The first rule that matches wins.

**All Original type.** Safari DNR is unreliable for regex redirects, rejects `|` in patterns (FB13251357), and DNR rules can run before Original rules regardless of list order. This ruleset uses Original only.

## Import

RedirectWeb has no CLI. The supported bulk path is import:

1. Download or generate [`rules.redirectweb`](./rules.redirectweb).
2. **Mac:** drag it onto the RedirectWeb window, or File > Import Rules.
3. **iPhone:** save it in Files, share the file, choose RedirectWeb.
4. iCloud Sync copies the rules to the other device.

After import:

- Turn off the same redirects in StopTheMadness Pro.
- In Safari, allow RedirectWeb on All Websites, including Private Browsing.
- Confirm Type is **Original** for all rules (not DNR).

## Updating rules (important: import duplicates)

RedirectWeb **adds** imported rules. It does not replace or merge by title. If you import a new `rules.redirectweb` on top of an old set, you will get duplicates.

To update after a change:

1. **Turn off iCloud Sync** in RedirectWeb settings (old rules can sync back after delete).
2. Delete **all** rules in My Rules.
3. Pull or download the latest `rules.redirectweb` from this repo (or run `python3 generate.py` locally).
4. Import the new file once.
5. Check Examples on **X status to Twitter Web Viewer** with `https://x.com/resend/status/2091897900800635319?s=20`. It should show `https://twitterwebviewer.com/?tweet=2091897900800635319`, not example.com.
6. Turn iCloud Sync back on if you use it.

There is no "reimport and overwrite" button. Deleting first is the whole workflow.

Regenerate locally:

```sh
python3 generate.py
```

## Combining www

All patterns use `(?:www.)?`, a **non-capturing** group, so both `https://x.com/foo` and `https://www.x.com/foo` hit the same rule.

Do not write `(www.)?`. That captures `www.` as `$1` and breaks rewrites.

## What the rules do

1. **Rewrite status URLs** on X and Twitter to Twitter Web Viewer (Original regex, `^` anchor, no trailing `$` so `?s=20` is fine).
2. **Kill roots and feeds** on X and Twitter (`/`, `/home`, `/explore`).
3. **Kill Twitter Web Viewer homepage** (exact `/` only, not `/?tweet=ID`).
4. **Facebook and Instagram:** kill homepage and feed tabs only. Direct links to posts, reels, groups, and so on still load.
5. **Reddit:** kill roots/feeds, rewrite deep links to Safereddit.
6. **Kill** all of `threads.net` and `threads.com`.

There is **no catch-all kill** for X/Twitter. Profiles and search still load. A wildcard catch-all with status exclusions was sending tweet links to example.com because wildcard `*` does not match `?query` in excludes.

Add another whole-site block by copying a Threads rule in `generate.py` (`kill_host(...)`).
