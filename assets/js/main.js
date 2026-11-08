/* Dr. Md. Isma Azam (Zico): site script (v1)
   Plain JS, no build step. Each block is independent so it can move into a
   React component or hook when the site is converted to Next.js. */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } }
  };

  /* ---------- chamber data (single source for status + booking) ---------- */
  // days: 0 = Sunday ... 6 = Saturday. Times in minutes from midnight, Asia/Dhaka.
  var CHAMBERS = {
    continental: {
      name: "Continental Hospital, Gulshan 2",
      days: [6, 0, 1, 2, 3, 4],
      start: 8 * 60 + 30,
      end: 16 * 60,
      hours: "8:30 AM to 4:00 PM",
      opens: "8:30 AM",
      closes: "4:00 PM",
      dayText: "Saturday to Thursday",
      phone: "10666"
    },
    popular: {
      name: "Popular Diagnostic Centre, Dhanmondi",
      days: [6, 1, 3],
      start: 22 * 60,
      end: 24 * 60,
      hours: "10:00 PM to 12:00 AM",
      opens: "10:00 PM",
      closes: "12:00 AM",
      dayText: "Saturday, Monday and Wednesday",
      phone: "09666 787801"
    },
    malibag: {
      name: "Dr. Sirajul Islam Medical College & Hospital, Malibag",
      days: null, // hours not yet confirmed: status shows "call to confirm"
      phone: "01927 333000"
    }
  };
  var DAY = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  function dhakaNow() {
    var parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: "Asia/Dhaka", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hour12: false, weekday: "short"
    }).formatToParts(new Date());
    var o = {};
    parts.forEach(function (p) { o[p.type] = p.value; });
    var y = +o.year, m = +o.month, d = +o.day;
    var dow = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
    return { y: y, m: m, d: d, dow: dow, mins: (+o.hour % 24) * 60 + (+o.minute) };
  }
  function iso(y, m, d) { return y + "-" + String(m).padStart(2, "0") + "-" + String(d).padStart(2, "0"); }
  function addDays(y, m, d, n) {
    var t = new Date(Date.UTC(y, m - 1, d + n));
    return { y: t.getUTCFullYear(), m: t.getUTCMonth() + 1, d: t.getUTCDate(), dow: t.getUTCDay() };
  }
  function nextOpenDates(key, count) {
    var c = CHAMBERS[key];
    if (!c || !c.days) return [];
    var now = dhakaNow(), out = [];
    for (var i = 0; i < 21 && out.length < count; i++) {
      var t = addDays(now.y, now.m, now.d, i);
      if (c.days.indexOf(t.dow) === -1) continue;
      if (i === 0 && now.mins >= c.end - 30) continue;
      out.push(t);
    }
    return out;
  }
  function prettyDate(t) {
    var mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][t.m - 1];
    return DAY[t.dow].slice(0, 3) + ", " + t.d + " " + mon;
  }

  /* ---------- theme ---------- */
  var root = document.documentElement;
  var savedTheme = store.get("dz-theme");
  if (savedTheme === "dark" || savedTheme === "light") root.setAttribute("data-theme", savedTheme);
  function syncThemeLabel() {
    var dark = (root.getAttribute("data-theme") || (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";
    $$("[data-theme-toggle]").forEach(function (b) { b.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode"); b.setAttribute("aria-pressed", String(dark)); });
  }
  syncThemeLabel();
  $$("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var cur = root.getAttribute("data-theme") ||
        (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
      var next = cur === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      store.set("dz-theme", next);
      syncThemeLabel();
    });
  });

  /* ---------- draft highlights (remove body.draft for launch) ---------- */
  if (store.get("dz-draft") === "off") document.body.classList.remove("draft");
  $$("[data-draft-toggle]").forEach(function (b) {
    var sync = function () { b.textContent = document.body.classList.contains("draft") ? "Hide highlights" : "Show highlights"; };
    sync();
    b.addEventListener("click", function () {
      document.body.classList.toggle("draft");
      store.set("dz-draft", document.body.classList.contains("draft") ? "on" : "off");
      sync();
    });
  });
  // keep the bar reachable even when highlights are hidden
  var bar = $(".draft-bar");
  if (bar) bar.style.display = "block";

  /* ---------- mobile drawer ---------- */
  var drawer = $("#drawer");
  var openBtn = $("[data-drawer-open]");
  function closeDrawer() {
    if (!drawer || drawer.hidden) return;
    drawer.hidden = true;
    document.body.style.overflow = "";
    if (openBtn) { openBtn.setAttribute("aria-expanded", "false"); openBtn.focus(); }
  }
  if (drawer && openBtn) {
    openBtn.addEventListener("click", function () {
      drawer.hidden = false;
      openBtn.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
      var first = $("a, button", drawer);
      if (first) first.focus();
    });
    $$("[data-drawer-close]", drawer).forEach(function (b) { b.addEventListener("click", closeDrawer); });
    drawer.addEventListener("click", function (e) { if (e.target === drawer) closeDrawer(); });
  }

  /* ---------- services dropdown ---------- */
  $$(".has-menu").forEach(function (item) {
    var btn = $("button", item), menu = $(".menu", item);
    if (!btn || !menu) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open;
      btn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", function (e) {
      if (!item.contains(e.target)) { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); }
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    closeDrawer();
    $$(".has-menu").forEach(function (item) {
      var menu = $(".menu", item), btn = $("button", item);
      if (menu && !menu.hidden) { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); btn.focus(); }
    });
  });

  /* ---------- chamber status ---------- */
  $$("[data-chamber-status]").forEach(function (el) {
    var c = CHAMBERS[el.getAttribute("data-chamber-status")];
    if (!c) return;
    if (!c.days) { el.textContent = "Call to confirm hours"; return; }
    var now = dhakaNow();
    var todayOpen = c.days.indexOf(now.dow) !== -1;
    if (todayOpen && now.mins >= c.start && now.mins < c.end) {
      el.textContent = "Open now, until " + c.closes; el.classList.add("is-open");
    } else if (todayOpen && now.mins < c.start) {
      el.textContent = "Today, " + c.hours; el.classList.add("is-today");
    } else {
      var n = nextOpenDates(el.getAttribute("data-chamber-status"), 1)[0];
      el.textContent = n ? "Next: " + DAY[n.dow] + ", " + c.opens : "Call to confirm";
    }
  });

  /* ---------- condition finder ---------- */
  var DATA = window.DZ_CONDITIONS || [];
  function norm(s) { return (s || "").toLowerCase().replace(/[’'`]/g, "").replace(/\s+/g, " ").trim(); }
  $$("[data-finder]").forEach(function (box) {
    var input = $("input", box), list = $(".finder-results", box), empty = $(".finder-empty", box);
    var limit = +(box.getAttribute("data-limit") || 8);
    function render(q) {
      q = norm(q);
      list.innerHTML = "";
      if (!q) { empty.hidden = true; return; }
      var hits = DATA.filter(function (c) {
        return norm(c.en + " " + c.bn + " " + (c.alt || "")).indexOf(q) !== -1;
      }).slice(0, limit);
      empty.hidden = hits.length > 0;
      hits.forEach(function (c) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = c.url;
        a.innerHTML = '<span class="t"></span><span class="s"></span>';
        a.querySelector(".t").textContent = c.en;
        var sm = document.createElement("small"); sm.textContent = c.bn; sm.setAttribute("lang", "bn");
        a.querySelector(".t").appendChild(sm);
        a.querySelector(".s").textContent = c.page;
        li.appendChild(a); list.appendChild(li);
      });
    }
    input.addEventListener("input", function () { render(input.value); });
    $$(".chips button", box).forEach(function (b) {
      b.addEventListener("click", function () { input.value = b.getAttribute("data-q"); render(input.value); input.focus(); });
    });
  });

  /* ---------- FAQ filter ---------- */
  $$("[data-faq-filter]").forEach(function (input) {
    var scope = document.getElementById(input.getAttribute("data-faq-filter"));
    var out = $("#" + input.getAttribute("aria-describedby"));
    input.addEventListener("input", function () {
      var q = norm(input.value), shown = 0;
      $$("details", scope).forEach(function (d) {
        var hit = !q || norm(d.textContent).indexOf(q) !== -1;
        d.hidden = !hit; if (hit) shown++;
        if (q && hit) d.open = true;
      });
      if (out) out.textContent = q ? shown + " matching question" + (shown === 1 ? "" : "s") : "";
    });
  });

  /* ---------- table of contents: highlight current section ---------- */
  var tocLinks = $$(".toc a[href^='#']");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          tocLinks.forEach(function (a) { a.classList.remove("is-current"); a.removeAttribute("aria-current"); });
          map[en.target.id].classList.add("is-current");
          map[en.target.id].setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  /* ---------- hospital call and appointment popup ---------- */
  var contactModal = $("#contact-modal");
  if (contactModal) {
    var contactOpener = null, contactOverflow = "";
    $$("[data-contact-open]").forEach(function (button) {
      button.addEventListener("click", function () {
        if (typeof contactModal.showModal !== "function") {
          window.location.href = "appointment";
          return;
        }
        if (contactModal.open) return;
        contactOpener = button;
        contactOverflow = document.documentElement.style.overflow;
        contactModal.showModal();
        document.documentElement.style.overflow = "hidden";
      });
    });
    $("[data-contact-close]", contactModal).addEventListener("click", function () { contactModal.close(); });
    contactModal.addEventListener("click", function (e) {
      if (e.target !== contactModal) return;
      var bounds = contactModal.getBoundingClientRect();
      if (e.clientX < bounds.left || e.clientX > bounds.right || e.clientY < bounds.top || e.clientY > bounds.bottom) contactModal.close();
    });
    // Native dialog handles Escape and focus trapping; restore the page on every close.
    contactModal.addEventListener("close", function () {
      document.documentElement.style.overflow = contactOverflow;
      if (contactOpener && contactOpener.isConnected) contactOpener.focus({ preventScroll: true });
    });
  }

  /* ---------- back to top ---------- */
  var toTop = $(".to-top");
  if (toTop) {
    var onScroll = function () { toTop.classList.toggle("is-visible", window.scrollY > 900); };
    window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
    toTop.addEventListener("click", function () { window.scrollTo({ top: 0 }); var m = $("#main"); if (m) m.focus({ preventScroll: true }); });
  }

  /* ---------- before / after compare ---------- */
  $$(".ba").forEach(function (ba) {
    var r = $(".ba-range", ba);
    if (r) r.addEventListener("input", function () { ba.style.setProperty("--pos", r.value + "%"); });
  });

  /* ---------- carousel ---------- */
  $$("[data-carousel]").forEach(function (c) {
    var track = $(".car-track", c);
    var step = function (dir) {
      var card = track.firstElementChild;
      var gap = parseFloat(window.getComputedStyle(track).columnGap) || 0;
      var w = card ? card.getBoundingClientRect().width + gap : 320;
      track.scrollBy({ left: dir * w, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    };
    var prev = $("[data-car-prev]", c), next = $("[data-car-next]", c);
    if (prev) prev.addEventListener("click", function () { step(-1); });
    if (next) next.addEventListener("click", function () { step(1); });
    // autoplay: advance every N ms, loop to the start, pause on hover, focus or touch
    var delay = +(c.getAttribute("data-autoplay") || 0);
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (delay && !reduce) {
      var paused = false, timer;
      var tick = function () {
        if (paused || document.hidden) return;
        var atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 8;
        if (atEnd) track.scrollTo({ left: 0, behavior: "smooth" }); else step(1);
      };
      timer = window.setInterval(tick, delay);
      ["mouseenter", "focusin", "touchstart", "pointerdown"].forEach(function (ev) { c.addEventListener(ev, function () { paused = true; }, { passive: true }); });
      ["mouseleave", "focusout"].forEach(function (ev) { c.addEventListener(ev, function () { paused = false; }); });
    }
    track.addEventListener("keydown", function (e) {
      if (e.target !== track) return;
      if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
    });
  });

  /* ---------- gallery filter ---------- */
  var filterBtns = $$("[data-filter]");
  if (filterBtns.length) {
    var scope = $("[data-filter-scope]"), countEl = $("#filter-count");
    filterBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.getAttribute("data-filter"), n = 0;
        filterBtns.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        $$("[data-cat]", scope).forEach(function (card) {
          var show = k === "all" || card.getAttribute("data-cat") === k;
          card.hidden = !show; if (show) n++;
        });
        if (countEl) countEl.textContent = n + " case" + (n === 1 ? "" : "s");
      });
    });
  }

  /* ---------- lightbox ---------- */
  var lb = $("#lightbox");
  if (lb && typeof lb.showModal === "function") {
    var lbImg = $("img", lb), lbCap = $(".lb-cap", lb);
    $$("[data-lightbox]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var img = $("img", btn);
        if (!img) return; // no photo yet: placeholder only
        lbImg.src = img.dataset.full || img.currentSrc || img.src; // largest optimized copy lbImg.alt = img.alt; lbCap.textContent = img.alt;
        lb.showModal();
      });
    });
    $("[data-lb-close]", lb).addEventListener("click", function () { lb.close(); });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
  }

  /* ---------- latest YouTube videos (newest first), replaces the built-in list ---------- */
  $$("[data-yt-key]").forEach(function (box) {
    var key = box.getAttribute("data-yt-key"), list = box.getAttribute("data-yt-list"), max = box.getAttribute("data-yt-max") || 20;
    if (!key || !window.fetch) return; // no key: keep the list that is already on the page
    var track = $(".car-track", box);
    var url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=" + max +
      "&playlistId=" + encodeURIComponent(list) + "&key=" + encodeURIComponent(key);
    fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) {
      var items = (d.items || []).filter(function (it) { return it.snippet && it.snippet.resourceId && it.snippet.title !== "Private video" && it.snippet.title !== "Deleted video"; });
      if (!items.length) return;
      track.innerHTML = "";
      items.forEach(function (it) {
        var sn = it.snippet, id = sn.resourceId.videoId, th = sn.thumbnails || {};
        var img = (th.high || th.medium || th.default || {}).url || ("https://i.ytimg.com/vi/" + id + "/hqdefault.jpg");
        var a = document.createElement("a");
        a.className = "video-card"; a.href = "https://www.youtube.com/watch?v=" + id; a.target = "_blank"; a.rel = "noopener";
        a.setAttribute("data-video", id); a.setAttribute("data-title", sn.title);
        var thumb = document.createElement("div"); thumb.className = "vc-thumb";
        var fig = document.createElement("figure"); fig.className = "ph ph--sm is-real"; fig.style.aspectRatio = "16/9";
        var im = document.createElement("img"); im.src = img; im.alt = "Video: " + sn.title; im.loading = "lazy"; im.decoding = "async";
        fig.appendChild(im); thumb.appendChild(fig);
        var play = document.createElement("span"); play.className = "play"; play.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5L8 5.5Z" fill="currentColor"/></svg>';
        thumb.appendChild(play); a.appendChild(thumb);
        var t = document.createElement("strong"); t.textContent = sn.title; if (/[\u0980-\u09FF]/.test(sn.title)) t.lang = "bn"; a.appendChild(t);
        var meta = document.createElement("span"); meta.className = "small muted";
        var dt = new Date(sn.publishedAt); meta.textContent = (isNaN(dt) ? "" : dt.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) + " · ") + "YouTube";
        a.appendChild(meta); track.appendChild(a);
      });
      track.scrollLeft = 0;
    }).catch(function () { /* keep the built-in list */ });
  });

  /* ---------- video popup ---------- */
  var vm = $("#video-modal");
  if (vm && typeof vm.showModal === "function") {
    var vmFrame = $(".vm-frame", vm), vmTitle = $(".vm-title", vm);
    var closeVm = function () { if (vm.open) vm.close(); };
    vm.addEventListener("close", function () { vmFrame.innerHTML = ""; }); // stops playback
    // one listener for all cards, so videos added later from YouTube also open in the popup
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("[data-video]");
      if (!a) return;
      (function () {
        e.preventDefault();
        var id = a.getAttribute("data-video"), t = a.getAttribute("data-title") || "Video";
        var f = document.createElement("iframe");
        f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + "?autoplay=1&rel=0";
        f.title = t; f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen"; f.allowFullscreen = true;
        vmFrame.innerHTML = ""; vmFrame.appendChild(f); vmTitle.textContent = t;
        vm.showModal();
      })();
    });
    $("[data-vm-close]", vm).addEventListener("click", closeVm);
    vm.addEventListener("click", function (e) { if (e.target === vm) closeVm(); });
  }

  /* ---------- case card link: jump to that case in the photo carousel ---------- */
  $$("[data-goto-case]").forEach(function (link) {
    link.addEventListener("click", function (e) {
      var key = link.getAttribute("data-goto-case");
      var card = document.querySelector('.car-photo[data-case="' + key + '"]');
      var section = document.getElementById("photos");
      if (!card || !section) return;
      e.preventDefault();
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      section.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      var track = card.parentElement;
      track.scrollTo({ left: card.offsetLeft - track.offsetLeft, behavior: reduce ? "auto" : "smooth" });
      card.focus({ preventScroll: true });
    });
  });

  /* ---------- year ---------- */
  $$("[data-year]").forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

  /* ---------- appointment request: sends the details to the assistant on WhatsApp ---------- */
  var form = $("#booking-form");
  if (form) {
    var waNumber = (form.closest("[data-wa]") || document.body).getAttribute("data-wa") || "8801716033364";
    var daysBox = $("#bk-days", form), chosenDay = "";
    var radios = $$('input[name="chamber"]', form);
    var chamberKey = function () { var r = $('input[name="chamber"]:checked', form); return r ? r.value : "popular"; };

    // preselect from links like appointment?chamber=continental&concern=plid
    try {
      var q = new URLSearchParams(window.location.search);
      var ch = q.get("chamber"), cn = q.get("concern");
      if (ch && CHAMBERS[ch]) radios.forEach(function (r) { r.checked = r.value === ch; });
      if (cn) { var opt = $('#b-concern option[value="' + cn + '"]', form); if (opt) opt.selected = true; }
    } catch (e) { /* ignore */ }

    function dayChip(label, value, selected) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "bk-day"; b.textContent = label;
      b.setAttribute("role", "radio"); b.setAttribute("aria-checked", selected ? "true" : "false");
      b.addEventListener("click", function () {
        $$(".bk-day", daysBox).forEach(function (x) { x.setAttribute("aria-checked", "false"); });
        b.setAttribute("aria-checked", "true"); chosenDay = value;
      });
      return b;
    }
    function refreshDays() {
      daysBox.innerHTML = ""; chosenDay = "";
      var key = chamberKey();
      daysBox.appendChild(dayChip("Earliest available", "", true));
      nextOpenDates(key, 4).forEach(function (t) { daysBox.appendChild(dayChip(prettyDate(t), prettyDate(t), false)); });
      if (key === "malibag") {
        var n = document.createElement("span"); n.className = "bk-day-note small muted";
        n.textContent = "The assistant will tell you the days for this chamber.";
        daysBox.appendChild(n);
      }
    }
    radios.forEach(function (r) { r.addEventListener("change", refreshDays); });
    refreshDays();

    var rules = {
      "b-name": function (v) { return v.trim().length >= 2 ? "" : "Please write the patient's name."; },
      "b-phone": function (v) {
        var d = v.replace(/[\s-]/g, "").replace(/^\+?88/, "");
        return /^01[3-9]\d{8}$/.test(d) ? "" : "Please write an 11-digit mobile number, like 017XXXXXXXX.";
      }
    };
    function validate(el) {
      var msg = rules[el.id](el.value);
      var err = $("#" + el.id + "-err");
      el.closest(".bk-field").classList.toggle("has-error", !!msg);
      err.textContent = msg; err.hidden = !msg;
      el.setAttribute("aria-invalid", msg ? "true" : "false");
      return !msg;
    }
    Object.keys(rules).forEach(function (id) {
      var el = document.getElementById(id);
      el.addEventListener("blur", function () { if (el.value) validate(el); });
      el.addEventListener("input", function () { if (el.getAttribute("aria-invalid") === "true") validate(el); });
    });

    var lastUrl = "";
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = Object.keys(rules).map(function (id) { return document.getElementById(id); }).filter(function (el) { return !validate(el); });
      if (bad.length) { bad[0].focus(); return; }
      var c = CHAMBERS[chamberKey()];
      var concern = $("#b-concern").value ? $("#b-concern").selectedOptions[0].textContent : "";
      var lines = [
        "Assalamu alaikum. I would like a serial for Dr. Md. Isma Azam (Zico).",
        "",
        "Patient: " + $("#b-name").value.trim(),
        "Mobile: " + $("#b-phone").value.trim(),
        "Chamber: " + c.name,
        "Preferred day: " + (chosenDay || "Earliest available")
      ];
      if (concern) lines.push("Problem: " + concern);
      var note = $("#b-notes").value.trim();
      if (note) lines.push("Note: " + note);
      lines.push("", "(Sent from the website)");
      lastUrl = "https://wa.me/" + waNumber + "?text=" + encodeURIComponent(lines.join("\n"));
      var w = window.open(lastUrl, "_blank", "noopener");
      if (!w) window.location.href = lastUrl; // popup blocked: open in this tab
      var done = $("#booking-success");
      $("#bk-reopen").href = lastUrl;
      form.hidden = true; done.hidden = false; done.focus();
    });
    $("#b-again").addEventListener("click", function () {
      $("#booking-success").hidden = true; form.hidden = false; $("#b-name").focus();
    });
  }

  /* ---------- numbers count up from 0 when they come into view ---------- */
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var counters = $$(".stat b, .ledger .n, .ledger-total, [data-countup]");
  if (!reduce && "IntersectionObserver" in window && counters.length) {
    var run = function (el) {
      var target = parseInt(el.textContent.replace(/[^\d]/g, ""), 10);
      if (!target) return;
      var withComma = /,/.test(el.textContent), t0 = null, dur = 1600;
      var show = function (n) { el.textContent = withComma ? n.toLocaleString("en-US") : String(n); };
      var step = function (t) {
        if (t0 === null) t0 = t;
        var p = Math.min((t - t0) / dur, 1), eased = 1 - Math.pow(1 - p, 3);
        show(Math.round(target * eased));
        if (p < 1) requestAnimationFrame(step); else show(target);
      };
      // keep the final width while counting so nothing around the number moves
      el.style.display = "inline-block"; el.style.minWidth = el.getBoundingClientRect().width + "px"; el.style.textAlign = "right";
      show(0); requestAnimationFrame(step);
    };
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { cio.unobserve(en.target); run(en.target); } });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---------- gentle reveal of sections and cards while scrolling ---------- */
  var revealSel = [
    "main .section-head", "main .block-head", "main .prose", "main .figure-row", "main .cols", "main .bn-box",
    ".svc-card", ".chamber", ".case-card", ".box", ".fb-card", ".video-card", ".ba-card", ".stat",
    ".contact-hospital", ".ot-photo-frame", ".faq details", ".notice", ".cta-band",
    "main .carousel", ".ledger:not(.ledger--float)", ".breakdown", ".timeline li"
  ].join(",");
  // phones and small tablets: no scroll reveal, content is simply there (feels faster while scrolling)
  var small = window.matchMedia("(max-width: 900px)").matches;
  if (!reduce && !small && "IntersectionObserver" in window) {
    var items = $$(revealSel).filter(function (el) { return !el.closest(".hero, .page-hero, .site-header, dialog, .drawer, .car-track"); });
    document.documentElement.classList.add("anim");
    items.forEach(function (el) {
      el.classList.add("reveal");
      var sib = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
      el.style.setProperty("--d", Math.min(sib, 5) * 70 + "ms"); // small stagger inside grids
    });
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target; rio.unobserve(el); el.classList.add("is-in");
        // once shown, drop the classes so hover effects and normal styles apply again
        setTimeout(function () { el.classList.remove("reveal", "is-in"); el.style.removeProperty("--d"); }, 1200);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach(function (el) { rio.observe(el); });
  }
})();
