/* bundle.js — Bundle Builder: tap appliances to build a bundle,
   get an automatic tiered discount, see the total before tax.
   Discount tiers come from config.json (bundleTiers) with sane defaults. */
(function () {
  "use strict";

  var DEFAULT_TIERS = [
    { minItems: 2, discountPct: 3 },
    { minItems: 3, discountPct: 5 },
    { minItems: 4, discountPct: 7 }
  ];
  var PHONE = "+13094344800";
  var SITE = "cadesliquidation.github.io";

  var items = window.BUNDLE_ITEMS || [];
  var selected = {};
  var tiers = DEFAULT_TIERS.slice();
  var activeFilter = "all";
  var query = "";

  function $(id) { return document.getElementById(id); }

  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function money(n) {
    var s = n % 1 === 0 ? String(n) : n.toFixed(2);
    return "$" + s.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  function tierFor(count) {
    var best = null;
    tiers.forEach(function (t) {
      if (count >= t.minItems && (!best || t.minItems > best.minItems)) best = t;
    });
    return best;
  }

  function nextTier(count) {
    var nxt = null;
    tiers.forEach(function (t) {
      if (t.minItems > count && (!nxt || t.minItems < nxt.minItems)) nxt = t;
    });
    return nxt;
  }

  function visibleItems() {
    return items.filter(function (it) {
      var okCat = activeFilter === "all" || it.category.toLowerCase() === activeFilter;
      var okQ = !query || it.title.toLowerCase().indexOf(query) !== -1;
      return okCat && okQ;
    });
  }

  function cardHTML(it) {
    var sel = !!selected[it.id];
    var retail = it.retail
      ? '<span class="bcard-retail">Retail $' + Number(it.retail).toLocaleString() + "</span>"
      : "";
    return '<button class="bcard' + (sel ? " selected" : "") + '" data-id="' + it.id +
      '" aria-pressed="' + sel + '">' +
      '<span class="bcard-check" aria-hidden="true">\u2713</span>' +
      '<span class="bcard-img"><img src="images/' + it.photo + '" alt="" loading="lazy"></span>' +
      '<span class="badge">' + escapeHTML(it.category) + "</span>" +
      '<span class="bcard-title">' + escapeHTML(it.title) + "</span>" +
      retail +
      '<span class="price">' + escapeHTML(it.price) + "</span>" +
      '<span class="bcard-details" role="button" tabindex="0" data-id="' + it.id + '">More details</span>' +
      "</button>";
  }

  var detailsModal = null;
  var detailsId = null;

  function findItem(id) {
    for (var i = 0; i < items.length; i++) if (items[i].id === id) return items[i];
    return null;
  }

  function buildDetailsModal() {
    detailsModal = document.createElement("div");
    detailsModal.className = "bmodal";
    detailsModal.setAttribute("hidden", "");
    detailsModal.innerHTML =
      '<div class="bmodal-card" role="dialog" aria-modal="true" aria-label="Listing details">' +
      '<button type="button" class="bmodal-x" aria-label="Close">\u00d7</button>' +
      '<img class="bmodal-img" alt="">' +
      '<div class="bmodal-body">' +
      '<span class="badge bmodal-cat"></span>' +
      '<h3 class="bmodal-title"></h3>' +
      '<p class="bmodal-price"></p>' +
      '<p class="bmodal-meta"></p>' +
      '<p class="bmodal-desc"></p>' +
      '<button type="button" class="btn bmodal-toggle"></button>' +
      "</div></div>";
    document.body.appendChild(detailsModal);
    detailsModal.querySelector(".bmodal-x").addEventListener("click", closeDetails);
    detailsModal.addEventListener("click", function (e) {
      if (e.target === detailsModal) closeDetails();
    });
    detailsModal.querySelector(".bmodal-toggle").addEventListener("click", function () {
      if (!detailsId) return;
      if (selected[detailsId]) {
        delete selected[detailsId];
      } else {
        var it = findItem(detailsId);
        if (it) selected[detailsId] = it;
      }
      renderGrid();
      renderSummary();
      syncDetailsToggle();
    });
    document.addEventListener("keydown", function (e) {
      if (detailsModal && !detailsModal.hidden && e.key === "Escape") closeDetails();
    });
  }

  function syncDetailsToggle() {
    var btn = detailsModal.querySelector(".bmodal-toggle");
    if (selected[detailsId]) {
      btn.className = "btn btn-ghost bmodal-toggle";
      btn.innerHTML = "\u2713 In your bundle \u2014 tap to remove";
    } else {
      btn.className = "btn btn-call bmodal-toggle";
      btn.textContent = "Add to bundle";
    }
  }

  function openDetails(id) {
    var it = findItem(id);
    if (!it) return;
    detailsId = id;
    var img = detailsModal.querySelector(".bmodal-img");
    img.src = "images/" + it.photo;
    img.alt = it.title;
    detailsModal.querySelector(".bmodal-cat").textContent = it.category;
    detailsModal.querySelector(".bmodal-title").textContent = it.title;
    var priceHtml = it.retail
      ? '<span class="bcard-retail">Retail $' + Number(it.retail).toLocaleString() + "</span> "
      : "";
    priceHtml += '<span class="price">' + escapeHTML(it.price) + "</span>";
    detailsModal.querySelector(".bmodal-price").innerHTML = priceHtml;
    detailsModal.querySelector(".bmodal-meta").textContent =
      it.condition + (it.fuel ? " \u00b7 " + it.fuel : "");
    detailsModal.querySelector(".bmodal-desc").innerHTML =
      escapeHTML(it.description || "No additional details yet \u2014 text Cade with questions.")
        .replace(/\n/g, "<br>");
    syncDetailsToggle();
    detailsModal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeDetails() {
    if (!detailsModal) return;
    detailsModal.hidden = true;
    document.body.style.overflow = "";
    detailsId = null;
  }

  function renderGrid() {
    var vis = visibleItems();
    $("bundle-grid").innerHTML = vis.map(cardHTML).join("");
    $("bundle-empty").hidden = vis.length !== 0;
  }

  function renderTiers() {
    $("bundle-tiers").innerHTML = tiers.map(function (t) {
      return '<span class="btier"><strong>' + t.discountPct + "% off</strong> " +
        t.minItems + "+ items</span>";
    }).join("");
  }

  function bundleMessage(list, subtotal, tier, discount, total) {
    var lines = list.map(function (it) { return "- " + it.title + " (" + it.price + ")"; });
    var msg = "Hi Cade! I'd like this bundle from " + SITE + ":\n" + lines.join("\n") +
      "\nSubtotal: " + money(subtotal);
    if (tier) msg += ", bundle discount (" + tier.discountPct + "%): -" + money(discount);
    return msg + "\nTotal before tax: " + money(total);
  }

  function renderSummary() {
    var box = $("bundle-summary");
    var list = Object.keys(selected).map(function (id) { return selected[id]; });
    var n = list.length;
    if (!n) {
      box.innerHTML = '<div class="bsummary"><h2>Your bundle</h2>' +
        '<p class="muted">Tap appliances to add them here. Bundles of 2 or more unlock a discount.</p></div>';
      return;
    }
    var subtotal = list.reduce(function (s, it) { return s + it.price_num; }, 0);
    var tier = tierFor(n);
    var discount = tier ? subtotal * tier.discountPct / 100 : 0;
    var total = subtotal - discount;
    var retailTotal = list.reduce(function (s, it) { return s + (it.retail || 0); }, 0);

    var itemsHTML = list.map(function (it) {
      return '<li><img src="images/' + it.photo + '" alt="">' +
        '<span class="bitem-title">' + escapeHTML(it.title) + "</span>" +
        '<span class="bitem-price">' + escapeHTML(it.price) + "</span>" +
        '<button class="bremove" data-id="' + it.id + '" aria-label="Remove">&times;</button></li>';
    }).join("");

    var discountRow = tier
      ? '<div class="bdiscount"><dt>Bundle discount (' + tier.discountPct + '%)</dt><dd>&minus;' + money(discount) + "</dd></div>"
      : "";
    var progress = "";
    var nxt = nextTier(n);
    if (nxt) {
      var need = nxt.minItems - n;
      progress = '<p class="bprogress">Add ' + need + " more item" + (need > 1 ? "s" : "") +
        " to unlock " + nxt.discountPct + "% off.</p>";
    }
    var saveLine = retailTotal > subtotal
      ? '<p class="bsave">You save ' + money(retailTotal - subtotal) + " off retail.</p>"
      : "";

    box.innerHTML = '<div class="bsummary"><h2>Your bundle <span class="bcount">' + n + "</span></h2>" +
      '<ul class="bitems">' + itemsHTML + "</ul>" +
      '<dl class="btotals">' +
      "<div><dt>Subtotal</dt><dd>" + money(subtotal) + "</dd></div>" +
      discountRow +
      '<div class="btotal"><dt>Total before tax</dt><dd>' + money(total) + "</dd></div>" +
      "</dl>" +
      '<p class="btaxnote">Plus sales tax. 14-day money-back guarantee.</p>' +
      saveLine + progress +
      '<a class="btn btn-call btn-lg bcta" id="bundle-sms" href="#">Text Cade this bundle</a>' +
      '<button class="btn btn-fb bcopy" id="bundle-copy" type="button">Copy bundle details</button>' +
      "</div>";

    var msg = bundleMessage(list, subtotal, tier, discount, total);
    $("bundle-sms").href = "sms:" + PHONE + "?&body=" + encodeURIComponent(msg);
    $("bundle-copy").addEventListener("click", function () {
      function done(btn, label) {
        btn.textContent = label;
        setTimeout(function () { btn.textContent = "Copy bundle details"; }, 2000);
      }
      var btn = $("bundle-copy");
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(msg).then(
          function () { done(btn, "Copied!"); },
          function () { done(btn, "Copy failed"); });
      } else {
        done(btn, "Copy not supported");
      }
    });
  }

  function init() {
    if (!$("bundle-grid")) return;
    buildDetailsModal();
    renderGrid();
    renderTiers();
    renderSummary();

    document.querySelectorAll(".bfilter").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.querySelectorAll(".bfilter").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        activeFilter = btn.getAttribute("data-filter");
        renderGrid();
      });
    });

    $("bundle-search").addEventListener("input", function (e) {
      query = e.target.value.trim().toLowerCase();
      renderGrid();
    });

    $("bundle-grid").addEventListener("keydown", function (e) {
      var det = e.target.closest(".bcard-details");
      if (det && (e.key === "Enter" || e.key === " ")) {
        e.preventDefault();
        e.stopPropagation();
        openDetails(det.getAttribute("data-id"));
      }
    });

    $("bundle-grid").addEventListener("click", function (e) {
      var det = e.target.closest(".bcard-details");
      if (det) {
        openDetails(det.getAttribute("data-id"));
        return;
      }
      var card = e.target.closest(".bcard");
      if (!card) return;
      var id = card.getAttribute("data-id");
      if (selected[id]) {
        delete selected[id];
      } else {
        var it = items.filter(function (x) { return x.id === id; })[0];
        if (it) selected[id] = it;
      }
      renderGrid();
      renderSummary();
    });

    $("bundle-summary").addEventListener("click", function (e) {
      var rm = e.target.closest(".bremove");
      if (!rm) return;
      delete selected[rm.getAttribute("data-id")];
      renderGrid();
      renderSummary();
    });

    fetch("config.json").then(function (r) { return r.json(); }).then(function (cfg) {
      if (cfg && Array.isArray(cfg.bundleTiers) && cfg.bundleTiers.length) {
        tiers = cfg.bundleTiers;
        renderTiers();
        renderSummary();
      }
    }).catch(function () { /* defaults stand */ });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
