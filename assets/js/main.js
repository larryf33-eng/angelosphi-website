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

  /* ---- photo lightbox (our-work pages) ----
     Every <a data-lightbox> is a real link to the full image, so the photos
     still open with JS off; this just upgrades them to an in-page viewer. */
  var lbLinks = [].slice.call(document.querySelectorAll("a[data-lightbox]"));
  if (lbLinks.length) {
    var lb, lbImg, lbCap, lbIdx = 0, lbReturn = null, lbTouchX = null;

    var lbBuild = function () {
      lb = document.createElement("div");
      lb.className = "lb" + (lbLinks.length === 1 ? " lb--single" : "");
      lb.hidden = true;
      lb.setAttribute("role", "dialog");
      lb.setAttribute("aria-modal", "true");
      lb.setAttribute("aria-label", "Photo viewer");
      lb.innerHTML =
        '<button class="lb__btn lb__close" type="button" aria-label="Close photo viewer">&times;</button>' +
        '<button class="lb__btn lb__prev" type="button" aria-label="Previous photo">&#8249;</button>' +
        '<figure class="lb__fig"><img class="lb__img" alt=""><figcaption class="lb__cap"></figcaption></figure>' +
        '<button class="lb__btn lb__next" type="button" aria-label="Next photo">&#8250;</button>';
      document.body.appendChild(lb);
      lbImg = lb.querySelector(".lb__img");
      lbCap = lb.querySelector(".lb__cap");

      lb.querySelector(".lb__close").addEventListener("click", lbClose);
      lb.querySelector(".lb__prev").addEventListener("click", function () { lbShow(lbIdx - 1); });
      lb.querySelector(".lb__next").addEventListener("click", function () { lbShow(lbIdx + 1); });
      lb.addEventListener("click", function (e) {
        if (e.target === lb || e.target.classList.contains("lb__fig")) lbClose();
      });
      lb.addEventListener("touchstart", function (e) { lbTouchX = e.changedTouches[0].clientX; }, { passive: true });
      lb.addEventListener("touchend", function (e) {
        if (lbTouchX === null) return;
        var dx = e.changedTouches[0].clientX - lbTouchX;
        lbTouchX = null;
        if (Math.abs(dx) > 50) lbShow(lbIdx + (dx < 0 ? 1 : -1));
      }, { passive: true });
    };

    var lbShow = function (i) {
      var n = lbLinks.length;
      lbIdx = (i + n) % n;
      var a = lbLinks[lbIdx], thumb = a.querySelector("img");
      lbImg.src = a.getAttribute("href");
      lbImg.alt = thumb ? thumb.alt : "";
      lbCap.textContent = (lbIdx + 1) + " / " + n;
      /* warm the next photo so arrowing through feels instant */
      var nxt = new Image();
      nxt.src = lbLinks[(lbIdx + 1) % n].getAttribute("href");
    };

    var lbOpen = function (i) {
      if (!lb) lbBuild();
      lbReturn = document.activeElement;
      lb.hidden = false;
      document.body.classList.add("lb-open");
      lbShow(i);
      lb.querySelector(".lb__close").focus();
    };

    var lbClose = function () {
      if (!lb || lb.hidden) return;
      lb.hidden = true;
      document.body.classList.remove("lb-open");
      if (lbReturn && lbReturn.focus) lbReturn.focus();
    };

    lbLinks.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        /* let ctrl/cmd/middle-click open the file in a new tab as normal */
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
        e.preventDefault();
        lbOpen(i);
      });
    });

    document.addEventListener("keydown", function (e) {
      if (!lb || lb.hidden) return;
      if (e.key === "Escape") lbClose();
      else if (e.key === "ArrowLeft") lbShow(lbIdx - 1);
      else if (e.key === "ArrowRight") lbShow(lbIdx + 1);
      else if (e.key === "Tab") {
        /* keep keyboard focus inside the viewer while it is open */
        var f = [].slice.call(lb.querySelectorAll(".lb__btn")).filter(function (b) { return b.offsetParent !== null; });
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  /* ---- year in footer ---- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
