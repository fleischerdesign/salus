(function() {
    let timerInterval = null;

    function formatTime(secs) {
        const m = Math.floor(secs / 60);
        const s = secs % 60;
        return m > 0 ? `${m}m ${s}s` : `${s}s`;
    }

    function playBeep() {
        // Vibrate phone (haptic feedback)
        if (navigator.vibrate) {
            navigator.vibrate([200, 100, 200]);
        }
        // Web Audio API beep
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            oscillator.type = "sine";
            oscillator.frequency.value = 880; // A5 note
            gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 0.3);
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
            updateTimerDisplay();
        } else {
            endTime = Date.now() + (remaining * 1000);
            sessionStorage.setItem("rest_timer_end", endTime.toString());
            updateTimerDisplay();
        }
    }

    function dismissTimer() {
        sessionStorage.removeItem("rest_timer_end");
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
})();
