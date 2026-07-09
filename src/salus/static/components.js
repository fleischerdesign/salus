/*
 * Salus Components JS — AUTO-GENERATED
 * Source: templates/components/[component]/script.js
 * Regenerate: uv run python tools/build_components.py
 */

/* @source src/salus/templates/components/ui/multi-select/script.js */
(function() {
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
})();


/* @source src/salus/templates/components/ui/notifications/bell/script.js */
(function() {
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
})();


/* @source src/salus/templates/components/ui/radio-group/script.js */
(function() {
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
})();


/* @source src/salus/templates/components/ui/rest-timer/script.js */
(function() {
(function() {
    let timerInterval = null;
    let keepAliveContext = null;
    let keepAliveNode = null;
    let keepAliveOscillator = null;

    function formatTime(secs) {
        const m = Math.floor(secs / 60);
        const s = secs % 60;
        return m > 0 ? `${m}m ${s}s` : `${s}s`;
    }

    function startAudioKeepAlive() {
        // Upgrade check: If running inside native Capacitor, skip web audio hack
        if (window.Capacitor) {
            return;
        }
        if (keepAliveContext) return;

        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            keepAliveContext = new AudioContextClass();
            
            // Create a silent audio path to keep context active
            keepAliveOscillator = keepAliveContext.createOscillator();
            keepAliveNode = keepAliveContext.createGain();
            
            keepAliveOscillator.frequency.value = 0; // sub-audible
            keepAliveNode.gain.value = 0.0;          // silent
            
            keepAliveOscillator.connect(keepAliveNode);
            keepAliveNode.connect(keepAliveContext.destination);
            
            keepAliveOscillator.start();
        } catch (e) {
            console.warn("Could not start background audio keep-alive:", e);
        }
    }

    function stopAudioKeepAlive() {
        if (keepAliveOscillator) {
            try { keepAliveOscillator.stop(); } catch (e) {}
            keepAliveOscillator = null;
        }
        if (keepAliveContext) {
            try { keepAliveContext.close(); } catch (e) {}
            keepAliveContext = null;
        }
    }

    function playBeep() {
        stopAudioKeepAlive();

        // Vibrate phone (haptic feedback)
        if (navigator.vibrate) {
            navigator.vibrate([200, 100, 200, 100, 200]);
        }
        // Web Audio API beep
        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            const audioCtx = new AudioContextClass();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            oscillator.type = "sine";
            oscillator.frequency.value = 880; // A5 note
            gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 0.4);
        } catch (e) {
            console.log("Audio beep failed", e);
        }
        if (typeof showToast === "function") {
            showToast("Rest time is up! Get ready for your next set. 💪", "success");
        }
        window.dispatchEvent(new CustomEvent("rest-timer-finished"));
    }

    function updateTimerDisplay() {
        const pill = document.getElementById("rest-timer-pill");
        const display = document.getElementById("rest-timer-countdown");
        if (!pill || !display) return;

        const endStr = sessionStorage.getItem("rest_timer_end");
        if (!endStr) {
            pill.removeAttribute("data-active");
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            return;
        }

        const endTime = parseInt(endStr, 10);
        const remaining = Math.max(0, Math.ceil((endTime - Date.now()) / 1000));

        if (remaining <= 0) {
            sessionStorage.removeItem("rest_timer_end");
            pill.removeAttribute("data-active");
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            playBeep();
            return;
        }

        display.innerText = formatTime(remaining);
        pill.setAttribute("data-active", "true");

        if (!timerInterval) {
            timerInterval = setInterval(updateTimerDisplay, 1000);
        }
    }

    function startTimer(duration) {
        const endTime = Date.now() + (duration * 1000);
        sessionStorage.setItem("rest_timer_end", endTime.toString());
        startAudioKeepAlive();
        updateTimerDisplay();
        window.dispatchEvent(new CustomEvent("rest-timer-started", { detail: { duration } }));
    }

    function adjustTimer(delta) {
        const endStr = sessionStorage.getItem("rest_timer_end");
        if (!endStr) return;
        let endTime = parseInt(endStr, 10);
        let remaining = Math.max(0, Math.ceil((endTime - Date.now()) / 1000));
        remaining = Math.max(0, remaining + delta);
        
        if (remaining <= 0) {
            sessionStorage.removeItem("rest_timer_end");
            stopAudioKeepAlive();
            updateTimerDisplay();
        } else {
            endTime = Date.now() + (remaining * 1000);
            sessionStorage.setItem("rest_timer_end", endTime.toString());
            startAudioKeepAlive();
            updateTimerDisplay();
        }
    }

    function dismissTimer() {
        sessionStorage.removeItem("rest_timer_end");
        stopAudioKeepAlive();
        updateTimerDisplay();
    }

    // Decoupled event listener to trigger timer from other parts of the app
    window.addEventListener("start-rest-timer", function(e) {
        if (e.detail && typeof e.detail.duration === "number") {
            startTimer(e.detail.duration);
        }
    });

    function bindEvents() {
        const addBtn = document.getElementById("rest-timer-add-btn");
        const closeBtn = document.getElementById("rest-timer-close-btn");
        if (addBtn && !addBtn.getAttribute("data-bound")) {
            addBtn.setAttribute("data-bound", "true");
            addBtn.addEventListener("click", function() { adjustTimer(30); });
        }
        if (closeBtn && !closeBtn.getAttribute("data-bound")) {
            closeBtn.setAttribute("data-bound", "true");
            closeBtn.addEventListener("click", dismissTimer);
        }
    }

    document.addEventListener("DOMContentLoaded", function() {
        bindEvents();
        updateTimerDisplay();
    });

    document.body.addEventListener("htmx:afterSwap", function() {
        // Re-bind listeners just in case htmx swapped base wrapper (though base is static)
        bindEvents();
        updateTimerDisplay();
    });

    // Fallback: If page reloads with a running timer, restart keep-alive on first user tap
    document.addEventListener("click", function() {
        const endStr = sessionStorage.getItem("rest_timer_end");
        if (endStr && parseInt(endStr, 10) > Date.now()) {
            startAudioKeepAlive();
        }
    });
})();
})();


/* @source src/salus/templates/components/ui/select/script.js */
(function() {
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
})();


/* @source src/salus/templates/components/ui/toast/script.js */
(function() {
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
})();

