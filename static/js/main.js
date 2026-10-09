/* =====================================================================
   AmropaliNet - client logic
   Language + theme, camera/upload, analysis, garden spread, encyclopedia
   ===================================================================== */
(() => {
    "use strict";

    const I18N = window.MANGO_I18N;
    const DISEASES = window.MANGO_DISEASES;
    const BY_KEY = Object.fromEntries(DISEASES.map((d) => [d.key, d]));
    const root = document.documentElement;
    const $ = (s, el = document) => el.querySelector(s);
    const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
    const show = (el) => el.classList.remove("hidden");
    const hide = (el) => el.classList.add("hidden");
    const store = {
        get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
        set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
    };
    const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const photoOf = (key) => "/static/img/diseases/" + key.toLowerCase().replace(/\s+/g, "-") + ".jpg";
    const imgSrc = (b64, url) => (b64 ? "data:image/jpeg;base64," + b64 : url || null);
    const DEMO = new URLSearchParams(location.search).has("demo");

    /* ---------------- Language ---------------- */
    let lang = root.getAttribute("lang") === "bn" ? "bn" : "en";
    const t = (key) => (I18N[lang] && I18N[lang][key]) || I18N.en[key] || key;
    const L = (obj) => (obj && (obj[lang] || obj.en)) || "";
    const BN_DIGITS = "০১২৩৪৫৬৭৮৯";
    const num = (s) => (lang === "bn" ? String(s).replace(/\d/g, (d) => BN_DIGITS[d]) : String(s));
    const pct = (x, dp = 1) => num((x * 100).toFixed(dp)) + "%";

    function applyI18n() {
        root.setAttribute("lang", lang);
        document.title = t("meta.title");
        $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
        $$("[data-i18n-attr]").forEach((el) => {
            el.dataset.i18nAttr.split(";").forEach((pair) => {
                const [attr, key] = pair.split(":");
                if (attr && key) el.setAttribute(attr.trim(), t(key.trim()));
            });
        });
        $$("[data-num]").forEach((el) => { el.textContent = num(el.dataset.num); });
        $$("[data-lang]").forEach((b) => {
            const on = b.dataset.lang === lang;
            b.classList.toggle("is-on", on);
            b.setAttribute("aria-pressed", String(on));
        });
        // Dynamic parts re-render in the new language
        renderCards();
        renderGardenTabs();
        renderGardenInfo();
        if (lastResult) renderResult(lastResult, false);
        if (lastNoMango) renderNotMango(lastNoMango.conf, false);
        if (statusState) setStatus(statusState.kind, statusState.titleKey, statusState.detail, statusState.detailKey);
        if (sheet.open && sheetKey) fillSheet(sheetKey);
    }

    function setLang(next) {
        if (next === lang) return;
        lang = next;
        store.set("mangoai-lang", lang);
        applyI18n();
    }
    $$("[data-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));

    /* ---------------- Theme ---------------- */
    function setTheme(theme, save = true) {
        root.setAttribute("data-theme", theme);
        $$("[data-theme-set]").forEach((b) => {
            const on = b.dataset.themeSet === theme;
            b.classList.toggle("is-on", on);
            b.setAttribute("aria-pressed", String(on));
        });
        const meta = $('meta[name="theme-color"]');
        if (meta) meta.setAttribute("content", theme === "dark" ? "#0F1D13" : "#2E7D32");
        if (save) store.set("mangoai-theme", theme);
    }
    $$("[data-theme-set]").forEach((b) => b.addEventListener("click", () => setTheme(b.dataset.themeSet)));
    setTheme(root.getAttribute("data-theme") === "dark" ? "dark" : "light", false);

    /* ---------------- Header, menu, active link ---------------- */
    const header = $("#header");
    const nav = $("#nav");
    const menuBtn = $("#menu-btn");
    const fab = $(".fab");

    function closeMenu() {
        nav.classList.remove("is-open");
        menuBtn.setAttribute("aria-expanded", "false");
    }
    menuBtn.addEventListener("click", () => {
        const open = !nav.classList.contains("is-open");
        nav.classList.toggle("is-open", open);
        menuBtn.setAttribute("aria-expanded", String(open));
    });
    $$(".nav__link").forEach((a) => a.addEventListener("click", closeMenu));
    document.addEventListener("click", (e) => {
        if (nav.classList.contains("is-open") && !nav.contains(e.target) && !menuBtn.contains(e.target)) closeMenu();
    });

    let ticking = false;
    window.addEventListener("scroll", () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
            header.classList.toggle("is-scrolled", window.scrollY > 8);
            ticking = false;
        });
    }, { passive: true });

    const navLinks = $$(".nav__link");
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const id = entry.target.id;
            navLinks.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === "#" + id));
            fab.classList.toggle("is-hidden", id === "detect" || id === "home");
        });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main > section[id]").forEach((s) => sectionObserver.observe(s));

    /* ---------------- Reveal on scroll ---------------- */
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-in");
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });
    $$(".reveal").forEach((el) => revealObserver.observe(el));

    /* ---------------- Toast ---------------- */
    const toast = $("#toast");
    const toastMsg = $("#toast-msg");
    const toastDetail = $("#toast-detail");
    let toastTimer = null;
    // detail: optional technical reason from the server (shown small, untranslated)
    function showError(key, detail) {
        toastMsg.textContent = t(key);
        toastDetail.textContent = detail || "";
        show(toast);
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => hide(toast), detail ? 15000 : 7000);
    }
    $("#toast-close").addEventListener("click", () => hide(toast));

    /* ---------------- Upload / camera ---------------- */
    const scanner = $("#scanner");
    const drop = $("#drop");
    const preview = $("#preview");
    const previewImg = $("#preview-img");
    const inputCamera = $("#input-camera");
    const inputGallery = $("#input-gallery");
    const btnCheck = $("#btn-check");
    const loading = $("#loading");
    const results = $("#results");
    const nomango = $("#nomango");

    const MAX_SIZE = 10 * 1024 * 1024;
    const SERVER_TYPES = ["image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"];
    const MAX_SIDE = 1600;

    let currentFile = null;
    let previewUrl = null;
    let lastResult = null;
    let lastNoMango = null;

    function openPicker(kind) {
        const input = kind === "camera" ? inputCamera : inputGallery;
        input.value = "";
        input.click();
    }
    $$("[data-action]").forEach((b) => b.addEventListener("click", () => {
        if (sheet.open) sheet.close();
        openPicker(b.dataset.action);
        document.getElementById("detect").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
    }));
    [inputCamera, inputGallery].forEach((inp) => inp.addEventListener("change", () => {
        if (inp.files && inp.files[0]) handleFile(inp.files[0]);
    }));

    // Drag and drop (desktop)
    ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("is-over"); }));
    ["dragleave", "dragend"].forEach((ev) => drop.addEventListener(ev, () => drop.classList.remove("is-over")));
    drop.addEventListener("drop", (e) => {
        e.preventDefault();
        drop.classList.remove("is-over");
        const f = e.dataTransfer && e.dataTransfer.files[0];
        if (f) handleFile(f);
    });

    // Resize big phone photos in the browser: faster upload, stays under 10 MB
    function loadImage(file) {
        return new Promise((resolve, reject) => {
            const url = URL.createObjectURL(file);
            const img = new Image();
            img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
            img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("decode")); };
            img.src = url;
        });
    }

    async function prepareFile(file) {
        let img;
        try {
            img = await loadImage(file);
        } catch (e) {
            // Browser cannot decode (e.g. TIFF): send as-is if the server accepts it
            if (SERVER_TYPES.includes(file.type) && file.size <= MAX_SIZE) return file;
            throw new Error(SERVER_TYPES.includes(file.type) ? "err.size" : "err.type");
        }
        const side = Math.max(img.naturalWidth, img.naturalHeight);
        if (side <= MAX_SIDE && file.size <= 2 * 1024 * 1024 && SERVER_TYPES.includes(file.type)) return file;

        const scale = Math.min(1, MAX_SIDE / side);
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.naturalWidth * scale);
        canvas.height = Math.round(img.naturalHeight * scale);
        canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
        const blob = await new Promise((r) => canvas.toBlob(r, "image/jpeg", 0.9));
        if (!blob) throw new Error("err.bad");
        const name = (file.name || "mango").replace(/\.[^.]+$/, "") + ".jpg";
        return new File([blob], name, { type: "image/jpeg" });
    }

    async function handleFile(file) {
        if (!file.type.startsWith("image/")) return showError("err.type");
        if (file.size > 40 * 1024 * 1024) return showError("err.size");
        hide(toast);
        try {
            currentFile = await prepareFile(file);
        } catch (e) {
            return showError(e.message.startsWith("err.") ? e.message : "err.bad");
        }
        if (currentFile.size > MAX_SIZE) { currentFile = null; return showError("err.size"); }

        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = URL.createObjectURL(currentFile);
        previewImg.src = previewUrl;
        lastResult = null;
        lastNoMango = null;
        hide(results);
        hide(nomango);
        hide(drop);
        show(preview);
        btnCheck.disabled = false;
        btnCheck.focus({ preventScroll: true });
    }

    function resetScanner() {
        currentFile = null;
        lastResult = null;
        lastNoMango = null;
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = null;
        previewImg.removeAttribute("src");
        hide(preview);
        hide(results);
        hide(nomango);
        show(drop);
    }
    $("#btn-change").addEventListener("click", () => { resetScanner(); openPicker("gallery"); });
    $("#btn-nomango-again").addEventListener("click", () => {
        resetScanner();
        openPicker("camera");
        scanner.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
    });
    $("#btn-again").addEventListener("click", () => {
        resetScanner();
        scanner.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
    });

    /* ---------------- Analyze ---------------- */
    function setBusy(busy) {
        scanner.classList.toggle("is-busy", busy);
        btnCheck.disabled = busy;
        $("#btn-change").disabled = busy;
        (busy ? show : hide)(loading);
    }

    // Real MAF-Net output for a dataset photo (Bacterial Canker), shown with ?demo=1
    function demoResult() {
        const order = ["Bacterial Canker", "Scab", "Anthracnose", "Stem End Rot", "Healthy", "Sooty Mould", "Powdery Mildew"];
        const scores = [0.9209, 0.0167, 0.0148, 0.0125, 0.0121, 0.0117, 0.0113];
        return {
            demo: true,
            predicted_class: order[0],
            confidence: scores[0],
            all_scores: order.map((c, i) => ({ class: c, score: scores[i] })),
            original_url: "/static/img/demo/photo.jpg",
            gradcam_url: "/static/img/demo/heat.jpg",
            marked_url: "/static/img/demo/marked.jpg",
            affected_percent: 11.2
        };
    }

    btnCheck.addEventListener("click", async () => {
        if (!currentFile) return;
        setBusy(true);
        hide(toast);
        try {
            let data;
            if (DEMO) {
                await new Promise((r) => setTimeout(r, 1600));
                data = demoResult();
            } else {
                const form = new FormData();
                form.append("image", currentFile);
                const res = await fetch("/api/analyze", { method: "POST", body: form });
                if (!res.ok) {
                    setBusy(false);
                    return handleApiError(await readError(res), false);
                }
                data = await res.json();
                if (!data.is_mango) { setBusy(false); return renderNotMango(data.mango_confidence); }
            }
            setBusy(false);
            lastResult = data;
            renderResult(data, true);
        } catch (e) {
            setBusy(false);
            showError(navigator.onLine === false ? "err.network" : (e instanceof TypeError ? "err.network" : "err.server"));
        }
    });

    /* ---------------- API errors ---------------- */
    async function readError(res) {
        let detail = null;
        try { detail = (await res.json()).detail; } catch (e) { /* not JSON */ }
        if (detail && typeof detail === "object") return { status: res.status, ...detail };
        return { status: res.status, code: null, message: typeof detail === "string" ? detail : "" };
    }

    function handleApiError(err, fromReport) {
        switch (err.code) {
            case "not_mango":
                return fromReport ? showError("err.notmango") : renderNotMango(err.mango_confidence);
            case "model_missing":
                setStatus("error", "st.model", err.message);
                return showError("err.model", err.message);
            case "mango_check_unavailable":
                setStatus("error", "st.clip", err.message);
                return showError("err.clip", err.message);
            case "bad_type": return showError("err.type");
            case "bn_pdf_unavailable": return showError("err.bnpdf", err.message);
            case "too_large": return showError("err.size");
            default:
                if (err.status === 422) return fromReport ? showError("err.notmango") : renderNotMango(null);
                if (err.status === 400) return showError("err.bad", err.message);
                return showError("err.server", err.message);
        }
    }

    function renderNotMango(conf, animate = true) {
        lastNoMango = { conf };
        lastResult = null;
        hide(results);
        $("#nomango-img").src = previewUrl || "";
        const p = conf == null ? "-" : pct(conf, 0);
        $("#nomango-sub").textContent = t("nm.sub").replace("{pct}", p);
        show(nomango);
        if (animate) {
            nomango.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
            nomango.focus({ preventScroll: true });
        }
    }

    /* ---------------- Model status (from /api/health) ---------------- */
    const statusBar = $("#model-status");
    let statusState = null;
    function setStatus(kind, titleKey, detail, detailKey) {
        statusState = kind ? { kind, titleKey, detail, detailKey } : null;
        if (!kind) return hide(statusBar);
        statusBar.className = "status status--" + kind;
        $("#status-icon").textContent = kind === "loading" ? "⏳" : "⚠️";
        $("#status-title").textContent = t(titleKey);
        $("#status-detail").textContent = detailKey ? t(detailKey) : (detail || "");
    }
    async function checkHealth(attempt = 0) {
        if (DEMO) return;
        try {
            const h = await (await fetch("/api/health", { cache: "no-store" })).json();
            if (h.model === "error") return setStatus("error", "st.model", h.model_error);
            if (h.mango_check === "error") return setStatus("error", "st.clip", h.mango_check_error);
            if ((h.model === "loading" || h.mango_check === "loading") && attempt < 200) {
                setStatus("loading", "st.loading", null, "st.loadingd");
                return setTimeout(() => checkHealth(attempt + 1), 3000);
            }
            setStatus(null);
        } catch (e) {
            setStatus("error", "st.offline", null, "st.offlined");
        }
    }

    function renderResult(data, animate) {
        const d = BY_KEY[data.predicted_class] || BY_KEY.Healthy;
        const healthy = d.key === "Healthy";
        const conf = Number(data.confidence) || 0;

        $("#demo-note").classList.toggle("hidden", !data.demo);
        const verdict = $("#verdict");
        verdict.classList.toggle("is-sick", !healthy);

        $("#verdict-title").innerHTML = healthy
            ? esc(t("res.healthy")) + " 🌿"
            : esc(t("res.sick")) + " <em>" + esc(L(d.name)) + "</em>";
        $("#verdict-sci").textContent = d.sci;
        $("#verdict-meta").innerHTML =
            `<span class="pill pill--${d.risk}">${esc(t("res.risk"))}: ${esc(t("risk." + d.risk))}</span>` +
            d.parts.map((p) => `<span class="pill">${esc(t("part." + p))}</span>`).join("");
        $("#verdict-warn").classList.toggle("hidden", conf >= 0.7);
        $("#ring-pct").textContent = pct(conf, 0);

        const ring = $("#ring-fill");
        const C = 2 * Math.PI * 50;
        ring.style.strokeDasharray = C;
        if (animate) {
            ring.style.strokeDashoffset = C;
            requestAnimationFrame(() => requestAnimationFrame(() => { ring.style.strokeDashoffset = C * (1 - conf); }));
        } else {
            ring.style.strokeDashoffset = C * (1 - conf);
        }

        $("#todo-list").innerHTML = L(d.remedies).map((r) => `<li>${esc(num(r))}</li>`).join("");
        $("#signs-list").innerHTML = L(d.symptoms).map((s) => `<li>${esc(s)}</li>`).join("");

        const scores = $("#scores");
        scores.innerHTML = (data.all_scores || []).map((s, i) => {
            const dd = BY_KEY[s.class];
            return `<div class="score${i === 0 ? " is-top" : ""}">
                <span>${esc(dd ? L(dd.name) : s.class)}</span><span>${pct(s.score, 1)}</span>
                <div class="score__bar"><i data-w="${(s.score * 100).toFixed(2)}"></i></div>
            </div>`;
        }).join("");
        requestAnimationFrame(() => requestAnimationFrame(() => {
            $$(".score__bar i", scores).forEach((b) => { b.style.width = b.dataset.w + "%"; });
        }));

        const heat = $("#heat");
        const orig = imgSrc(data.original_base64, data.original_url) || previewUrl;
        const cam = imgSrc(data.gradcam_base64, data.gradcam_url);
        const marked = healthy ? null : imgSrc(data.marked_base64, data.marked_url);
        $("#img-original").src = orig || "";
        if (cam) $("#img-heat").src = cam;
        if (marked) $("#img-marked").src = marked;
        $("#img-heat").closest("figure").classList.toggle("hidden", !cam);
        $("#fig-marked").classList.toggle("hidden", !marked);
        heat.classList.toggle("heat--three", !!(cam && marked));
        $(".heat__note", $("#heat-card")).classList.toggle("hidden", !cam);
        $("#heat-legend").classList.toggle("hidden", !cam);
        heat.classList.toggle("hidden", !orig && !cam);
        const aff = $("#heat-affected");
        if (healthy) aff.textContent = t("res.noaffected");
        else if (data.affected_percent != null) aff.textContent = t("res.affected").replace("{pct}", num(Math.round(data.affected_percent)) + "%");
        else aff.textContent = "";
        aff.classList.toggle("is-healthy", healthy);
        $("#img-original").alt = t("res.photo");
        $("#img-heat").alt = t("res.heat");
        $("#img-marked").alt = t("res.marked");

        $("#btn-to-garden").onclick = () => selectGarden(d.key, true);

        hide(nomango);
        show(results);
        if (animate) {
            results.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
            results.focus({ preventScroll: true });
        }
    }

    /* ---------------- Report ---------------- */
    const reportForm = $("#report-form");
    const reportName = $("#report-name");
    const reportErr = $("#report-err");
    const reportBusy = $("#report-busy");
    const pdfButtons = $$("[data-pdf-lang]");

    $("#btn-to-report").addEventListener("click", (e) => {
        e.preventDefault();
        $("#report").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
        setTimeout(() => reportName.focus({ preventScroll: true }), reducedMotion ? 0 : 450);
    });

    reportName.addEventListener("input", () => {
        if (reportName.value.trim()) { reportForm.classList.remove("has-error"); hide(reportErr); }
    });

    reportForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        // Which button was pressed: Bangla or English PDF (Enter key -> current page language)
        const pdfLang = (e.submitter && e.submitter.dataset.pdfLang) || lang;
        const name = reportName.value.trim();
        if (!name) {
            reportForm.classList.add("has-error");
            show(reportErr);
            reportName.focus();
            return;
        }
        if (!currentFile) return;
        if (lastResult && lastResult.demo) return showError("rep.demo");

        show(reportBusy);
        pdfButtons.forEach((b) => { b.disabled = true; });
        try {
            const form = new FormData();
            form.append("image", currentFile);
            form.append("user_name", name);
            form.append("lang", pdfLang);
            const res = await fetch("/api/report", { method: "POST", body: form });
            if (!res.ok) {
                handleApiError(await readError(res), true);
            } else {
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                // ASCII file name: some browsers refuse non-Latin download names
                const safeName = name.replace(/[^A-Za-z0-9_-]+/g, "_").replace(/^_+|_+$/g, "") || "report";
                a.download = "AmropaliNet_Report_" + safeName + (pdfLang === "bn" ? "_BN" : "_EN") + ".pdf";
                document.body.appendChild(a);
                a.click();
                a.remove();
                setTimeout(() => URL.revokeObjectURL(url), 2000);
            }
        } catch (err) {
            showError("err.network");
        } finally {
            hide(reportBusy);
            pdfButtons.forEach((b) => { b.disabled = false; });
        }
    });

    /* ---------------- Garden impact ---------------- */
    const orchard = $("#orchard");
    const treesG = $("#orchard-trees");
    const particlesG = $("#orchard-particles");
    const stages = $("#stages");
    const TREE_X = [60, 180, 300, 420, 540];
    let gardenKey = "Anthracnose";
    let gardenTimers = [];
    let gardenPlayed = false;

    const SVGNS = "http://www.w3.org/2000/svg";
    treesG.innerHTML = TREE_X.map((x) => `
        <g class="g-tree">
            <rect x="${x - 6}" y="150" width="12" height="46" rx="4" fill="#7B5237"/>
            <circle class="halo" cx="${x}" cy="118" r="46"/>
            <circle class="crown" cx="${x}" cy="120" r="40"/>
            <circle class="crown crown--b" cx="${x - 16}" cy="104" r="22"/>
            <circle class="crown crown--b" cx="${x + 18}" cy="108" r="20"/>
            <circle cx="${x}" cy="114" r="44" fill="url(#g-shade)" pointer-events="none"/>
            <ellipse cx="${x - 14}" cy="138" rx="6" ry="8" fill="#FFB300"/>
            <ellipse cx="${x + 16}" cy="132" rx="6" ry="8" fill="#FFB300"/>
            <g class="spots">
                <circle cx="${x - 8}" cy="112" r="6"/><circle cx="${x + 14}" cy="122" r="5"/><circle cx="${x - 20}" cy="126" r="4.5"/>
            </g>
            <path class="shine" d="M${x + 30} 82 l3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3z" fill="#FFD54F"/>
        </g>`).join("");
    const treeEls = $$(".g-tree", treesG);
    orchard.insertAdjacentHTML("afterbegin", `<defs><radialGradient id="g-shade" cx="35%" cy="30%" r="75%">
        <stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>
        <stop offset="1" stop-color="#000" stop-opacity=".28"/></radialGradient></defs>`);

    function clearGarden() {
        gardenTimers.forEach(clearTimeout);
        gardenTimers = [];
        particlesG.innerHTML = "";
        treeEls.forEach((el) => el.classList.remove("is-sick", "is-safe"));
        $$("li", stages).forEach((li) => li.classList.remove("is-on"));
    }

    function hop(from, to, delay) {
        for (let k = 0; k < 3; k++) {
            gardenTimers.push(setTimeout(() => {
                const c = document.createElementNS(SVGNS, "circle");
                c.setAttribute("class", "particle");
                c.setAttribute("cx", TREE_X[from]);
                c.setAttribute("cy", 110 + k * 8);
                c.setAttribute("r", 3.2);
                c.style.setProperty("--dx", (TREE_X[to] - TREE_X[from]) + "px");
                particlesG.appendChild(c);
                c.addEventListener("animationend", () => c.remove());
            }, delay + k * 220));
        }
    }

    function at(ms, fn) { gardenTimers.push(setTimeout(fn, reducedMotion ? 0 : ms)); }

    function playGarden() {
        clearGarden();
        const d = BY_KEY[gardenKey];
        orchard.style.setProperty("--tone", d.tone);
        orchard.setAttribute("aria-label", L(d.name) + " - " + L(d.spread));
        const healthy = d.key === "Healthy";
        stages.classList.toggle("is-healthy", healthy);
        if (healthy) {
            treeEls.forEach((el, i) => at(200 + i * 180, () => el.classList.add("is-safe")));
            return;
        }
        const stageLi = $$("li", stages);
        at(250, () => { treeEls[2].classList.add("is-sick"); stageLi[0].classList.add("is-on"); });
        if (!reducedMotion) { hop(2, 1, 1000); hop(2, 3, 1000); }
        at(2300, () => { treeEls[1].classList.add("is-sick"); treeEls[3].classList.add("is-sick"); stageLi[1].classList.add("is-on"); });
        if (!reducedMotion) { hop(1, 0, 3000); hop(3, 4, 3000); }
        at(4300, () => { treeEls[0].classList.add("is-sick"); treeEls[4].classList.add("is-sick"); stageLi[2].classList.add("is-on"); });
    }

    function renderGardenTabs() {
        const tabs = $("#garden-tabs");
        tabs.innerHTML = DISEASES.map((d) => `
            <button class="tab" type="button" role="tab" data-key="${esc(d.key)}" aria-selected="${d.key === gardenKey}">
                ${d.emoji} ${esc(L(d.name))}
            </button>`).join("");
        $$(".tab", tabs).forEach((b) => b.addEventListener("click", () => selectGarden(b.dataset.key, false)));
    }

    function renderGardenInfo() {
        const d = BY_KEY[gardenKey];
        const parts = d.parts.length
            ? d.parts.map((p) => `<span class="pill">${esc(t("part." + p))}</span>`).join("")
            : `<span class="pill pill--none">${esc(t("risk.none"))}</span>`;
        $("#garden-info").innerHTML = `
            <h3><span class="emoji" aria-hidden="true">${d.emoji}</span>${esc(L(d.name))}</h3>
            <span class="pill pill--${d.risk}">${esc(t("res.risk"))}: ${esc(t("risk." + d.risk))}</span>
            <div class="info-row"><h4>${esc(t("garden.parts"))}</h4><div class="parts">${parts}</div></div>
            <div class="info-row"><h4>${esc(t("garden.spread"))}</h4><p>${esc(L(d.spread))}</p></div>
            <div class="info-row"><h4>${esc(t("garden.season"))}</h4><p>${esc(num(L(d.season)))}</p></div>
            <div class="info-row"><h4>${esc(t("garden.look"))}</h4><ul>${L(d.symptoms).slice(0, 3).map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>`;
        const info = $("#garden-info");
        info.style.animation = "none";
        void info.offsetWidth;
        info.style.animation = "";
    }

    function selectGarden(key, scroll) {
        gardenKey = key;
        $$("#garden-tabs .tab").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.key === key)));
        renderGardenInfo();
        playGarden();
        gardenPlayed = true;
        if (scroll) document.getElementById("garden").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
    }
    $("#btn-replay").addEventListener("click", playGarden);

    new IntersectionObserver((entries, obs) => {
        if (entries[0].isIntersecting) {
            if (!gardenPlayed) { playGarden(); gardenPlayed = true; }
            obs.disconnect();
        }
    }, { threshold: 0.35 }).observe(orchard);

    /* ---------------- Encyclopedia ---------------- */
    const cards = $("#cards");
    let filter = "all";

    function renderCards() {
        cards.innerHTML = DISEASES.map((d) => `
            <button class="card" type="button" data-key="${esc(d.key)}" style="--tone:${d.tone}">
                <span class="card__emoji card__emoji--photo" aria-hidden="true"><img src="${photoOf(d.key)}" alt="" loading="lazy" width="56" height="56" /></span>
                <span class="card__name">${esc(L(d.name))}</span>
                <span class="card__sci">${esc(d.sci)}</span>
                <span class="card__short">${esc(L(d.short))}</span>
                <span class="card__foot">
                    <span class="pill pill--${d.risk}">${esc(t("risk." + d.risk))}</span>
                    <span class="card__more">${esc(t("dis.open"))} <i aria-hidden="true">→</i></span>
                </span>
            </button>`).join("");
        $$(".card", cards).forEach((c) => c.addEventListener("click", () => openSheet(c.dataset.key)));
        applyFilter(false);
    }

    function applyFilter(animate) {
        let i = 0;
        $$(".card", cards).forEach((c) => {
            const d = BY_KEY[c.dataset.key];
            const match = filter === "all" || d.parts.includes(filter);
            c.classList.toggle("is-dim", !match);
            c.classList.remove("pop");
            if (match && animate) {
                c.style.animationDelay = (i++ * 50) + "ms";
                void c.offsetWidth;
                c.classList.add("pop");
            }
        });
    }
    $$(".filter").forEach((f) => f.addEventListener("click", () => {
        filter = f.dataset.filter;
        $$(".filter").forEach((x) => {
            x.classList.toggle("is-active", x === f);
            x.setAttribute("aria-pressed", String(x === f));
        });
        applyFilter(true);
    }));

    /* ---------------- Disease detail sheet ---------------- */
    const sheet = $("#sheet");
    const sheetBody = $("#sheet-body");
    let sheetKey = null;
    let sheetOpener = null;

    function fillSheet(key) {
        const d = BY_KEY[key];
        const list = (arr, tag = "ul") => `<${tag}>${arr.map((x) => `<li>${esc(num(x))}</li>`).join("")}</${tag}>`;
        sheetBody.innerHTML = `
            <div class="sheet__hero" style="--tone:${d.tone}">
                <button class="sheet__close" type="button" aria-label="${esc(t("dis.close"))}">✕</button>
                <div class="card__emoji card__emoji--photo" style="--tone:${d.tone}" aria-hidden="true"><img src="${photoOf(d.key)}" alt="" width="64" height="64" /></div>
                <h3 id="sheet-title">${esc(L(d.name))}</h3>
                <p class="card__sci">${esc(d.sci)}</p>
                <div class="verdict__meta" style="margin-top:10px">
                    <span class="pill pill--${d.risk}">${esc(t("res.risk"))}: ${esc(t("risk." + d.risk))}</span>
                    ${d.parts.map((p) => `<span class="pill">${esc(t("part." + p))}</span>`).join("")}
                </div>
            </div>
            <div class="sheet__body">
                <p class="sheet__desc">${esc(L(d.desc))}</p>
                <div class="sheet__grid">
                    <div class="sheet__block"><h4>👀 ${esc(t("dis.symptoms"))}</h4>${list(L(d.symptoms))}</div>
                    <div class="sheet__block"><h4>🌬️ ${esc(t("dis.spread"))}</h4><p>${esc(L(d.spread))}</p></div>
                </div>
                <div class="sheet__block"><h4>✅ ${esc(t("dis.treatment"))}</h4>${list(L(d.remedies), "ol")}</div>
                <div class="sheet__block"><h4>🛡️ ${esc(t("dis.prevent"))}</h4>${list(L(d.prevent))}</div>
            </div>
            <div class="sheet__cta">
                <button class="btn btn--mango" type="button" data-sheet-scan><span aria-hidden="true">📷</span><span>${esc(t("dis.scan"))}</span></button>
            </div>`;
        $(".sheet__close", sheetBody).addEventListener("click", () => sheet.close());
        $("[data-sheet-scan]", sheetBody).addEventListener("click", () => {
            sheet.close();
            openPicker("camera");
            document.getElementById("detect").scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" });
        });
    }

    function openSheet(key) {
        sheetKey = key;
        sheetOpener = document.activeElement;
        fillSheet(key);
        if (typeof sheet.showModal === "function") sheet.showModal();
        else sheet.setAttribute("open", "");
        sheetBody.scrollTop = 0;
        document.body.style.overflow = "hidden";
    }
    sheet.addEventListener("close", () => {
        document.body.style.overflow = "";
        sheetKey = null;
        if (sheetOpener && sheetOpener.focus) sheetOpener.focus({ preventScroll: true });
    });
    sheet.addEventListener("click", (e) => { if (e.target === sheet) sheet.close(); });

    /* ---------------- How it works: steps light up in turn ---------------- */
    const flowSteps = $$("#flow .flow__step");
    let flowIdx = 0, flowTimer = null;
    function flowTick() {
        flowSteps.forEach((el, i) => { el.classList.toggle("is-on", i === flowIdx); el.classList.toggle("is-done", i < flowIdx); });
        flowIdx = (flowIdx + 1) % (flowSteps.length + 1);
        flowTimer = setTimeout(flowTick, flowIdx === 0 ? 2200 : 1300);
    }
    if (!reducedMotion) {
        new IntersectionObserver((entries) => {
            clearTimeout(flowTimer);
            if (entries[0].isIntersecting) { flowIdx = 0; flowTick(); }
        }, { threshold: 0.4 }).observe($("#flow"));
    }

    /* ---------------- Developers: code tabs + copy ---------------- */
    const codeTabs = $$(".code__tab");
    const codePanels = $$(".code__panel");
    codeTabs.forEach((tab) => tab.addEventListener("click", () => {
        codeTabs.forEach((x) => x.setAttribute("aria-selected", String(x === tab)));
        codePanels.forEach((p) => { p.hidden = p.dataset.panel !== tab.dataset.code; });
    }));
    const copyBtn = $("#code-copy");
    copyBtn.addEventListener("click", async () => {
        const panel = codePanels.find((p) => !p.hidden);
        const text = panel ? panel.innerText : "";
        try {
            await navigator.clipboard.writeText(text);
        } catch (e) {
            // Fallback for http:// pages where the clipboard API is blocked
            const ta = document.createElement("textarea");
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            try { document.execCommand("copy"); } catch (err) { /* ignore */ }
            ta.remove();
        }
        const label = $("[data-i18n]", copyBtn);
        label.textContent = t("dev.copied");
        copyBtn.classList.add("is-done");
        setTimeout(() => { label.textContent = t("dev.copy"); copyBtn.classList.remove("is-done"); }, 1600);
    });

    /* ---------------- Init ---------------- */
    applyI18n();
    checkHealth();
})();
