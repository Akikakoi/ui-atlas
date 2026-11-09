/* UI Atlas —— 静态图鉴：读 styles.json 渲染画廊 / 详情（可改 token、可分享、可导出）/ 对比。
   无构建步骤、无依赖。文件分区：工具 → 索引 → 画廊 → 详情 → 对比 → 路由。 */
(function () {
  'use strict';

  var DATA = null,
      grid = document.getElementById('grid'),
      state = { q: '', group: '', form: '', layout: '', fav: false, recent: false, picked: new Set() },
      editState = {},   // id -> tokens（用户改过的值）
      S = null,         // 当前打开的样式
      lastFocus = null,
      io = null;

  var FORM_LABEL = { landing: '落地页', admin: '后台', app: 'App' };
  var LAYOUT_LABEL = { landing: '落地页版式', admin: '后台', app: 'App', grid: '网格版式', poster: '海报版式', console: '控制台版式', article: '长文版式' };
  // 只有这几种「非默认版式」才值得在卡片上单独标注
  var LAYOUT_TAG = { grid: 1, poster: 1, console: 1, article: 1 };
  var SHORT = { bg: 'b', surface: 's', ink: 'i', muted: 'm', accent: 'a', line: 'l', radius: 'r', font: 'f' };
  var SHORT_REV = {};
  for (var sk in SHORT) SHORT_REV[SHORT[sk]] = sk;

  /* ================================================================= 工具 */
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      var v = attrs[k];
      if (v === null || v === undefined) continue;
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else if (k === 'onclick') n.addEventListener('click', v);
      else n.setAttribute(k, v);
    }
    (children || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function isHex(v) { return /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(v); }
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  /* ---------- 颜色：解析 / 叠加 / 对比度 ---------- */
  function parseColor(v) {
    if (!v) return null;
    v = String(v).trim();
    var m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(v);
    if (m) {
      var h = m[1];
      if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
      return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16), 1];
    }
    m = /^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$/.exec(v);
    if (m) return [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4]];
    return null;
  }
  function over(fg, bg) {
    var a = fg[3];
    return [fg[0] * a + bg[0] * (1 - a), fg[1] * a + bg[1] * (1 - a), fg[2] * a + bg[2] * (1 - a), 1];
  }
  function relLum(c) {
    function ch(x) { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2]);
  }
  function ratioRgb(a, b) {
    var l1 = relLum(a), l2 = relLum(b), hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
  }
  /** fg 对 bg 的对比度；bg 可以是半透明（叠到 page 上）。 */
  function contrastOn(fgStr, bgStr, pageStr) {
    var fg = parseColor(fgStr), bg = parseColor(bgStr), page = parseColor(pageStr || bgStr);
    if (!fg || !bg || !page) return null;
    var pageRgb = page[3] < 1 ? over(page, [255, 255, 255, 1]) : page;
    var bgRgb = bg[3] < 1 ? over(bg, pageRgb) : bg;
    var fgRgb = fg[3] < 1 ? over(fg, bgRgb) : fg;
    return ratioRgb(fgRgb, bgRgb);
  }
  function lumOf(str) {
    var c = parseColor(str);
    if (!c) return 0.5;
    var rgb = c[3] < 1 ? over(c, [255, 255, 255, 1]) : c;
    return relLum(rgb);
  }
  function satOf(str) {
    var c = parseColor(str);
    if (!c) return 0;
    var r = c[0] / 255, g = c[1] / 255, b = c[2] / 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2;
    if (mx === mn) return 0;
    var d = mx - mn;
    return l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
  }
  function hexToHsl(str) {
    var c = parseColor(str);
    if (!c) return null;
    var r = c[0] / 255, g = c[1] / 255, b = c[2] / 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
    var h = 0, s = 0, l = (mx + mn) / 2;
    if (d) {
      s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
      if (mx === r) h = ((g - b) / d) % 6;
      else if (mx === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h *= 60;
      if (h < 0) h += 360;
    }
    return [Math.round(h), Math.round(s * 100), Math.round(l * 100)];
  }
  function rating(r) {
    if (r === null) return { cls: '', txt: 'n/a' };
    if (r >= 4.5) return { cls: 'pass', txt: r.toFixed(1) + ':1 ✓ ' + (r >= 7 ? 'AAA' : 'AA') };
    if (r >= 3) return { cls: 'low', txt: r.toFixed(1) + ':1 AA-' };
    return { cls: 'low', txt: r.toFixed(1) + ':1 ✗' };
  }

  /* ---------- 本地存储 ---------- */
  function load(key, dflt) {
    try { var v = JSON.parse(localStorage.getItem(key)); return v === null ? dflt : v; }
    catch (e) { return dflt; }
  }
  function save(key, v) { try { localStorage.setItem(key, JSON.stringify(v)); } catch (e) {} }
  var FAV = new Set(load('uiatlas.fav', []));
  var RECENT = load('uiatlas.recent', []);

  function markRecent(id) {
    RECENT = [id].concat(RECENT.filter(function (x) { return x !== id; })).slice(0, 10);
    save('uiatlas.recent', RECENT);
    var n = document.getElementById('n-recent');
    if (n) n.textContent = RECENT.length;
    syncDropdowns();
  }

  /* ---------- 缩略图缩放 ---------- */
  function fitShot(shot) {
    var f = shot.querySelector('iframe');
    if (!f) return;
    var w = shot.clientWidth;
    if (w < 40) return;
    var s = w / 1280;
    f.style.transform = 'scale(' + s + ')';
    f.style.height = (shot.clientHeight / s) + 'px';
  }
  function mountShot(shot) {
    var f = shot.querySelector('iframe');
    if (!f || f.dataset.mounted) return;
    f.dataset.mounted = '1';
    f.src = f.dataset.src;
    fitShot(shot);
  }

  /* ================================================================= 搜索索引 */
  var SYN = [
    ['玻璃', 'glass', 'glassmorphism', '毛玻璃', '磨砂'],
    ['粗野', 'brutal', 'brutalism', 'neubrutalism', '硬边'],
    ['拟物', 'skeuo', 'skeuomorphism', '实物'],
    ['新拟物', 'neumorph', 'neumorphism', 'soft ui', '软 ui'],
    ['暗色', '深色', '黑底', 'dark', '暗黑', '夜间'],
    ['浅色', '白底', '亮色', 'light'],
    ['终端', 'terminal', 'cli', '命令行', 'console', 'shell', 'tui'],
    ['等宽', 'mono', 'monospace', '代码'],
    ['衬线', 'serif', '宋体', '明朝', '书卷'],
    ['极简', 'minimal', 'minimalism', '简约', '克制'],
    ['中式', '中国', 'chinese', '国风', '水墨', '东方', '东方'],
    ['像素', 'pixel', '8bit', '8-bit'],
    ['蒸汽波', 'vaporwave', 'vapor'],
    ['赛博', 'cyber', 'cyberpunk', '霓虹', 'neon'],
    ['杂志', 'editorial', '编辑', '排版', '报纸'],
    ['看板', 'dashboard', '数据', '仪表'],
    ['渐变', 'gradient', '光晕'],
    ['手账', 'journal', 'memo', '笔记', '手写'],
    ['装饰', 'deco', 'artdeco', '金线'],
    ['复古', 'retro', '怀旧', 'y2k', 'web2', 'web 2.0'],
    ['全息', 'hud', 'hologram', '战术'],
    ['北欧', 'scandi', 'nordic', '侘寂'],
    ['孟菲斯', 'memphis', '企业插画'],
    ['高端', 'luxury', '奢侈', '品牌'],
    ['大圆角', '圆润', '柔和'],
    ['直角', '圆角0', '零圆角', '方正']
  ];

  function aliases(term) {
    var out = [term];
    SYN.forEach(function (g) {
      for (var i = 0; i < g.length; i++) {
        var k = g[i];
        if (k === term || k.indexOf(term) >= 0 || term.indexOf(k) >= 0) { out = out.concat(g); return; }
      }
    });
    return out;
  }

  function describe(s) {
    var t = s.tokens, d = [];
    var r = parseFloat(t.radius) || 0;
    d.push('圆角' + r);
    if (r === 0) d.push('圆角0', '直角', '零圆角', '方正');
    else if (r <= 6) d.push('小圆角', '克制');
    else if (r >= 16) d.push('大圆角', '圆润');
    var L = lumOf(t.bg);
    if (L < 0.2) d.push('深色', '黑底', '暗色', '夜间');
    else if (L < 0.5) d.push('中灰', '低明度');
    else if (L > 0.82) d.push('浅色', '白底', '亮色');
    else d.push('浅色', '米色', '纸感');
    if (/mono|courier|consolas|cascadia/i.test(t.font)) d.push('等宽', '终端', '代码');
    if (/serif|georgia|songti|simsun|times|kaiti/i.test(t.font)) d.push('衬线', '宋体', '书卷');
    if (/helvetica|arial|segoe|-apple-system|trebuchet|roboto/i.test(t.font)) d.push('无衬线', '瑞士');
    var sat = satOf(t.accent);
    if (sat > 0.75) d.push('高饱和', '撞色');
    if (sat < 0.12) d.push('低饱和', '素');
    if (s.form !== 'landing') d.push(FORM_LABEL[s.form]);
    if (LAYOUT_TAG[s.layout]) d.push(LAYOUT_LABEL[s.layout]);
    if (LAYOUT_TAG[s.layout]) d.push(LAYOUT_LABEL[s.layout]);
    return d;
  }

  function indexData() {
    DATA.styles.forEach(function (s) {
      s._desc = describe(s);
      s._hay = [s.id, s.name, s.name_en, s.era, s.group, FORM_LABEL[s.form] || '',
                (s.features || []).join(' '), s.prompt || '', s.avoid || '',
                (s.sources || []).join(' '), s._desc.join(' ')].join(' ').toLowerCase();
      s._lum = lumOf(s.tokens.bg);
      s._radius = parseFloat(s.tokens.radius) || 0;
    });
  }

  function match(s) {
    if (state.group && s.group !== state.group) return false;
    if (state.form && s.form !== state.form) return false;
    if (state.layout && s.layout !== state.layout) return false;
    if (state.fav && !FAV.has(s.id)) return false;
    if (state.recent && RECENT.indexOf(s.id) < 0) return false;
    if (!state.q) return true;
    var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    return terms.every(function (t) {
      return aliases(t).some(function (a) { return s._hay.indexOf(a.toLowerCase()) >= 0; });
    });
  }

  /* 空结果时给三条最近的，而不是干瘪一句「没有」 */
  function nearest() {
    var q = state.q.toLowerCase();
    var qr = /圆角\s*(\d+)/.exec(q);
    return DATA.styles.map(function (s) {
      var score = 0;
      if (q && s._hay.indexOf(q) >= 0) score += 6;
      if (state.group && s.group === state.group) score += 2;
      if (state.form && s.form === state.form) score += 2;
      if (qr) score += Math.max(0, 3 - Math.abs((+qr[1]) - s._radius) / 8);
      score += Math.max(0, 2 - Math.abs(lumOf(s.tokens.bg) - (q.indexOf('黑') >= 0 || q.indexOf('暗') >= 0 ? 0.05 : 0.9)) * 3);
      return { s: s, score: score };
    }).sort(function (a, b) { return b.score - a.score; }).slice(0, 3).map(function (x) { return x.s; });
  }

  /* ================================================================= 画廊 */
  function card(s) {
    var f = el('iframe', { 'data-src': s.demo, title: s.name + ' 样例', tabindex: '-1', scrolling: 'no' });
    var shot = el('div', { class: 'shot', role: 'button', tabindex: '0', 'aria-label': '打开《' + s.name + '》详情' }, [
      el('div', { class: 'sk', text: '加载预览…' }),
      f,
      el('a', { class: 'fb', href: s.demo, target: '_blank', rel: 'noopener', text: '预览加载失败 · 点这里打开 →' })
    ]);
    f.addEventListener('load', function () {
      if (f.dataset.mounted) shot.classList.add('ready');
    });
    setTimeout(function () { if (!shot.classList.contains('ready')) shot.classList.add('failed'); }, 8000);
    shot.addEventListener('click', function (e) {
      if (e.target.classList && e.target.classList.contains('fb')) return;
      goDetail(s.id);
    });
    shot.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); goDetail(s.id); }
    });

    var cb = el('input', { type: 'checkbox', 'aria-label': '把《' + s.name + '》选入对比' });
    cb.checked = state.picked.has(s.id);
    cb.addEventListener('change', function () {
      if (cb.checked) {
        if (state.picked.size >= 2) { cb.checked = false; flashPicked(); return; }
        state.picked.add(s.id);
      } else { state.picked.delete(s.id); }
      syncPicked();
    });

    var star = el('button', { class: 'star', type: 'button', 'aria-pressed': FAV.has(s.id) ? 'true' : 'false',
      'aria-label': '收藏《' + s.name + '》', title: '收藏', text: FAV.has(s.id) ? '★' : '☆' });
    star.addEventListener('click', function () {
      if (FAV.has(s.id)) FAV.delete(s.id); else FAV.add(s.id);
      save('uiatlas.fav', Array.from(FAV));
      star.textContent = FAV.has(s.id) ? '★' : '☆';
      star.setAttribute('aria-pressed', FAV.has(s.id) ? 'true' : 'false');
      ['landing', 'grid', 'poster', 'console', 'article'].forEach(function (k) {
      var n = document.getElementById('n-lay-' + k);
      if (n) n.textContent = count(function (s) { return s.layout === k; });
    });
    document.getElementById('n-fav').textContent = FAV.size;
      if (state.fav) render();
    });

    var more = el('button', { class: 'linkish', type: 'button', text: '看详情 →' });
    more.addEventListener('click', function () { goDetail(s.id); });

    var ratio = contrastOn(s.tokens.ink, s.tokens.bg);
    var aaCls = ratio !== null && ratio >= 4.5 ? 'aa' : 'aa low';

    return el('article', { class: 'card', 'data-id': s.id }, [
      shot,
      el('div', { class: 'card-body' }, [
        el('div', { class: 'card-title' }, [el('b', { text: s.name }), el('span', { text: s.name_en })]),
        el('div', { class: 'card-meta' }, [
          el('i', { class: 'form', text: FORM_LABEL[s.form] || '落地页' }),
          LAYOUT_TAG[s.layout] ? el('i', { class: 'lay', text: LAYOUT_LABEL[s.layout] }) : null,
          el('i', { text: s.group === 'classic' ? '经典 UI' : '风格平移' }),
          s.era ? el('i', { text: s.era }) : null,
          el('i', { text: s.tokens.radius + ' 圆角' }),
          el('i', { class: aaCls, text: '对比 ' + (ratio === null ? 'n/a' : ratio.toFixed(1)) })
        ]),
        el('div', { class: 'card-foot' }, [
          el('label', {}, [cb, el('span', { text: '选入对比' })]),
          el('span', { class: 'spacer' }),
          star,
          more
        ])
      ])
    ]);
  }

  function emptyBlock() {
    var box = el('div', { class: 'empty' }, [
      el('h2', { text: '没有匹配的风格' }),
      el('p', { text: '可以试试更短的关键词，或按形态 / 分组筛选。' })
    ]);
    var picks = nearest();
    if (picks.length) {
      var row = el('div', { class: 'sug' }, [
        el('span', { text: '相近的三条：', style: 'align-self:center;font-size:13px' })
      ]);
      picks.forEach(function (s) {
        var b = el('button', { type: 'button', text: s.name + ' · ' + (FORM_LABEL[s.form] || '') });
        b.addEventListener('click', function () { goDetail(s.id); });
        row.appendChild(b);
      });
      box.appendChild(row);
    }
    return box;
  }

  function render() {
    syncDropdowns();
    grid.textContent = '';
    if (io) io.disconnect();
    var list = DATA.styles.filter(match);
    document.getElementById('count-info').textContent = list.length + ' / ' + DATA.styles.length + ' 条';
    if (!list.length) { grid.appendChild(emptyBlock()); return; }
    list.forEach(function (s) {
      var c = card(s);
      grid.appendChild(c);
      var shot = c.querySelector('.shot');
      if (io) io.observe(shot); else mountShot(shot);
    });
  }

  function syncPicked() {
    var n = state.picked.size;
    document.getElementById('picked-info').textContent = n ? '已选 ' + n + ' / 2' : '未选';
    document.getElementById('compare-btn').disabled = n !== 2;
  }
  function flashPicked() {
    var e = document.getElementById('picked-info');
    e.textContent = '最多选 2 个';
    setTimeout(syncPicked, 1200);
  }

  /* ================================================================= 复制 */
  function copy(text, btn, okText) {
    var done = function () {
      if (!btn) return;
      var old = btn.textContent;
      btn.textContent = okText || '已复制 ✓';
      setTimeout(function () { btn.textContent = old; }, 1200);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(text); done(); });
    } else { fallback(text); done(); }
  }
  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
  }

  /* ================================================================= 对比 */
  /* ================================================================= 对比 */
  var COMPARE_IDS = [];

  function fontClass(font) {
    if (/mono|courier|consolas|cascadia/i.test(font)) return '等宽';
    if (/serif|georgia|songti|simsun|times|kaiti/i.test(font)) return '衬线';
    return '无衬线';
  }

  function conclusion(a, b) {
    var out = [];
    var diffLayout = (a.layout || 'landing') !== (b.layout || 'landing');
    if (a.tokens.radius !== b.tokens.radius) out.push('圆角 ' + a.tokens.radius + ' ↔ ' + b.tokens.radius);
    var la = lumOf(a.tokens.bg), lb = lumOf(b.tokens.bg);
    if (Math.abs(la - lb) >= 0.25) out.push(la < lb ? '底色一暗一亮' : '底色一亮一暗');
    var sa = satOf(a.tokens.accent), sb = satOf(b.tokens.accent);
    if (Math.min(sa, sb) > 0.02 && Math.max(sa, sb) / Math.min(sa, sb) >= 1.6) {
      out.push('主色饱和差 ' + (Math.max(sa, sb) / Math.min(sa, sb)).toFixed(1) + ' 倍');
    } else if (a.tokens.accent !== b.tokens.accent) {
      out.push('主色不同');
    }
    var fa = fontClass(a.tokens.font), fb = fontClass(b.tokens.font);
    if (fa !== fb) out.push('字体 ' + fa + ' vs ' + fb);
    if (!out.length) out.push('两条风格的 tokens 完全一致，差异都来自各自的 CSS');
    var head = diffLayout
      ? '版式不同（' + LAYOUT_LABEL[a.layout || 'landing'] + ' vs ' + LAYOUT_LABEL[b.layout || 'landing']
        + '），布局不能直接比，下面只比 tokens。'
      : '';
    return head + '差在：' + out.join('；') + '。';
  }

  function openCompare() {
    if (state.picked.size !== 2) return;
    lastFocus = document.activeElement;
    COMPARE_IDS = Array.from(state.picked);
    var a = DATA.styles.find(function (x) { return x.id === COMPARE_IDS[0]; });
    var b = DATA.styles.find(function (x) { return x.id === COMPARE_IDS[1]; });

    document.getElementById('c-title').textContent = a.name + '  ×  ' + b.name;
    document.getElementById('c-conclusion').textContent = conclusion(a, b);
    document.getElementById('c-th-a').textContent = a.name;
    document.getElementById('c-th-b').textContent = b.name;

    var body = document.getElementById('c-body');
    body.textContent = '';
    var frames = [];
    [a, b].forEach(function (s) {
      var f = el('iframe', { src: s.demo, title: s.name + ' 样例' });
      frames.push(f);
      body.appendChild(el('div', { class: 'compare-cell' }, [
        el('header', {}, [
          el('b', { text: s.name }),
          el('span', { text: FORM_LABEL[s.form] + ' · ' + s.tokens.radius + ' 圆角' })
        ]),
        f
      ]));
    });

    // 差异表
    var tb = document.getElementById('c-diff-body');
    tb.textContent = '';
    Object.keys(a.tokens).forEach(function (k) {
      var va = a.tokens[k], vb = b.tokens[k];
      var diff = va !== vb;
      var row = el('tr', { class: diff ? 'diff' : '' });
      row.appendChild(el('td', { text: k }));
      [va, vb].forEach(function (v) {
        var td = el('td');
        var c = parseColor(v);
        if (c && k !== 'font') {
          var sw = el('span', { class: 'sw' });
          sw.style.background = v;
          td.appendChild(sw);
        }
        td.appendChild(document.createTextNode(v));
        row.appendChild(td);
      });
      tb.appendChild(row);
    });

    // 同步滚动（同源 iframe，直接接管内部 scroll）
    frames.forEach(function (f, i) {
      f.addEventListener('load', function () {
        try {
          var w = f.contentWindow;
          w.addEventListener('scroll', function () {
            if (!document.getElementById('c-sync').checked) return;
            var other = frames[1 - i];
            try {
              var ow = other.contentWindow, d = other.contentDocument.documentElement;
              var max = d.scrollHeight - ow.innerHeight;
              var src = w.document.documentElement;
              var smax = src.scrollHeight - w.innerHeight;
              if (max > 0 && smax > 0) ow.scrollTo(0, Math.round(w.scrollY / smax * max));
            } catch (e) {}
          }, { passive: true });
        } catch (e) {}
      });
    });

    compare.hidden = false;
    setTimeout(function () { document.getElementById('c-close').focus(); }, 30);
  }

  document.getElementById('compare-btn').addEventListener('click', openCompare);
  document.getElementById('c-close').addEventListener('click', function () {
    compare.hidden = true;
    COMPARE_IDS = [];
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  });
  document.getElementById('c-diff-toggle').addEventListener('click', function () {
    var d = document.getElementById('c-diff');
    var show = d.hidden;
    d.hidden = !show;
    this.setAttribute('aria-expanded', show ? 'true' : 'false');
  });


  /* ================================================================= 筛选下拉 */
  var DD_LABEL = {
    group: { "": "全部", classic: "经典 UI", shift: "风格平移" },
    form: { "": "全部", landing: "落地页", admin: "后台", app: "App" },
    layout: { "": "全部", landing: "落地页", grid: "网格", poster: "海报",
              console: "控制台", article: "长文" }
  };

  function closeMenus() {
    document.querySelectorAll(".dd-menu").forEach(function (m) { m.hidden = true; });
    document.querySelectorAll(".dd-btn").forEach(function (b) { b.setAttribute("aria-expanded", "false"); });
  }

  function syncDropdowns() {
    document.querySelectorAll(".dd").forEach(function (dd) {
      var k = dd.getAttribute("data-dd");
      var v = dd.querySelector(".dd-v");
      if (!v) return;
      if (k === "mine") {
        var mine = [];
        if (state.fav) mine.push("收藏 " + FAV.size);
        if (state.recent) mine.push("最近 " + RECENT.length);
        v.textContent = mine.length ? mine.join(" · ") : "未设置";
        dd.classList.toggle("is-set", mine.length > 0);
      } else {
        var label = (DD_LABEL[k] || {})[state[k]];
        if (label === undefined) label = state[k] || "全部";
        v.textContent = label;
        dd.classList.toggle("is-set", !!state[k]);
      }
    });
  }

  document.querySelectorAll(".dd").forEach(function (dd) {
    var btn = dd.querySelector(".dd-btn"), menu = dd.querySelector(".dd-menu");
    if (!btn || !menu) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = menu.hidden;
      closeMenus();
      menu.hidden = !open;
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".dd")) closeMenus();
  });

  /* ================================================================= 顶栏与路由 */
  var q = document.getElementById('q');
  var qt = null;
  q.addEventListener('input', function () {
    clearTimeout(qt);
    qt = setTimeout(function () { state.q = q.value.trim(); render(); }, 120);
  });
  q.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { q.value = ''; state.q = ''; render(); }
  });

  document.querySelectorAll('.chip[data-k]').forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.getAttribute('data-k'), v = b.getAttribute('data-v');
      if (k === 'fav' || k === 'recent') {
        state[k] = !state[k];
        b.setAttribute('aria-pressed', state[k] ? 'true' : 'false');
      } else {
        state[k] = v;
        document.querySelectorAll('.chip[data-k="' + k + '"]').forEach(function (x) {
          x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
        });
      }
      closeMenus();
      syncDropdowns();
      render();
    });
  });

  function focusables(box) {
    return Array.prototype.filter.call(
      box.querySelectorAll('a[href],button:not([disabled]),input,select,textarea,pre,[tabindex]:not([tabindex="-1"])'),
      function (n) { return n.offsetParent !== null || n === document.activeElement; }
    );
  }

  document.addEventListener('keydown', function (e) {
    var openBox = !compare.hidden ? compare.querySelector('.compare-box') : null;

    if (e.key === 'Escape') {
      closeMenus();
      if (!compare.hidden) {
        compare.hidden = true;
        if (lastFocus && lastFocus.focus) lastFocus.focus();
        return;
      }
    }
    if (e.key === '/' && document.activeElement !== q && !openBox) {
      e.preventDefault(); q.focus();
    }
    if (e.key === 'Tab' && openBox) {
      var f = focusables(openBox);
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (!openBox.contains(document.activeElement)) { e.preventDefault(); first.focus(); return; }
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  window.addEventListener('resize', function () {
    document.querySelectorAll('.shot').forEach(fitShot);
  });

  /* ================================================================= 跳转到详情页 */
  function saveUiState() {
    try {
      sessionStorage.setItem('uiatlas.gallery', JSON.stringify({
        q: state.q, group: state.group, form: state.form, layout: state.layout,
        fav: state.fav, recent: state.recent, y: window.scrollY
      }));
    } catch (e) {}
  }
  function restoreUiState() {
    try {
      var s = JSON.parse(sessionStorage.getItem('uiatlas.gallery') || 'null');
      if (!s) return;
      state.q = s.q || ''; state.group = s.group || ''; state.form = s.form || '';
      state.layout = s.layout || ''; state.fav = !!s.fav; state.recent = !!s.recent;
      q.value = state.q;
      window.__restoreY = s.y || 0;
    } catch (e) {}
  }
  function syncChips() {
    document.querySelectorAll('.chip[data-k]').forEach(function (c) {
      var k = c.getAttribute('data-k'), v = c.getAttribute('data-v');
      if (k === 'fav') c.setAttribute('aria-pressed', state.fav ? 'true' : 'false');
      else if (k === 'recent') c.setAttribute('aria-pressed', state.recent ? 'true' : 'false');
      else c.setAttribute('aria-pressed', state[k] === v ? 'true' : 'false');
    });
  }
  function goDetail(id) {
    saveUiState();
    location.href = 'detail.html?id=' + encodeURIComponent(id);
  }

  window.addEventListener('scroll', function () {
    clearTimeout(window.__st);
    window.__st = setTimeout(saveUiState, 250);
  }, { passive: true });

  /* ================================================================= 启动 */
  fetch('styles.json').then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }).then(function (d) {
    DATA = d;
    indexData();

    var count = function (fn) { return d.styles.filter(fn).length; };
    document.getElementById('n-sub').textContent = d.total;
    document.getElementById('n-all').textContent = d.total;
    document.getElementById('n-classic').textContent = count(function (s) { return s.group === 'classic'; });
    document.getElementById('n-shift').textContent = count(function (s) { return s.group === 'shift'; });
    document.getElementById('n-form-all').textContent = d.total;
    document.getElementById('n-landing').textContent = count(function (s) { return s.form === 'landing'; });
    document.getElementById('n-admin').textContent = count(function (s) { return s.form === 'admin'; });
    document.getElementById('n-app').textContent = count(function (s) { return s.form === 'app'; });
    ['landing', 'grid', 'poster', 'console', 'article'].forEach(function (k) {
      var n = document.getElementById('n-lay-' + k);
      if (n) n.textContent = count(function (s) { return s.layout === k; });
    });
    document.getElementById('n-fav').textContent = FAV.size;
    document.getElementById('n-recent').textContent = RECENT.length;

    if ('IntersectionObserver' in window) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          mountShot(en.target);
          io.unobserve(en.target);
        });
      }, { rootMargin: '300px 0px' });
    }

    restoreUiState();
    syncChips();
    render();
    if (window.__restoreY) window.scrollTo(0, window.__restoreY);
    if (/^#\/s\//.test(location.hash)) {
      // 旧的 hash 分享链接 → 跳到独立详情页
      location.replace('detail.html?id=' + location.hash.slice(4));
    }
  }).catch(function (err) {
    window.__errstack = (err && err.stack) || String(err);
    grid.appendChild(el('div', { class: 'empty' }, [
      el('h2', { text: '读不到 styles.json（' + err.message + '）' }),
      el('p', { text: '用 file:// 直接打开时浏览器会拦截 fetch；请运行 serve.py 或 启动预览.bat。' })
    ]));
  });
})();
