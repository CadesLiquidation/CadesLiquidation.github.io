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
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        var f = btn.getAttribute("data-filter");
        var visible = 0;
        grid.querySelectorAll(".card").forEach(function (card) {
          var cats = (card.getAttribute("data-cats") || "").split(" ");
          var show = f === "all" || cats.indexOf(f) !== -1;
          card.style.display = show ? "" : "none";
          if (show) visible++;
        });
        if (emptyMsg) emptyMsg.hidden = visible !== 0;
      });
    });
  }

  function initGallery() {
    var main = document.getElementById("gallery-main");
    if (!main) return;
    document.querySelectorAll(".thumb").forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        main.src = thumb.getAttribute("data-full");
        document.querySelectorAll(".thumb").forEach(function (t) {
          t.classList.remove("current");
        });
        thumb.classList.add("current");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initFilters();
    initGallery();
    fetch(configPath())
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(applyConfig)
      .catch(function () { /* keep baked-in placeholders */ });
  });
})();
