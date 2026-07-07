document.addEventListener("click", function(e) {
    // 1. Toggle notifications dropdown
    var trigger = e.target.closest(".notifications-menu__trigger");
    if (trigger) {
        var isOpen = trigger.getAttribute("aria-expanded") === "true";
        
        // Close other notification triggers if they exist
        document.querySelectorAll(".notifications-menu__trigger").forEach(function(t) {
            if (t !== trigger) t.setAttribute("aria-expanded", "false");
        });
        
        trigger.setAttribute("aria-expanded", !isOpen ? "true" : "false");
        return;
    }
    
    // 2. Click outside to close
    var activeTrigger = document.querySelector(".notifications-menu__trigger[aria-expanded='true']");
    if (activeTrigger) {
        var menu = activeTrigger.closest(".notifications-menu");
        if (!menu.contains(e.target)) {
            activeTrigger.setAttribute("aria-expanded", "false");
        }
    }
});

// Close on Escape key press
document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
        var activeTrigger = document.querySelector(".notifications-menu__trigger[aria-expanded='true']");
        if (activeTrigger) {
            activeTrigger.setAttribute("aria-expanded", "false");
            activeTrigger.focus();
        }
    }
});
