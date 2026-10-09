/* =====================================================================
   AmropaliNet - Streamlit bridge (loaded only by streamlit_app.py)
   The website runs unchanged inside a Streamlit component. Its fetch("/api/...")
   calls are passed to Python through Streamlit, which answers them with the
   mango_disease_ai REST API in memory, so main.js needs no changes.
   ===================================================================== */
(() => {
    "use strict";

    const post = (type, extra) =>
        window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type }, extra), "*");

    // ?demo=1 on the Streamlit page URL (the frame is served from the same origin)
    try {
        window.MANGO_DEMO = new URLSearchParams(window.parent.location.search).has("demo");
    } catch (e) {
        window.MANGO_DEMO = false;
    }

    // Streamlit creates the component frame with scrolling="no", which blocks mouse wheel,
    // touch and keyboard scrolling of the website. Remove it (and again if it comes back).
    try {
        const frame = window.frameElement;
        if (frame) {
            const allowScroll = () => {
                if (frame.getAttribute("scrolling") === "no") frame.removeAttribute("scrolling");
            };
            allowScroll();
            new MutationObserver(allowScroll).observe(frame, { attributes: true, attributeFilter: ["scrolling"] });
        }
    } catch (e) {
        /* frame not reachable: nothing to do */
    }

    // One request at a time: Streamlit keeps only the latest component value.
    const queue = [];
    let current = null;
    let ready = false;
    let seq = 0;

    function pump() {
        if (!ready || current || !queue.length) return;
        current = queue.shift();
        current.timer = setTimeout(() => finish(null, new TypeError("Streamlit did not answer")), 300000);
        post("streamlit:setComponentValue", { value: current.req, dataType: "json" });
    }

    function finish(response, error) {
        const done = current;
        current = null;
        clearTimeout(done.timer);
        if (error) done.reject(error);
        else done.resolve(response);
        pump();
    }

    window.addEventListener("message", (event) => {
        const data = event.data;
        if (!data || data.type !== "streamlit:render") return;
        ready = true;
        const response = data.args && data.args.response;
        if (current && response && response.id === current.req.id) finish(response);
        else pump();
    });

    function call(req) {
        req.id = Date.now().toString(36) + "-" + (++seq);
        return new Promise((resolve, reject) => {
            queue.push({ req, resolve, reject });
            pump();
        });
    }

    const blobToBase64 = (blob) =>
        new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(String(reader.result).split(",", 2)[1] || "");
            reader.onerror = () => reject(reader.error);
            reader.readAsDataURL(blob);
        });

    async function encodeForm(body) {
        const fields = {};
        const files = {};
        if (body instanceof FormData) {
            for (const [key, value] of body.entries()) {
                if (value instanceof Blob) {
                    files[key] = {
                        name: value.name || "photo.jpg",
                        type: value.type || "application/octet-stream",
                        b64: await blobToBase64(value)
                    };
                } else {
                    fields[key] = String(value);
                }
            }
        }
        return { fields, files };
    }

    const realFetch = window.fetch.bind(window);
    window.fetch = async (input, init = {}) => {
        if (typeof input !== "string" || !input.startsWith("/api/")) return realFetch(input, init);
        const { fields, files } = await encodeForm(init.body);
        const r = await call({ method: (init.method || "GET").toUpperCase(), path: input, fields, files });
        const body = r.b64 != null ? Uint8Array.from(atob(r.b64), (c) => c.charCodeAt(0)) : r.text || "";
        return new Response(body, { status: r.status || 500, headers: { "Content-Type": r.content_type || "text/plain" } });
    };

    post("streamlit:componentReady", { apiVersion: 1 });
})();
