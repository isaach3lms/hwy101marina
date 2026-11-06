(function () {
  "use strict";

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", open ? "false" : "true");
      toggle.setAttribute("aria-expanded", open ? "false" : "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.getAttribute("data-open") === "true") {
        nav.setAttribute("data-open", "false");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // Contact form: post the lead to Web3Forms from the browser (free plans reject
  // server-side calls). Anything unexpected falls back to the normal server post.
  var cf = document.querySelector("form[data-web3forms]");
  if (cf && window.fetch) {
    cf.addEventListener("submit", function (e) {
      var val = function (n) { var el = cf.querySelector('[name="' + n + '"]'); return el ? el.value.trim() : ""; };
      var thanks = cf.getAttribute("data-thanks");
      if (val("website")) { e.preventDefault(); window.location = thanks; return; }

      var digits = val("phone").replace(/\D/g, "");
      if (digits.length === 11 && digits.charAt(0) === "1") digits = digits.slice(1);
      var ok = val("name") && val("message") && digits.length === 10 && cf.checkValidity();
      if (!ok) return; // let the server show the field errors

      e.preventDefault();
      var btn = cf.querySelector('button[type="submit"]');
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Sending...";

      var sel = cf.querySelector('[name="interest"]');
      var interest = sel.options[sel.selectedIndex].text;
      var data = {
        access_key: cf.getAttribute("data-web3forms"),
        subject: "New " + interest.toLowerCase() + " inquiry from " + val("name"),
        from_name: "101 Marina Website",
        name: val("name"),
        phone: val("phone"),
        interest: interest,
        message: val("message"),
        botcheck: ""
      };
      if (val("email")) data.email = val("email");

      var fallback = function () { btn.disabled = false; btn.textContent = label; cf.submit(); };
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json(); })
        .then(function (j) { if (j && j.success) { window.location = thanks; } else { fallback(); } })
        .catch(fallback);
    });
  }

  // Lightbox for photo grids
  var grids = document.querySelectorAll("[data-lightbox]");
  if (!grids.length || typeof HTMLDialogElement === "undefined") return;

  var dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.setAttribute("aria-label", "Photo viewer");
  dlg.innerHTML =
    '<div class="lb-inner">' +
    '<button class="lb-btn lb-close" type="button" aria-label="Close">&times;</button>' +
    '<button class="lb-btn lb-prev" type="button" aria-label="Previous photo">&lsaquo;</button>' +
    '<img alt="">' +
    '<button class="lb-btn lb-next" type="button" aria-label="Next photo">&rsaquo;</button>' +
    "</div>";
  document.body.appendChild(dlg);

  var img = dlg.querySelector("img");
  var buttons = [];
  var index = 0;

  function show(i) {
    index = (i + buttons.length) % buttons.length;
    img.src = buttons[index].getAttribute("data-full");
    img.alt = buttons[index].getAttribute("data-alt") || "";
  }

  grids.forEach(function (grid) {
    var items = Array.prototype.slice.call(grid.querySelectorAll(".photo-btn"));
    items.forEach(function (btn, i) {
      btn.addEventListener("click", function () {
        buttons = items;
        show(i);
        dlg.showModal();
      });
    });
  });

  dlg.querySelector(".lb-close").addEventListener("click", function () { dlg.close(); });
  dlg.querySelector(".lb-prev").addEventListener("click", function () { show(index - 1); });
  dlg.querySelector(".lb-next").addEventListener("click", function () { show(index + 1); });
  dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target.classList.contains("lb-inner")) dlg.close(); });
  dlg.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") show(index - 1);
    if (e.key === "ArrowRight") show(index + 1);
  });
})();
