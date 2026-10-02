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
  var activeColor = "all";
  var activeFuel = "all";
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
      var okColor = activeColor === "all" || it.color === activeColor;
      var okFuel = activeFuel === "all" || it.fuel === activeFuel;
      return okCat && okQ && okColor && okFuel;
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
      "</button>";
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

  function wireFilterPopup() {
    var toggle = $("filter-toggle");
    var pop = $("filter-pop");
    var countBadge = $("filter-count");
    if (!toggle || !pop) return;

    function updateCount() {
      var n = (activeColor !== "all" ? 1 : 0) + (activeFuel !== "all" ? 1 : 0);
      countBadge.hidden = n === 0;
      countBadge.textContent = n;
    }
    function setPills(containerId, val) {
      var c = $(containerId);
      if (!c) return;
      Array.prototype.forEach.call(c.querySelectorAll(".fpill"), function (p) {
        p.classList.toggle("active", p.getAttribute("data-val") === val);
      });
    }
    function closePop() {
      pop.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    }
    pop.addEventListener("click", function (e) {
      var pill = e.target.closest(".fpill");
      if (pill) {
        var val = pill.getAttribute("data-val");
        var group = pill.parentElement.id;
        if (group === "filter-colors") activeColor = val; else activeFuel = val;
        setPills(group, val);
        renderGrid();
        updateCount();
        return;
      }
      if (e.target.closest("#filter-clear")) {
        activeColor = "all"; activeFuel = "all";
        setPills("filter-colors", "all");
        setPills("filter-fuels", "all");
        renderGrid();
        updateCount();
      }
    });
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = pop.hidden;
      pop.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", function (e) {
      if (!pop.hidden && !e.target.closest(".filter-wrap")) closePop();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closePop();
    });
  }

  function init() {
    if (!$("bundle-grid")) return;
    // color pills from what's actually in stock
    var colors = [];
    items.forEach(function (it) {
      if (it.color && colors.indexOf(it.color) === -1) colors.push(it.color);
    });
    colors.sort();
    var colorPills = $("filter-colors");
    colors.forEach(function (c) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "fpill";
      b.setAttribute("data-val", c);
      b.textContent = c.charAt(0).toUpperCase() + c.slice(1);
      colorPills.appendChild(b);
    });
    renderGrid();
    renderTiers();
    renderSummary();
    wireFilterPopup();

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

    $("bundle-grid").addEventListener("click", function (e) {
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
