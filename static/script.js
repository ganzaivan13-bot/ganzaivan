
// Portfolio language switch: English (EN) and Kinyarwanda (RW).

const languageButtons = document.querySelectorAll(".language-btn");
const savedLanguage = localStorage.getItem("ganzaPortfolioLanguage") || "en";

function setLanguage(language) {
    const lang = language === "rw" ? "rw" : "en";

    document.documentElement.lang = lang;
    document.body.dataset.language = lang;

    // Translate ordinary text without destroying form controls.
    document.querySelectorAll("[data-en], [data-en-html]").forEach(element => {

        // Labels are handled separately so their inputs remain intact.
        if (element.hasAttribute("data-label-en")) {
            return;
        }

        if (element.hasAttribute("data-en-html")) {
            const translation =
                element.getAttribute(`data-${lang}-html`) ||
                element.getAttribute("data-en-html");

            element.innerHTML = translation;
        } else {
            const translation =
                element.getAttribute(`data-${lang}`) ||
                element.getAttribute("data-en");

            element.textContent = translation;
        }
    });

    // Translate labels while preserving their input/select/textarea elements.
    document.querySelectorAll("[data-label-en]").forEach(element => {
        const textNode = Array.from(element.childNodes).find(
            node =>
                node.nodeType === Node.TEXT_NODE &&
                node.textContent.trim()
        );

        if (textNode) {
            const translation =
                element.getAttribute(`data-label-${lang}`) ||
                element.getAttribute("data-label-en");

            // Keep the form control and replace only the label's text.
            textNode.textContent = translation + " ";
        }
    });

    // Translate placeholders.
    document.querySelectorAll("[data-placeholder-en]").forEach(element => {
        element.placeholder =
            element.getAttribute(`data-placeholder-${lang}`) ||
            element.getAttribute("data-placeholder-en");
    });

    // Translate booking confirmation and validation messages.
    const flashTranslations = {
        "Please complete all required fields.":
            "Uzuza ahantu hose hasabwa.",
        "Your booking request has been received. I'll contact you soon.":
            "Ubusabe bwawe twabwakiriye. Tuzakuvugisha vuba."
    };

    document.querySelectorAll(".flash").forEach(element => {
        if (!element.dataset.originalText) {
            element.dataset.originalText = element.textContent.trim();
        }

        const original = element.dataset.originalText;

        element.textContent =
            lang === "rw"
                ? (flashTranslations[original] || original)
                : original;
    });

    // Update active language buttons.
    languageButtons.forEach(button => {
        const active = button.dataset.lang === lang;

        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
    });

    localStorage.setItem("ganzaPortfolioLanguage", lang);
}

// Language button events.
languageButtons.forEach(button => {
    button.addEventListener("click", () => {
        setLanguage(button.dataset.lang);
    });
});

// Mobile navigation.
const toggle = document.querySelector(".menu-toggle");
const links = document.querySelector(".nav-links");

if (toggle && links) {
    toggle.addEventListener("click", () => {
        const open = links.classList.toggle("open");

        toggle.setAttribute("aria-expanded", String(open));
    });

    links.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            links.classList.remove("open");
            toggle.setAttribute("aria-expanded", "false");
        });
    });
}

// Prevent users from selecting a past preferred date.
const dateInput = document.querySelector('input[name="preferred_date"]');

if (dateInput) {
    const today = new Date();

    const localDate = new Date(
        today.getTime() - today.getTimezoneOffset() * 60000
    ).toISOString().split("T")[0];

    dateInput.min = localDate;
}

// Apply the saved language when the page loads.
setLanguage(savedLanguage);
