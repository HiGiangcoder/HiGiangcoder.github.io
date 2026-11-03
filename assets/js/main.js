/* =========================================================================
   Hành vi nhỏ của blog: đổi sáng/tối, thanh tiến độ đọc, lọc bài viết.
   Không phụ thuộc thư viện ngoài.
   ========================================================================= */

(function () {
  "use strict";

  /* ---------------------------------------------------------------
     Sáng / tối
     --------------------------------------------------------------- */

  var root = document.documentElement;
  var STORAGE_KEY = "theme";
  var saved = null;

  try {
    saved = window.localStorage.getItem(STORAGE_KEY);
  } catch (error) {
    saved = null;
  }

  if (saved === "light" || saved === "dark") {
    root.setAttribute("data-theme", saved);
  }

  var toggle = document.querySelector(".theme-toggle");
  var media = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function prefersDark() {
    return !!(media && media.matches);
  }

  function isDarkMode() {
    var explicit = root.getAttribute("data-theme");
    if (explicit === "dark") return true;
    if (explicit === "light") return false;
    return prefersDark();
  }

  function syncToggle() {
    if (!toggle) return;
    var dark = isDarkMode();
    toggle.setAttribute("aria-pressed", String(dark));
    toggle.setAttribute(
      "aria-label",
      dark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"
    );
    toggle.setAttribute(
      "title",
      dark ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"
    );
  }

  if (toggle) {
    syncToggle();

    toggle.addEventListener("click", function () {
      var next = isDarkMode() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        window.localStorage.setItem(STORAGE_KEY, next);
      } catch (error) {
        /* Trình duyệt chặn localStorage — vẫn đổi được trong phiên này. */
      }
      syncToggle();
    });

    if (media) {
      var onSchemeChange = function () {
        if (!root.getAttribute("data-theme")) syncToggle();
      };
      if (typeof media.addEventListener === "function") {
        media.addEventListener("change", onSchemeChange);
      } else if (typeof media.addListener === "function") {
        media.addListener(onSchemeChange);
      }
    }
  }

  /* ---------------------------------------------------------------
     Thanh tiến độ đọc (chỉ có ở trang bài viết)
     --------------------------------------------------------------- */

  var progress = document.querySelector(".reading-progress");

  if (progress) {
    var updateProgress = function () {
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      var percent = max > 0 ? (window.scrollY / max) * 100 : 0;
      progress.style.width = Math.min(100, Math.max(0, percent)) + "%";
    };

    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
  }

  /* ---------------------------------------------------------------
     Mục lục bài viết (outline) — tự động từ các tiêu đề H2/H3
     --------------------------------------------------------------- */

  var outline = document.getElementById("post-outline");
  var outlineNav = document.getElementById("post-outline-nav");
  var postBody = document.querySelector(".post-body");

  if (outline && outlineNav && postBody) {
    var headings = postBody.querySelectorAll("h2, h3, h4");
    if (headings.length >= 2) {
      var list = document.createElement("ul");
      list.className = "post-outline-list";

      headings.forEach(function (heading) {
        if (!heading.id) {
          heading.id = heading.textContent
            .trim()
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
        }

        var item = document.createElement("li");
        item.className =
          "post-outline-item post-outline-" + heading.tagName.toLowerCase();

        var link = document.createElement("a");
        link.href = "#" + heading.id;
        link.textContent = heading.textContent;

        item.appendChild(link);
        list.appendChild(item);
      });

      outlineNav.appendChild(list);
      outline.hidden = false;

      outlineNav.addEventListener("click", function (event) {
        var target = event.target;
        if (target && target.tagName === "A") {
          event.preventDefault();
          var id = target.getAttribute("href").slice(1);
          var el = document.getElementById(id);
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
            history.replaceState(null, "", "#" + id);
          }
        }
      });
    }
  }

  /* ---------------------------------------------------------------
     Tìm kiếm & lọc theo chủ đề (trang /bai-viet/)
     --------------------------------------------------------------- */

  var searchInput = document.getElementById("post-search");
  var postList = document.getElementById("post-list");

  if (searchInput && postList) {
    var cards = Array.prototype.slice.call(
      postList.querySelectorAll(".post-card")
    );
    var chips = Array.prototype.slice.call(
      document.querySelectorAll("[data-topic-filter]")
    );
    var resultCount = document.getElementById("result-count");
    var emptyState = document.getElementById("empty-state");
    var activeTopic = "all";

    // Bỏ dấu tiếng Việt để gõ không dấu vẫn tìm được.
    var normalize = function (value) {
      return (value || "")
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/đ/g, "d");
    };

    var items = cards.map(function (card) {
      return {
        el: card,
        topic: card.getAttribute("data-topic") || "",
        text: normalize(card.getAttribute("data-search") || "")
      };
    });

    var applyFilters = function () {
      var query = normalize(searchInput.value.trim());
      var visible = 0;

      items.forEach(function (item) {
        var matchesTopic =
          activeTopic === "all" || item.topic === activeTopic;
        var matchesQuery = !query || item.text.indexOf(query) !== -1;
        var show = matchesTopic && matchesQuery;

        item.el.hidden = !show;
        if (show) visible += 1;
      });

      if (resultCount) {
        resultCount.textContent = visible + " bài viết";
      }
      if (emptyState) {
        emptyState.hidden = visible !== 0;
      }
    };

    chips.forEach(function (chip) {
      chip.setAttribute(
        "aria-pressed",
        String(chip.getAttribute("data-topic-filter") === activeTopic)
      );

      chip.addEventListener("click", function () {
        activeTopic = chip.getAttribute("data-topic-filter") || "all";

        chips.forEach(function (otherChip) {
          var active = otherChip === chip;
          otherChip.classList.toggle("is-active", active);
          otherChip.setAttribute("aria-pressed", String(active));
        });

        applyFilters();
      });
    });

    searchInput.addEventListener("input", applyFilters);
    applyFilters();
  }
})();
