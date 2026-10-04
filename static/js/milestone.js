/* Sikkim Escapes · "Milestone" behaviour. Plain JS, no dependencies.
   Every feature is opt-in through data attributes, so pages that do not use one pay nothing for it. */
(function () {
  "use strict";
  var d = document, root = d.documentElement, body = d.body;
  var $ = function (s, el) { return (el || d).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || d).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var store = {
    get: function (k) { try { return window.sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.sessionStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };

  /* ---------- reveal on scroll ---------- */
  var rv = $$(".rv");
  if (!("IntersectionObserver" in window) || reduce) {
    rv.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    rv.forEach(function (el) { io.observe(el); });
    /* never leave content hidden if something goes wrong */
    setTimeout(function () { rv.forEach(function (el) { el.classList.add("is-in"); }); }, 4000);
  }

  /* ---------- masthead shadow, altimeter rail, floating CTA, buy bar ---------- */
  var mast = $(".mast"), railNow = $("[data-rail-now]"), fab = $("[data-fab]"), buybar = $("[data-buybar]");
  var buyAfter = $("[data-buybar-after]");
  function onScroll() {
    var y = window.pageYOffset || root.scrollTop;
    var max = Math.max(1, root.scrollHeight - window.innerHeight);
    if (mast) mast.classList.toggle("is-scrolled", y > 8);
    if (railNow) railNow.style.bottom = Math.min(100, (y / max) * 100).toFixed(1) + "%";
    if (fab) fab.classList.toggle("is-on", y > 700 && !(buybar && buybar.classList.contains("is-on")));
    if (buybar) {
      var limit = buyAfter ? buyAfter.getBoundingClientRect().bottom + y : 600;
      var on = y > limit;
      buybar.classList.toggle("is-on", on);
      body.classList.toggle("has-buybar", on);
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- mega menus ---------- */
  var drops = $$(".nav__drop");
  function closeDrops(except) {
    drops.forEach(function (dr) {
      if (dr === except) return;
      dr.classList.remove("is-open");
      var b = $("button", dr);
      if (b) b.setAttribute("aria-expanded", "false");
    });
  }
  drops.forEach(function (dr) {
    var btn = $("button", dr), timer;
    if (!btn) return;
    btn.addEventListener("click", function () {
      var open = !dr.classList.contains("is-open");
      closeDrops(dr);
      dr.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
    dr.addEventListener("mouseenter", function () {
      if (!window.matchMedia("(hover: hover)").matches) return;
      clearTimeout(timer);
      closeDrops(dr);
      dr.classList.add("is-open");
      btn.setAttribute("aria-expanded", "true");
    });
    dr.addEventListener("mouseleave", function () {
      if (!window.matchMedia("(hover: hover)").matches) return;
      timer = setTimeout(function () { dr.classList.remove("is-open"); btn.setAttribute("aria-expanded", "false"); }, 180);
    });
  });
  d.addEventListener("click", function (e) { if (!e.target.closest(".nav__drop")) closeDrops(); });

  /* ---------- mobile sheet ---------- */
  var sheet = $(".sheet");
  function sheetOpen(open) {
    if (!sheet) return;
    sheet.classList.toggle("is-open", open);
    body.style.overflow = open ? "hidden" : "";
    if (open) { var c = $("[data-sheet-close]", sheet); if (c) c.focus(); }
  }
  $$("[data-sheet-open]").forEach(function (b) { b.addEventListener("click", function () { sheetOpen(true); }); });
  $$("[data-sheet-close]").forEach(function (b) { b.addEventListener("click", function () { sheetOpen(false); }); });

  /* ---------- search overlay ---------- */
  var search = $(".search"), q = $("#q"), results = search ? $(".search__results", search) : null, index = null, lastFocus;
  function loadIndex() {
    if (index || !q) return Promise.resolve(index);
    return fetch(q.getAttribute("data-search-url"), { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (rows) { index = rows; return rows; })
      .catch(function () { index = []; return index; });
  }
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function render(term) {
    if (!results) return;
    var t = norm(term).trim();
    if (!t) { results.innerHTML = ""; return; }
    var words = t.split(/\s+/), price = null, m = t.match(/(\d[\d,]{3,})/);
    if (m) price = parseInt(m[1].replace(/,/g, ""), 10);
    var hits = (index || []).map(function (row) {
      var hay = norm(row[0] + " " + row[2] + " " + row[3]), score = 0;
      for (var i = 0; i < words.length; i++) {
        if (price && /\d/.test(words[i])) continue;
        if (hay.indexOf(words[i]) === -1) return null;
        score += norm(row[0]).indexOf(words[i]) === 0 ? 3 : (norm(row[0]).indexOf(words[i]) > -1 ? 2 : 1);
      }
      return { row: row, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 14);
    results.innerHTML = hits.length ? hits.map(function (h) {
      return '<li><a href="' + esc(h.row[1]) + '"><span>' + esc(h.row[0]) + '</span><small>' + esc(h.row[2]) + (h.row[3] ? " · " + esc(h.row[3]) : "") + "</small></a></li>";
    }).join("") : '<li style="padding:12px;color:var(--ink-3)">Nothing found. Try a place, a district or "homestay".</li>';
  }
  function searchOpen(open) {
    if (!search) return;
    if (open) {
      lastFocus = d.activeElement;
      search.hidden = false;
      body.style.overflow = "hidden";
      loadIndex().then(function () { render(q.value); });
      setTimeout(function () { q.focus(); }, 30);
    } else {
      search.hidden = true;
      body.style.overflow = "";
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
  }
  $$("[data-search-open]").forEach(function (b) { b.addEventListener("click", function () { sheetOpen(false); searchOpen(true); }); });
  $$("[data-search-close]").forEach(function (b) { b.addEventListener("click", function () { searchOpen(false); }); });
  if (search) search.addEventListener("click", function (e) { if (e.target === search) searchOpen(false); });
  if (q) q.addEventListener("input", function () { render(q.value); });

  d.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { searchOpen(false); sheetOpen(false); closeDrops(); fabOpen(false); }
    if (e.key === "/" && search && search.hidden && !/input|textarea|select/i.test((e.target.tagName || ""))) { e.preventDefault(); searchOpen(true); }
  });

  /* ---------- floating CTA ---------- */
  var fabBtn = fab ? $(".fab__toggle", fab) : null, fabPanel = $("#fab-panel");
  function fabOpen(open) {
    if (!fabBtn || !fabPanel) return;
    fabPanel.hidden = !open;
    fabBtn.setAttribute("aria-expanded", String(open));
  }
  if (fabBtn) fabBtn.addEventListener("click", function () { fabOpen(fabPanel.hidden); });
  if (fab) {
    var msVal = $(".ms__val", fab);
    if (msVal) {
      /* the milestone counts the road from Gangtok as you read: decorative, matches page length */
      window.addEventListener("scroll", function () {
        var max = Math.max(1, root.scrollHeight - window.innerHeight);
        msVal.textContent = Math.round(((window.pageYOffset || 0) / max) * 125) + " km";
      }, { passive: true });
    }
  }

  /* ---------- planning nudge ---------- */
  var nudge = $("[data-nudge]");
  if (nudge && !store.get("se-nudge")) {
    var shown = false;
    var show = function () { if (shown) return; shown = true; nudge.hidden = false; store.set("se-nudge", "1"); };
    setTimeout(show, 45000);
    window.addEventListener("scroll", function () {
      var max = Math.max(1, root.scrollHeight - window.innerHeight);
      if ((window.pageYOffset || 0) / max > 0.6) show();
    }, { passive: true });
    $$("[data-nudge-close]", nudge).forEach(function (b) { b.addEventListener("click", function () { nudge.hidden = true; }); });
  }

  /* ---------- tabs: [data-tabs] > .tab[aria-controls] ---------- */
  $$("[data-tabs]").forEach(function (box) {
    var tabs = $$(".tab", box);
    function select(tab) {
      tabs.forEach(function (t) {
        var on = t === tab, panel = d.getElementById(t.getAttribute("aria-controls"));
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        if (panel) panel.hidden = !on;
      });
    }
    tabs.forEach(function (t, i) {
      t.setAttribute("role", "tab");
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var n = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (n) { var nx = tabs[(i + n + tabs.length) % tabs.length]; nx.focus(); select(nx); }
      });
    });
    var start = tabs.filter(function (t) { return t.getAttribute("aria-selected") === "true"; })[0] || tabs[0];
    if (start) select(start);
  });

  /* ---------- fill cards: complete the last row of a grid with planning prompts ---------- */
  function fillGrids() {
    $$("[data-fill]").forEach(function (grid) {
      var fills = $$("[data-fill-card]", grid);
      fills.forEach(function (f) { f.hidden = true; });
      var items = $$(":scope > :not([data-fill-card])", grid).filter(function (el) { return !el.hidden && el.offsetParent !== null; });
      var cols = getComputedStyle(grid).gridTemplateColumns.split(" ").filter(Boolean).length || 1;
      if (!items.length || cols < 2) return;
      var gap = (cols - (items.length % cols)) % cols;
      for (var i = 0; i < Math.min(gap, fills.length); i++) fills[i].hidden = false;
    });
  }
  fillGrids();
  var rt;
  window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(fillGrids, 150); });

  /* ---------- filters: [data-filters] controls a [data-filter-target] grid of [data-item] ----------
     select[data-filter="region"]      -> exact match on item data-region
     select[data-filter="themes"]      -> value contained in space-separated data-themes
     select[data-filter-range="price"] -> value "lo-hi", numeric range on data-price      */
  $$("[data-filters]").forEach(function (form) {
    var target = d.getElementById(form.getAttribute("data-filters")) || $("[data-filter-target]");
    if (!target) return;
    var count = $("[data-filter-count]", form), empty = $("[data-filter-empty]");
    var items = $$("[data-item]", target);
    function apply() {
      var n = 0;
      var controls = $$("select, input[type=radio]:checked, button[aria-pressed=true]", form);
      items.forEach(function (it) {
        var ok = controls.every(function (c) {
          var v = c.value !== undefined && c.tagName !== "BUTTON" ? c.value : c.getAttribute("data-value");
          if (!v) return true;
          var key = c.getAttribute("data-filter"), range = c.getAttribute("data-filter-range");
          if (range) {
            var parts = v.split("-"), x = parseFloat(it.getAttribute("data-" + range) || "0");
            return x >= parseFloat(parts[0] || "0") && x < parseFloat(parts[1] || "1e12");
          }
          if (!key) return true;
          var have = (it.getAttribute("data-" + key) || "").split(" ");
          return have.indexOf(v) > -1;
        });
        it.hidden = !ok;
        if (ok) n++;
      });
      if (count) count.textContent = n + (n === 1 ? " result" : " results");
      if (empty) empty.hidden = n > 0;
      fillGrids();
    }
    form.addEventListener("change", apply);
    $$("button[data-value]", form).forEach(function (b) {
      b.addEventListener("click", function () {
        var group = b.getAttribute("data-filter");
        $$('button[data-filter="' + group + '"]', form).forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
        apply();
      });
    });
    var reset = $("[data-filter-reset]", form);
    if (reset) reset.addEventListener("click", function () {
      $$("select", form).forEach(function (s) { s.selectedIndex = 0; });
      $$("button[data-value]", form).forEach(function (o) { o.setAttribute("aria-pressed", String(!o.getAttribute("data-value"))); });
      apply();
    });
    /* preselect from the query string, e.g. ?region=north-sikkim&tier=budget */
    var params = new URLSearchParams(window.location.search);
    $$("select", form).forEach(function (s) {
      var k = s.getAttribute("data-filter") || s.getAttribute("data-filter-range");
      if (k && params.get(k)) s.value = params.get(k);
    });
    apply();
  });

  /* ---------- plan wizard ---------- */
  $$("[data-wizard]").forEach(function (form) {
    var steps = $$(".wizard__step", form), marks = $$(".wizard__steps li", form), bar = $(".wizard__bar span", form);
    if (steps.length < 2) return;
    var i = 0;
    /* jump to the first step with a server-side error */
    steps.forEach(function (s, k) { if (i === 0 && $(".errorlist", s)) i = k; });
    function go(n) {
      i = Math.max(0, Math.min(steps.length - 1, n));
      steps.forEach(function (s, k) { s.classList.toggle("is-on", k === i); });
      marks.forEach(function (m, k) { m.classList.toggle("is-on", k <= i); });
      if (bar) bar.style.width = ((i + 1) / steps.length * 100) + "%";
    }
    form.setAttribute("data-ready", "");
    $$("[data-next]", form).forEach(function (b) {
      b.addEventListener("click", function () {
        var bad = $$("input, select, textarea", steps[i]).filter(function (f) { return f.willValidate && !f.checkValidity(); });
        if (bad.length) { bad[0].reportValidity(); return; }
        go(i + 1);
        form.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      });
    });
    $$("[data-prev]", form).forEach(function (b) { b.addEventListener("click", function () { go(i - 1); }); });
    go(i);
  });

  /* ---------- the climb (home): steps switch the sticky photo and the altimeter ---------- */
  var climbSteps = $$(".climb__step");
  if (climbSteps.length && "IntersectionObserver" in window) {
    var imgs = $$(".climb__img"), meter = $("[data-climb-alt]"), cbar = $(".climb__bar i"), top = 0;
    climbSteps.forEach(function (s) { top = Math.max(top, +s.getAttribute("data-alt") || 0); });
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var k = climbSteps.indexOf(en.target), alt = +en.target.getAttribute("data-alt") || 0;
        climbSteps.forEach(function (s, j) { s.classList.toggle("is-on", j === k); });
        imgs.forEach(function (im, j) { im.classList.toggle("is-on", j === k); });
        if (meter) meter.textContent = alt.toLocaleString("en-IN");
        if (cbar) cbar.style.height = (top ? alt / top * 100 : 0) + "%";
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    climbSteps.forEach(function (s) { cio.observe(s); });
  }

  /* ---------- on-page table of contents highlight ---------- */
  var tocLinks = $$(".toc-side a[href^='#']");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { var t = d.getElementById(a.getAttribute("href").slice(1)); if (t) map[t.id] = a; });
    var tio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          tocLinks.forEach(function (a) { a.classList.remove("is-on"); });
          map[en.target.id].classList.add("is-on");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { tio.observe(d.getElementById(id)); });
  }

  /* ---------- analytics: data-cta clicks and data-cta-form submits (GA4 only if configured) ---------- */
  function track(name, label) { if (typeof window.gtag === "function") window.gtag("event", name, { cta: label, page: location.pathname }); }
  d.addEventListener("click", function (e) { var a = e.target.closest("[data-cta]"); if (a) track("cta_click", a.getAttribute("data-cta")); });
  $$("[data-cta-form]").forEach(function (f) { f.addEventListener("submit", function () { track("lead_form", f.getAttribute("data-cta-form")); }); });
})();
