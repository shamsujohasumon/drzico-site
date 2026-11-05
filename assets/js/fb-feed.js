/* Latest Facebook posts: renders up to 8 cards from a JSON feed.
   Feed URL comes from data-feed on #fb-feed. Empty = not connected yet:
   draft mode shows sample cards, the live site hides the whole section. */
(function () {
  var root = document.getElementById("fb-feed");
  if (!root) return;
  var section = root.closest("section"), grid = root.querySelector(".fb-grid");
  var feed = (root.getAttribute("data-feed") || "").trim();
  var page = root.getAttribute("data-page") || "https://www.facebook.com/";
  var MAX = 8;
  var SAMPLE = [{"id":"sample-1","type":"photo","message":"Sample post 1. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-14T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"assets/img/_opt/team-photo-480.webp","video":""},{"id":"sample-2","type":"photo","message":"Sample post 2. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-13T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"assets/img/_opt/services/plid-lumbar-disc-surgery/plid-lumbar-disc-surgery-case-03-480.webp","video":""},{"id":"sample-3","type":"photo","message":"Sample post 3. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-12T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"assets/img/_opt/services/plid-lumbar-disc-surgery/plid-lumbar-disc-surgery-case-11-480.webp","video":""},{"id":"sample-4","type":"text","message":"Sample post 4. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-11T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"","video":""},{"id":"sample-5","type":"video","message":"Sample post 5. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-10T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"assets/img/_opt/services/plid-lumbar-disc-surgery/plid-lumbar-disc-surgery-what-is-plid-480.webp","video":""},{"id":"sample-6","type":"photo","message":"Sample post 6. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-09T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"assets/img/_opt/services/plid-lumbar-disc-surgery/plid-lumbar-disc-surgery-case-07-480.webp","video":""},{"id":"sample-7","type":"photo","message":"Sample post 7. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-08T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"assets/img/_opt/services/plid-lumbar-disc-surgery/plid-lumbar-disc-surgery-case-14-480.webp","video":""},{"id":"sample-8","type":"photo","message":"Sample post 8. Real Facebook posts will appear here automatically once the feed is connected.","time":"2026-10-07T09:00:00+0000","url":"https://www.facebook.com/isme.azam.37","image":"assets/img/_opt/services/plid-lumbar-disc-surgery/plid-lumbar-disc-surgery-case-01-480.webp","video":""}];
  var ok = function (u) { return typeof u === "string" && /^https:\/\//.test(u) || (typeof u === "string" && /^assets\//.test(u)); };

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  function fmt(t) { var d = new Date(t); return isNaN(d) ? "" : d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }); }
  function clip(s) { s = (s || "").replace(/\s+/g, " ").trim(); return s.length > 170 ? s.slice(0, 167).trim() + "..." : s; }

  function card(p) {
    var a = el("article", "fb-card");
    var media = el("div", "fb-media");
    if (p.type === "video" && ok(p.video)) {
      var v = el("video"); v.controls = true; v.preload = "none"; v.setAttribute("playsinline", "");
      if (ok(p.image)) v.poster = p.image;
      v.src = p.video; v.setAttribute("aria-label", "Video from Facebook");
      media.appendChild(v);
    } else if (ok(p.image)) {
      var link = el("a"); link.href = p.url; link.target = "_blank"; link.rel = "noopener";
      var im = el("img"); im.src = p.image; im.alt = clip(p.message) || "Facebook post"; im.loading = "lazy"; im.decoding = "async";
      // if the picture cannot be loaded, show the plain Facebook placeholder instead of a broken image
      im.onerror = function () { media.innerHTML = ""; media.className = "fb-media fb-media--text"; media.appendChild(el("span", "fb-f", "f")); };
      link.appendChild(im);
      if (p.type === "video") { var pl = el("span", "fb-play", "\u25B6"); pl.setAttribute("aria-hidden", "true"); link.appendChild(pl); link.setAttribute("aria-label", "Watch video on Facebook"); }
      media.appendChild(link);
    } else {
      media.className += " fb-media--text"; media.appendChild(el("span", "fb-f", "f"));
    }
    a.appendChild(media);
    var body = el("div", "fb-body");
    var when = fmt(p.time); if (when) body.appendChild(el("time", "fb-date", when));
    if (p.message) body.appendChild(el("p", "fb-text", clip(p.message)));
    var more = el("a", "fb-more", "View on Facebook"); more.href = ok(p.url) ? p.url : page; more.target = "_blank"; more.rel = "noopener";
    body.appendChild(more); a.appendChild(body);
    return a;
  }

  function show(posts) {
    posts = (posts || []).slice(0, MAX);
    if (!posts.length) { section.hidden = true; return; }
    grid.innerHTML = ""; posts.forEach(function (p) { grid.appendChild(card(p)); });
    root.classList.add("is-ready");
  }

  if (!feed) {
    if (document.body.classList.contains("draft")) {
      root.classList.add("is-sample");
      show(SAMPLE);
    } else section.hidden = true;
    return;
  }
  fetch(feed, { headers: { Accept: "application/json" } })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (d) { show(Array.isArray(d) ? d : d.posts); })
    .catch(function () { grid.innerHTML = ""; grid.appendChild(el("p", "muted", "Latest posts could not be loaded right now. Please visit our Facebook page.")); });
})();
