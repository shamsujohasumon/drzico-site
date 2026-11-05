# Facebook latest posts: setup

The home page has a "Latest from Facebook" section (8 cards, photo or video or text). It reads a small JSON feed that a Cloudflare Worker builds from the Facebook Page. Until the feed is connected, the live site hides the section (draft mode shows sample cards).

Needs: a Facebook PAGE (a personal profile cannot be read by the API) and admin access to it.

1. developers.facebook.com: create an app (type Business), add the Facebook Login for Business or Graph API Explorer. In Graph API Explorer pick the Page, give permissions `pages_show_list` and `pages_read_engagement` (and `pages_read_user_content` if asked), then generate a Page access token.
2. Turn it into a long-lived Page token (Access Token Debugger > Extend, or exchange the user token first, then request /me/accounts). A Page token made from a long-lived user token does not expire.
3. Find the Page ID (Page > About > Page transparency, or /me/accounts).
4. Deploy `fb-feed-worker/`: `npm i -g wrangler`, `wrangler login`, `wrangler secret put FB_PAGE_ID`, `wrangler secret put FB_PAGE_TOKEN`, edit ALLOWED_ORIGIN in wrangler.toml, then `wrangler deploy`.
5. Open the Worker address in the browser. You should see `{"posts":[...]}`.
6. In `_build/build.py` set `FB_FEED_URL = "https://your-worker.workers.dev"`, run `python3 _build/build.py`, upload the site.

New posts appear within about 10 minutes (the Worker caches for 10 minutes).
