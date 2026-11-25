"""Gera as páginas do restante do fluxo (agenda, profissionais, perfil, pagamento, ferramentas...).
Rode depois de build_forms.py:  python3 build_forms.py && python3 build_pages.py"""
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    from python.build_forms import page

def head(title, sub=None, back='index.html', sub_id=None):
    s = f'<div class="sub"{f" id={chr(34)}{sub_id}{chr(34)}" if sub_id else ""}>{sub}</div>' if sub is not None else ''
    return f"""<header class="head">
  <a class="back" id="back" href="{back}" aria-label="Voltar"><svg class="i thick"><use href="#i-back"/></svg></a>
  <div class="t"><h1>{title}</h1>{s}</div>
</header>"""

def write(name, title, body, script):
    open(name + '.html', 'w').write(page(title, body, script))

# ------------------------------------------------------------------ 3 · agendar
write('agendar', 'Dia e horário', head('Dia e horário', 'Passo 2 de 3') + """
<div class="body">
  <div class="chips" id="agTags"></div>
  <div class="card cal">
    <div class="cal-h">
      <button class="cal-nav" id="calPrev" aria-label="Mês anterior"><svg class="i thick"><use href="#i-back"/></svg></button>
      <b id="calTitle"></b>
      <button class="cal-nav" id="calNext" aria-label="Próximo mês"><svg class="i thick"><use href="#i-next"/></svg></button>
    </div>
    <div class="dow" aria-hidden="true"><div>D</div><div>S</div><div>T</div><div>Q</div><div>Q</div><div>S</div><div>S</div></div>
    <div class="days" id="days"></div>
  </div>
  <div class="sec"><div class="sec-t">Horário</div><div class="slots" id="slots"></div></div>
</div>
<div class="foot">
  <div class="summary"><svg class="i s18 thick"><use href="#i-clock"/></svg><span id="agSummary"></span></div>
  <a class="btn primary" href="profissionais.html">Ver profissionais disponíveis<svg class="i s18 thick"><use href="#i-next"/></svg></a>
</div>""", """
const S = FX.state, { $, $$ } = FX;
S.mode = 'agendado';
FX.back(S.service + '.html');
let view = { y: S.date.y, m: S.date.m };
const same = (a, b) => a.y === b.y && a.m === b.m && a.d === b.d;
const t0 = { y: FX.today0.getFullYear(), m: FX.today0.getMonth(), d: FX.today0.getDate() };
function slotOk(t) {
  if (!same(S.date, t0)) return true;
  const [h, mi] = t.split(':').map(Number);
  return new Date(S.date.y, S.date.m, S.date.d, h, mi) > new Date(Date.now() + 3600000);
}
function render() {
  $('#agTags').innerHTML = `<span class="tag">${FX.svc().label}</span>` + (S.women ? '<span class="tag violet">Só profissionais mulheres</span>' : '');
  const { y, m } = view, isCur = y === t0.y && m === t0.m;
  $('#calTitle').textContent = `${FX.MONTHS[m]} ${y}`;
  $('#calPrev').disabled = isCur;
  $('#calNext').disabled = (y - t0.y) * 12 + m - t0.m >= 3;
  const first = new Date(y, m, 1).getDay(), total = new Date(y, m + 1, 0).getDate();
  let h = '<span></span>'.repeat(first);
  for (let d = 1; d <= total; d++) {
    const past = new Date(y, m, d) < FX.today0, isT = isCur && d === t0.d, sel = same(S.date, { y, m, d });
    h += `<button class="day${isT ? ' today' : ''}" data-d="${d}" ${past ? 'disabled' : ''} aria-pressed="${sel}" aria-label="${d} de ${FX.MONTHS[m]}${isT ? ', hoje' : ''}">${d}</button>`;
  }
  $('#days').innerHTML = h;
  if (!slotOk(S.time)) S.time = FX.TIMES.find(slotOk) || S.time;
  $('#slots').innerHTML = FX.TIMES.map((t) => `<button class="slot" data-t="${t}" ${slotOk(t) ? '' : 'disabled'} aria-pressed="${t === S.time}">${t}</button>`).join('');
  $('#agSummary').textContent = FX.whenText() + '. Só aparece quem está livre nesse horário.';
  FX.save();
}
$('#calPrev').onclick = () => { view.m--; if (view.m < 0) { view.m = 11; view.y--; } render(); };
$('#calNext').onclick = () => { view.m++; if (view.m > 11) { view.m = 0; view.y++; } render(); };
$('#days').onclick = (e) => { const b = e.target.closest('[data-d]'); if (b) { S.date = { y: view.y, m: view.m, d: +b.dataset.d }; render(); } };
$('#slots').onclick = (e) => { const b = e.target.closest('[data-t]'); if (b) { S.time = b.dataset.t; render(); } };
render();
""")

# ------------------------------------------------------------------ 4 · profissionais
write('profissionais', 'Profissionais disponíveis', head('Disponíveis agora', '', 'agendar.html', 'prSub') + """
<div class="body" style="gap:14px">
  <div class="req-card"><div class="ic"><svg class="i s18" id="rcIcon"><use href="#i-bolt"/></svg></div><div style="min-width:0"><b id="rcTitle"></b><span class="hint" id="rcSub"></span></div></div>
  <div class="chips">
    <button class="chip sm women" id="fWomen" aria-pressed="true"><svg class="i s16 thick"><use href="#i-check"/></svg>Só mulheres</button>
    <button class="chip sm" id="fNear" aria-pressed="true">Mais perto</button>
    <button class="chip sm" id="fRate" aria-pressed="false">Melhor nota</button>
  </div>
  <div class="sec" style="gap:12px" id="proList"></div>
</div>
<div class="foot tight">
  <a class="btn link" id="rush" href="hoje.html"><svg class="i s18 thick"><use href="#i-bolt"/></svg>Prefiro não escolher: o primeiro disponível aceita</a>
  <div class="hint center">Dados ilustrativos do protótipo</div>
</div>""", """
const S = FX.state, { $ } = FX;
S.mode = 'agendado'; let sort = 'near';
FX.back('agendar.html');
$('#prSub').textContent = `${FX.whenText()} · ${FX.svc().label}`;
$('#rcTitle').textContent = FX.summaryLine();
$('#rcSub').textContent = 'Estimativa a partir de ' + FX.brl(FX.price());
$('#rush').onclick = () => { S.mode = 'hoje'; FX.save(); };
function list() {
  return FX.PROS.filter((p) => !S.women || p.f).sort(sort === 'rate' ? (a, b) => b.rating - a.rating || a.km - b.km : (a, b) => a.km - b.km);
}
function render() {
  $('#fWomen').setAttribute('aria-pressed', S.women);
  $('#fNear').setAttribute('aria-pressed', sort === 'near');
  $('#fRate').setAttribute('aria-pressed', sort === 'rate');
  $('#proList').innerHTML = list().map((p) => `
    <article class="card pro">
      <div class="pro-top"><div class="avatar">${p.ini}</div>
        <div class="pro-id"><b>${p.name}</b><div class="ver">${FX.icon('shield', 's14 thick')}Identidade verificada</div></div>
        <div class="rate"><b>${FX.icon('star', 's16 star')}${FX.rate(p.rating)}</b><span>${p.n} avaliações</span></div></div>
      <div class="dist">${FX.icon('pin', 's16 thick')}${FX.km(p.km)} km de você</div>
      <div class="row2"><a class="btn outline sm" href="perfil.html" data-pro="${p.id}">Ver perfil</a><a class="btn primary sm" href="pagamento.html" data-pro="${p.id}">Reservar</a></div>
    </article>`).join('');
  FX.save();
}
$('#proList').addEventListener('click', (e) => { const a = e.target.closest('[data-pro]'); if (a) { S.pro = a.dataset.pro; S.mode = 'agendado'; FX.save(); } });
$('#fWomen').onclick = () => { S.women = !S.women; render(); };
$('#fNear').onclick = () => { sort = 'near'; render(); };
$('#fRate').onclick = () => { sort = 'rate'; render(); };
render();
""")

# ------------------------------------------------------------------ 5 · perfil
write('perfil', 'Perfil do profissional', head('Perfil', None, 'profissionais.html') + """
<div class="body" style="gap:16px" id="perfilBody"></div>
<div class="foot split">
  <button class="sq" id="msgBtn" aria-label="Enviar mensagem com fotos e vídeos"><svg class="i"><use href="#i-msg"/></svg></button>
  <a class="btn primary" id="reservar" href="pagamento.html" style="flex:1"></a>
</div>""", """
const S = FX.state, { $ } = FX, p = FX.pro(), s = FX.svc();
FX.back(S.mode === 'hoje' ? 'hoje.html' : 'profissionais.html');
$('#perfilBody').innerHTML = `
  <div class="ph"><div class="avatar lg">${p.ini}</div><div style="min-width:0"><h2>${p.name}</h2><div class="role">${FX.proRole(p)} · São Paulo, SP</div>
    <div class="tags"><span class="tag mint">${FX.icon('check', 's14 thick')}Identidade</span><span class="tag mint">${FX.icon('check', 's14 thick')}Cursos</span></div></div></div>
  <div class="stats"><div><b>${FX.icon('star', 's16 star')}${FX.rate(p.rating)}</b><span>Avaliação</span></div><div><b>${p.n}</b><span>Serviços</span></div><div><b>${FX.km(p.km)} km</b><span>De você</span></div></div>
  <div class="sec"><div class="sec-t">Portfólio</div><div class="port">${s.port.map((l) => `<div>${FX.icon('camera', 's22')}${l}</div>`).join('')}</div></div>
  <div class="sec"><div class="sec-t">Avaliações de clientes</div>${FX.REVIEWS.map((r) => `<div class="review"><header><span>${r.who}</span><span>${FX.icon('star', 's14 star')}${r.r}</span></header><p>${r.t}</p></div>`).join('')}
    <div class="hint center">Dados ilustrativos do protótipo</div></div>`;
$('#reservar').textContent = S.mode === 'hoje' ? 'Confirmar e pagar' : 'Reservar · ' + FX.whenText();
$('#msgBtn').onclick = () => FX.toast('Mensagem com fotos e vídeos disponível na próxima versão.');
""")

# ------------------------------------------------------------------ 6 · hoje
write('hoje', 'Mais rápido possível', head('Mais rápido possível', '', 'index.html', 'hjSub') + """
<div class="body">
  <div class="tag violet" id="hjWomen" style="align-self:flex-start"><svg class="i s16 thick"><use href="#i-user"/></svg>Preferência: profissional mulher</div>
  <div class="req-card"><div class="ic"><svg class="i s18"><use href="#i-bolt"/></svg></div><div style="min-width:0"><b id="rcTitle"></b><span class="hint">Estimativa a partir de <span id="rcPrice"></span></span></div></div>
  <div class="card steps" id="hjSteps" aria-live="polite"></div>
  <div class="match" id="hjMatch" hidden>
    <div class="top"><div class="avatar xl" id="hjAv"></div>
      <div style="flex:1;min-width:0"><b id="hjName"></b><div class="m"><svg class="i s16 star"><use href="#i-star"/></svg><span id="hjMeta"></span></div></div></div>
    <div class="eta"><svg class="i s18"><use href="#i-clock"/></svg><span id="hjEta"></span></div>
    <a class="btn" href="perfil.html">Ver perfil e portfólio<svg class="i s18 thick"><use href="#i-next"/></svg></a>
  </div>
</div>
<div class="foot tight">
  <a class="btn primary" id="hjPay" href="pagamento.html" aria-disabled="true">Confirmar e pagar</a>
  <button class="btn ghost" id="hjOther" disabled>Buscar outro profissional</button>
</div>""", """
const S = FX.state, { $ } = FX;
S.mode = 'hoje'; FX.back(S.service + '.html');
const pool = FX.PROS.filter((p) => !S.women || p.f).sort((a, b) => a.km - b.km);
$('#hjSub').textContent = `${FX.svc().label} · hoje`;
$('#hjWomen').hidden = !S.women;
$('#rcTitle').textContent = FX.summaryLine(); $('#rcPrice').textContent = FX.brl(FX.price());
let timers = [], accepted = false;
const later = (f, ms) => timers.push(setTimeout(f, ms));
function start() {
  timers.forEach(clearTimeout); timers = []; accepted = false;
  S.pro = pool[S.rushIdx % pool.length].id; FX.save();
  const p = FX.pro(), media = (S.media.img + S.media.vid) ? ' com fotos e vídeo' : '';
  $('#hjMatch').hidden = true; $('#hjPay').setAttribute('aria-disabled', 'true'); $('#hjOther').disabled = true;
  const draw = (st) => {
    $('#hjSteps').innerHTML = [
      ['done', `Pedido enviado${media}`],
      [st >= 1 ? 'done' : 'now seeking', 'Profissionais próximos avisados'],
      [st >= 2 ? 'now' : st === 1 ? 'now seeking' : 'wait', st >= 2 ? `${p.name.split(' ')[0]} aceitou o seu pedido` : 'Aguardando alguém aceitar'],
      ['wait', 'A caminho']
    ].map(([c, t]) => `<div class="step ${c}"><div class="dot">${FX.icon('check')}</div><div>${t}</div></div>`).join('');
  };
  draw(0); later(() => draw(1), 900);
  later(() => {
    draw(2); accepted = true;
    $('#hjAv').textContent = p.ini; $('#hjName').textContent = p.name;
    $('#hjMeta').textContent = `${FX.rate(p.rating)} · Identidade verificada`;
    $('#hjEta').textContent = `Chega hoje por volta de ${FX.eta(p)} · ${FX.km(p.km)} km`;
    $('#hjMatch').hidden = false; $('#hjPay').setAttribute('aria-disabled', 'false'); $('#hjOther').disabled = false;
  }, 2400);
}
$('#hjPay').addEventListener('click', (e) => { if (!accepted) e.preventDefault(); else FX.save(); });
$('#hjOther').onclick = () => { S.rushIdx++; start(); };
start();
""")

# ------------------------------------------------------------------ 7 · pagamento
write('pagamento', 'Pagamento protegido', head('Confirmar e pagar', 'Passo 3 de 3', 'profissionais.html') + """
<div class="body" style="gap:16px">
  <div class="card kv">
    <div class="r"><span>Serviço</span><span id="pgSvc"></span></div>
    <div class="r"><span>Profissional</span><span id="pgPro"></span></div>
    <div class="r"><span>Quando</span><span id="pgWhen"></span></div>
    <div class="r"><label for="addr">Endereço</label><input class="addr" id="addr" autocomplete="street-address" placeholder="Rua, número e bairro"></div>
    <details class="ans"><summary>Ver respostas do pedido</summary><dl id="pgAns"></dl></details>
    <hr>
    <div class="total"><span>Estimativa do serviço</span><b id="pgTotal"></b></div>
    <small>O valor final é confirmado pela profissional depois de ver suas fotos e vídeos. Você aprova antes de ela começar.</small>
  </div>
  <div class="note"><svg class="i s24"><use href="#i-lock"/></svg><div><b>Pagamento protegido</b>O valor fica retido e só é liberado ao profissional quando você confirma que o serviço foi concluído.</div></div>
  <fieldset class="pay">
    <legend>Como pagar</legend>
    <label class="opt"><input type="radio" name="pag" value="pix" checked><span>Pix</span><small>Aprovação na hora</small></label>
    <label class="opt"><input type="radio" name="pag" value="cartao"><span>Cartão de crédito</span></label>
  </fieldset>
</div>
<div class="foot" style="gap:8px">
  <button class="btn primary" id="payBtn"><svg class="i thick"><use href="#i-lock"/></svg><span id="payLabel"></span></button>
  <div class="hint center">Cancelamento sem custo até 2 horas antes do horário.</div>
</div>""", """
const S = FX.state, { $, $$ } = FX;
FX.back(S.mode === 'hoje' ? 'hoje.html' : 'profissionais.html');
$('#pgSvc').textContent = FX.summaryLine();
$('#pgPro').textContent = FX.pro().name;
$('#pgWhen').textContent = FX.whenText();
$('#pgTotal').textContent = FX.brl(FX.price());
$('#addr').value = S.address;
const extra = [...S.answers.slice(1).map((a) => [a.q, a.a])];
if (S.desc) extra.push(['Detalhes', S.desc]);
const nm = S.media.img + S.media.vid; if (nm) extra.push(['Fotos e vídeos', nm + ' arquivo(s) enviados']);
$('#pgAns').innerHTML = extra.length ? extra.map(([q, a]) => `<div><dt>${q}</dt><dd>${a.replace(/</g, '&lt;')}</dd></div>`).join('') : '<div><dd>Sem respostas adicionais.</dd></div>';
if (!extra.length) $('.ans').hidden = true;
function label() { const c = $('input[name=pag]:checked').value === 'cartao'; $('#payLabel').textContent = `Pagar ${FX.brl(FX.price())} ${c ? 'no cartão' : 'com segurança'}`; }
$$('input[name=pag]').forEach((r) => r.addEventListener('change', label)); label();
$('#addr').addEventListener('input', (e) => e.target.classList.remove('err'));
$('#payBtn').onclick = () => {
  const a = $('#addr');
  if (!a.value.trim()) { a.classList.add('err'); a.focus(); return FX.toast('Informe o endereço do atendimento.'); }
  S.address = a.value.trim();
  $('#payBtn').disabled = true; $('#payLabel').textContent = 'Processando…';
  setTimeout(() => {
    S.orders.unshift({ icon: FX.svc().icon, title: `${FX.svc().label} · ${FX.pro().name}`, sub: FX.whenText(), st: 'Confirmado' });
    S.last = { title: 'Pedido confirmado', text: `${FX.pro().name.split(' ')[0]} atende você ${FX.whenText()}. O pagamento fica protegido até você confirmar o serviço.` };
    FX.save(); location.href = 'confirmado.html';
  }, 900);
};
""")

# ------------------------------------------------------------------ confirmado
write('confirmado', 'Confirmado', """<div class="body" style="justify-content:center;align-items:center;text-align:center;gap:12px">
  <div class="ok" style="width:72px;height:72px;border-radius:50%;background:var(--green);color:#fff;display:grid;place-items:center"><svg class="i" style="width:36px;height:36px;stroke-width:2.4"><use href="#i-check"/></svg></div>
  <h1 class="h1" id="cfTitle"></h1>
  <p id="cfText" style="color:var(--muted);line-height:1.5;max-width:300px"></p>
</div>
<div class="foot">
  <a class="btn primary" href="pedidos.html">Ver meus pedidos</a>
  <a class="btn ghost" href="index.html">Voltar ao início</a>
</div>""", """
const L = FX.state.last || { title: 'Tudo certo', text: 'Seu pedido foi registrado.' };
FX.$('#cfTitle').textContent = L.title; FX.$('#cfText').textContent = L.text;
""")

# ------------------------------------------------------------------ 8 · ferramentas
write('ferramentas', 'Aluguel de ferramentas', """<div class="body" style="gap:14px;padding-top:20px">
  <h1 class="h1">Aluguel de ferramentas</h1>
  <label class="search"><svg class="i" style="color:var(--muted)"><use href="#i-search"/></svg><input type="search" id="toolQ" aria-label="Buscar ferramenta" placeholder="Buscar furadeira, escada..."></label>
  <div class="scrollchips" id="toolCats"></div>
  <div class="protect">
    <b><svg class="i s18"><use href="#i-shield"/></svg>Proteção FIX UP em todo aluguel</b>
    <p><svg class="i s16 thick"><use href="#i-check"/></svg>Checklist com fotos na retirada e na devolução</p>
    <p><svg class="i s16 thick"><use href="#i-check"/></svg>Caução devolvida após a conferência</p>
    <p><svg class="i s16 thick"><use href="#i-check"/></svg>Cobertura se a ferramenta falhar sem mau uso</p>
  </div>
  <div class="sec" style="gap:12px" id="toolList"></div>
  <div class="hint center">Dados e valores ilustrativos do protótipo</div>
</div>
<nav class="tabbar"></nav>""", """
FX.tabbar('ferramentas');
const S = FX.state, { $ } = FX; let cat = 'Todas', q = '';
function render() {
  $('#toolCats').innerHTML = ['Todas', 'Furadeiras', 'Escadas', 'Pintura'].map((c) => `<button class="chip" data-cat="${c}" aria-pressed="${c === cat}">${c}</button>`).join('');
  const k = q.trim().toLowerCase();
  const l = FX.TOOLS.filter((t) => (cat === 'Todas' || t.cat === cat) && (!k || (t.name + ' ' + t.cat).toLowerCase().includes(k)));
  $('#toolList').innerHTML = l.length ? l.map((t) => `
    <article class="tool"><div class="th">${FX.icon(t.icon)}</div>
      <div class="in"><b>${t.name}</b><small>${t.owner} · ${FX.km(t.km)} km · Estado: ${t.cond}</small><div class="pr">R$ ${t.price} por dia</div></div>
      <a class="btn primary" href="checklist.html" data-rent="${t.id}" aria-label="Alugar ${t.name}">Alugar</a></article>`).join('')
    : `<div class="empty">${FX.icon('search')}<b>Nada encontrado</b>Tente outro nome ou veja todas as categorias.</div>`;
}
$('#toolQ').addEventListener('input', (e) => { q = e.target.value; render(); });
document.addEventListener('click', (e) => {
  const c = e.target.closest('[data-cat]'); if (c) { cat = c.dataset.cat; render(); }
  const r = e.target.closest('[data-rent]'); if (r) { S.tool = r.dataset.rent; FX.save(); }
});
render();
""")

# ------------------------------------------------------------------ 9 · checklist
write('checklist', 'Checklist de retirada', head('Checklist de retirada', '', 'ferramentas.html', 'ckSub') + """
<div class="body" style="gap:16px">
  <div class="stepper" aria-label="Etapas do aluguel"><span class="on">Retirada</span><i></i><span>Uso</span><i></i><span>Devolução</span></div>
  <div class="sec"><div class="sec-h"><div class="sec-t">1. Fotos do estado</div><div class="hint" id="ckCount"></div></div><div class="shots" id="shots"></div></div>
  <div class="sec"><div class="sec-t">2. Confira com o dono</div><div class="sec" id="ckItems"></div></div>
  <div class="note"><svg class="i s22"><use href="#i-shield"/></svg><div>As fotos ficam salvas e são comparadas com as da devolução. Se a ferramenta falhar sem mau uso, a cobertura FIX UP entra e a caução é devolvida.</div></div>
</div>
<div class="foot" style="gap:8px">
  <button class="btn primary" id="ckConfirm">Confirmar retirada</button>
  <div class="hint center" id="ckDeposit"></div>
</div>""", """
const S = FX.state, { $ } = FX, t = FX.tool(), k = FX.KITS[t.kit];
$('#ckSub').textContent = `${t.name} · ${t.owner}`;
$('#ckDeposit').textContent = `Caução de ${FX.brl(t.deposit)} liberada após a devolução conferida.`;
const shots = k.shots.map(() => true), checks = k.checks.map(() => true);
function render() {
  $('#shots').innerHTML = k.shots.map((l, i) => `<button class="shot" data-shot="${i}" aria-pressed="${shots[i]}">${FX.icon('camera', 's22')}${l}</button>`).join('');
  $('#ckItems').innerHTML = k.checks.map((c, i) => `<label class="check"><input type="checkbox" data-chk="${i}" ${checks[i] ? 'checked' : ''}>${c}</label>`).join('');
  const n = shots.filter(Boolean).length;
  $('#ckCount').textContent = `${n} de ${k.shots.length}`;
  $('#ckConfirm').disabled = !(n === k.shots.length && checks.every(Boolean));
}
$('#shots').onclick = (e) => { const b = e.target.closest('[data-shot]'); if (b) { shots[+b.dataset.shot] = !shots[+b.dataset.shot]; render(); } };
$('#ckItems').onchange = (e) => { const c = e.target.closest('[data-chk]'); if (c) { checks[+c.dataset.chk] = c.checked; render(); } };
$('#ckConfirm').onclick = () => {
  S.orders.unshift({ icon: t.icon, title: t.name, sub: `Aluguel · ${t.owner} · R$ ${t.price} por dia`, st: 'Em uso' });
  S.last = { title: 'Retirada confirmada', text: `As fotos de ${t.name.toLowerCase()} foram salvas. Na devolução, vamos comparar com elas e liberar a caução de ${FX.brl(t.deposit)}.` };
  FX.save(); location.href = 'confirmado.html';
};
render();
""")

# ------------------------------------------------------------------ pedidos e perfil
write('pedidos', 'Pedidos', """<div class="body" style="gap:14px;padding-top:20px">
  <h1 class="h1">Meus pedidos</h1>
  <div class="sec" style="gap:12px" id="orderList"></div>
</div>
<nav class="tabbar"></nav>""", """
FX.tabbar('pedidos');
const o = FX.state.orders;
FX.$('#orderList').innerHTML = o.length ? o.map((x) => `<article class="order"><div class="ic">${FX.icon(x.icon)}</div><div class="in"><b>${x.title}</b><small>${x.sub}</small></div><span class="st">${x.st}</span></article>`).join('')
  : `<div class="empty">${FX.icon('list')}<b>Nenhum pedido ainda</b>Quando você contratar um serviço ou alugar uma ferramenta, ele aparece aqui.<a class="btn primary sm" style="padding:0 20px;margin-top:6px" href="index.html">Fazer um pedido</a></div>`;
""")

write('conta', 'Perfil', """<div class="body" style="gap:16px;padding-top:20px">
  <h1 class="h1">Perfil</h1>
  <div class="ph"><div class="avatar lg">MA</div><div><h2>Mariana</h2><div class="role">São Paulo, SP</div></div></div>
  <div class="menu">
    <button data-soon><svg class="i"><use href="#i-pin"/></svg><span>Meus endereços</span><svg class="i s18"><use href="#i-next"/></svg></button>
    <button data-soon><svg class="i"><use href="#i-card"/></svg><span>Formas de pagamento</span><svg class="i s18"><use href="#i-next"/></svg></button>
    <button data-soon><svg class="i"><use href="#i-help"/></svg><span>Ajuda</span><svg class="i s18"><use href="#i-next"/></svg></button>
  </div>
</div>
<nav class="tabbar"></nav>""", "FX.tabbar('conta');")
print('paginas ok')
