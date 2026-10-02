/* site.js — injects config.json values into the static pages.
   - [data-config="key"]        -> sets element text to config[key] (if non-empty)
   - [data-config-href="key"]   -> sets href to config[key]; the element is
                                   revealed only when the value is non-empty.
   Contact buttons are hidden in the static HTML and only shown when their
   config value exists, so empty placeholders never render as dead links.
   Also powers the category filter on index.html and the photo gallery on
   listing pages. No external dependencies. */
(function () {
  "use strict";

  function configPath() {
    return window.location.pathname.indexOf("/listings/") !== -1
      ? "../config.json"
      : "config.json";
  }

  function applyConfig(config) {
    if (!config || typeof config !== "object") return;
    document.querySelectorAll("[data-config]").forEach(function (el) {
      var v = config[el.getAttribute("data-config")];
      if (typeof v === "string" && v.length > 0) el.textContent = v;
    });
    document.querySelectorAll("[data-config-href]").forEach(function (el) {
      var v = config[el.getAttribute("data-config-href")];
      if (typeof v === "string" && v.length > 0) {
        el.setAttribute("href", v);
        el.removeAttribute("hidden");
      } else {
        el.setAttribute("hidden", "");
      }
    });
  }

  function initFilters() {
    var grid = document.getElementById("catalog-grid");
    if (!grid) return;
    var buttons = document.querySelectorAll(".filter-btn");
    var emptyMsg = document.getElementById("grid-empty");
    var search = document.getElementById("catalog-search");
    var activeCat = "all";
    var query = "";
    function apply() {
      var visible = 0;
      grid.querySelectorAll(".card").forEach(function (card) {
        var cats = (card.getAttribute("data-cats") || "").split(" ");
        var title = (card.querySelector("h3") || { textContent: "" }).textContent.toLowerCase();
        var show = (activeCat === "all" || cats.indexOf(activeCat) !== -1) &&
          (!query || title.indexOf(query) !== -1);
        card.style.display = show ? "" : "none";
        if (show) visible++;
      });
      if (emptyMsg) emptyMsg.hidden = visible !== 0;
    }
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        activeCat = btn.getAttribute("data-filter");
        apply();
      });
    });
    if (search) search.addEventListener("input", function (e) {
      query = e.target.value.trim().toLowerCase();
      apply();
    });
  }

  function initDescToggle() {
    var desc = document.getElementById("listing-desc");
    var btn = document.getElementById("desc-toggle");
    if (!desc || !btn) return;
    desc.classList.add("collapsed");
    // only offer the toggle when the text actually overflows
    if (desc.scrollHeight <= desc.clientHeight + 4) {
      desc.classList.remove("collapsed");
      return;
    }
    btn.hidden = false;
    btn.addEventListener("click", function () {
      var collapsed = desc.classList.toggle("collapsed");
      btn.textContent = collapsed ? "View more" : "Show less";
    });
  }

  function initShare() {
    var btn = document.getElementById("share-listing");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var url = window.location.href;
      if (navigator.share) {
        navigator.share({ title: document.title, url: url }).catch(function () {});
      } else if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () {
          btn.textContent = "Link copied!";
          setTimeout(function () { btn.textContent = "Share this listing"; }, 2000);
        });
      }
    });
  }

  function initGallery() {
    var main = document.getElementById("gallery-main");
    var gallery = document.querySelector(".gallery");
    if (!main || !gallery) return;
    var photos = [main.getAttribute("src")];
    var thumbs = Array.prototype.slice.call(document.querySelectorAll(".thumb"));
    thumbs.forEach(function (t) { photos.push(t.getAttribute("data-full")); });
    var idx = 0;
    function show(i) {
      idx = (i + photos.length) % photos.length;
      main.src = photos[idx];
      thumbs.forEach(function (t, ti) {
        t.classList.toggle("current", ti + 1 === idx);
      });
    }
    thumbs.forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        if (thumb.classList.contains("thumb-more")) {
          var strip = thumb.closest(".thumbs");
          if (strip) strip.classList.remove("collapsed");
          thumb.classList.remove("thumb-more");
          thumb.removeAttribute("data-remaining");
        }
        show(photos.indexOf(thumb.getAttribute("data-full")));
      });
    });
    // Swipe left/right on the gallery to move between photos.
    var startX = null;
    gallery.addEventListener("touchstart", function (e) {
      if (e.touches.length === 1) startX = e.touches[0].clientX;
    }, { passive: true });
    gallery.addEventListener("touchend", function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      startX = null;
      if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
    });
  }

  function initLightbox() {
    var gallery = document.querySelector(".gallery");
    var main = document.getElementById("gallery-main");
    if (!gallery || !main) return;
    var photos = [main.getAttribute("src")];
    Array.prototype.forEach.call(document.querySelectorAll(".thumb"), function (t) {
      var full = t.getAttribute("data-full");
      if (full) photos.push(full);
    });
    var lb = document.createElement("div");
    lb.className = "lightbox";
    lb.setAttribute("hidden", "");
    lb.innerHTML =
      '<button type="button" class="lb-btn lb-close" aria-label="Close">\u00d7</button>' +
      '<button type="button" class="lb-btn lb-prev" aria-label="Previous photo">\u2039</button>' +
      '<img class="lb-img" alt="Enlarged listing photo">' +
      '<button type="button" class="lb-btn lb-next" aria-label="Next photo">\u203a</button>';
    document.body.appendChild(lb);
    var img = lb.querySelector(".lb-img");
    var idx = 0;
    function show(i) {
      idx = (i + photos.length) % photos.length;
      img.src = photos[idx];
    }
    function open() {
      var i = photos.indexOf(main.getAttribute("src"));
      show(i === -1 ? 0 : i);
      lb.hidden = false;
      document.body.style.overflow = "hidden";
    }
    function close() {
      lb.hidden = true;
      document.body.style.overflow = "";
      // leave the gallery on the photo the lightbox was viewing
      if (idx > 0) {
        var thumb = document.querySelector('.thumb[data-full="' + photos[idx] + '"]');
        if (thumb) thumb.click(); else main.src = photos[idx];
      } else {
        main.src = photos[0];
      }
    }
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function (e) { e.stopPropagation(); show(idx - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function (e) { e.stopPropagation(); show(idx + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (lb.hidden) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowLeft") show(idx - 1);
      else if (e.key === "ArrowRight") show(idx + 1);
    });
    // Tap (not swipe) on the main photo opens the lightbox.
    var tX = null, tY = null;
    main.addEventListener("touchstart", function (e) {
      if (e.touches.length === 1) { tX = e.touches[0].clientX; tY = e.touches[0].clientY; }
    }, { passive: true });
    main.addEventListener("touchend", function (e) {
      if (tX === null) return;
      var dx = e.changedTouches[0].clientX - tX, dy = e.changedTouches[0].clientY - tY;
      tX = tY = null;
      if (Math.abs(dx) < 10 && Math.abs(dy) < 10) open();
    });
    main.addEventListener("click", open);
  }

  function initCatTiles() {
    document.querySelectorAll("[data-goto-filter]").forEach(function (tile) {
      tile.addEventListener("click", function () {
        var key = tile.getAttribute("data-goto-filter");
        var btn = document.querySelector('.filter-btn[data-filter="' + key + '"]');
        if (btn) btn.click();
        var target = document.getElementById("catalog");
        if (target) target.scrollIntoView({ behavior: "smooth" });
      });
    });
  }

  function initReviewsModal() {
    var openBtn = document.getElementById("reviews-open");
    var modal = document.getElementById("reviews-modal");
    if (!openBtn || !modal) return;
    function open() {
      modal.removeAttribute("hidden");
      document.body.style.overflow = "hidden";
      var close = modal.querySelector(".modal-close");
      if (close) close.focus();
    }
    function close() {
      modal.setAttribute("hidden", "");
      document.body.style.overflow = "";
      openBtn.focus();
    }
    openBtn.addEventListener("click", open);
    modal.addEventListener("click", function (e) {
      if (e.target === modal || e.target.hasAttribute("data-close-modal")) close();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !modal.hasAttribute("hidden")) close();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initFilters();
    initCatTiles();
    initGallery();
    initLightbox();
    initReviewsModal();
    initShare();
    initDescToggle();
    fetch(configPath())
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(applyConfig)
      .catch(function () { /* keep baked-in placeholders */ });
  });
})();
