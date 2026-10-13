(function () {
  "use strict";
  var script = document.currentScript;
  if (!script || !script.src) { return; }
  var src = new URL(script.src);
  var widgetId = src.searchParams.get("id");
  var apiBase = src.origin;
  if (!widgetId) { console.error("[widget] missing id in script URL"); return; }

  function make(tag, props, text) {
    var node = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (k) { node.setAttribute(k, props[k]); });
    }
    if (text) { node.textContent = text; }
    return node;
  }

  function clearErrors(form) {
    form.querySelectorAll("[data-error-for]").forEach(function (e) { e.textContent = ""; });
  }

  function showErrors(form, fields) {
    Object.keys(fields).forEach(function (name) {
      var slot = form.querySelector('[data-error-for="' + name + '"]');
      if (slot) { slot.textContent = fields[name]; }
    });
  }

  function render(cfg) {
    var box = make("div", {
      "data-widget-id": cfg.id,
      style: "max-width:420px;padding:16px;border:1px solid #ccc;border-radius:8px;font-family:sans-serif"
    });
    box.appendChild(make("h3", { style: "margin:0 0 8px" }, cfg.title));
    if (cfg.description) {
      box.appendChild(make("p", { style: "margin:0 0 12px;color:#555" }, cfg.description));
    }

    var form = make("form", { novalidate: "novalidate" });
    var inputs = {};

    cfg.fields.forEach(function (f) {
      var wrap = make("div", { style: "margin-bottom:10px" });
      var labelText = f.label + (f.required ? " *" : "");
      wrap.appendChild(make("label", { style: "display:block;font-size:14px;margin-bottom:4px" }, labelText));
      var input = f.type === "textarea"
        ? make("textarea", { rows: "4" })
        : make("input", { type: f.type === "email" ? "email" : "text" });
      input.setAttribute("style", "width:100%;box-sizing:border-box;padding:6px");
      inputs[f.name] = input;
      wrap.appendChild(input);
      wrap.appendChild(make("div", { "data-error-for": f.name, style: "color:#b00020;font-size:12px" }));
      form.appendChild(wrap);
    });

    // Honeypot: hidden from humans, bots fill it in.
    var trap = make("input", {
      type: "text", name: "website", tabindex: "-1", autocomplete: "off",
      "aria-hidden": "true", style: "position:absolute;left:-9999px;opacity:0"
    });
    form.appendChild(trap);

    var button = make("button", { type: "submit", style: "padding:8px 16px;cursor:pointer" }, cfg.button_text);
    var status = make("div", { style: "margin-top:10px;font-size:14px" });
    form.appendChild(button);
    form.appendChild(status);
    box.appendChild(form);
    script.parentNode.insertBefore(box, script);

    // One key per page load: a retried click is stored only once.
    var key = "w-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var data = {};
      Object.keys(inputs).forEach(function (n) { data[n] = inputs[n].value; });
      clearErrors(form);
      status.textContent = "";
      button.disabled = true;

      fetch(apiBase + "/submissions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ widget_id: cfg.id, data: data, idempotency_key: key, website: trap.value })
      })
        .then(function (r) {
          return r.json().catch(function () { return {}; }).then(function (body) {
            return { ok: r.ok, status: r.status, body: body };
          });
        })
        .then(function (res) {
          if (res.ok) {
            form.style.display = "none";
            box.appendChild(make("p", null, "Thanks! We received your message."));
            return;
          }
          if (res.status === 400 && res.body.fields) {
            showErrors(form, res.body.fields);
            status.textContent = "Please fix the highlighted fields.";
          } else if (res.status === 429) {
            status.textContent = "Too many attempts. Please wait a moment and try again.";
          } else {
            status.textContent = res.body.error || "Something went wrong. Please try again.";
          }
          button.disabled = false;
        })
        .catch(function () {
          status.textContent = "Network error. Please try again.";
          button.disabled = false;
        });
    });
  }

  fetch(apiBase + "/widgets/" + encodeURIComponent(widgetId) + "/config")
    .then(function (r) {
      if (!r.ok) { throw new Error("config request failed: " + r.status); }
      return r.json();
    })
    .then(render)
    .catch(function (e) { console.error("[widget]", e); });
})();
