// --- CSRF helper: define globally at the very top ---
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// --- Souline Timeline Script with Toast Notifications ---
document.addEventListener("DOMContentLoaded", function () {
  const csrftoken = getCookie("csrftoken");

  // --- Toast helper ---
  function showToast(message, type = "success") {
    const existing = document.getElementById("toast-container");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "toast-container";
    const base =
      "fixed top-5 right-5 px-5 py-3 rounded-lg shadow-lg text-white font-medium transition-all duration-300 opacity-0 z-50";
    const color =
      type === "error"
        ? "bg-red-500"
        : type === "warning"
        ? "bg-yellow-500 text-[#446178]"
        : "bg-[#FFA04D]";
    toast.className = `${base} ${color}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => (toast.style.opacity = "1"), 100);
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  // --- Handle Post creation ---
  const postForm = document.getElementById("postForm");
  if (postForm) {
    postForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const url = postForm.getAttribute("action");
      const formData = new FormData(postForm);

      fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: formData,
      })
        .then((res) => {
          if (!res.ok) return res.json().then((r) => Promise.reject(r));
          return res.json();
        })
        .then((data) => {
          if (data.success) {
            const posts = document.getElementById("posts");
            posts.insertAdjacentHTML("afterbegin", data.html);
            postForm.reset();
            showToast("Posted successfully!");
          }
        })
        .catch(() => showToast("Failed to post.", "error"));
    });
  }

  // --- Handle Likes ---
  document.body.addEventListener("click", function (e) {
    const likeBtn = e.target.closest(".like-btn");
    if (likeBtn) {
      const postId = likeBtn.dataset.postId;
      fetch(`/timeline/post/${postId}/like/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken, Accept: "application/json" },
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.success) {
            const countSpan = likeBtn.querySelector(".like-count");
            if (countSpan) countSpan.innerText = data.like_count;
            likeBtn.innerHTML =
              (data.action === "liked" ? "❤️" : "🤍") +
              ` <span class="like-count">${data.like_count}</span>`;
            showToast(
              data.action === "liked" ? "You liked a post!" : "Like removed",
              data.action === "liked" ? "success" : "warning"
            );
          } else if (data.error === "login_required") {
            showToast("Please log in to like posts.", "warning");
          }
        })
        .catch(() => showToast("Error toggling like", "error"));
    }
  });

  // --- Handle Comments ---
  document.body.addEventListener("submit", function (e) {
    const commentForm = e.target.closest(".comment-form");
    if (commentForm) {
      e.preventDefault();
      const postId = commentForm.dataset.postId;
      const url = commentForm.getAttribute("action");
      const formData = new FormData(commentForm);

      fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: formData,
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.success) {
            const comments = document.getElementById("comments-for-" + postId);
            comments.insertAdjacentHTML("beforeend", data.html);
            commentForm.querySelector('input[name="text"]').value = "";
            showToast("Comment added!");
          } else if (data.error === "login_required") {
            showToast("Please log in to comment.", "warning");
          }
        })
        .catch(() => showToast("Failed to comment", "error"));
    }
  });

  // --- Edit post ---
  document.body.addEventListener("click", function (e) {
    const editBtn = e.target.closest(".edit-btn");
    if (editBtn) {
      const postId = editBtn.dataset.postId;
      const postEl = document.getElementById(`post-${postId}`);
      const textEl = postEl.querySelector(".post-body p");
      const oldText = textEl ? textEl.innerText : "";

      textEl.outerHTML = `
        <textarea id="edit-text-${postId}" class="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-[#FFA04D]">${oldText}</textarea>
        <div class="mt-2 flex gap-2">
          <button class="save-edit-btn bg-[#FFA04D] text-white rounded-lg px-3 py-1" data-post-id="${postId}">Save</button>
          <button class="cancel-edit-btn border border-gray-300 rounded-lg px-3 py-1" data-post-id="${postId}">Cancel</button>
        </div>
      `;
    }
  });

  // --- Save edited post ---
  document.body.addEventListener("click", function (e) {
    const saveBtn = e.target.closest(".save-edit-btn");
    if (saveBtn) {
      const postId = saveBtn.dataset.postId;
      const textarea = document.getElementById(`edit-text-${postId}`);
      const newText = textarea.value.trim();

      fetch(`/timeline/post/${postId}/edit/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken"), "Accept": "application/json" },
        body: new URLSearchParams({ text: newText }),
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.success) {
            const postEl = document.getElementById(`post-${postId}`);
            postEl.outerHTML = data.html;
            showToast("Post updated!");
          } else {
            showToast("Failed to edit post", "error");
          }
        })
        .catch(() => showToast("Error editing post", "error"));
    }
  });

  // --- Delete post ---
  document.body.addEventListener("click", function (e) {
    const deleteBtn = e.target.closest(".delete-btn");
    if (deleteBtn && confirm("Are you sure you want to delete this post?")) {
      const postId = deleteBtn.dataset.postId;

      fetch(`/timeline/post/${postId}/delete/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken"), "Accept": "application/json" },
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.success) {
            document.getElementById(`post-${postId}`).remove();
            showToast("Post deleted!", "warning");
          } else {
            showToast("You can only delete your own posts", "error");
          }
        })
        .catch(() => showToast("Error deleting post", "error"));
    }
  });
});
