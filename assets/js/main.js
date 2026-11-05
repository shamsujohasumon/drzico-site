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
          window.location.href = "appointment.html";
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

  /* ---------- video popup ---------- */
  var vm = $("#video-modal");
  if (vm && typeof vm.showModal === "function") {
    var vmFrame = $(".vm-frame", vm), vmTitle = $(".vm-title", vm);
    var closeVm = function () { if (vm.open) vm.close(); };
    vm.addEventListener("close", function () { vmFrame.innerHTML = ""; }); // stops playback
    $$("[data-video]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var id = a.getAttribute("data-video"), t = a.getAttribute("data-title") || "Video";
        var f = document.createElement("iframe");
        f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + "?autoplay=1&rel=0";
        f.title = t; f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen"; f.allowFullscreen = true;
        vmFrame.innerHTML = ""; vmFrame.appendChild(f); vmTitle.textContent = t;
        vm.showModal();
      });
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

  /* ---------- appointment request form ---------- */
  var form = $("#booking-form");
  if (form) {
    var dateInput = $("#b-date", form), chamberSel = $("#b-chamber", form), hint = $("#b-date-hint", form), chips = $("#b-next", form);
    var now = dhakaNow();
    dateInput.min = iso(now.y, now.m, now.d);
    var max = addDays(now.y, now.m, now.d, 60);
    dateInput.max = iso(max.y, max.m, max.d);

    // preselect concern from ?concern= in the URL (links from service pages)
    try {
      var qs = new URLSearchParams(window.location.search).get("concern");
      if (qs) { var opt = $('#b-concern option[value="' + qs + '"]', form); if (opt) opt.selected = true; }
      var ch = new URLSearchParams(window.location.search).get("chamber");
      if (ch && CHAMBERS[ch]) chamberSel.value = ch;
    } catch (e) { /* ignore */ }

    function refreshDates() {
      var key = chamberSel.value;
      chips.innerHTML = "";
      if (CHAMBERS[key] && CHAMBERS[key].days) {
        hint.textContent = "This chamber sits on " + CHAMBERS[key].dayText + ", " + CHAMBERS[key].hours + ".";
        nextOpenDates(key, 4).forEach(function (t) {
          var b = document.createElement("button");
          b.type = "button"; b.textContent = prettyDate(t);
          b.addEventListener("click", function () { dateInput.value = iso(t.y, t.m, t.d); validate(dateInput); });
          chips.appendChild(b);
        });
      } else if (key === "malibag") {
        hint.textContent = "Hours at this chamber are confirmed by phone. Pick a preferred date and the team will confirm.";
      } else {
        hint.textContent = "Choose a chamber first to see its days.";
      }
    }
    chamberSel.addEventListener("change", function () { refreshDates(); if (dateInput.value) validate(dateInput); });
    refreshDates();

    var rules = {
      "b-name": function (v) { return v.trim().length >= 3 ? "" : "Enter the patient's full name (at least 3 letters)."; },
      "b-phone": function (v) {
        var d = v.replace(/[\s-]/g, "").replace(/^\+?88/, "");
        return /^01[3-9]\d{8}$/.test(d) ? "" : "Enter an 11-digit Bangladeshi mobile number, for example 017XXXXXXXX.";
      },
      "b-age": function (v) { return v === "" || (+v >= 0 && +v <= 110) ? "" : "Age must be between 0 and 110."; },
      "b-chamber": function (v) { return v ? "" : "Choose a chamber."; },
      "b-date": function (v) {
        if (!v) return "Choose a preferred date.";
        if (v < dateInput.min) return "Choose today or a later date.";
        var cc = CHAMBERS[chamberSel.value];
        if (cc && cc.days) {
          var p = v.split("-"), dow = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])).getUTCDay();
          if (cc.days.indexOf(dow) === -1) return "This chamber is on " + cc.dayText + " only. Pick one of those days.";
        }
        return "";
      },
      "b-concern": function (v) { return v ? "" : "Choose the main problem, or \"Not sure\"."; },
      "b-consent": function (v, el) { return el.checked ? "" : "Please tick this box to continue."; }
    };
    function validate(el) {
      var fn = rules[el.id]; if (!fn) return true;
      var msg = fn(el.value, el);
      var field = el.closest(".field") || el.closest(".check");
      var err = $("#" + el.id + "-err");
      if (field) field.classList.toggle("has-error", !!msg);
      if (err) { err.textContent = msg; err.hidden = !msg; }
      el.setAttribute("aria-invalid", msg ? "true" : "false");
      return !msg;
    }
    Object.keys(rules).forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      el.addEventListener(el.type === "checkbox" || el.tagName === "SELECT" ? "change" : "blur", function () { validate(el); });
      // clear an error as soon as the input becomes valid, so the layout does not jump on the next click
      el.addEventListener("input", function () { if (el.getAttribute("aria-invalid") === "true") validate(el); });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = [];
      Object.keys(rules).forEach(function (id) {
        var el = document.getElementById(id);
        if (el && !validate(el)) bad.push(el);
      });
      var summary = $("#b-summary");
      if (bad.length) {
        summary.hidden = false;
        summary.innerHTML = "<strong>Please fix " + bad.length + " field" + (bad.length > 1 ? "s" : "") + ":</strong><ul></ul>";
        var ul = $("ul", summary);
        bad.forEach(function (el) {
          var li = document.createElement("li"), a = document.createElement("a");
          a.href = "#" + el.id; a.textContent = $("#" + el.id + "-err").textContent;
          li.appendChild(a); ul.appendChild(li);
        });
        bad[0].focus();
        return;
      }
      summary.hidden = true;

      var btn = $("button[type=submit]", form);
      btn.disabled = true; btn.textContent = "Sending...";
      var data = {
        name: $("#b-name").value.trim(),
        phone: $("#b-phone").value.trim(),
        age: $("#b-age").value,
        chamber: CHAMBERS[chamberSel.value].name,
        date: dateInput.value,
        concern: $("#b-concern").selectedOptions[0].textContent,
        mri: $("#b-mri").value,
        notes: $("#b-notes").value.trim()
      };
      // TODO(Next.js): POST `data` to /api/appointments and show the result.
      window.setTimeout(function () {
        var ok = $("#booking-success");
        var dl = $("dl", ok); dl.innerHTML = "";
        [["Patient", data.name], ["Mobile", data.phone], ["Chamber", data.chamber], ["Preferred date", data.date], ["Problem", data.concern], ["MRI / CT", data.mri]].forEach(function (r) {
          var dt = document.createElement("dt"), dd = document.createElement("dd");
          dt.textContent = r[0]; dd.textContent = r[1] || "Not given"; dl.appendChild(dt); dl.appendChild(dd);
        });
        $("#b-call-number").textContent = CHAMBERS[chamberSel.value].phone;
        ok._text = "Appointment request\n" + [["Patient", data.name], ["Mobile", data.phone], ["Age", data.age], ["Chamber", data.chamber], ["Preferred date", data.date], ["Problem", data.concern], ["MRI / CT", data.mri], ["Notes", data.notes]].map(function (r) { return r[0] + ": " + (r[1] || "-"); }).join("\n");
        form.hidden = true; ok.hidden = false; ok.focus();
        btn.disabled = false; btn.textContent = "Send request";
      }, 500);
    });

    var copyBtn = $("#b-copy"), again = $("#b-again");
    if (copyBtn) copyBtn.addEventListener("click", function () {
      var txt = $("#booking-success")._text || "";
      var done = function () { copyBtn.textContent = "Copied"; setTimeout(function () { copyBtn.textContent = "Copy details"; }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, function () { copyBtn.textContent = "Copy blocked"; });
    });
    if (again) again.addEventListener("click", function () {
      form.reset(); refreshDates(); form.hidden = false; $("#booking-success").hidden = true; $("#b-name").focus();
    });
  }
})();
