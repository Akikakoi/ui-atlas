/* UI Atlas · 动效图鉴：读 effects.json 渲染画廊 / 工作台预览与源码。
   与 app.js 同一套约定：无依赖、无构建，hash 直达某个效果。 */
(function () {
  'use strict';

  var DATA = null,
      SNIPPETS = null,
      grid = document.getElementById('fx-grid'),
      modal = document.getElementById('fxWorkbench'),
      wbBox = document.querySelector('.fx-wb-box'),
      wbFrame = document.getElementById('wb-frame'),
      wbStage = document.getElementById('wb-stage'),
      wbLoading = document.getElementById('wb-loading'),
      notesBtn = document.getElementById('wb-notes-btn'),
      qInput = document.getElementById('q'),
      state = { q: '', cat: '', fav: false },
      openId = null,
      lastFocus = null,
      curSrc = '',
      curTab = 'all',
      cache = {},
      snippetCache = {},
      io = null,
      ioAway = null,
      mountedShots = [],
      moreMenu = null,
      moreTrigger = null,
      moreOwner = null,
      toastEl = document.getElementById('fxToast'),
      toastTimer = null,
      uiReady = false,
      pageRegions = [
        document.querySelector('header.top'),
        document.getElementById('fx-grid'),
        document.querySelector('.foot'),
        document.querySelector('.skip')
      ];

  /* 锁滚动时把滚动条宽度补成 body 右内边距，避免弹层打开瞬间的布局位移 */
  function lockScroll(on) {
    if (on) {
      var sbw = window.innerWidth - document.documentElement.clientWidth;
      if (sbw > 0) document.body.style.paddingRight = sbw + 'px';
    } else {
      document.body.style.paddingRight = '';
    }
  }

  function setPageInert(on) {
    pageRegions.forEach(function (r) {
      if (!r) return;
      if (on) r.setAttribute('inert', '');
      else r.removeAttribute('inert');
    });
  }

  /* 焦点从 iframe 内容 Tab 出来时，keydown 派发给子文档，父级 trap 收不到；
     用 focusout 兜底：焦点落到弹层外就立即拉回。 */
  modal.addEventListener('focusout', function () {
    if (modal.hidden) return;
    setTimeout(function () {
      if (!modal.hidden && !modal.contains(document.activeElement)) {
        document.getElementById('wb-close').focus();
      }
    }, 0);
  });

  var CAT = {}, FAM = {}, TRIG = { hover: '悬停', scroll: '滚动', click: '点击', view: '进入视口', load: '加载', auto: '自动', drag: '拖拽' };
  var LEVEL = { 1: '基础', 2: '进阶', 3: '复杂' };

  /* ------------------------------------------------------------ 工具 */
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
  function byId(id) {
    return DATA ? DATA.effects.filter(function (e) { return e.id === id; })[0] : null;
  }
  /* demo 文件名固定，加版本号避免浏览器沿用缓存里的旧页面 */
  function demoSrc(e) {
    return e.demo + '?v=' + ((DATA && DATA.demoV) || '1');
  }
  function snippetSrc(e) {
    return 'effects/snippets/' + e.id + '.html?v=1';
  }
  function hasSnippet(e) {
    return !!(e && SNIPPETS && SNIPPETS.has(e.id));
  }
  function load(k, dflt) {
    try { var v = JSON.parse(localStorage.getItem(k)); return v === null ? dflt : v; }
    catch (e) { return dflt; }
  }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  var FAV = new Set(load('uiatlas.fx.fav', []));

  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('on'); }, 1900);
  }

  /* ------------------------------------------------------------ 筛选状态 */
  function restoreUiState() {
    var saved = null;
    try { saved = JSON.parse(sessionStorage.getItem('uiatlas.fx.ui') || 'null'); } catch (e) {}
    if (saved) {
      state.q = saved.q || '';
      state.cat = saved.cat || '';
      state.fav = !!saved.fav;
      window.__fxRestoreY = saved.y || 0;
    }
    try {
      var p = new URLSearchParams(location.search);
      if (p.has('q') || p.has('cat')) {
        var q = (p.get('q') || '').trim(), cat = p.get('cat') || '';
        /* 链接里的筛选优先；和上次不一致时从头看，不沿用旧滚动位置 */
        if (!(saved && q === saved.q && cat === saved.cat)) window.__fxRestoreY = 0;
        state.q = q;
        state.cat = cat;
      }
    } catch (e) {}
  }
  function saveUiState() {
    if (!uiReady) return;
    try {
      sessionStorage.setItem('uiatlas.fx.ui', JSON.stringify({
        q: state.q, cat: state.cat, fav: state.fav, y: window.scrollY
      }));
    } catch (e) {}
  }
  function syncUrl() {
    try {
      var p = new URLSearchParams();
      if (state.q) p.set('q', state.q);
      if (state.cat) p.set('cat', state.cat);
      var qs = p.toString();
      history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + (location.hash || ''));
    } catch (e) {}
  }
  function applyUrlState() {
    var p;
    try { p = new URLSearchParams(location.search); } catch (e) { return; }
    var q = (p.get('q') || '').trim(), cat = p.get('cat') || '';
    if (cat && !CAT[cat]) cat = '';
    if (q === state.q && cat === state.cat) return;
    state.q = q;
    state.cat = cat;
    qInput.value = q;
    render();
  }

  /* ------------------------------------------------------------ 搜索同义词 */
  var SYN = [
    ['磁吸', '吸附', 'magnetic', 'magnet', '按钮'],
    ['光斑', 'spotlight', '聚光', '高光', '卡片'],
    ['倾斜', 'tilt', '3d', '透视', '深度'],
    ['光标', 'cursor', '指针', '跟随'],
    ['预览', 'preview', '悬停', 'hover', '列表'],
    ['入场', 'reveal', '出现', '渐入', 'observer'],
    ['视差', 'parallax', '分层', '纵深', '滚动'],
    ['钉住', 'pin', 'sticky', '横向', 'horizontal'],
    ['擦亮', 'scrub', '高亮', '阅读'],
    ['进度', 'progress', '章节', '阅读'],
    ['数字', 'counter', '计数', '统计'],
    ['逐字', 'split', '上浮', '标题', '字'],
    ['乱码', 'scramble', '解码', '终端', '噪声'],
    ['打字', 'typewriter', '输入', '光标'],
    ['跑马灯', 'marquee', '循环', '字幕'],
    ['翻转', 'swap', '替换', '双语', '导航'],
    ['裁切', 'clip', '揭示', '图片', '颗粒'],
    ['过滤', 'filter', 'flip', '筛选', '网格'],
    ['手风琴', 'accordion', '折叠', '展开', 'faq'],
    ['标签', 'tabs', '下划线', '切换'],
    ['涟漪', 'ripple', '点击', '水波'],
    ['提示', 'toast', '通知', '堆叠', '反馈'],
    ['骨架', 'skeleton', '加载', '占位', 'shimmer'],
    ['点赞', 'like', '粒子', '心形', 'burst'],
    ['渐变', 'mesh', '极光', '光斑', '背景', 'aurora'],
    ['粒子', 'particles', 'canvas', '连线', '星座'],
    ['颗粒', 'grain', '噪点', '胶片', 'noise'],
    ['转场', 'transition', '共享元素', '换页', 'view transition'],
    ['遮罩', 'curtain', '擦除', '色板', '转场'],
    ['抽屉', 'drawer', '底部', '拖拽', 'sheet', '手势'],
    ['点阵', '斥力', 'dots', 'grid', '推开'],
    ['skew', '速度', '扭曲', 'velocity', '惯性'],
    ['堆叠', 'stack', '层叠', 'sticky', '叠'],
    ['荧光', '划线', '高亮', 'highlight', 'mark'],
    ['模糊', '聚焦', 'blur', 'focus', '合焦'],
    ['分段', '胶囊', '滑块', 'segmented', '控件'],
    ['长按', '按住', 'hold', '确认', '误删'],
    ['波浪', '波纹', '等高线', 'waves', '流动'],
    ['展开', 'expand', '详情', '模态', '放大'],
    ['主题', '圆形', 'wipe', '暗色', '扩散'],
    ['放大镜', '缩放', 'zoom', 'lens', '镜片', '细节'],
    ['吸附', 'snap', '分页', '逐屏', '圆点'],
    ['图文', '随行', 'sticky', '长文', '分栏'],
    ['扫光', 'sweep', 'gradient', '彩色', '文字渐变'],
    ['波浪文字', 'wave', 'sin', '呼吸', '逐字'],
    ['拖拽排序', 'drag', 'sort', '重排', '排序'],
    ['顶栏', '导航栏', '收缩', 'header', 'sticky'],
    ['按钮', 'loading', '成功', '对勾', '提交'],
    ['星空', '星星', 'starfield', '穿越', '纵深'],
    ['菜单', '全屏', 'menu', 'overlay', '导航'],
    ['拖尾', '轨迹', 'trail', 'canvas', '余温', '光标'],
    ['缩放', '滚动缩放', 'zoom', 'scale', '镜头', '推进'],
    ['描边', '画线', 'stroke', 'dashoffset', '路径', 'svg'],
    ['里程表', 'odometer', '翻牌', '滚轮', '数字'],
    ['抖动', 'jitter', 'shake', '发抖', '错误', '校验', '表单'],
    ['变形', 'morph', '展开', '搜索框', '伸缩', '输入框'],
    ['自动保存', 'autosave', '保存', '草稿', '防抖'],
    ['流光', '边框', 'conic', '旋转', '渐变'],
    ['汉堡', 'hamburger', '图标变形', '叉'],
    ['拖拽惯性', '甩动', 'inertia', '动量', 'drag'],
    ['填充', '点亮', '逐字', '阅读', 'fill', '滚动文字'],
    ['弧线', 'textpath', '曲线', '路径文字', '排版'],
    ['分栏', 'split', 'separator', 'resize', '对比'],
    ['复制', 'copy', '剪贴板', 'clipboard', '已复制'],
    ['提示', 'tooltip', '气泡', '延迟', '悬停说明'],
    ['透视', '网格', 'grid', 'synthwave', '纵深', 'perspective'],
    ['路由', 'route', '进度条', '加载', '导航'],
    ['旋钮', 'knob', '角度', 'atan2', '旋转调节'],
    ['序列', '帧', 'sequence', 'frames', '交叉淡化', '逐帧'],
    ['轮换', 'rotate', '关键词', '词', 'hero'],
    ['故障', 'glitch', '切片', 'rgb', '扫描线'],
    ['瀑布流', 'masonry', '多列', '重排'],
    ['侧栏', 'rail', 'sidebar', '折叠导航', '收轨'],
    ['角标', 'badge', '徽标', '未读', '通知数字'],
    ['下拉刷新', 'pull', 'refresh', '手势刷新', '下拉'],
    ['字符雨', 'matrix', '数字雨', '代码雨'],
    ['翻卡', 'flip', '3d', '正反面', '卡片翻转'],
    ['擦洗', 'scrub', '胶片', '逐帧', '时间线'],
    ['唱片', 'rotate', '齿轮', '角度', '表盘'],
    ['斥力', 'repel', '推开', '文字散开'],
    ['下划线', 'underline', '链接线', '展开线'],
    ['横滑', 'drag', 'gallery', '拖拽画廊', 'swipe'],
    ['底部导航', 'tabbar', '底栏', '手机导航'],
    ['撤销', 'undo', '删除', '恢复', '撤回'],
    ['纸屑', 'confetti', '撒花', '庆祝', '礼花'],
    ['熔岩', 'lava', 'gooey', '液态', 'blob', '黏'],
    ['推入', 'push', '详情页', '返回', '层级'],
    ['Dock', '邻近', '放大图标', 'macos', '图标'],
    ['图片平移', 'pan', '视差', '镜头', '图片'],
    ['色相', 'hue', '换色', '背景色', '滚动换色'],
    ['探照灯', 'spotlight', '遮罩文字', '手电筒', '文字遮罩'],
    ['表格', 'table', '展开行', '行详情', 'colspan'],
    ['步骤', 'stepper', '向导', '多步', '步骤进度'],
    ['对勾', 'check', '勾选', '完成', '成功'],
    ['音频', '波形', 'audio', 'wave', '播放', '声音'],
    ['体积光', 'rays', '光束', '舞台光'],
    ['错峰', 'stagger', '入场', '延迟', '逐个']
  ];
  function aliases(term) {
    var out = [term];
    SYN.forEach(function (g) {
      for (var i = 0; i < g.length; i++) {
        if (g[i] === term || g[i].indexOf(term) >= 0 || term.indexOf(g[i]) >= 0) { out = out.concat(g); return; }
      }
    });
    return out;
  }

  function index() {
    DATA.cats.forEach(function (c) { CAT[c.id] = c.name; });
    (DATA.families || []).forEach(function (f) { FAM[f.id] = f; });
    DATA.effects.forEach(function (e) {
      var fam = FAM[e.family] || {};
      e._cat = CAT[e.cat] || e.cat;
      e._trig = TRIG[e.trigger] || e.trigger;
      e._family = fam.name || e.family || '';
      e._famNote = fam.note || '';
      e._hay = [e.id, e.name, e.name_en, e._cat, e._trig, LEVEL[e.level],
                e.family || '', e._family, e._famNote,
                (e.tech || []).join(' '), (e.features || []).join(' '),
                e.how || '', e.watch || '', (e.tags || []).join(' ')].join(' ').toLowerCase();
    });
  }

  function match(e) {
    if (state.cat && e.cat !== state.cat) return false;
    if (state.fav && !FAV.has(e.id)) return false;
    if (!state.q) return true;
    var terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    return terms.every(function (t) {
      return aliases(t).some(function (a) { return e._hay.indexOf(a.toLowerCase()) >= 0; });
    });
  }

  /* 别名会放大命中面，原顺序下精确名会被挤到十几位之后 */
  function score(e) {
    var q = state.q.toLowerCase().trim();
    if (!q) return 0;
    var name = e.name.toLowerCase(), en = (e.name_en || '').toLowerCase(), id = e.id.toLowerCase();
    if (name === q || en === q || id === q) return 0;
    var terms = q.split(/\s+/).filter(Boolean);
    function allIn(s) { return terms.every(function (t) { return s.indexOf(t) >= 0; }); }
    if (allIn(name) || allIn(en)) return 1;
    if (name.indexOf(q) >= 0 || en.indexOf(q) >= 0) return 2;
    if (e._hay.indexOf(q) >= 0) return 3;
    return 4;
  }

  /* ------------------------------------------------------------ 预览挂载 */
  function fitShot(shot) {
    var f = shot.querySelector('iframe');
    if (!f) return;
    var w = shot.clientWidth, h = shot.clientHeight;
    if (w < 40 || h < 40) return;
    var s = .72;
    f.style.width = (w / s) + 'px';
    f.style.height = (h / s) + 'px';
    f.style.transform = 'scale(' + s + ')';
  }
  function mount(shot) {
    var f = shot.querySelector('iframe');
    if (!f || f.dataset.mounted) return;
    f.dataset.mounted = '1';
    fitShot(shot);
    f.src = f.dataset.src;
    /* 最多保留 24 个预览，超出的先卸载最久的一个 */
    mountedShots = mountedShots.filter(function (s) { return s !== shot; });
    mountedShots.push(shot);
    while (mountedShots.length > 24) {
      var old = mountedShots.shift();
      if (old && old !== shot && old.__unmount) old.__unmount();
    }
    if (shot.__fail) shot.__fail();
  }

  function unmount(shot) {
    var f = shot.querySelector('iframe');
    if (!f || !f.dataset.mounted) return;
    if (shot.__unmount) shot.__unmount();
  }
  function tidy(f) {
    try {
      var d = f.contentDocument;
      if (!d || d.getElementById('fx-no-scroll')) return;
      var s = d.createElement('style');
      s.id = 'fx-no-scroll';
      s.textContent = '::-webkit-scrollbar{width:0;height:0}html{scrollbar-width:none}';
      (d.head || d.documentElement).appendChild(s);
    } catch (e) {}
  }

  /* ------------------------------------------------------------ 源码读取 */
  function fetchSource(e) {
    if (cache[e.id]) return Promise.resolve(cache[e.id]);
    return fetch(demoSrc(e)).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.text();
    }).then(function (t) { cache[e.id] = t; return t; });
  }
  function fetchSnippet(e) {
    if (snippetCache[e.id]) return Promise.resolve(snippetCache[e.id]);
    return fetch(snippetSrc(e)).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.text();
    }).then(function (t) {
      snippetCache[e.id] = t;
      return t;
    });
  }
  function slices(src, snippet) {
    var css = (src.match(/<style>([\s\S]*?)<\/style>/i) || [])[1] || '';
    var js = (src.match(/<script>([\s\S]*?)<\/script>/i) || [])[1] || '';
    return { all: src, css: css.trim(), js: js.trim(), snippet: (snippet || '').trim() };
  }

  /* 卡片「⋯」更多菜单：单个共享浮层，挂到 body 上避免被 .fx-card 的 overflow:hidden 裁掉 */
  function ensureMoreMenu() {
    if (moreMenu) return moreMenu;
    var item = function (tag, act, text) {
      var attrs = { class: 'fx-more-item', 'data-act': act, text: text };
      if (tag === 'a') { attrs.href = '#'; attrs.target = '_blank'; attrs.rel = 'noopener'; }
      else attrs.type = 'button';
      return el(tag, attrs);
    };
    moreMenu = el('div', { class: 'fx-more-menu', role: 'menu', hidden: '' }, [
      item('a', 'raw', '原页 ↗'),
      item('button', 'replay', '重播预览'),
      item('button', 'css', '复制 CSS'),
      item('button', 'dl', '下载 .html')
    ]);
    document.body.appendChild(moreMenu);

    moreMenu.addEventListener('click', function (ev) {
      var it = ev.target.closest ? ev.target.closest('.fx-more-item') : null;
      if (!it || !moreOwner) return;
      var e = moreOwner.e, shot = moreOwner.shot, act = it.getAttribute('data-act');
      if (act === 'raw') {
        it.href = demoSrc(e);
        closeMoreMenu();
        return;
      }
      closeMoreMenu();
      if (act === 'replay') replayShot(shot, null);
      else if (act === 'css') copyCss(e, null);
      else if (act === 'dl') downloadCard(e, null);
    });
    return moreMenu;
  }

  function closeMoreMenu() {
    if (moreMenu) moreMenu.hidden = true;
    if (moreTrigger) moreTrigger.setAttribute('aria-expanded', 'false');
    moreTrigger = null;
    moreOwner = null;
  }

  function openMoreMenu(btn, e, shot) {
    ensureMoreMenu();
    var wasOpen = !moreMenu.hidden && moreTrigger === btn;
    closeMoreMenu();
    if (wasOpen) return;
    moreOwner = { e: e, shot: shot };
    moreTrigger = btn;
    btn.setAttribute('aria-expanded', 'true');
    var raw = moreMenu.querySelector('[data-act="raw"]');
    raw.href = demoSrc(e);
    moreMenu.hidden = false;

    var r = btn.getBoundingClientRect();
    var menuW = moreMenu.offsetWidth, menuH = moreMenu.offsetHeight;
    var left = Math.min(r.right - menuW, innerWidth - menuW - 8);
    if (left < 8) left = 8;
    var top = r.bottom + 6;
    if (top + menuH > innerHeight - 8) top = r.top - menuH - 6;
    if (top < 8) top = 8;
    moreMenu.style.left = left + 'px';
    moreMenu.style.top = top + 'px';
  }

  document.addEventListener('click', function (ev) {
    if (!moreMenu || moreMenu.hidden) return;
    if (moreMenu.contains(ev.target) || (moreTrigger && moreTrigger.contains(ev.target))) return;
    closeMoreMenu();
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && moreMenu && !moreMenu.hidden) {
      var t = moreTrigger;
      closeMoreMenu();
      if (t) t.focus();
    }
  });
  addEventListener('scroll', function () { if (moreMenu && !moreMenu.hidden) closeMoreMenu(); }, true);
  addEventListener('resize', closeMoreMenu);

  function withSource(e, btn, fn) {
    var old = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = '读取…'; }
    fetchSource(e).then(function (src) {
      if (btn) { btn.disabled = false; btn.textContent = old; }
      fn(src);
    }).catch(function (err) {
      if (btn) { btn.disabled = false; btn.textContent = old; }
      toast('读不到源码：' + err.message + '（请用 serve.py 打开本站）');
    });
  }

  function writeClipboard(text, done) {
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
  function copy(text, btn) {
    writeClipboard(text, function () {
      if (!btn) return;
      var old = btn.textContent;
      btn.textContent = '已复制 ✓';
      setTimeout(function () { btn.textContent = old; }, 1200);
    });
  }
  function saveFile(e, src) {
    var blob = new Blob([src], { type: 'text/html;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = e.id + '.html';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    toast('已下载 ' + e.id + '.html');
  }
  function copyCss(e, btn) {
    withSource(e, btn, function (src) {
      var css = slices(src).css;
      if (!css) { toast('这条效果没有独立 CSS'); return; }
      writeClipboard(css, function () { toast('已复制《' + e.name + '》的 CSS'); });
    });
  }
  function downloadCard(e, btn) {
    withSource(e, btn, function (src) { saveFile(e, src); });
  }
  function replayShot(shot, btn) {
    var f = shot.querySelector('iframe');
    if (!f) return;
    if (f.dataset.mounted !== '1') { mount(shot); toast('已加载预览'); return; }
    shot.classList.remove('ready');
    f.src = f.dataset.src + '&r=' + Date.now();
    if (shot.__fail) shot.__fail();
    if (btn) {
      btn.classList.add('on');
      setTimeout(function () { btn.classList.remove('on'); }, 700);
    }
    toast('已重播');
  }

  /* ------------------------------------------------------------ 卡片 */
  function card(e) {
    var failTimer = null;

    function fail(shot) {
      if (f.dataset.mounted !== '1' || shot.classList.contains('ready') || shot.classList.contains('failed')) return;
      shot.classList.add('failed');
      var box = shot.querySelector('.fx-loading');
      if (!box || box.dataset.failed) return;
      box.dataset.failed = '1';
      box.textContent = '';
      box.appendChild(el('span', { text: '预览加载失败' }));
      box.appendChild(el('small', { text: '可能刚从 file:// 打开，或网络较慢。' }));
      var retry = el('button', { type: 'button', text: '重试' });
      retry.addEventListener('click', function (ev) {
        ev.stopPropagation();
        shot.classList.remove('failed');
        delete box.dataset.failed;
        box.textContent = '';
        box.appendChild(document.createTextNode('加载预览…'));
        f.dataset.mounted = '';
        mount(shot);
      });
      box.appendChild(retry);
    }

    var f = el('iframe', { 'data-src': demoSrc(e), title: e.name + ' 交互预览', loading: 'lazy' });
    f.addEventListener('load', function () {
      if (!f.dataset.mounted) return;
      clearTimeout(failTimer);
      /* 404 也会触发 load：同源时检查文档标题，识别错误页 */
      try {
        var d = f.contentDocument;
        if (d && /^error/i.test(d.title || '')) { fail(shot); return; }
      } catch (err) {}
      shot.classList.add('ready');
      shot.classList.remove('failed');
      tidy(f);
    });

    var shot = el('div', { class: 'fx-shot' }, [
      el('span', { class: 'fx-loading', text: '加载预览…' }),
      f
    ]);

    shot.__fail = function () { failTimer = setTimeout(function () { fail(shot); }, 8000); };

    shot.__unmount = function () {
      clearTimeout(failTimer);
      f.dataset.mounted = '';
      shot.classList.remove('ready', 'failed');
      f.src = 'about:blank';
      mountedShots = mountedShots.filter(function (s) { return s !== shot; });
      var box = shot.querySelector('.fx-loading');
      if (box) { delete box.dataset.failed; box.textContent = '加载预览…'; }
      if (io) io.observe(shot);
    };

    var star = el('button', {
      class: 'star', type: 'button', title: '收藏',
      'aria-label': '收藏《' + e.name + '》',
      'aria-pressed': FAV.has(e.id) ? 'true' : 'false',
      text: FAV.has(e.id) ? '★' : '☆'
    });
    star.addEventListener('click', function () {
      if (FAV.has(e.id)) FAV.delete(e.id); else FAV.add(e.id);
      save('uiatlas.fx.fav', Array.from(FAV));
      star.textContent = FAV.has(e.id) ? '★' : '☆';
      star.setAttribute('aria-pressed', FAV.has(e.id) ? 'true' : 'false');
      document.getElementById('n-fav').textContent = FAV.size;
      if (state.fav) render();
    });

    var dots = el('span', { class: 'fx-level', title: '实现难度：' + LEVEL[e.level] });
    for (var i = 1; i <= 3; i++) dots.appendChild(el('i', { class: i <= e.level ? 'on' : '' }));
    dots.appendChild(el('em', { text: LEVEL[e.level] }));

    var previewBtn = el('button', {
      class: 'fx-preview-btn', type: 'button', text: '看效果 →',
      title: '打开工作台：交互预览 + 源码 + 说明',
      'aria-label': '查看《' + e.name + '》的效果与源码'
    });
    previewBtn.addEventListener('click', function () { openFx(e.id, 'preview'); });

    var more = el('button', {
      class: 'fx-more-btn', type: 'button', text: '⋯',
      title: '更多：原页 / 重播 / 复制 CSS / 下载',
      'aria-label': '《' + e.name + '》的更多操作',
      'aria-haspopup': 'menu', 'aria-expanded': 'false'
    });
    more.addEventListener('click', function () { openMoreMenu(more, e, shot); });

    return el('article', { class: 'fx-card', 'data-id': e.id }, [
      shot,
      el('div', { class: 'fx-body' }, [
        el('div', { class: 'fx-title' }, [el('b', { text: e.name }), el('span', { text: e.name_en })]),
        el('p', { class: 'fx-how', text: e.features[0] }),
        el('div', { class: 'fx-meta' }, [
          e._cat ? el('i', { class: 'cat', text: e._cat }) : null,
          el('i', { class: 'trig', text: e._trig }),
          e._family ? el('i', { class: 'fam', title: '机制：' + e._family + (e._famNote ? ' · ' + e._famNote : ''), text: e._family }) : null,
          el('i', { text: (e.tech || [])[0] || 'CSS' }),
          e.depth && e.depth.cost ? el('i', { class: 'cost', 'data-tier': e.depth.cost.tier, text: '成本 ' + e.depth.cost.tier }) : null,
          e.level >= 3 ? el('i', { text: '慎用' }) : null
        ]),
        el('div', { class: 'fx-foot' }, [
          el('span', {}, [star]),
          dots,
          el('span', { class: 'spacer' }),
          el('span', { class: 'fx-acts' }, [previewBtn, more])
        ])
      ])
    ]);
  }

  function emptyBlock() {
    var box = el('div', { class: 'empty' }, [
      el('h2', { text: '没有匹配的效果' }),
      el('p', { text: '换个更短的关键词，或点下面的类别重新开始。' })
    ]);
    var picks = DATA.effects.filter(function (e) {
      return (!state.cat || e.cat === state.cat) ? true : false;
    }).slice(0, 3);
    if (!picks.length) picks = DATA.effects.slice(0, 3);
    var row = el('div', { class: 'sug' }, [el('span', { text: '可以先看：', style: 'align-self:center;font-size:13px' })]);
    picks.forEach(function (e) {
      var b = el('button', { type: 'button', text: e.name + ' · ' + e._cat });
      b.addEventListener('click', function () {
        state.q = ''; state.cat = ''; state.fav = false;
        qInput.value = '';
        render();
      });
      row.appendChild(b);
    });
    box.appendChild(row);
    return box;
  }

  function render() {
    grid.textContent = '';
    if (io) io.disconnect();
    if (ioAway) ioAway.disconnect();
    mountedShots = [];
    document.querySelectorAll('.fx-cats .chip').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-cat') === state.cat ? 'true' : 'false');
    });
    document.getElementById('fav-only').setAttribute('aria-pressed', state.fav ? 'true' : 'false');
    document.getElementById('n-fav').textContent = FAV.size;

    var list = DATA.effects.filter(match);
    if (state.q) {
      list = list.slice().sort(function (a, b) { return score(a) - score(b); });
      /* 输入完整标题时只留精确命中，避免别名把结果扩成几十条 */
      var exact = list.filter(function (e) { return score(e) === 0; });
      if (exact.length) list = exact;
    }
    document.getElementById('count-info').textContent = list.length + ' / ' + DATA.total + ' 个';
    if (!list.length) {
      grid.appendChild(emptyBlock());
      syncUrl();
      saveUiState();
      return;
    }

    list.forEach(function (e) {
      var c = card(e);
      grid.appendChild(c);
      var shot = c.querySelector('.fx-shot');
      if (io) io.observe(shot); else mount(shot);
      if (ioAway) ioAway.observe(shot);
    });

    syncUrl();
    saveUiState();
  }

  /* ------------------------------------------------------------ 工作台 */
  function fitStage() {
    if (!wbStage || modal.hidden) return;
    var w = wbStage.clientWidth, h = wbStage.clientHeight;
    if (w < 40 || h < 40) return;
    var s = Math.min((w - 24) / 600, (h - 24) / 450);
    s = Math.max(.2, s);
    wbFrame.style.transform = 'translate(-50%,-50%) scale(' + s.toFixed(4) + ')';
  }

  function openEntry() {
    return openId ? byId(openId) : null;
  }
  function currentSnippet() {
    var e = openEntry();
    return e ? (snippetCache[e.id] || '') : '';
  }
  function currentText() {
    if (!curSrc) return '';
    var s = slices(curSrc, currentSnippet());
    return (s[curTab] || '').trim();
  }
  function resetTabs(e) {
    var snip = document.querySelector('.code-tabs button[data-tab="snippet"]');
    if (snip) snip.removeAttribute('title');
    document.querySelectorAll('.code-tabs button').forEach(function (b) {
      var t = b.dataset.tab;
      b.hidden = t === 'snippet' && !hasSnippet(e);
      b.disabled = t === 'snippet' ? !hasSnippet(e) : false;
      b.setAttribute('aria-selected', t === 'all' ? 'true' : 'false');
    });
    document.getElementById('wb-copy').disabled = true;
  }
  function paintTab() {
    var s = slices(curSrc, currentSnippet());
    var txt = s[curTab] || '';
    var code = document.getElementById('wb-code');
    if (curTab === 'snippet' && !s.snippet) {
      code.textContent = '正在读取最小用法…';
      document.getElementById('wb-lines').textContent = '';
      document.getElementById('wb-copy').disabled = true;
    } else {
      code.textContent = txt.trim();
      var lines = txt.trim() ? txt.trim().split('\n').length : 0;
      document.getElementById('wb-lines').textContent =
        lines + ' 行 · ' + (txt.length / 1024).toFixed(1) + ' KB' + (curTab === 'snippet' ? ' · 最小用法' : ' · 单文件');
      document.getElementById('wb-copy').disabled = !txt.trim();
    }
    document.querySelectorAll('.code-tabs button').forEach(function (b) {
      b.setAttribute('aria-selected', b.dataset.tab === curTab ? 'true' : 'false');
    });
  }
  function setTab(name) {
    var e = openEntry();
    if (!curSrc || !e) return;
    var s = slices(curSrc, currentSnippet());
    var ok = name === 'all' ? true : name === 'snippet' ? hasSnippet(e) : !!s[name];
    if (!ok) name = 'all';
    curTab = name;
    document.querySelectorAll('.code-tabs button').forEach(function (b) {
      var t = b.dataset.tab;
      b.hidden = t === 'snippet' && !hasSnippet(e);
      b.disabled = t === 'snippet' ? !hasSnippet(e) : !s[t];
    });
    paintTab();
  }

  function renderNotes(e) {
    document.getElementById('wb-title').textContent = e.name;
    document.getElementById('wb-sub').textContent =
      e.name_en + ' · ' + e._cat + ' · ' + e._trig + (e._family ? ' · ' + e._family : '');
    document.getElementById('wb-open').href = demoSrc(e);
    document.getElementById('wb-how').textContent = e.how;
    document.getElementById('wb-watch').textContent = e.watch;

    var d = e.depth || {};
    var anatomy = document.getElementById('wb-anatomy');
    anatomy.textContent = '';
    (d.anatomy || []).forEach(function (t) { anatomy.appendChild(el('li', { text: t })); });

    var params = document.getElementById('wb-params');
    params.textContent = '';
    (d.params || []).forEach(function (p) {
      params.appendChild(el('dt', { text: p[0] }));
      params.appendChild(el('dd', { text: p[1] }));
    });

    var variants = document.getElementById('wb-variants');
    variants.textContent = '';
    (d.variants || []).forEach(function (v) {
      variants.appendChild(el('li', {}, [el('b', { text: v[0] }), el('span', { text: v[1] })]));
    });

    var sameWrap = document.getElementById('wb-same-wrap');
    var sameBtn = document.getElementById('wb-same-open');
    var base = e.variant_of ? byId(e.variant_of) : null;
    if (base) {
      document.getElementById('wb-same').textContent =
        '与《' + base.name + '》同属「' + e._family + '」，共用同一套内核；本条只换了载体、触发方式或参数。';
      sameBtn.textContent = '打开《' + base.name + '》→';
      sameBtn.onclick = function () { openFx(base.id, 'code'); };
      sameWrap.hidden = false;
    } else {
      sameWrap.hidden = true;
    }

    var cost = d.cost || {};
    var tier = document.getElementById('wb-cost-tier');
    tier.textContent = cost.tier || '—';
    tier.setAttribute('data-tier', cost.tier || '');
    document.getElementById('wb-cost-note').textContent = cost.note || '';
    document.getElementById('wb-avoid').textContent = d.avoid || '';

    var ul = document.getElementById('wb-features');
    ul.textContent = '';
    e.features.forEach(function (f) { ul.appendChild(el('li', { text: f })); });
    var tags = document.getElementById('wb-tech');
    tags.textContent = '';
    (e.tech || []).forEach(function (t) { tags.appendChild(el('span', { text: t })); });
  }

  function openFx(id, entry, push) {
    var e = byId(id);
    if (!e) return;
    if (!openId) {
      lastFocus = document.activeElement;
      /* hash 直达时 activeElement 是 body，关闭后应回到该卡片 */
      if (!lastFocus || lastFocus === document.body) {
        var c = grid.querySelector('.fx-card[data-id="' + id + '"]');
        lastFocus = c ? c.querySelector('.fx-preview-btn') : null;
      }
    }
    openId = id;
    curSrc = '';
    curTab = 'all';

    modal.hidden = false;
    document.body.classList.add('fx-lock');
    lockScroll(true);
    setPageInert(true);
    wbBox.classList.remove('notes-on');
    notesBtn.setAttribute('aria-expanded', 'false');

    renderNotes(e);
    resetTabs(e);

    wbStage.classList.remove('ready');
    wbLoading.textContent = '加载预览…';
    wbFrame.title = '效果预览：' + e.name;
    wbFrame.src = demoSrc(e);

    document.getElementById('wb-code').textContent = '载入源码…';
    document.getElementById('wb-lines').textContent = '';
    document.getElementById('wb-copy').disabled = true;

    fetchSource(e).then(function (src) {
      if (openId !== id) return;
      curSrc = src;
      setTab('all');
    }).catch(function (err) {
      if (openId !== id) return;
      document.getElementById('wb-code').textContent =
        '读不到源码（' + err.message + '）。\n请用 serve.py 打开本站，file:// 会被浏览器拦截 fetch。';
    });

    if (hasSnippet(e)) {
      fetchSnippet(e).then(function () {
        if (openId !== id) return;
        var b = document.querySelector('.code-tabs button[data-tab="snippet"]');
        if (b) { b.hidden = false; b.disabled = false; }
        if (curTab === 'snippet') paintTab();
      }).catch(function () {
        if (openId !== id) return;
        var b = document.querySelector('.code-tabs button[data-tab="snippet"]');
        if (b) { b.disabled = true; b.title = '最小用法读取失败'; }
        if (curTab === 'snippet') { curTab = 'all'; paintTab(); }
        toast('最小用法读取失败');
      });
    }

    if (push !== false) {
      history.pushState({ fx: id }, '', (entry === 'preview' ? '#z=' : '#') + encodeURIComponent(id));
    }
    requestAnimationFrame(fitStage);
    setTimeout(fitStage, 80);
    setTimeout(function () { document.getElementById('wb-close').focus(); }, 30);
  }

  function closeFx(cleanHash) {
    if (!openId) return;
    var id = openId;
    openId = null;
    modal.hidden = true;
    wbBox.classList.remove('notes-on');
    notesBtn.setAttribute('aria-expanded', 'false');
    wbFrame.src = 'about:blank';
    wbStage.classList.remove('ready');
    document.body.classList.remove('fx-lock');
    lockScroll(false);
    setPageInert(false);
    if (cleanHash !== false) {
      var h = decodeURIComponent(location.hash.slice(1));
      if (h === id || h === 'z=' + id) {
        history.replaceState(null, '', location.pathname + location.search);
      }
    }
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    lastFocus = null;
  }

  function replayWorkbench() {
    var e = openEntry();
    if (!e) return;
    wbStage.classList.remove('ready');
    wbLoading.textContent = '重新加载…';
    wbFrame.src = demoSrc(e) + '&r=' + Date.now();
    var b = document.getElementById('wb-replay');
    b.classList.add('on');
    setTimeout(function () { b.classList.remove('on'); }, 700);
    toast('已重播');
  }

  function downloadWorkbench() {
    var e = openEntry();
    if (!e) return;
    if (curSrc) { saveFile(e, curSrc); return; }
    withSource(e, document.getElementById('wb-download'), function (src) { saveFile(e, src); });
  }

  /* ------------------------------------------------------------ 交互绑定 */
  var qt = null;
  qInput.addEventListener('input', function () {
    clearTimeout(qt);
    qt = setTimeout(function () {
      state.q = qInput.value.trim();
      render();
    }, 120);
  });
  qInput.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      qInput.value = '';
      state.q = '';
      render();
    }
  });

  document.getElementById('random').addEventListener('click', function () {
    var e = DATA.effects[Math.floor(Math.random() * DATA.effects.length)];
    state.q = ''; state.cat = ''; state.fav = false;
    qInput.value = '';
    render();
    var c = grid.querySelector('.fx-card[data-id="' + e.id + '"]');
    if (!c) return;
    c.scrollIntoView({ block: 'center', behavior: 'smooth' });
    mount(c.querySelector('.fx-shot'));
    c.classList.add('flash');
    setTimeout(function () { c.classList.remove('flash'); }, 1400);
  });

  document.getElementById('fav-only').addEventListener('click', function () {
    state.fav = !state.fav;
    render();
  });

  document.querySelectorAll('.code-tabs button').forEach(function (b) {
    b.addEventListener('click', function () {
      if (curSrc && !b.disabled) setTab(b.dataset.tab);
    });
  });
  document.getElementById('wb-close').addEventListener('click', function () { closeFx(); });
  notesBtn.addEventListener('click', function () {
    var on = wbBox.classList.toggle('notes-on');
    notesBtn.setAttribute('aria-expanded', on ? 'true' : 'false');
  });
  document.getElementById('wb-replay').addEventListener('click', replayWorkbench);
  document.getElementById('wb-download').addEventListener('click', downloadWorkbench);
  document.getElementById('wb-copy').addEventListener('click', function () {
    var txt = currentText();
    if (txt) copy(txt, this);
  });
  modal.addEventListener('click', function (e) { if (e.target === modal) closeFx(); });

  wbFrame.addEventListener('load', function () {
    if (!openId) return;
    try {
      var d = wbFrame.contentDocument;
      if (d && /^error/i.test(d.title || '')) { wbLoading.textContent = '预览加载失败'; return; }
    } catch (e) {}
    wbStage.classList.add('ready');
    tidy(wbFrame);
    fitStage();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.hidden) {
      if (wbBox.classList.contains('notes-on')) {
        wbBox.classList.remove('notes-on');
        notesBtn.setAttribute('aria-expanded', 'false');
        return;
      }
      closeFx();
      return;
    }
    if (e.key === '/' && document.activeElement !== qInput && (modal.hidden || !modal.contains(document.activeElement))) {
      e.preventDefault(); qInput.focus();
    }
    if (e.key === 'Tab' && !modal.hidden) {
      var f = Array.prototype.filter.call(
        modal.querySelectorAll('a[href],button:not([disabled]),iframe,[tabindex]:not([tabindex="-1"])'),
        function (n) { return n.offsetParent !== null; }
      );
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (!modal.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
      else if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  function hashTarget() {
    var h = decodeURIComponent(location.hash.slice(1));
    if (h.slice(0, 2) === 'z=') return { zoom: h.slice(2) };
    return { code: h };
  }

  addEventListener('popstate', function () {
    applyUrlState();
    var t = hashTarget();
    if (t.zoom && byId(t.zoom)) { openFx(t.zoom, 'preview', false); return; }
    if (t.code && byId(t.code)) { openFx(t.code, 'code', false); return; }
    closeFx(false);
  });

  addEventListener('resize', function () {
    clearTimeout(window.__fxr);
    window.__fxr = setTimeout(function () {
      document.querySelectorAll('.fx-shot').forEach(function (s) {
        if (s.classList.contains('ready')) fitShot(s);
      });
      if (!modal.hidden) fitStage();
    }, 160);
  });

  addEventListener('scroll', function () {
    clearTimeout(window.__fxs);
    window.__fxs = setTimeout(saveUiState, 250);
  }, { passive: true });

  /* ------------------------------------------------------------ 启动 */
  Promise.all([
    fetch('effects.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }),
    fetch('effects-snippets.json?v=1').then(function (r) {
      return r.ok ? r.json() : { ids: [] };
    }).catch(function () { return { ids: [] }; })
  ]).then(function (res) {
    DATA = res[0];
    SNIPPETS = new Set((res[1] && res[1].ids) || []);
    index();

    restoreUiState();
    if (state.cat && !CAT[state.cat]) state.cat = '';
    qInput.value = state.q;

    var counts = {};
    DATA.effects.forEach(function (e) { counts[e.cat] = (counts[e.cat] || 0) + 1; });

    var cats = document.getElementById('cats');
    cats.appendChild(el('button', { class: 'chip', type: 'button', 'data-cat': '', 'aria-pressed': state.cat ? 'false' : 'true' },
      [document.createTextNode('全部'), el('small', { text: DATA.total })]));
    DATA.cats.forEach(function (c) {
      var b = el('button', { class: 'chip', type: 'button', 'data-cat': c.id, 'aria-pressed': state.cat === c.id ? 'true' : 'false' },
        [document.createTextNode(c.name), el('small', { text: counts[c.id] || 0 })]);
      b.addEventListener('click', function () {
        state.cat = state.cat === c.id ? '' : c.id;
        render();
      });
      cats.appendChild(b);
    });
    cats.querySelector('.chip[data-cat=""]').addEventListener('click', function () {
      state.cat = ''; render();
    });

    document.getElementById('n-sub').textContent = DATA.total;
    document.getElementById('n-fav').textContent = FAV.size;

    if ('IntersectionObserver' in window) {
      io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          mount(en.target);
          io.unobserve(en.target);
        });
      }, { rootMargin: '500px 0px' });
      /* 离视口太远的预览主动卸载，滚回来会重新挂载 */
      ioAway = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (!en.isIntersecting) unmount(en.target); });
      }, { rootMargin: '1400px 0px' });
    }

    render();
    if (window.__fxRestoreY) window.scrollTo(0, window.__fxRestoreY);
    uiReady = true;

    var t = hashTarget();
    if (t.zoom && byId(t.zoom)) openFx(t.zoom, 'preview', false);
    else if (t.code && byId(t.code)) openFx(t.code, 'code', false);
    else if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  }).catch(function (err) {
    grid.appendChild(el('div', { class: 'empty' }, [
      el('h2', { text: '读不到 effects.json（' + err.message + '）' }),
      el('p', { text: '用 file:// 直接打开时浏览器会拦截 fetch；请运行 serve.py 或 启动预览.bat。' })
    ]));
  });
})();
