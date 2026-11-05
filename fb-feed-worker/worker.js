// Cloudflare Worker: returns the latest Facebook Page posts as simple JSON for the website.
// Secrets (Worker settings): FB_PAGE_ID, FB_PAGE_TOKEN. Variable: ALLOWED_ORIGIN (e.g. https://drzico.com)
const GRAPH = "https://graph.facebook.com/v23.0"; // use the current Graph API version

export default {
  async fetch(req, env, ctx) {
    const cors = { "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN || "*", "Vary": "Origin" };
    if (req.method === "OPTIONS") return new Response(null, { headers: { ...cors, "Access-Control-Allow-Methods": "GET" } });
    const cache = caches.default, key = new Request(new URL(req.url).origin + "/fb-posts");
    let res = await cache.match(key);
    if (res) { const out = new Response(res.body, res); out.headers.set("Access-Control-Allow-Origin", cors["Access-Control-Allow-Origin"]); return out; }

    const fields = "id,message,created_time,permalink_url,full_picture,status_type,attachments{media_type,media,url}";
    const api = `${GRAPH}/${env.FB_PAGE_ID}/posts?fields=${encodeURIComponent(fields)}&limit=12&access_token=${env.FB_PAGE_TOKEN}`;
    const r = await fetch(api);
    if (!r.ok) return new Response(JSON.stringify({ posts: [], error: r.status }), { status: 502, headers: { "Content-Type": "application/json", ...cors } });
    const data = await r.json();

    const posts = (data.data || []).map((p) => {
      const att = p.attachments && p.attachments.data && p.attachments.data[0];
      const isVideo = att && /video/i.test(att.media_type || "");
      return {
        id: p.id,
        type: isVideo ? "video" : p.full_picture ? "photo" : "text",
        message: p.message || "",
        time: p.created_time,
        url: p.permalink_url,
        image: p.full_picture || (att && att.media && att.media.image && att.media.image.src) || "",
        video: isVideo && att.media && att.media.source ? att.media.source : "",
      };
    }).filter((p) => p.message || p.image || p.video).slice(0, 8);

    res = new Response(JSON.stringify({ posts }), { headers: { "Content-Type": "application/json", "Cache-Control": "public, max-age=600", ...cors } });
    ctx.waitUntil(cache.put(key, res.clone()));
    return res;
  },
};
