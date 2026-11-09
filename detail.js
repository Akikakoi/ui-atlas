/* UI Atlas —— 风格详情页（detail.html?id=<id>）
   从 app.js 拆出的详情逻辑：大预览 + 可编辑 tokens + 对比度 + 导出 + 分享。
   工具函数与 app.js 各有一份（项目无构建步骤，刻意不抽公共包），改一处记得同步另一处。 */
(function () {
  'use strict';

  var DATA = null, S = null, curFmt = 'css';
  var editState = {};   // id -> tokens（用户改过的值）

  var SHORT = { bg: 'b', surface: 's', ink: 'i', muted: 'm', accent: 'a', line: 'l', radius: 'r', font: 'f' };
  var SHORT_REV = {};
  for (var sk in SHORT) SHORT_REV[SHORT[sk]] = sk;
  var FORM_LABEL = { landing: '落地页', admin: '后台', app: 'App' };
  var LAYOUT_LABEL = { landing: '落地页版式', admin: '后台', app: 'App', grid: '网格版式', poster: '海报版式', console: '控制台版式', article: '长文版式' };

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
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

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
  function contrastOn(fgStr, bgStr, pageStr) {
    var fg = parseColor(fgStr), bg = parseColor(bgStr), page = parseColor(pageStr || bgStr);
    if (!fg || !bg || !page) return null;
    var pageRgb = page[3] < 1 ? over(page, [255, 255, 255, 1]) : page;
    var bgRgb = bg[3] < 1 ? over(bg, pageRgb) : bg;
    var fgRgb = fg[3] < 1 ? over(fg, bgRgb) : fg;
    var l1 = relLum(fgRgb), l2 = relLum(bgRgb);
    var hi = Math.max(l1, l2), lo = Math.min(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
  }
  function rating(r) {
    if (r === null) return { cls: '', txt: 'n/a' };
    if (r >= 4.5) return { cls: 'pass', txt: r.toFixed(1) + ':1 ✓ ' + (r >= 7 ? 'AAA' : 'AA') };
    if (r >= 3) return { cls: 'low', txt: r.toFixed(1) + ':1 AA-' };
    return { cls: 'low', txt: r.toFixed(1) + ':1 ✗' };
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

  /* ================================================================= 导出格式 */
  function cssText(tokens) {
    return ':root {\n' + Object.keys(tokens).map(function (k) {
      return '  --' + k + ': ' + tokens[k] + ';';
    }).join('\n') + '\n}';
  }
  function smRadius(r) {
    var n = parseFloat(r);
    if (isNaN(n)) return '8px';
    return (n === 0 ? 0 : Math.min(8, n)) + 'px';
  }
  function tailwindText(tokens) {
    var keys = ['bg', 'surface', 'ink', 'muted', 'accent', 'line'];
    var colors = keys.map(function (k) { return "        " + k + ": '" + tokens[k] + "',"; }).join('\n');
    var fonts = tokens.font.split(',').map(function (x) {
      return "'" + x.trim().replace(/^['"]|['"]$/g, '') + "'";
    }).join(', ');
    return '// tailwind.config.js\nmodule.exports = {\n  theme: {\n    extend: {\n      colors: {\n'
      + colors + '\n      },\n      borderRadius: {\n        DEFAULT: \'' + tokens.radius + '\',\n        sm: \''
      + smRadius(tokens.radius) + '\',\n      },\n      fontFamily: {\n        sans: [' + fonts + '],\n      },\n'
      + '    },\n  },\n};';
  }
  function shadcnText(tokens) {
    var map = [['background', 'bg'], ['card', 'surface'], ['foreground', 'ink'],
               ['muted-foreground', 'muted'], ['primary', 'accent'], ['border', 'line']];
    var body = map.map(function (p) {
      var hsl = hexToHsl(tokens[p[1]]);
      if (!hsl) return '  /* --' + p[0] + ': ' + tokens[p[1]] + ' （非纯色，需手动换算） */';
      var extra = parseColor(tokens[p[1]])[3] < 1 ? '  /* 原值 ' + tokens[p[1]] + ' 半透明 */' : '';
      return '  --' + p[0] + ': ' + hsl[0] + ' ' + hsl[1] + '% ' + hsl[2] + '%;' + extra;
    }).join('\n');
    return '/* app.css —— shadcn 变量命名映射 */\n:root {\n' + body + '\n  --radius: ' + tokens.radius + ';\n}\n'
      + '\n/* tailwind.config 里记得：colors 用 hsl(var(--background)) 这类写法 */';
  }
  var FMT = { css: cssText, tailwind: tailwindText, shadcn: shadcnText };
  function setFmt(fmt) {
    curFmt = fmt;
    document.querySelectorAll('#d-export .tabs button').forEach(function (b) {
      b.setAttribute('aria-selected', b.dataset.fmt === fmt ? 'true' : 'false');
    });
    var code = document.getElementById('d-export-code');
    code.textContent = S ? FMT[fmt](tokensOf(S)) : '';
    document.getElementById('d-export-copy').onclick = function () { copy(code.textContent, this); };
  }

  /* ================================================================= tokens */
  function tokensOf(s) {
    if (!editState[s.id]) editState[s.id] = Object.assign({}, s.tokens);
    return editState[s.id];
  }
  function changedKeys(s) {
    var t = tokensOf(s), out = {};
    Object.keys(s.tokens).forEach(function (k) { if (t[k] !== s.tokens[k]) out[k] = 1; });
    return out;
  }
  function applyVars(iframe, tokens) {
    try {
      var root = iframe.contentDocument.documentElement;
      Object.keys(tokens).forEach(function (k) { root.style.setProperty('--' + k, tokens[k]); });
    } catch (e) { /* iframe 未就绪 */ }
  }
  function shareUrl(s, tokens) {
    var base = location.origin + location.pathname;
    var qs = [];
    Object.keys(SHORT).forEach(function (k) {
      if (tokens[k] !== undefined && tokens[k] !== s.tokens[k]) {
        qs.push(SHORT[k] + '=' + encodeURIComponent(tokens[k]));
      }
    });
    return base + '?id=' + encodeURIComponent(s.id) + (qs.length ? '&' + qs.join('&') : '');
  }
  function updateContrast(tokens) {
    var parts = [
      ['ink/bg', contrastOn(tokens.ink, tokens.bg)],
      ['ink/surface', contrastOn(tokens.ink, tokens.surface, tokens.bg)],
      ['ink/accent', contrastOn(tokens.ink, tokens.accent, tokens.bg)]
    ];
    var box = document.getElementById('d-contrast');
    box.textContent = '';
    parts.forEach(function (p, i) {
      if (i) box.appendChild(document.createTextNode(' · '));
      box.appendChild(document.createTextNode(p[0] + ' '));
      var b = el('b', { text: rating(p[1]).txt });
      b.className = rating(p[1]).cls;
      box.appendChild(b);
    });
    box.appendChild(document.createTextNode('   （WCAG 正文需 ≥ 4.5:1）'));
  }
  function syncHash(s, tokens) {
    var qs = [];
    Object.keys(SHORT).forEach(function (k) {
      if (tokens[k] !== undefined && tokens[k] !== s.tokens[k]) {
        qs.push(SHORT[k] + '=' + encodeURIComponent(tokens[k]));
      }
    });
    var url = location.pathname + '?id=' + encodeURIComponent(s.id) + (qs.length ? '&' + qs.join('&') : '');
    history.replaceState(null, '', url);
  }

  function buildTokens(s, iframe) {
    var box = document.getElementById('d-tokens');
    box.textContent = '';
    var tokens = tokensOf(s);
    var changed = changedKeys(s);

    function commit() {
      applyVars(iframe, tokens);
      updateContrast(tokens);
      document.getElementById('d-export-code').textContent = FMT[curFmt](tokens);
      syncHash(s, tokens);
    }

    Object.keys(s.tokens).forEach(function (k) {
      var row = el('div', { class: 'tok' + (changed[k] ? ' changed' : ''), 'data-k': k });
      row.appendChild(el('span', { class: 'tk', text: k }));

      var out = el('code', { text: tokens[k] });
      var ctrl;

      if (/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(tokens[k])) {
        ctrl = el('input', { type: 'color', value: tokens[k], 'aria-label': k });
        ctrl.addEventListener('input', function () {
          tokens[k] = ctrl.value; out.textContent = ctrl.value;
          row.classList.toggle('changed', tokens[k] !== s.tokens[k]);
          commit();
        });
      } else if (k === 'radius') {
        ctrl = el('input', { type: 'range', min: '0', max: '40', step: '1',
          value: String(clamp(parseFloat(tokens[k]) || 0, 0, 40)), 'aria-label': k });
        ctrl.addEventListener('input', function () {
          tokens[k] = ctrl.value + 'px'; out.textContent = tokens[k];
          row.classList.toggle('changed', tokens[k] !== s.tokens[k]);
          commit();
        });
      } else {
        ctrl = el('input', { type: 'text', value: tokens[k], 'aria-label': k, spellcheck: 'false' });
        ctrl.addEventListener('input', function () {
          tokens[k] = ctrl.value; out.textContent = ctrl.value;
          row.classList.toggle('changed', tokens[k] !== s.tokens[k]);
          commit();
        });
      }

      var cr = el('span', { class: 'cr' });
      if (k !== 'bg' && parseColor(tokens[k])) {
        var r = contrastOn(tokens[k], tokens.bg);
        if (r !== null) { cr.textContent = r.toFixed(1); cr.className = 'cr ' + rating(r).cls; }
      }

      row.appendChild(ctrl);
      row.appendChild(out);
      row.appendChild(cr);
      box.appendChild(row);
    });

    box.appendChild(el('div', { class: 'tok-bar' }, [
      el('button', {
        class: 'btn small', type: 'button', text: '重置为原值',
        onclick: function () {
          delete editState[s.id];
          try { iframe.contentDocument.documentElement.removeAttribute('style'); } catch (e) {}
          buildTokens(s, iframe);
          syncHash(s, s.tokens);
        }
      }),
      el('button', {
        class: 'btn small', type: 'button', text: '复制 CSS 变量',
        onclick: function () { copy(cssText(tokensOf(s)), this); }
      }),
      el('span', { class: 'tok-hint', text: '改动只作用于预览' })
    ]));

    commit();
  }

  /* ================================================================= 渲染 */
  function renderDetail(s, params) {
    S = s;
    var applied = 0;
    if (params) {
      var t = tokensOf(s);
      Object.keys(params).forEach(function (k) {
        if (s.tokens[k] !== undefined && params[k] !== t[k]) { t[k] = params[k]; applied++; }
      });
    }

    document.title = s.name + ' · UI Atlas';
    document.getElementById('d-name').textContent = s.name + ' · ' + s.name_en;
    document.getElementById('d-sub').textContent =
      (s.group === 'classic' ? '经典 UI 风格' : '风格平移（来自动效库）')
      + ' · ' + (FORM_LABEL[s.form] || '落地页')
      + (LAYOUT_LABEL[s.layout] && s.layout !== 'landing' ? ' · ' + LAYOUT_LABEL[s.layout] : '')
      + (s.era ? ' · ' + s.era : '');

    var banner = document.getElementById('d-banner');
    banner.hidden = applied === 0;
    banner.textContent = applied ? '已套用分享链接里的 ' + applied + ' 处改动（右侧高亮）。' : '';

    var df = document.getElementById('d-frame');
    df.style.opacity = '.35';
    df.onload = function () {
      df.style.opacity = '1';
      applyVars(df, tokensOf(s));
    };
    df.src = s.demo;
    document.getElementById('d-open').href = s.demo;

    var ul = document.getElementById('d-features');
    ul.textContent = '';
    s.features.forEach(function (f) { ul.appendChild(el('li', { text: f })); });

    document.getElementById('d-avoid').textContent = s.avoid || '（暂无）';

    var src = document.getElementById('d-sources');
    src.textContent = '';
    (s.sources || []).forEach(function (x) { src.appendChild(el('li', { text: x })); });

    document.getElementById('d-prompt').textContent = s.prompt;
    document.getElementById('d-copy-prompt').onclick = function () { copy(s.prompt, this); };

    var exp = document.getElementById('d-export');
    exp.hidden = true;
    document.getElementById('d-export-btn').setAttribute('aria-expanded', 'false');
    curFmt = 'css';
    setFmt('css');
    buildTokens(s, df);

    document.getElementById('d-share').onclick = function () {
      copy(shareUrl(s, tokensOf(s)), this, '链接已复制 ✓');
    };
  }

  function showMissing(id) {
    document.title = '没有这个风格 · UI Atlas';
    document.getElementById('d-name').textContent = '没有找到「' + (id || '?') + '」';
    document.getElementById('d-sub').textContent = '链接可能不完整，回图鉴里重新选一条吧。';
    document.querySelector('.dp-body').hidden = true;
    document.getElementById('d-open').hidden = true;
    document.getElementById('d-share').hidden = true;
    document.getElementById('d-export-btn').hidden = true;
  }

  /* ================================================================= 启动 */
  var qs = new URLSearchParams(location.search);
  var wantId = qs.get('id') || '';
  var params = {};
  Object.keys(SHORT).forEach(function (k) {
    var v = qs.get(SHORT[k]);
    if (v !== null) params[k] = v;
  });

  fetch('styles.json').then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }).then(function (d) {
    DATA = d;
    var s = DATA.styles.find(function (x) { return x.id === wantId; });
    if (!s) { showMissing(wantId); return; }
    renderDetail(s, params);
  }).catch(function (err) {
    showMissing(wantId);
    document.getElementById('d-sub').textContent = '读不到 styles.json（' + err.message + '），请用 serve.py 打开。';
  });
})();
