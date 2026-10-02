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
    var colorSel = document.getElementById("color-filter");
    var fuelSel = document.getElementById("fuel-filter");
    var activeCat = "all";
    function apply() {
      var color = colorSel ? colorSel.value : "all";
      var fuel = fuelSel ? fuelSel.value : "all";
      var visible = 0;
      grid.querySelectorAll(".card").forEach(function (card) {
        var cats = (card.getAttribute("data-cats") || "").split(" ");
        var show = (activeCat === "all" || cats.indexOf(activeCat) !== -1) &&
          (color === "all" || card.getAttribute("data-color") === color) &&
          (fuel === "all" || card.getAttribute("data-fuel") === fuel);
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
    if (colorSel) colorSel.addEventListener("change", apply);
    if (fuelSel) fuelSel.addEventListener("change", apply);
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
    initReviewsModal();
    fetch(configPath())
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(applyConfig)
      .catch(function () { /* keep baked-in placeholders */ });
  });
})();
