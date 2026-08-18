# RedirectWeb rules

Kill homepages and feeds, rewrite X and Reddit deep links to frontends, block Threads. Landing pad is `https://example.com/` (a reserved, boring page).

RedirectWeb matches **top of the list first**. Kills come before rewrites.

## Import (this is the programmatic path)

RedirectWeb has no CLI. The supported bulk path is import:

1. Download [`rules.redirectweb`](./rules.redirectweb).
2. **Mac:** drag it onto the RedirectWeb window, or File > Import Rules.
3. **iPhone:** save it in Files, share the file, choose RedirectWeb.
4. iCloud Sync copies the rules to the other device.

After import:

- Delete RedirectWeb's sample rule (it also uses example.com).
- Turn off the same redirects in StopTheMadness Pro.
- In Safari, allow RedirectWeb on All Websites, including Private Browsing.
- Confirm Type is **DNR**, Resource Types is `main_frame`.
- If a rule errors in Examples, switch that one to Original (you may get a one-frame flash).

To change the list later, edit `generate.py`, run `python3 generate.py`, import the new `rules.redirectweb` again. RedirectWeb does not merge; remove the old copies if it duplicates.

There is an MDM `enforcedRuleSet` format with the same JSON, but that is for supervised org devices, not a personal phone.

## Combining www

Yes for www vs bare host. All patterns use `(?:www.)?`, which is a **non-capturing** group, so both `https://x.com/foo` and `https://www.x.com/foo` hit the same rule and `$1` stays the path.

Do not write `(www.)?`. That captures `www.` as `$1` and breaks rewrites.

These still cannot be one DNR rule, because Safari DNR rejects `|` in regex:

- `x.com` and `twitter.com`
- `threads.net` and `threads.com`
- `reddit.com`, `old.reddit.com`, and `new.reddit.com`

Original type could merge those with pipes, but Original can load the origin page first. This set stays on DNR.

## What the rules do

1. **Kill roots and feeds** on X, Twitter, xcancel, Reddit, Safereddit (`/`, `/home`, `/explore`, `/r/all`, `/r/popular`).
2. **Rewrite** remaining `x.com` / `twitter.com` paths to `xcancel.com`, and Reddit (including old/new) to `safereddit.com`.
3. **Kill** all of `threads.net` and `threads.com`.

Add another whole-site block by copying a Threads rule in `generate.py` (`kill_host(...)`).
