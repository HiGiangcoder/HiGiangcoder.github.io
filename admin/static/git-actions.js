/*
 * Gỡ / đăng lại bài trên GitHub không reload trang.
 *
 * Form cần có class "js-git-action" và data-git-state="tracked|untracked".
 * Phạm vi cập nhật là phần tử gần nhất có [data-git-scope].
 */
(function () {
  "use strict";

  function setBusy(button, busy) {
    if (!button) return;
    if (busy) {
      button.dataset.originalHtml = button.innerHTML;
      button.disabled = true;
      button.innerHTML = '<span class="spinner"></span>' + button.dataset.originalHtml;
    } else {
      button.disabled = false;
      if (button.dataset.originalHtml) {
        button.innerHTML = button.dataset.originalHtml;
      }
    }
  }

  function applyState(scope, tracked) {
    var state = tracked ? "tracked" : "untracked";
    scope.querySelectorAll("form.js-git-action").forEach(function (form) {
      form.hidden = form.dataset.gitState !== state;
    });

    var pill = scope.querySelector("[data-git-pill]");
    if (pill) {
      pill.textContent = tracked ? "Đã đăng GitHub" : "Chưa đăng GitHub";
      pill.classList.toggle("pill-ok", tracked);
      pill.classList.toggle("pill-warn", !tracked);
    }

    var description = scope.querySelector("[data-git-description]");
    if (description) {
      description.textContent = tracked
        ? "Bài này đang được đăng trên GitHub. Bạn có thể gỡ nó khỏi GitHub nhưng vẫn giữ file trên máy."
        : "Bài này chưa được đăng trên GitHub hoặc đã bị gỡ. Bạn có thể đăng lại.";
    }

    // Trong danh sách bài viết: chuyển dòng sang đúng khu vực
    // "Đang quản lý" / "Lưu trữ" mà không cần tải lại trang.
    var row = scope.closest("[data-post-row]");
    if (row) {
      var target = document.querySelector(
        tracked ? "[data-managed-section]" : "[data-archived-section]"
      );
      var tbody = target && target.querySelector("tbody");
      if (tbody && row.parentElement !== tbody) {
        tbody.prepend(row);
      }
      row.hidden = false;
      document.dispatchEvent(new CustomEvent("git-state-changed"));
    }
  }

  function showStatus(scope, message, ok) {
    var status = scope.querySelector("[data-git-status]");
    if (status) {
      status.textContent = message;
      status.className = "save-status " + (ok ? "ok" : "error");
    }
    var link = scope.querySelector("[data-git-publish-link]");
    if (link) link.hidden = false;
  }

  document.addEventListener("submit", function (event) {
    var form = event.target.closest("form.js-git-action");
    if (!form) return;

    event.preventDefault();
    var scope = form.closest("[data-git-scope]") || document;
    var button = form.querySelector('button[type="submit"]');
    setBusy(button, true);

    var status = scope.querySelector("[data-git-status]");
    if (status) {
      status.textContent = "Đang xử lý...";
      status.className = "save-status pending";
    }

    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (response) {
        return response.json().then(function (body) {
          if (!response.ok) throw new Error(body.detail || "Thao tác thất bại.");
          return body;
        });
      })
      .then(function (body) {
        if (body.ok && typeof body.tracked === "boolean") {
          applyState(scope, body.tracked);
        }
        showStatus(
          scope,
          body.summary || (body.ok ? "Thành công." : "Thất bại."),
          body.ok
        );
      })
      .catch(function (error) {
        showStatus(scope, error.message || "Thao tác thất bại.", false);
      })
      .finally(function () {
        setBusy(button, false);
      });
  });
})();
