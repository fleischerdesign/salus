document.addEventListener("click", function(e) {
    var radio = e.target.closest("input[type='radio'][name='theme']");
    if (radio) {
        var theme = radio.value;
        
        // Trigger smooth transition
        document.documentElement.classList.add("theme-transition");
        document.documentElement.setAttribute("data-theme", theme);
        
        setTimeout(function() {
            document.documentElement.classList.remove("theme-transition");
        }, 300);

        if (typeof showToast === "function") {
            showToast("Theme updated!", "success");
        }
    }
});
