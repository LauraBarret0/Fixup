/* FIX UP – base compartilhada entre as páginas: estado, dados ilustrativos,
   ícones, abas, aviso (toast) e lógica dos formulários. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const FX = (window.FX = { $, $$ });

  /* ---------- Utilidades ---------- */
  FX.icon = (n, c = "") =>
    `<svg class="i ${c}" aria-hidden="true"><use href="#i-${n}"/></svg>`;
  FX.brl = (v) =>
    "R$ " + v.toLocaleString("pt-BR", { minimumFractionDigits: 2 });
  FX.km = (v) => v.toLocaleString("pt-BR", { minimumFractionDigits: 1 });
  FX.rate = (v) => String(v).replace(".", ",");
  const pad = (n) => String(n).padStart(2, "0");
  FX.WD = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];
  FX.MO = [
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
  ];
  FX.MONTHS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
  ];
  FX.TIMES = ["08:00", "09:00", "10:00", "14:00", "16:00", "18:00"];

  /* ---------- Dados ilustrativos ---------- */
  FX.SERVICES = [
    {
      id: "eletrica",
      label: "Elétrica",
      icon: "bolt",
      min: 190,
      role: ["Eletricista", "Eletricista"],
      port: ["Quadro de luz", "Chuveiro", "Tomadas"],
    },
    {
      id: "encanamento",
      label: "Encanamento",
      icon: "drop",
      min: 170,
      role: ["Encanadora", "Encanador"],
      port: ["Vazamento", "Torneira", "Sifão"],
    },
    {
      id: "pintura",
      label: "Pintura",
      icon: "roller",
      min: 320,
      role: ["Pintora", "Pintor"],
      port: ["Sala", "Fachada", "Textura"],
    },
    {
      id: "montagem",
      label: "Montagem",
      icon: "cube",
      min: 140,
      role: ["Montadora", "Montador"],
      port: ["Guarda-roupa", "Estante", "Cama"],
    },
  ];
  FX.PROS = [
    {
      id: "camila",
      name: "Camila Rocha",
      ini: "CR",
      rating: 4.9,
      n: 86,
      km: 1.2,
      f: true,
    },
    {
      id: "fernanda",
      name: "Fernanda Lima",
      ini: "FL",
      rating: 4.8,
      n: 54,
      km: 2.4,
      f: true,
    },
    {
      id: "juliana",
      name: "Juliana Matos",
      ini: "JM",
      rating: 4.7,
      n: 31,
      km: 3.1,
      f: true,
    },
    {
      id: "bruno",
      name: "Bruno Alves",
      ini: "BA",
      rating: 4.8,
      n: 120,
      km: 1.9,
      f: false,
    },
    {
      id: "diego",
      name: "Diego Santos",
      ini: "DS",
      rating: 4.6,
      n: 42,
      km: 2.8,
      f: false,
    },
  ];
  FX.REVIEWS = [
    {
      who: "Paula R.",
      r: "5,0",
      t: "Pontual e deixou tudo limpo.",
    },
    {
      who: "Ricardo T.",
      r: "4,5",
      t: "Acabamento caprichado. Recomendo para quem quer resolver rápido.",
    },
  ];
  FX.TOOLS = [
    {
      id: "furadeira",
      name: "Furadeira de impacto",
      cat: "Furadeiras",
      owner: "Carlos M.",
      km: 1.4,
      cond: "ótimo",
      price: 25,
      deposit: 150,
      icon: "toolbox",
      kit: "furadeira",
    },
    {
      id: "escada",
      name: "Escada de 7 degraus",
      cat: "Escadas",
      owner: "Ana P.",
      km: 2.0,
      cond: "bom",
      price: 15,
      deposit: 80,
      icon: "ladder",
      kit: "escada",
    },
    {
      id: "parafusadeira",
      name: "Parafusadeira sem fio",
      cat: "Furadeiras",
      owner: "Rafael C.",
      km: 3.2,
      cond: "ótimo",
      price: 20,
      deposit: 120,
      icon: "toolbox",
      kit: "furadeira",
    },
    {
      id: "kitpintura",
      name: "Kit de pintura (rolo e bandeja)",
      cat: "Pintura",
      owner: "Marina S.",
      km: 2.6,
      cond: "bom",
      price: 12,
      deposit: 40,
      icon: "roller",
      kit: "pintura",
    },
  ];
  FX.KITS = {
    furadeira: {
      shots: ["Frente", "Lado", "Cabo", "Brocas"],
      checks: [
        "Liga e desliga normalmente",
        "Sem rachaduras ou peças soltas",
        "Acessórios completos (brocas e maleta)",
      ],
    },
    escada: {
      shots: ["Frente", "Lado", "Degraus", "Travas"],
      checks: [
        "Degraus firmes e sem folga",
        "Travas funcionando",
        "Sem amassados ou ferrugem",
      ],
    },
    pintura: {
      shots: ["Rolo", "Cabo", "Bandeja", "Pincéis"],
      checks: [
        "Rolo sem tinta seca",
        "Bandeja sem rachaduras",
        "Acessórios completos (pincéis e fita)",
      ],
    },
  };

  /* ---------- Estado compartilhado (localStorage, com plano B em window.name) ---------- */
  const KEY = "fixup.v2";
  const d0 = new Date(),
    today0 = new Date(d0.getFullYear(), d0.getMonth(), d0.getDate());
  const tm = new Date(today0);
  tm.setDate(tm.getDate() + 1);
  const DEF = {
    service: "eletrica",
    intent: null,
    women: true,
    answers: [],
    price: 0,
    form: {},
    media: { img: 0, vid: 0 },
    desc: "",
    date: { y: tm.getFullYear(), m: tm.getMonth(), d: tm.getDate() },
    time: "10:00",
    mode: "agendado",
    pro: "camila",
    rushIdx: 0,
    tool: "furadeira",
    orders: [],
    address: "Rua das Flores, 120 · São Paulo",
    last: null,
  };
  function read() {
    let raw = null;
    try {
      raw = localStorage.getItem(KEY);
    } catch (e) {
      /* sem acesso */
    }
    if (!raw) {
      try {
        if (window.name.indexOf('{"fxs":') === 0)
          raw = JSON.stringify(JSON.parse(window.name).fxs);
      } catch (e) {
        /* ignora */
      }
    }
    try {
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }
  FX.state = Object.assign({}, DEF, read());
  if (new Date(FX.state.date.y, FX.state.date.m, FX.state.date.d) < today0)
    FX.state.date = DEF.date;
  FX.today0 = today0;
  FX.save = () => {
    const j = JSON.stringify(FX.state);
    try {
      localStorage.setItem(KEY, j);
    } catch (e) {
      /* ignora */
    }
    try {
      if (!window.name || window.name.indexOf('{"fxs":') === 0)
        window.name = JSON.stringify({ fxs: FX.state });
    } catch (e) {
      /* ignora */
    }
  };
  FX.svc = () =>
    FX.SERVICES.find((s) => s.id === FX.state.service) || FX.SERVICES[0];
  FX.pro = () => FX.PROS.find((p) => p.id === FX.state.pro) || FX.PROS[0];
  FX.tool = () => FX.TOOLS.find((t) => t.id === FX.state.tool) || FX.TOOLS[0];
  FX.proRole = (p) => FX.svc().role[p.f ? 0 : 1];
  FX.price = () => FX.state.price || FX.svc().min;
  FX.eta = (p) => {
    const t = new Date(Date.now() + (20 + p.km * 8) * 60000);
    t.setMinutes(Math.ceil(t.getMinutes() / 5) * 5, 0, 0);
    return `${pad(t.getHours())}:${pad(t.getMinutes())}`;
  };
  FX.whenText = () => {
    const s = FX.state;
    if (s.mode === "hoje") return "hoje · por volta de " + FX.eta(FX.pro());
    const dt = new Date(s.date.y, s.date.m, s.date.d);
    return `${FX.WD[dt.getDay()]}, ${s.date.d} ${FX.MO[s.date.m]} · ${s.time}`;
  };
  /* Primeira resposta do formulário + extras: vira o "título" do pedido. */
  FX.summaryLine = () => {
    const a = FX.state.answers;
    if (!a.length) return FX.svc().label;
    const qty = a.find((x) => x.qty);
    return `${FX.svc().label} · ${a[0].a}` + (qty ? ` · ${qty.a}` : "");
  };
  FX.back = (url) => {
    const b = $("#back");
    if (b) b.setAttribute("href", url);
  };

  /* ---------- Fotos reais (pasta image/) ---------- */
  FX.IMG = "../image/"; // pasta das imagens, relativa às páginas .html
  FX.PORTFOLIO_COUNT = 2; // quantas fotos de portfólio por profissional (camila1.jpg, camila2.jpg...)
  FX.photos = (p) =>
    Array.from(
      { length: FX.PORTFOLIO_COUNT },
      (_, i) => `${FX.IMG}portfolio/${p.id}${i + 1}.jpg`,
    );
  FX.lightbox = (src, alt) => {
    const el = document.createElement("div");
    el.className = "sheet";
    el.style.alignItems = "center";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-label", alt || "Foto");
    el.innerHTML =
      '<img alt="" style="width:100%;max-height:100%;object-fit:contain"><button class="x" aria-label="Fechar" style="position:absolute;top:16px;right:16px;width:44px;height:44px;border-radius:50%;background:#fff;display:grid;place-items:center">' +
      FX.icon("close") +
      "</button>";
    el.querySelector("img").src = src;
    el.querySelector("img").alt = alt || "";
    el.onclick = () => el.remove();
    document.querySelector(".app").append(el);
  };

  /* ---------- Ícones (sprite) ---------- */
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/></symbol>
<symbol id="i-drop" viewBox="0 0 24 24"><path d="M12 3s6 6.5 6 11a6 6 0 01-12 0c0-4.5 6-11 6-11z"/></symbol>
<symbol id="i-roller" viewBox="0 0 24 24"><rect x="4" y="4" width="14" height="5" rx="1"/><path d="M18 6.5h2v5h-9v3"/><rect x="9.5" y="14.5" width="3" height="6" rx="1"/></symbol>
<symbol id="i-cube" viewBox="0 0 24 24"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/></symbol>
<symbol id="i-pin" viewBox="0 0 24 24"><path d="M12 21s-7-6.2-7-11a7 7 0 0114 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></symbol>
<symbol id="i-back" viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></symbol>
<symbol id="i-next" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></symbol>
<symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></symbol>
<symbol id="i-star" viewBox="0 0 24 24"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9L12 3z"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24"><path d="M5 12l4.5 4.5L19 7"/></symbol>
<symbol id="i-camera" viewBox="0 0 24 24"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13.5" r="3.5"/></symbol>
<symbol id="i-video" viewBox="0 0 24 24"><rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3"/></symbol>
<symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></symbol>
<symbol id="i-calendar" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></symbol>
<symbol id="i-toolbox" viewBox="0 0 24 24"><rect x="3" y="8" width="18" height="12" rx="2"/><path d="M9 8V6a1 1 0 011-1h4a1 1 0 011 1v2M3 13h18"/></symbol>
<symbol id="i-ladder" viewBox="0 0 24 24"><path d="M8 3v18M16 3v18M8 7h8M8 12h8M8 17h8"/></symbol>
<symbol id="i-home" viewBox="0 0 24 24"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/></symbol>
<symbol id="i-list" viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/></symbol>
<symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></symbol>
<symbol id="i-lock" viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></symbol>
<symbol id="i-msg" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/></symbol>
<symbol id="i-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></symbol>
<symbol id="i-tag" viewBox="0 0 24 24"><path d="M3 12V4h8l9 9-8 8-9-9z"/><circle cx="7.5" cy="8.5" r="1"/></symbol>
<symbol id="i-card" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18"/></symbol>
<symbol id="i-help" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 114 2c-.9.6-1.5 1-1.5 2M12 17h.01"/></symbol>
<symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
<symbol id="i-minus" viewBox="0 0 24 24"><path d="M5 12h14"/></symbol>
<symbol id="i-warn" viewBox="0 0 24 24"><path d="M12 3l10 18H2L12 3z"/><path d="M12 10v5M12 18h.01"/></symbol>
</svg>`,
  );

  /* ---------- Abas e aviso ---------- */

  FX.tabbar = (active) => {
    const nav = $(".tabbar");
    if (!nav) return;

    nav.setAttribute("aria-label", "Navegação principal");

    const inPages = location.pathname.includes("/pages/");

    const links = inPages
      ? {
          inicio: "../index.html",
          pedidos: "pedidos.html",
          ferramentas: "ferramentas.html",
          conta: "conta.html",
        }
      : {
          inicio: "index.html",
          pedidos: "pages/pedidos.html",
          ferramentas: "pages/ferramentas.html",
          conta: "pages/conta.html",
        };

    nav.innerHTML = [
      ["inicio", "home", "Início"],
      ["pedidos", "list", "Pedidos"],
      ["ferramentas", "toolbox", "Ferramentas"],
      ["conta", "user", "Perfil"],
    ]
      .map(
        ([id, ic, label]) =>
          `<a class="tab" href="${links[id]}" ${
            id === active ? 'aria-current="page"' : ""
          }>${FX.icon(ic, "s24")}${label}</a>`,
      )
      .join("");
  };

  let toastT;
  FX.toast = (msg) => {
    $(".toast")?.remove();
    const t = document.createElement("div");
    t.className = "toast";
    t.setAttribute("role", "status");
    t.textContent = msg;
    $(".app").append(t);
    clearTimeout(toastT);
    toastT = setTimeout(() => t.remove(), 2600);
  };
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-soon]"))
      FX.toast("Disponível na próxima versão.");
  });
  const h1 = $("h1");
  if (h1) {
    h1.setAttribute("tabindex", "-1");
    setTimeout(() => h1.focus({ preventScroll: true }), 300);
  }

  /* ---------- Formulário por serviço ---------- */
  FX.initForm = (form) => {
    const S = FX.state;
    const key = S.service;
    const saved = (S.form && S.form[key]) || {};

    /* restaura respostas anteriores (ao voltar da agenda, por exemplo) */
    Object.entries(saved).forEach(([name, vals]) => {
      $$(`[name="${name}"]`, form).forEach((el) => {
        if (el.type === "radio" || el.type === "checkbox")
          el.checked = vals.includes(el.value);
        else el.value = vals[0];
      });
    });
    const desc = $("#problema");
    if (desc) desc.value = S.desc || "";

    const checked = (n, v) =>
      form.querySelector(`[name="${n}"][value="${v}"]:checked`);
    const labelOf = (el) =>
      el.closest("label")?.querySelector("span")?.textContent.trim() ||
      el.value;

    function refresh() {
      $$("[data-showif]", form).forEach((el) => {
        const [n, v] = el.dataset.showif.split("=");
        const on = !!checked(n, v);
        el.hidden = !on;
        $$("input,select,textarea", el).forEach((i) => {
          i.disabled = !on;
        });
      });
      let total = 0;
      $$("input:checked,select", form).forEach((i) => {
        if (i.disabled) return;
        if (i.tagName === "SELECT")
          total += Number(i.selectedOptions[0]?.dataset.price || 0);
        else total += Number(i.dataset.price || 0);
      });
      $$("input[data-unit]", form).forEach((i) => {
        if (!i.disabled)
          total += (Number(i.value) - 1) * Number(i.dataset.unit);
      });
      const est = $("#est");
      if (est) est.textContent = total > 0 ? FX.brl(total) : "—";
      return total;
    }

    /* contadores (+ e −) */
    form.addEventListener("click", (e) => {
      const b = e.target.closest("[data-step]");
      if (!b) return;
      const i = b.parentElement.querySelector("input");
      const v = Math.min(
        Number(i.max),
        Math.max(Number(i.min), Number(i.value) + Number(b.dataset.step)),
      );
      i.value = v;
      refresh();
    });

    /* validação com mensagem em português */
    form.addEventListener(
      "invalid",
      (e) => {
        const f = e.target.closest(".q");
        if (f) {
          f.classList.add("err");
          $(".q-err", f)?.removeAttribute("hidden");
        }
      },
      true,
    );
    form.addEventListener("change", (e) => {
      const f = e.target.closest(".q");
      if (f) {
        f.classList.remove("err");
        $(".q-err", f)?.setAttribute("hidden", "");
      }
      refresh();
    });

    /* fotos e vídeos */
    const media = $("#media"),
      file = $("#file");
    const urls = [];
    function drawMedia() {
      media.innerHTML =
        `<button type="button" class="tile add" id="addMedia">${FX.icon("camera", "s22")}Adicionar</button>` +
        urls
          .map(
            (m, i) =>
              `<div class="tile">${m.type === "video" ? `<video src="${m.url}" muted playsinline></video>` : `<img src="${m.url}" alt="Foto enviada">`}<button type="button" class="x" data-rm="${i}" aria-label="Remover">${FX.icon("close")}</button></div>`,
          )
          .join("");
    }
    if (media) {
      drawMedia();
      media.addEventListener("click", (e) => {
        if (e.target.closest("#addMedia")) file.click();
        const r = e.target.closest("[data-rm]");
        if (r) {
          urls.splice(Number(r.dataset.rm), 1);
          drawMedia();
        }
      });
      file.addEventListener("change", () => {
        [...file.files].forEach((f) =>
          urls.push({
            type: f.type.startsWith("video") ? "video" : "image",
            url: URL.createObjectURL(f),
          }),
        );
        file.value = "";
        drawMedia();
      });
    }

    /* preferência por profissional mulher */
    const sw = $("#womenSwitch");
    if (sw) {
      sw.setAttribute("aria-checked", S.women);
      sw.addEventListener("click", () => {
        S.women = !S.women;
        sw.setAttribute("aria-checked", S.women);
      });
    }

    refresh();

    /* envio: guarda as respostas e vai para a próxima página */
    let submitter = null;
    form.addEventListener("click", (e) => {
      const b = e.target.closest("button[type=submit]");
      if (b) submitter = b;
    });
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const btn = e.submitter || submitter || $("button[type=submit]", form);
      const answers = [],
        raw = {};
      $$("input,select,textarea", form).forEach((el) => {
        if (!el.name || el.disabled) return;
        if (el.type === "radio" || el.type === "checkbox") {
          if (el.checked) (raw[el.name] ||= []).push(el.value);
        } else (raw[el.name] ||= []).push(el.value);
      });
      $$(".q[data-q]", form).forEach((q) => {
        if (q.hidden) return;
        const picked = $$("input:checked", q).map(labelOf);
        let a = picked.join(", ");
        let qty = false;
        const sel = $("select", q);
        if (sel && sel.value) a = sel.selectedOptions[0].textContent.trim();
        const num = $("input[type=number]", q);
        if (num) {
          a = `${num.value} ${num.dataset.suffix || ""}`.trim();
          qty = true;
        }
        if (a) answers.push({ q: q.dataset.q, a, qty });
      });
      S.answers = answers;
      S.form[key] = raw;
      S.price = refresh();
      S.desc = ($("#problema")?.value || "").trim();
      S.media = {
        img: urls.filter((m) => m.type === "image").length,
        vid: urls.filter((m) => m.type === "video").length,
      };
      S.mode = btn?.dataset.mode || "agendado";
      FX.save();
      location.href = btn?.dataset.next || "agendar.html";
    });
  };
})();
