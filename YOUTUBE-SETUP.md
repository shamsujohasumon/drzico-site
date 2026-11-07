# Latest YouTube videos: setup (once, about 10 minutes, free)

1. Go to https://console.cloud.google.com and create a project (any name).
2. APIs & Services > Library > search "YouTube Data API v3" > Enable.
3. APIs & Services > Credentials > Create credentials > API key. Copy the key.
4. Click the key > Application restrictions: Websites > add `https://neurosurgeonzico-ismaazam.com/*` and `https://www.neurosurgeonzico-ismaazam.com/*`.
   API restrictions: Restrict key > YouTube Data API v3. Save.
5. In `_build/build.py` set `YT_API_KEY = "your key"`, run `python3 _build/build.py`, push.

The home page then shows the 20 newest videos of the channel, newest first, and updates by itself when a new video is uploaded.
Without a key (or if YouTube is unreachable) the short list in `VIDEOS` is shown instead.
The free quota (10,000 units a day) is far more than needed: each page view uses 1 unit.
