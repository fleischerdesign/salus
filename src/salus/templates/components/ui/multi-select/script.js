(function() {
    function initMultiSelects() {
        document.querySelectorAll(".multi-select").forEach(function(container) {
            // Avoid double initialization
            if (container.getAttribute("data-initialized")) return;
            container.setAttribute("data-initialized", "true");

            const hiddenInput = container.querySelector(`input[type="hidden"]`);
            const searchInput = container.querySelector(`.multi-select__search`);
            const controlArea = container.querySelector(`.multi-select__control`);
            const tagsContainer = container.querySelector(`.multi-select__tags`);
            const options = container.querySelectorAll(`.multi-select__option`);
            const noOptionsMsg = container.querySelector(`.multi-select__no-options`);

            let selectedValues = [];
            const initialVal = hiddenInput.value;
            if (initialVal) {
                selectedValues = initialVal.split(",").filter(Boolean);
            }

            // Sync chips on startup
            renderChips();
            syncDropdownStates();

            // Focus search input when clicking anywhere in control area
            controlArea.addEventListener("click", function(e) {
                if (e.target !== searchInput && !e.target.closest(".multi-select__chip-close")) {
                    searchInput.focus();
                }
            });

            // Show dropdown on focus
            searchInput.addEventListener("focus", function() {
                container.setAttribute("data-open", "true");
                filterOptions();
            });

            // Filter options on input
            searchInput.addEventListener("input", function() {
                container.setAttribute("data-open", "true");
                filterOptions();
            });

            // Handle keyboard navigation in dropdown
            searchInput.addEventListener("keydown", function(e) {
                if (e.key === "Backspace" && !searchInput.value && selectedValues.length > 0) {
                    // Remove last chip
                    selectedValues.pop();
                    updateValue();
                    e.preventDefault();
                } else if (e.key === "Escape") {
                    container.removeAttribute("data-open");
                    searchInput.blur();
                } else if (e.key === "Enter") {
                    e.preventDefault(); // Prevent form submission!
                    
                    // Find first visible option and select it
                    let firstVisible = null;
                    options.forEach(function(opt) {
                        if (!firstVisible && opt.style.display !== "none") {
                            firstVisible = opt;
                        }
                    });
                    
                    if (firstVisible) {
                        firstVisible.click();
                    }
                }
            });

            // Handle selecting options from dropdown
            options.forEach(function(option) {
                option.addEventListener("click", function(e) {
                    const value = option.getAttribute("data-value");
                    const index = selectedValues.indexOf(value);

                    if (index === -1) {
                        selectedValues.push(value);
                    } else {
                        selectedValues.splice(index, 1);
                    }

                    updateValue();
                    searchInput.value = "";
                    searchInput.focus();
                    filterOptions();
                    e.stopPropagation();
                });
            });

            // Close dropdown when clicking outside
            document.addEventListener("click", function(e) {
                if (!container.contains(e.target)) {
                    container.removeAttribute("data-open");
                }
            });

            function filterOptions() {
                const query = searchInput.value.toLowerCase().trim();
                let visibleCount = 0;

                options.forEach(function(option) {
                    const label = (option.getAttribute("data-label") || "").toLowerCase();
                    const matchesQuery = label.includes(query);
                    
                    if (matchesQuery) {
                        option.style.display = "block";
                        visibleCount++;
                    } else {
                        option.style.display = "none";
                    }
                });

                if (noOptionsMsg) {
                    noOptionsMsg.style.display = visibleCount === 0 ? "block" : "none";
                }
            }

            function syncDropdownStates() {
                options.forEach(function(option) {
                    const value = option.getAttribute("data-value");
                    const isSelected = selectedValues.includes(value);
                    option.setAttribute("data-selected", isSelected ? "true" : "false");
                });
            }

            function renderChips() {
                tagsContainer.innerHTML = "";
                selectedValues.forEach(function(val) {
                    // Find option to get label
                    let label = val;
                    const option = container.querySelector(`.multi-select__option[data-value="${val}"]`);
                    if (option) {
                        label = option.getAttribute("data-label");
                    }

                    const chip = document.createElement("span");
                    chip.className = "multi-select__chip";
                    chip.innerHTML = `${label} <span class="multi-select__chip-close" data-value="${val}">&times;</span>`;
                    
                    // Bind delete click
                    chip.querySelector(".multi-select__chip-close").addEventListener("click", function(e) {
                        const valToRemove = this.getAttribute("data-value");
                        selectedValues = selectedValues.filter(v => v !== valToRemove);
                        updateValue();
                        e.stopPropagation();
                    });

                    tagsContainer.appendChild(chip);
                });
                
                // Adjust placeholder
                const originalPlaceholder = searchInput.getAttribute("placeholder") || searchInput.getAttribute("data-placeholder") || "";
                if (selectedValues.length > 0) {
                    if (!searchInput.getAttribute("data-placeholder")) {
                        searchInput.setAttribute("data-placeholder", originalPlaceholder);
                    }
                    searchInput.removeAttribute("placeholder");
                } else {
                    const placeholderToSet = originalPlaceholder || searchInput.getAttribute("data-placeholder") || "";
                    if (placeholderToSet) {
                        searchInput.setAttribute("placeholder", placeholderToSet);
                    }
                }
            }

            function updateValue() {
                hiddenInput.value = selectedValues.join(",");
                renderChips();
                syncDropdownStates();
                
                // Trigger change event
                const event = new Event("change", { bubbles: true });
                hiddenInput.dispatchEvent(event);
            }
        });
    }

    // Initialize on load and on HTMX swaps
    document.addEventListener("DOMContentLoaded", initMultiSelects);
    document.body.addEventListener("htmx:afterSwap", initMultiSelects);
})();
