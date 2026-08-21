/* Angelos C. Painting Inc. — site behaviour
   Small, dependency-free. Nothing here is required for the page to render. */

(function () {
  "use strict";

  /* ---- mobile nav toggle ---- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---- nav dropdowns ----
     Desktop opens them on hover and on keyboard focus (CSS :hover /
     :focus-within), so no JS is needed there. Inside the mobile drawer the
     same markup becomes a tap-to-expand accordion, which is what this drives.
     The caret button also gives keyboard and touch users an explicit control
     rather than relying on hover. */
  var ddItems = [].slice.call(document.querySelectorAll(".nav__item"));
  var isDesktop = function () { return window.matchMedia("(min-width: 901px)").matches; };

  var closeAll = function (except) {
    ddItems.forEach(function (item) {
      if (item === except) return;
      item.classList.remove("is-open");
      var t = item.querySelector(".dd-toggle");
      if (t) t.setAttribute("aria-expanded", "false");
    });
  };

  ddItems.forEach(function (item) {
    var toggle = item.querySelector(".dd-toggle");
    if (!toggle) return;

    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var open = !item.classList.contains("is-open");
      closeAll(item);
      item.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    /* on desktop, hovering one dropdown should drop any that was pinned open */
    item.addEventListener("mouseenter", function () {
      if (isDesktop()) closeAll();
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeAll();
      if (document.activeElement && document.activeElement.blur) {
        document.activeElement.blur();
      }
    }
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest || !e.target.closest(".nav__item")) closeAll();
  });

  /* dropdowns pinned open on mobile shouldn't stay open after a resize */
  var lastDesktop = isDesktop();
  window.addEventListener("resize", function () {
    var now = isDesktop();
    if (now !== lastDesktop) {
      lastDesktop = now;
      closeAll();
      if (nav) nav.classList.remove("is-open");
      if (toggle) toggle.setAttribute("aria-expanded", "false");
    }
  });

  /* ---- header shadow on scroll ---- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-stuck", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---- mark the current page in the nav ---- */
  var here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav .nav__link[href]").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === here) a.classList.add("is-active");
  });

  /* ---- contact form ----
     No backend is wired up yet. Until one is, the form hands the message
     off to the visitor's mail client so nothing is silently lost.
     Replace this block with a real POST to your CRM / form endpoint. */
  var form = document.querySelector("form[data-estimate-form]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var d = new FormData(form);
      var body = [
        "Name: " + (d.get("name") || ""),
        "Phone: " + (d.get("phone") || ""),
        "Email: " + (d.get("email") || ""),
        "Town: " + (d.get("town") || ""),
        "Service: " + (d.get("service") || ""),
        "",
        d.get("message") || ""
      ].join("\n");

      window.location.href =
        "mailto:" + form.dataset.estimateForm +
        "?subject=" + encodeURIComponent("Free estimate request — " + (d.get("name") || "Website")) +
        "&body=" + encodeURIComponent(body);

      var note = form.querySelector(".form-note");
      if (note) {
        note.textContent =
          "Opening your email app with the request. If nothing opens, call (914) 384-3187 and we'll take the details over the phone.";
      }
    });
  }

  /* ---- year in footer ---- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
