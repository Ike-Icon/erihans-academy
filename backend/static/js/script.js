// Empty string = same-origin requests. This works when FastAPI serves this
// frontend itself (the recommended deploy — see README). If you instead host
// the frontend separately from the backend (Netlify + Render, for example),
// set this to your backend's full URL, e.g. "https://erihans-api.onrender.com".
const API_BASE = "";

document.getElementById("year").textContent = new Date().getFullYear();

// Count up the hero stat numbers (1,200+, 5, 92%) from 0 as the page loads.
function animateCount(el, duration = 1400) {
  const target = Number(el.dataset.countTo);
  const suffix = el.dataset.suffix || "";
  const start = performance.now();

  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    // Ease-out so it starts fast and settles gently on the final number.
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(target * eased);
    el.textContent = current.toLocaleString("en-US") + suffix;

    if (progress < 1) {
      requestAnimationFrame(tick);
    }
  }
  requestAnimationFrame(tick);
}

document.querySelectorAll("[data-count-to]").forEach((el) => animateCount(el));

// Mobile nav toggle
const navToggle = document.getElementById("nav-toggle");
const mainNav = document.getElementById("main-nav");
navToggle.addEventListener("click", () => {
  const open = mainNav.classList.toggle("is-open");
  navToggle.setAttribute("aria-expanded", open ? "true" : "false");
});

// Generic helper to post JSON and report status in a target element
async function postJSON(url, payload, statusEl, successMessage) {
  statusEl.dataset.state = "";
  statusEl.textContent = "Sending…";
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed (${res.status})`);
    }
    statusEl.dataset.state = "ok";
    statusEl.textContent = successMessage;
    return true;
  } catch (err) {
    statusEl.dataset.state = "error";
    statusEl.textContent = err.message || "Something went wrong. Try again.";
    return false;
  }
}

// Enrollment / callback form (only present on the Student Registration page)
const enrollForm = document.getElementById("enroll-form");
if (enrollForm) {
  // Pre-select the program dropdown if the link included ?program=..., e.g.
  // a "Register for this program" button from a program detail page.
  const params = new URLSearchParams(window.location.search);
  const requestedProgram = params.get("program");
  const programSelect = document.getElementById("program");
  if (requestedProgram && programSelect) {
    const match = [...programSelect.options].find((o) => o.value === requestedProgram);
    if (match) programSelect.value = requestedProgram;
  }

  const enrollStatus = document.getElementById("form-status");
  enrollForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = document.getElementById("enroll-submit");
    const data = Object.fromEntries(new FormData(enrollForm).entries());

    submitBtn.disabled = true;
    const ok = await postJSON(
      `${API_BASE}/api/enroll`,
      data,
      enrollStatus,
      "Got it. An advisor will call you within two working days."
    );
    submitBtn.disabled = false;
    if (ok) enrollForm.reset();
  });
}

// Contact form (only present on the Contact Us page)
const contactForm = document.getElementById("contact-form");
if (contactForm) {
  const contactStatus = document.getElementById("contact-status");
  contactForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = document.getElementById("contact-submit");
    const data = Object.fromEntries(new FormData(contactForm).entries());

    submitBtn.disabled = true;
    const ok = await postJSON(
      `${API_BASE}/api/contact`,
      data,
      contactStatus,
      "Message sent. We'll get back to you within two working days."
    );
    submitBtn.disabled = false;
    if (ok) contactForm.reset();
  });
}

// Newsletter form
const newsletterForm = document.getElementById("newsletter-form");
const newsletterStatus = document.getElementById("newsletter-status");
newsletterForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("newsletter-email").value;

  const ok = await postJSON(
    `${API_BASE}/api/newsletter`,
    { email },
    newsletterStatus,
    "Subscribed. Watch your inbox on Mondays."
  );
  if (ok) newsletterForm.reset();
});



