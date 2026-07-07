document.addEventListener("click", function(e) {
    // 1. Click on Option
    var option = e.target.closest(".select__option");
    if (option) {
        var dropdown = option.closest(".select__dropdown");
        if (dropdown) {
            var selectWrapper = dropdown.closest(".select");
            var hiddenInput = dropdown.querySelector("input[type='hidden']");
            var trigger = selectWrapper.querySelector(".select__trigger");
            var valueDisplay = trigger.querySelector(".select__value");
            
            // Set value
            var val = option.getAttribute("data-value");
            hiddenInput.value = val;
            
            // Set label
            valueDisplay.textContent = option.textContent.trim();
            valueDisplay.classList.remove("select__placeholder");
            
            // Mark selected
            dropdown.querySelectorAll(".select__option").forEach(function(opt) {
                opt.removeAttribute("aria-selected");
            });
            option.setAttribute("aria-selected", "true");
            
            // Close dropdown
            trigger.setAttribute("aria-expanded", "false");
            
            // Dispatch change event on the hidden input to trigger HTMX or JS changes
            hiddenInput.dispatchEvent(new Event("change", { bubbles: true }));
        }
        return;
    }
    
    // 2. Click outside to close
    var activeTrigger = document.querySelector(".select__trigger[aria-expanded='true']");
    if (activeTrigger) {
        var selectWrapper = activeTrigger.closest(".select");
        if (!selectWrapper.contains(e.target)) {
            activeTrigger.setAttribute("aria-expanded", "false");
        }
    }
});
