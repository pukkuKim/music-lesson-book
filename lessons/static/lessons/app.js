const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

document.querySelectorAll(".assignment").forEach((el) => {
    el.addEventListener("click", async (event) => {
        const circle = event.target.closest(".circle");
        if (!circle || circle.classList.contains("filled") || el.dataset.busy)
            return;

        el.dataset.busy = "1";
        const feedback = el.querySelector(".feedback");
        try {
            const res = await fetch(el.dataset.url, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            const next = el.querySelector(".circle:not(.filled)");
            next.classList.add("filled", "pop");
            feedback.textContent = data.message;
            if (data.is_done) el.classList.add("complete");

            const done = el
                .closest(".piece")
                .querySelector(".piece-progress .done");
            done.textContent = Number(done.textContent) + 1;
        } catch (err) {
            feedback.textContent = "Couldn't save that one — please try again.";
        } finally {
            delete el.dataset.busy;
        }
    });
});
