function showToast(message, type) {
    type = type || "success";
    var container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    
    var toast = document.createElement("div");
    toast.className = "toast toast--" + type;
    
    // Choose icon based on type
    var iconName = "info";
    var iconColor = "var(--color-primary)";
    if (type === "success") {
        iconName = "check_circle";
        iconColor = "var(--color-tertiary-600)";
    } else if (type === "error") {
        iconName = "error";
        iconColor = "var(--color-error-500)";
    }
    
    toast.innerHTML = `
        <div class="toast__icon">
            <span class="material-symbols-outlined icon icon--20" style="color:${iconColor}">${iconName}</span>
        </div>
        <div class="toast__content">${message}</div>
        <button class="toast__close" type="button" aria-label="Close">
            <span class="material-symbols-outlined icon icon--16">close</span>
        </button>
    `;
    
    // Bind close button click
    var closeBtn = toast.querySelector(".toast__close");
    closeBtn.addEventListener("click", function() {
        dismissToast(toast);
    });
    
    container.appendChild(toast);
    
    // Auto-dismiss after 4 seconds
    var timer = setTimeout(function() {
        dismissToast(toast);
    }, 4000);
    
    // Store timer on element to avoid issues if manually closed
    toast._dismissTimer = timer;
}

function dismissToast(toast) {
    if (toast._dismissing) return;
    toast._dismissing = true;
    if (toast._dismissTimer) clearTimeout(toast._dismissTimer);
    
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px) scale(0.95)";
    
    // Remove from DOM after fade animation completes (300ms)
    setTimeout(function() {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Global HTMX integration
document.addEventListener("show-toast", function(e) {
    var detail = e.detail;
    // HTMX dispatches with direct detail if JSON payload is string/dict
    if (detail) {
        var message = detail.message || detail.value || (typeof detail === "string" ? detail : "");
        var type = detail.type || "success";
        if (message) {
            showToast(message, type);
        }
    }
});
