"""Gera index.html e os 4 formulários por serviço (cada um é um .html estático).
Para mudar uma pergunta, edite o dicionário do serviço abaixo e rode: python3 build_forms.py
Os demais arquivos .html já estão prontos e podem ser editados direto."""
from html import escape as e

HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F7F6F1">
<title>FIX UP – %(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="app">
<main class="screen">
%(body)s
</main>
</div>
<script src="fixup.js"></script>
<script>
%(script)s
</script>
</body>
</html>
"""

def page(title, body, script):
    return HEAD % dict(title=title, body=body, script=script.strip())

# ---------------------------------------------------------------- formulários
def opts(n, items, kind='radio', pills=False):
    out = []
    for it in items:
        v, label = it[0], it[1]
        price = it[2] if len(it) > 2 else 0
        attrs = f'type="{kind}" name="{n}" value="{v}"' + (f' data-price="{price}"' if price else '')
        if kind == 'radio':
            attrs += ' required'
        cls = 'pill' if pills else 'opt'
        out.append(f'<label class="{cls}"><input {attrs}><span>{e(label)}</span></label>')
    return '\n        '.join(out)

def question(q):
    t = q['t']
    show = f' data-showif="{q["showif"]}" hidden' if q.get('showif') else ''
    hint = f'\n      <p class="hint">{e(q["hint"])}</p>' if q.get('hint') else ''
    err = '\n      <p class="q-err" hidden>Escolha uma opção para continuar.</p>'
    if t == 'opts':
        inner = f'<div class="opts">\n        {opts(q["n"], q["opts"])}\n      </div>'
    elif t == 'pills':
        inner = f'<div class="pills">\n        {opts(q["n"], q["opts"], pills=True)}\n      </div>'
    elif t == 'check':
        inner = f'<div class="opts">\n        {opts(q["n"], q["opts"], "checkbox")}\n      </div>'
        err = ''
    elif t == 'select':
        os_ = ''.join(f'<option value="{v}"' + (f' data-price="{p}"' if p else '') + f'>{e(l)}</option>' for v, l, p in q['opts'])
        inner = f'<select class="sel" name="{q["n"]}" aria-label="{e(q["q"])}" required><option value="">Selecione</option>{os_}</select>'
    elif t == 'stepper':
        inner = (f'<div class="stp"><button type="button" data-step="-1" aria-label="Diminuir"><svg class="i"><use href="#i-minus"/></svg></button>'
                 f'<input type="number" name="{q["n"]}" value="1" min="1" max="{q.get("max", 20)}" readonly data-unit="{q.get("unit", 0)}" data-suffix="{q["suffix"]}" aria-label="{e(q["q"])}">'
                 f'<button type="button" data-step="1" aria-label="Aumentar"><svg class="i"><use href="#i-plus"/></svg></button></div>')
        err = ''
    tip = ''
    if q.get('tip'):
        tn, tv, text = q['tip']
        tip = f'\n    <div class="tip" role="note" data-showif="{tn}={tv}" hidden><svg class="i s18"><use href="#i-warn"/></svg><div>{e(text)}</div></div>'
    return (f'    <fieldset class="q" data-q="{e(q["q"])}"{show}>\n      <legend>{e(q["q"])}</legend>{hint}\n      {inner}{err}\n    </fieldset>{tip}')

SERVICES = {
 'eletrica': dict(label='Elétrica', icon='bolt', qs=[
  dict(n='tipo', t='opts', q='Qual serviço você precisa?', opts=[
    ('tomada', 'Trocar tomada ou interruptor', 120), ('chuveiro', 'Instalar ou trocar chuveiro', 160),
    ('luminaria', 'Instalar luminária, ventilador ou lustre', 150), ('disjuntor', 'Disjuntor desarmando ou falta de energia', 190),
    ('ponto', 'Criar ponto novo de tomada ou luz', 200), ('outro', 'Outro serviço elétrico', 150)]),
  dict(n='instalacao', t='opts', q='O local já possui a instalação necessária?', hint='Fiação e ponto de energia no lugar onde o serviço será feito.', opts=[
    ('sim', 'Sim, a fiação e o ponto já existem', 0), ('nao', 'Não, precisa passar fiação nova', 90), ('nsei', 'Não sei dizer', 0)]),
  dict(n='qtd', t='stepper', q='Quantos pontos serão atendidos?', suffix='ponto(s)', unit=40),
  dict(n='imovel', t='pills', q='Tipo de imóvel', opts=[('casa', 'Casa'), ('apto', 'Apartamento'), ('comercio', 'Comércio')]),
  dict(n='tensao', t='pills', q='Qual é a tensão da tomada?', opts=[('127', '127 V'), ('220', '220 V'), ('nsei', 'Não sei')]),
  dict(n='material', t='opts', q='Quem fornece o material?', opts=[
    ('eu', 'Eu já tenho o material'), ('pro', 'O profissional leva e cobra à parte'), ('nsei', 'Preciso de orientação')]),
  dict(n='risco', t='check', q='Algum alerta de segurança agora?', opts=[('sim', 'Cheiro de queimado, faísca ou fios aquecendo')],
       tip=('risco', 'sim', 'Desligue o disjuntor geral e não use o ponto até o profissional chegar. Se houver fogo ou choque, ligue 193.')),
 ]),
 'encanamento': dict(label='Encanamento', icon='drop', qs=[
  dict(n='tipo', t='opts', q='Qual é o problema?', opts=[
    ('vazamento', 'Vazamento', 150), ('entupimento', 'Entupimento (pia, ralo ou vaso)', 140),
    ('torneira', 'Trocar torneira, sifão ou chuveiro', 120), ('sanitario', 'Instalar ou trocar vaso, pia ou tanque', 200),
    ('pressao', 'Pouca pressão ou caixa d’água', 180), ('outro', 'Outro problema hidráulico', 150)]),
  dict(n='local', t='pills', q='Onde está o problema?', opts=[('cozinha', 'Cozinha'), ('banheiro', 'Banheiro'), ('lavanderia', 'Lavanderia'), ('externa', 'Área externa')]),
  dict(n='vazando', t='pills', q='Está vazando água agora?', opts=[('sim', 'Sim'), ('nao', 'Não')],
       tip=('vazando', 'sim', 'Feche o registro mais próximo ou o registro geral para evitar desperdício e dano ao piso.')),
  dict(n='registro', t='opts', q='Você consegue fechar o registro?', opts=[('sim', 'Sim, sei onde fica'), ('nao', 'Não consigo ou não sei onde fica')]),
  dict(n='tubo', t='pills', q='A tubulação é aparente ou embutida?', hint='Embutida é a que passa dentro da parede ou do piso.', opts=[
    ('aparente', 'Aparente'), ('embutida', 'Embutida', 80), ('nsei', 'Não sei')]),
  dict(n='material', t='opts', q='Quem fornece o material?', opts=[
    ('eu', 'Eu já tenho a peça ou o material'), ('pro', 'O profissional leva e cobra à parte'), ('nsei', 'Preciso de orientação')]),
 ]),
 'pintura': dict(label='Pintura', icon='roller', qs=[
  dict(n='tipo', t='opts', q='O que você quer pintar?', opts=[
    ('parede', 'Parede interna', 300), ('fachada', 'Fachada ou parede externa', 450), ('teto', 'Teto', 250),
    ('portas', 'Portas, janelas ou portão', 180), ('textura', 'Textura ou grafiato', 380)]),
  dict(n='area', t='select', q='Qual é a área aproximada?', opts=[
    ('p', 'Até 20 m²', 0), ('m', '20 a 50 m²', 200), ('g', '50 a 100 m²', 500), ('gg', 'Mais de 100 m²', 900)]),
  dict(n='condicao', t='opts', q='Como está a superfície hoje?', hint='A pintura só aguenta se a base estiver preparada.', opts=[
    ('boa', 'Em bom estado', 0), ('mofo', 'Mofo ou infiltração', 150), ('rachada', 'Descascando ou com rachaduras', 120), ('nsei', 'Não sei avaliar', 0)]),
  dict(n='tinta', t='pills', q='Quem fornece a tinta?', opts=[('eu', 'Eu compro a tinta'), ('pro', 'O profissional leva e cobra à parte')]),
  dict(n='mobilia', t='pills', q='O local está vazio ou com móveis?', opts=[('vazio', 'Vazio'), ('moveis', 'Com móveis (precisa proteger)', 60)]),
  dict(n='altura', t='pills', q='Qual é a altura do local?', opts=[('normal', 'Pé-direito normal'), ('alto', 'Alto (precisa de andaime ou escada grande)', 100)]),
 ]),
 'montagem': dict(label='Montagem', icon='cube', qs=[
  dict(n='tipo', t='opts', q='O que precisa ser montado?', opts=[
    ('guarda', 'Guarda-roupa', 180), ('cama', 'Cama ou beliche', 120), ('estante', 'Estante ou rack', 140),
    ('mesa', 'Mesa ou escrivaninha', 100), ('armario', 'Armário de cozinha ou banheiro', 250), ('outro', 'Outro móvel', 140)]),
  dict(n='qtd', t='stepper', q='Quantos móveis?', suffix='móvel(is)', unit=70, max=10),
  dict(n='caixa', t='pills', q='Os móveis já estão em casa, com manual e peças?', opts=[('sim', 'Sim, tudo completo'), ('falta', 'Faltam peças ou manual')]),
  dict(n='parede', t='pills', q='Precisa fixar na parede?', hint='Furar a parede exige furadeira e bucha certa para o tipo de parede.', opts=[('sim', 'Sim', 40), ('nao', 'Não')]),
  dict(n='tparede', t='pills', q='Qual é o tipo de parede?', showif='parede=sim', opts=[('alvenaria', 'Alvenaria'), ('drywall', 'Drywall'), ('nsei', 'Não sei')]),
  dict(n='acesso', t='pills', q='Como é o acesso ao local?', opts=[('terreo', 'Térreo ou elevador'), ('escada', 'Só por escada')]),
  dict(n='desmontar', t='check', q='Mais alguma coisa?', opts=[('sim', 'Desmontar e levar o móvel antigo', 60)]),
 ]),
}

COMMON = """
    <fieldset class="q">
      <legend><label for="problema">Algum detalhe a mais? <span class="hint" style="font-weight:400">(opcional)</span></label></legend>
      <textarea class="field" id="problema" rows="3" placeholder="%(ph)s"></textarea>
    </fieldset>
    <div class="sec">
      <div class="sec-h"><div class="sec-t">Fotos e vídeos</div><div class="hint">Opcional · ajuda a estimar o preço</div></div>
      <div class="media" id="media"></div>
      <input type="file" id="file" accept="image/*,video/*" multiple hidden>
    </div>
    <div class="prefer">
      <div class="av"><svg class="i"><use href="#i-user"/></svg></div>
      <div class="tx"><b>Prefiro profissional mulher</b><span>Vale para agendar e para o pedido imediato.</span></div>
      <button type="button" class="switch" id="womenSwitch" role="switch" aria-checked="true" aria-label="Preferir profissional mulher"></button>
    </div>"""
PLACEHOLDER = {
 'eletrica': 'Ex.: a tomada da sala esquenta quando ligo o ferro.',
 'encanamento': 'Ex.: a pia da cozinha vaza embaixo, perto do sifão.',
 'pintura': 'Ex.: quarto de 12 m², parede com mancha perto da janela.',
 'montagem': 'Ex.: guarda-roupa de 6 portas, tem criança pequena no quarto.',
}

def form_page(sid):
    d = SERVICES[sid]
    qs = '\n'.join(question(q) for q in d['qs'])
    body = f"""<header class="head">
  <a class="back" id="back" href="index.html" aria-label="Voltar"><svg class="i thick"><use href="#i-back"/></svg></a>
  <div class="t"><h1>{d['label']}</h1><div class="sub">Passo 1 de 3 · conte o que precisa</div></div>
</header>
<form id="form" class="screen-form" style="display:contents">
  <div class="body" style="gap:22px">
    <div class="tag" id="urgentTag" hidden style="align-self:flex-start"><svg class="i s16 thick"><use href="#i-bolt"/></svg>Pedido para hoje</div>
{qs}
{COMMON % dict(ph=PLACEHOLDER[sid])}
  </div>
  <div class="foot">
    <div class="est"><span>Estimativa a partir de</span><b id="est">—</b></div>
    <button type="submit" class="btn primary" id="btnSched" data-next="agendar.html" data-mode="agendado"><svg class="i"><use href="#i-calendar"/></svg>Agendar e escolher o profissional</button>
    <button type="submit" class="btn outline" id="btnNow" data-next="hoje.html" data-mode="hoje"><svg class="i"><use href="#i-bolt"/></svg>Mais rápido possível</button>
  </div>
</form>"""
    script = f"""
const S = FX.state;
S.service = '{sid}';
const urgent = S.intent === 'hoje';
FX.initForm(document.getElementById('form'));
if (urgent) {{
  document.getElementById('urgentTag').hidden = false;
  const a = document.getElementById('btnSched'), b = document.getElementById('btnNow');
  a.className = 'btn outline'; b.className = 'btn primary';
  b.parentNode.insertBefore(b, a);
}}
S.intent = null; FX.save();
"""
    return page(d['label'], body, script)

for sid in SERVICES:
    open(f'{sid}.html', 'w').write(form_page(sid))

# ---------------------------------------------------------------- início
home = """<div class="body home">
  <div class="brand">
    <div class="logo"><div class="mark"><svg class="i thick"><use href="#i-roller"/></svg></div><div><b>FIX</b><span>UP</span></div></div>
    <div class="loc"><svg class="i s16 thick"><use href="#i-pin"/></svg>São Paulo, SP</div>
  </div>
  <div>
    <div class="eyebrow">CUIDADO COM A SUA CASA</div>
    <h1 class="hello">Olá, Mariana.<br><em>O que você precisa resolver hoje?</em></h1>
  </div>
  <div class="sec">
    <div class="sec-t">Serviços</div>
    <div class="svc-grid">
      <a class="svc" href="eletrica.html"><svg class="i s26"><use href="#i-bolt"/></svg><span>Elétrica</span></a>
      <a class="svc" href="encanamento.html"><svg class="i s26"><use href="#i-drop"/></svg><span>Encanamento</span></a>
      <a class="svc" href="pintura.html"><svg class="i s26"><use href="#i-roller"/></svg><span>Pintura</span></a>
      <a class="svc" href="montagem.html"><svg class="i s26"><use href="#i-cube"/></svg><span>Montagem</span></a>
    </div>
  </div>
  <button class="promo dark" id="urgent">
    <div class="ic"><svg class="i s22 thick"><use href="#i-bolt"/></svg></div>
    <div class="tx"><b>Precisa para hoje?</b><span>O primeiro profissional disponível aceita o seu pedido.</span></div>
    <svg class="i thick"><use href="#i-next"/></svg>
  </button>
  <a class="promo light" href="ferramentas.html">
    <div class="ic"><svg class="i s22"><use href="#i-toolbox"/></svg></div>
    <div class="tx"><b>Alugue ferramentas</b><span>Com checklist de fotos e garantia.</span></div>
    <svg class="i thick"><use href="#i-next"/></svg>
  </a>
  <div class="trust">
    <div><svg class="i s22"><use href="#i-shield"/></svg>Profissionais verificados</div>
    <div><svg class="i s22"><use href="#i-star"/></svg>Avaliações reais dos dois lados</div>
    <div><svg class="i s22"><use href="#i-tag"/></svg>Preço claro antes de contratar</div>
  </div>
</div>
<nav class="tabbar"></nav>"""
home_js = """
FX.tabbar('inicio');
const S = FX.state;
document.querySelectorAll('.svc').forEach((a) => a.addEventListener('click', () => { S.intent = null; FX.save(); }));
document.getElementById('urgent').addEventListener('click', () => {
  const el = document.createElement('div');
  el.className = 'sheet'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-labelledby', 'shT');
  el.innerHTML = '<div style="align-items:stretch;text-align:left"><h2 id="shT" tabindex="-1" style="text-align:center;margin-bottom:8px">Qual serviço para hoje?</h2>' +
    FX.SERVICES.map((s) => `<a class="btn outline" href="${s.id}.html" data-s="${s.id}">${FX.icon(s.icon)}${s.label}</a>`).join('') +
    '<button class="btn ghost" type="button" id="cancel">Cancelar</button></div>';
  document.querySelector('.app').append(el);
  el.querySelector('#shT').focus();
  el.addEventListener('click', (e) => {
    if (e.target === el || e.target.closest('#cancel')) return el.remove();
    if (e.target.closest('[data-s]')) { S.intent = 'hoje'; FX.save(); }
  });
});
"""
open('index.html', 'w').write(page('Início', home, home_js))
print('ok')
