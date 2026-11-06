/* Jing Chen Homes V2 · 全站公共脚本 */
(function () {
  'use strict';
  var EN = document.documentElement.lang === 'en';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };

  /* 手机菜单 */
  var bg = $('.sburger'), links = $('.slinks');
  if (bg && links) bg.addEventListener('click', function () {
    var o = links.classList.toggle('open');
    bg.setAttribute('aria-expanded', o ? 'true' : 'false');
  });

  /* 旧首页锚点跳到新页面 */
  if (document.body.dataset.page === 'home' && location.hash) {
    var M = { '#sold': 'sold.html', '#reviews': 'about.html#reviews', '#about': 'about.html', '#contact': 'contact.html', '#market': 'areas.html', '#market-report': 'areas.html#market', '#market-budget': 'areas.html#budget', '#market-cities': 'areas.html#cities', '#compare-guides': 'areas.html#compare', '#market-tools': 'insights.html', '#homes': 'buy.html#search', '#services': 'buy.html' };
    if (M[location.hash]) location.replace(M[location.hash] + (location.search || ''));
  }

  /* 图片加载失败时隐藏 */
  $$('img[data-hide-on-error]').forEach(function (i) {
    var h = function () { var p = i.closest('.ph'); if (p) p.classList.add('none'); };
    i.addEventListener('error', h);
    if (i.complete && !i.naturalWidth) h();
  });

  /* 成交筛选 */
  var soldGrid = $('#soldGrid');
  if (soldGrid) {
    var cards = $$('.prop', soldGrid), fc = $('#fCity'), fy = $('#fYear'), fp = $('#fPrice'), fs = $('#fSide'), cnt = $('#soldCount'), empty = $('#soldEmpty');
    var apply = function () {
      var n = 0;
      cards.forEach(function (c) {
        var d = c.dataset, price = +d.price, p = fp.value, ok = (!fc.value || d.city === fc.value) && (!fy.value || d.year === fy.value) && (!fs.value || d.side === fs.value);
        if (p) { var r = p.split('-'); ok = ok && price >= +r[0] && (!r[1] || price < +r[1]); }
        c.hidden = !ok; if (ok) n++;
      });
      cnt.textContent = EN ? 'Showing ' + n + ' of ' + cards.length + ' sales' : '显示 ' + n + ' / ' + cards.length + ' 笔成交';
      empty.hidden = n !== 0;
    };
    [fc, fy, fp, fs].forEach(function (x) { x.addEventListener('change', apply); });
    var q0 = new URLSearchParams(location.search).get('city');
    if (q0 && [].some.call(fc.options, function (o) { return o.value === q0; })) fc.value = q0;
    apply();
  }

  /* 文章中心：分类 + 搜索 */
  var artGrid = $('#artGrid');
  if (artGrid) {
    var arts = $$('[data-cat]', artGrid), chips = $$('.chip[data-f]'), qi = $('#artQ'), ac = $('#artCount'), ae = $('#artEmpty'), cat = '';
    var run = function () {
      var q = (qi.value || '').trim().toLowerCase(), n = 0;
      arts.forEach(function (a) {
        var ok = (!cat || a.dataset.cat === cat) && (!q || a.textContent.toLowerCase().indexOf(q) >= 0);
        a.hidden = !ok; if (ok) n++;
      });
      ac.textContent = EN ? n + ' articles' : '共 ' + n + ' 篇';
      ae.hidden = n !== 0;
    };
    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        cat = c.dataset.f;
        chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
        run();
      });
    });
    qi.addEventListener('input', run);
    var qc = new URLSearchParams(location.search).get('cat');
    if (qc) { var m = chips.filter(function (c) { return c.dataset.f === qc; })[0]; if (m) m.click(); }
    run();
  }

  /* 找房入口：跳转 Zillow 对应城市 */
  var sb = $('#searchGo');
  if (sb) {
    var sc = $('#searchCity');
    var qc2 = new URLSearchParams(location.search).get('city');
    if (qc2 && [].some.call(sc.options, function (o) { return o.value === qc2; })) sc.value = qc2;
    sb.addEventListener('click', function () {
      var slug = sc.value.toLowerCase().replace(/ /g, '-') + '-ca';
      window.open('https://www.zillow.com/' + slug + '/', '_blank', 'noopener');
    });
  }

  /* 咨询表单 */
  var form = $('#leadForm');
  if (form) {
    var started = Date.now(), ta = form.elements.message, sel = form.elements.intent;
    var P = EN ? {
      买房: 'I would like to talk about buying in the Bay Area.\nBudget range:\nWork location:\nCities of interest:\nTarget move-in time:',
      卖房: 'I would like to talk about selling.\nCity or address:\nExpected timing:\nMain concerns:',
      估值: 'I would like a free home value consultation.\nProperty address:\nHome type and recent updates:\nWhen might you sell:',
      换房: 'I would like to plan a move.\nCurrent home city:\nWhere I would like to move:\nTiming:',
      投资: 'I would like to talk about investment property.\nArea of interest:\nBudget:\nGoal (rental income, long-term hold, etc.):',
      其他: ''
    } : {
      买房: '我想咨询在湾区买房。\n预算范围：\n工作地点：\n意向城市：\n希望入住的时间：',
      卖房: '我想咨询卖房。\n房屋所在城市或地址：\n预计出售时间：\n目前最关心的问题：',
      估值: '我想预约免费房屋估值咨询。\n房屋地址：\n房型和近期改动：\n可能的出售时间：',
      换房: '我想讨论换房安排。\n现住房所在城市：\n想搬去的城市：\n时间计划：',
      投资: '我想咨询投资房。\n关注的区域：\n预算：\n目标（出租收益、长期持有等）：',
      其他: ''
    };
    var entries = $$('.entry');
    var filled = '';
    var pick = function (v, keep) {
      sel.value = v;
      entries.forEach(function (e) { e.setAttribute('aria-pressed', e.dataset.intent === v ? 'true' : 'false'); });
      if (!keep && (!ta.value || ta.value === filled)) { ta.value = P[v] || ''; filled = ta.value; }
    };
    entries.forEach(function (e) { e.addEventListener('click', function () { pick(e.dataset.intent); form.elements.name.focus(); }); });
    sel.addEventListener('change', function () { pick(sel.value); });

    var q = new URLSearchParams(location.search);
    var askMap = { buy: '买房', sell: '卖房', swap: '换房', invest: '投资', valuation: '估值', general: '其他', compare: '买房', budget: '买房', city: '买房' };
    var city = (q.get('city') || '').replace(/\+/g, ' ');
    var cs = form.elements.city;
    if (city && [].some.call(cs.options, function (o) { return o.value === city; })) cs.value = city;
    var ask = q.get('type') || q.get('ask');
    if (ask && askMap[ask]) {
      pick(askMap[ask]);
      var topic = (q.get('topic') || '').replace(/[<>]/g, '').slice(0, 40);
      if (ask === 'compare') { ta.value = EN ? 'I am comparing ' + (topic || city || 'a few cities') + ' and would like to talk it through.\nBudget range:\nWork location:\nTiming:' : '我在比较' + (topic || city || '几个城市') + '，想进一步讨论。\n预算范围：\n工作地点：\n时间安排：'; filled = ta.value; }
    }

    var setErr = function (el, msg) {
      var box = el.parentNode.querySelector('.err');
      el.setAttribute('aria-invalid', msg ? 'true' : 'false');
      if (box) box.textContent = msg || '';
    };
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var f = form.elements, ok = true, first = null;
      var fail = function (el, m) { setErr(el, m); ok = false; first = first || el; };
      [f.name, f.phone, f.email, f.intent].forEach(function (x) { setErr(x, ''); });
      if (!f.name.value.trim()) fail(f.name, EN ? 'Please enter your name.' : '请填写姓名。');
      var ph = f.phone.value.trim(), em = f.email.value.trim();
      if (!ph && !em) fail(f.phone, EN ? 'Please give a phone number or email.' : '电话和 Email 至少填写一项。');
      if (ph && ph.replace(/\D/g, '').length < 7) fail(f.phone, EN ? 'Please check the phone number.' : '请检查电话号码。');
      if (em && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) fail(f.email, EN ? 'Please check the email address.' : '请检查 Email 地址。');
      if (!f.intent.value) fail(f.intent, EN ? 'Please choose a topic.' : '请选择需求类型。');
      if (!ok) { first.focus(); return; }

      var btn = $('#leadSubmit'), alertBox = $('#formAlert'), label = btn.textContent;
      alertBox.hidden = true; btn.disabled = true; btn.textContent = EN ? 'Sending...' : '提交中...';
      fetch('/api/lead', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: f.name.value, phone: ph, email: em, intent: f.intent.value, city: f.city.value, message: f.message.value, lang: EN ? 'en' : 'zh', source_url: location.href, referrer: document.referrer, company_website: f.company_website.value, elapsed: Date.now() - started })
      }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.ok) throw new Error(j.error || r.status); }); })
        .then(function () {
          var okb = $('#formOk'); form.hidden = true; okb.hidden = false; okb.setAttribute('tabindex', '-1'); okb.focus();
        })
        .catch(function () {
          alertBox.hidden = false;
          alertBox.textContent = EN ? 'Your message was not sent. Please try again, or call Jing at 925-917-4019.' : '提交没有成功，内容尚未发送。请稍后重试，或直接拨打 925-917-4019。';
          alertBox.focus && alertBox.focus();
        })
        .then(function () { btn.disabled = false; btn.textContent = label; });
    });
  }

  /* 计算器 */
  var money = function (n) { return (n < 0 ? '-$' : '$') + Math.abs(Math.round(n)).toLocaleString('en-US'); };
  var num = function (id) { var e = document.getElementById(id); var v = parseFloat(String(e.value).replace(/[,$\s]/g, '')); return isFinite(v) ? v : 0; };
  var out = function (id, v) { var e = document.getElementById(id); if (e) e.textContent = v; };

  var bc = $('#buyerCalc');
  if (bc) {
    var run1 = function () {
      var price = num('bPrice'), down = price * num('bDown') / 100, loan = Math.max(price - down, 0), r = num('bRate') / 1200, n = num('bTerm') * 12;
      var pi = n ? (r ? loan * r / (1 - Math.pow(1 + r, -n)) : loan / n) : 0;
      var tax = price * num('bTax') / 1200, ins = num('bIns') / 12, hoa = num('bHoa'), oth = num('bMello') / 12, close = price * num('bClose') / 100;
      out('rDown', money(down)); out('rClose', money(close)); out('rCash', money(down + close)); out('rLoan', money(loan));
      out('rPI', money(pi)); out('rTax', money(tax)); out('rIns', money(ins)); out('rHoa', money(hoa + oth)); out('rMonth', money(pi + tax + ins + hoa + oth));
      var w = $('#pmiNote'); if (w) w.hidden = num('bDown') >= 20;
    };
    bc.addEventListener('input', run1); run1();
  }

  var nc = $('#netCalc');
  if (nc) {
    var TT = JSON.parse($('#transferTax').textContent), cc = $('#nCity'), edited = false;
    var taxFor = function (slug, price) {
      var c = (TT.cities || {})[slug] || {}, rate = (TT.county_rate_per_1000 || 0) + (c.city_rate_per_1000 || 0);
      /* 分档按成交总价落点决定，税率适用于全部成交价：min 不含、max 含 */
      (c.tiers || []).forEach(function (x) { if (price > x.min && (x.max === null || x.max === undefined || price <= x.max)) rate = (TT.county_rate_per_1000 || 0) + x.total_city_rate_per_1000; });
      var t = rate * price / 1000;
      return t;
    };
    var run2 = function () {
      var price = num('nPrice'), slug = cc.value, tEl = document.getElementById('nTransfer'), c = (TT.cities || {})[slug] || {};
      if (!edited) tEl.value = Math.round(taxFor(slug, price));
      var nt = $('#nCityNote'); if (nt) nt.textContent = (EN ? c.note_en : c.note_zh) || '';
      var pay = num('nPayoff'), comm = price * (num('nList') + num('nBuyer')) / 100, tr = num('nTransfer'), esc = num('nEscrow'), prep = num('nPrep'), cred = num('nCredit'), oth = num('nOther');
      var cost = comm + tr + esc + prep + cred + oth;
      out('rPrice', money(price)); out('rPay', money(pay)); out('rComm', money(comm)); out('rTrans', money(tr)); out('rEsc', money(esc)); out('rPrep', money(prep + cred + oth)); out('rNet', money(price - pay - cost));
    };
    document.getElementById('nTransfer').addEventListener('input', function () { edited = true; });
    cc.addEventListener('change', function () { edited = false; });
    nc.addEventListener('input', run2); nc.addEventListener('change', run2); run2();
  }
})();

/* 邮编相册 Lightbox：左右切换、手机滑动、计数、关闭、说明 */
(function () {
  'use strict';
  var EN = document.documentElement.lang === 'en';
  var box, img, cap, count, items = [], at = 0, back = null;
  function show(i) {
    at = (i + items.length) % items.length;
    img.src = items[at].getAttribute('href');
    img.alt = items[at].getAttribute('data-cap') || '';
    cap.textContent = items[at].getAttribute('data-cap') || '';
    count.textContent = (at + 1) + ' / ' + items.length;
  }
  function close() {
    box.hidden = true;
    img.removeAttribute('src');
    document.body.style.overflow = '';
    if (back) back.focus();
  }
  function build() {
    box = document.createElement('div');
    box.className = 'zlb';
    box.hidden = true;
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-label', EN ? 'Photo gallery' : '照片相册');
    box.innerHTML = '<div class="zlb-top"><span class="zlb-count" aria-live="polite"></span><button type="button" class="zlb-close" aria-label="' + (EN ? 'Close' : '关闭') + '">×</button></div>' +
      '<div class="zlb-stage"><img alt=""></div><p class="zlb-cap"></p>' +
      '<button type="button" class="zlb-prev" aria-label="' + (EN ? 'Previous photo' : '上一张') + '">‹</button>' +
      '<button type="button" class="zlb-next" aria-label="' + (EN ? 'Next photo' : '下一张') + '">›</button>';
    document.body.appendChild(box);
    img = box.querySelector('img'); cap = box.querySelector('.zlb-cap'); count = box.querySelector('.zlb-count');
    box.querySelector('.zlb-close').onclick = close;
    box.querySelector('.zlb-prev').onclick = function () { show(at - 1); };
    box.querySelector('.zlb-next').onclick = function () { show(at + 1); };
    box.querySelector('.zlb-stage').addEventListener('click', function (e) { if (e.target !== img) close(); });
    var x0 = null;
    box.addEventListener('touchstart', function (e) { x0 = e.touches.length === 1 ? e.touches[0].clientX : null; }, { passive: true });
    box.addEventListener('touchend', function (e) {
      if (x0 === null || items.length < 2) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) show(at + (dx < 0 ? 1 : -1));
      x0 = null;
    });
    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(at - 1);
      else if (e.key === 'ArrowRight') show(at + 1);
    });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-lb] .zshot');
    if (!a || e.metaKey || e.ctrlKey) return;
    e.preventDefault();
    if (!box) build();
    items = [].slice.call(a.parentNode.querySelectorAll('.zshot'));
    back = a;
    box.classList.toggle('one', items.length < 2);
    box.hidden = false;
    document.body.style.overflow = 'hidden';
    show(items.indexOf(a));
    box.querySelector('.zlb-close').focus();
  });
})();
