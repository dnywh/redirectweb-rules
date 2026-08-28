# RedirectWeb rules

Kill homepages and feeds, rewrite X tweet links to Twitter Web Viewer, rewrite Reddit to Safereddit, block Threads. Landing pad is `https://example.com/` (a reserved, boring page).

RedirectWeb matches **top of the list first**. The first rule that matches wins.

**DNR vs Original:** Homepage kills use DNR (fast). X/Twitter tweet rewrites and the "kill other URLs" catch-all use **Original** type. Safari DNR is unreliable for regex redirects and rejects `|` in patterns (FB13251357). A DNR catch-all was sending status links to example.com when the DNR tweet rule failed to match.

## Import

RedirectWeb has no CLI. The supported bulk path is import:

1. Download or generate [`rules.redirectweb`](./rules.redirectweb).
2. **Mac:** drag it onto the RedirectWeb window, or File > Import Rules.
3. **iPhone:** save it in Files, share the file, choose RedirectWeb.
4. iCloud Sync copies the rules to the other device.

After import:

- Turn off the same redirects in StopTheMadness Pro.
- In Safari, allow RedirectWeb on All Websites, including Private Browsing.
- Confirm Type is **DNR** for homepage kills, **Original** for tweet viewer rules.
- If a rule errors in Examples, switch that one to Original (you may get a one-frame flash).

## Updating rules (important: import duplicates)

RedirectWeb **adds** imported rules. It does not replace or merge by title. If you import a new `rules.redirectweb` on top of an old set, you will get duplicates.

To update after a change like the xcancel shutdown:

1. In RedirectWeb, delete the old rules first. Easiest: select all in My Rules and delete, or delete only the xcancel-related ones if you prefer.
2. Pull or download the latest `rules.redirectweb` from this repo (or run `python3 generate.py` locally).
3. Import the new file once.
4. Wait for iCloud Sync on your other device, or import there too if sync is slow.

There is no "reimport and overwrite" button. Deleting first is the whole workflow.

Regenerate locally:

```sh
python3 generate.py
```

## Combining www

All patterns use `(?:www.)?`, a **non-capturing** group, so both `https://x.com/foo` and `https://www.x.com/foo` hit the same rule.

Do not write `(www.)?`. That captures `www.` as `$1` and breaks rewrites.

Safari DNR rejects `|` in regex. Tweet rules use Original type instead. These stay as separate DNR rules:

- `x.com` and `twitter.com` homepage kills
- `threads.net` and `threads.com`
- `reddit.com`, `old.reddit.com`, and `new.reddit.com`

## What the rules do

1. **Kill roots and feeds** on X and Twitter (`/`, `/home`, `/explore`).
2. **Rewrite status URLs** on X and Twitter to Twitter Web Viewer (Original + wildcard).
3. **Kill other X/Twitter URLs** (Original, with status URL exclusions that include `?s=20`).
4. **Kill Twitter Web Viewer root** so you cannot open the viewer homepage and scroll.
5. **Facebook and Instagram:** kill homepage and feed tabs only. Direct links to posts, reels, groups, and so on still load.
6. **Reddit** unchanged: kill roots/feeds, rewrite deep links to Safereddit.
7. **Kill** all of `threads.net` and `threads.com`.

Add another whole-site block by copying a Threads rule in `generate.py` (`kill_host(...)`).
