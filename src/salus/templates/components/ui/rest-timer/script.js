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
