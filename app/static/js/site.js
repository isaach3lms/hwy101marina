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
