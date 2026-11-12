/* UI Atlas · 动效图鉴：读 effects.json 渲染画廊 / 源码弹层。
   与 app.js 同一套约定：无依赖、无构建，hash 直达某个效果。 */
(function () {
  'use strict';

  var DATA = null,
      grid = document.getElementById('fx-grid'),
      modal = document.getElementById('codeModal'),
      state = { q: '', cat: '', fav: false },
      openId = null,
      lastFocus = null,
      curSrc = '',
      curTab = 'all',
      cache = {},
      io = null,
      ioAway = null,
      mountedShots = [],
      notesBtn = document.getElementById('cm-notes'),
      codeBox = document.querySelector('.fx-code-box'),
      zoomModal = document.getElementById('zoomModal'),
      zoomFrame = document.getElementById('zm-frame'),
      zoomStage = document.getElementById('zm-stage'),
      zoomOpenId = null,
      zoomLastFocus = null;

  var zoomRegions = [
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

  function setZoomInert(on) {
    zoomRegions.forEach(function (r) {
      if (!r) return;
      if (on) r.setAttribute('inert', '');
      else r.removeAttribute('inert');
    });
  }

  /* 焦点从 iframe 内容 Tab 出来时，keydown 派发给子文档，父级 trap 收不到；
     用 focusout 兜底：焦点落到弹层外就立即拉回。 */
  zoomModal.addEventListener('focusout', function () {
    if (zoomModal.hidden) return;
    setTimeout(function () {
      if (!zoomModal.hidden && !zoomModal.contains(document.activeElement)) {
        document.getElementById('zm-open').focus();
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
  /* 「原页」统一走 view.html：默认全宽打开真实页面，页内可切 600 × 450 画板对照 */
  function viewHref(id) {
    return 'view.html?id=' + encodeURIComponent(id);
  }
  /* demo 文件名固定，加版本号避免浏览器沿用缓存里的旧页面 */
  function demoSrc(e) {
    return e.demo + '?v=' + ((DATA && DATA.demoV) || '1');
  }
  function load(k, dflt) {
    try { var v = JSON.parse(localStorage.getItem(k)); return v === null ? dflt : v; }
    catch (e) { return dflt; }
  }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  var FAV = new Set(load('uiatlas.fx.fav', []));

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
      f,
      el('span', { class: 'fx-badge' }, [el('i'), document.createTextNode(e._cat)])
    ]);

    var act = el('div', { class: 'fx-act' }, [
      el('a', { href: viewHref(e.id), target: '_blank', rel: 'noopener', text: '原页' })
    ]);
    shot.appendChild(act);

    var zoomBtn = el('button', {
      class: 'fx-zoom-btn', type: 'button', text: '放大',
      title: '等比例放大预览', 'aria-label': '放大《' + e.name + '》'
    });
    zoomBtn.addEventListener('click', function (ev) { ev.stopPropagation(); openZoom(e.id); });
    shot.appendChild(zoomBtn);

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

    var more = el('button', { class: 'linkish', type: 'button', text: '看代码 →' });
    more.addEventListener('click', function () { openCode(e.id); });

    return el('article', { class: 'fx-card', 'data-id': e.id }, [
      shot,
      el('div', { class: 'fx-body' }, [
        el('div', { class: 'fx-title' }, [el('b', { text: e.name }), el('span', { text: e.name_en })]),
        el('p', { class: 'fx-how', text: e.features[0] }),
        el('div', { class: 'fx-meta' }, [
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
          more
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
        document.getElementById('q').value = '';
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
    if (!list.length) { grid.appendChild(emptyBlock()); return; }

    list.forEach(function (e) {
      var c = card(e);
      grid.appendChild(c);
      var shot = c.querySelector('.fx-shot');
      if (io) io.observe(shot); else mount(shot);
      if (ioAway) ioAway.observe(shot);
    });
  }

  /* ------------------------------------------------------------ 等比例放大 */
  function fitZoom() {
    if (zoomModal.hidden) return;
    var w = zoomStage.clientWidth, h = zoomStage.clientHeight;
    if (w < 40 || h < 40) return;
    var s = Math.min((w - 28) / 600, (h - 28) / 450);
    s = Math.max(.2, s);
    zoomFrame.style.transform = 'translate(-50%,-50%) scale(' + s.toFixed(4) + ')';
  }

  function openZoom(id, push) {
    var e = byId(id);
    if (!e) return;
    zoomOpenId = id;
    zoomLastFocus = document.activeElement;
    /* hash 直达 / popstate 恢复时 activeElement 是 body，关闭后应回到该卡片而非无处可去 */
    if (!zoomLastFocus || zoomLastFocus === document.body) {
      zoomLastFocus = grid.querySelector('.fx-card[data-id="' + id + '"] .fx-zoom-btn') || null;
    }
    document.getElementById('zm-title').textContent = e.name;
    document.getElementById('zm-sub').textContent = e.name_en + ' · ' + e._cat + ' · 600 × 450 等比放大';
    document.getElementById('zm-open').href = viewHref(e.id);
    zoomFrame.title = '放大预览：' + e.name;
    zoomStage.classList.remove('ready');
    zoomModal.hidden = false;
    document.body.classList.add('fx-lock');
    lockScroll(true);
    setZoomInert(true);
    zoomFrame.src = demoSrc(e);
    fitZoom();
    if (push !== false) history.pushState({ z: id }, '', '#z=' + encodeURIComponent(id));
    setTimeout(function () { document.getElementById('zm-close').focus(); }, 50);
  }

  function closeZoom(cleanHash) {
    if (!zoomOpenId) return;
    var id = zoomOpenId;
    zoomOpenId = null;
    zoomModal.hidden = true;
    zoomStage.classList.remove('ready');
    zoomFrame.src = 'about:blank';
    document.body.classList.remove('fx-lock');
    lockScroll(false);
    setZoomInert(false);
    if (cleanHash !== false && decodeURIComponent(location.hash.slice(1)) === 'z=' + id) {
      history.replaceState(null, '', location.pathname + location.search);
    }
    if (zoomLastFocus && zoomLastFocus.focus) zoomLastFocus.focus();
  }

  /* ------------------------------------------------------------ 源码弹层 */
  function getSource(e) {
    if (cache[e.id]) return Promise.resolve(cache[e.id]);
    return fetch(demoSrc(e)).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.text();
    }).then(function (t) { cache[e.id] = t; return t; });
  }

  function slices(src) {
    var css = (src.match(/<style>([\s\S]*?)<\/style>/i) || [])[1] || '';
    var js = (src.match(/<script>([\s\S]*?)<\/script>/i) || [])[1] || '';
    return { all: src, css: css.trim(), js: js.trim() };
  }

  function currentText() {
    if (!curSrc) return '';
    var s = slices(curSrc);
    return (s[curTab] || '').trim();
  }

  function paintTab() {
    var s = slices(curSrc);
    var txt = s[curTab] || '';
    var code = document.getElementById('cm-code');
    code.textContent = txt.trim();
    document.getElementById('cm-lines').textContent =
      txt.trim().split('\n').length + ' 行 · ' + (s.all.length / 1024).toFixed(1) + ' KB · 单文件';
    document.querySelectorAll('.code-tabs button').forEach(function (b) {
      b.setAttribute('aria-selected', b.dataset.tab === curTab ? 'true' : 'false');
    });
  }

  function setTab(name) {
    curTab = name;
    document.querySelectorAll('.code-tabs button').forEach(function (b) {
      b.disabled = !slices(curSrc)[b.dataset.tab];
    });
    paintTab();
  }

  function openCode(id, push) {
    var e = byId(id);
    if (!e) return;
    lastFocus = document.activeElement;
    openId = id;
    modal.hidden = false;
    document.body.classList.add('fx-lock');
    lockScroll(true);

    document.getElementById('cm-title').textContent = e.name;
    document.getElementById('cm-sub').textContent =
      e.name_en + ' · ' + e._cat + ' · ' + e._trig + (e._family ? ' · ' + e._family : '');
    document.getElementById('cm-how').textContent = e.how;
    document.getElementById('cm-watch').textContent = e.watch;

    var d = e.depth || {};
    var anatomy = document.getElementById('cm-anatomy');
    anatomy.textContent = '';
    (d.anatomy || []).forEach(function (t) { anatomy.appendChild(el('li', { text: t })); });

    var params = document.getElementById('cm-params');
    params.textContent = '';
    (d.params || []).forEach(function (p) {
      params.appendChild(el('dt', { text: p[0] }));
      params.appendChild(el('dd', { text: p[1] }));
    });

    var variants = document.getElementById('cm-variants');
    variants.textContent = '';
    (d.variants || []).forEach(function (v) {
      variants.appendChild(el('li', {}, [el('b', { text: v[0] }), el('span', { text: v[1] })]));
    });

    var sameWrap = document.getElementById('cm-same-wrap');
    var sameBtn = document.getElementById('cm-same-open');
    var base = e.variant_of ? byId(e.variant_of) : null;
    if (base) {
      document.getElementById('cm-same').textContent =
        '与《' + base.name + '》同属「' + e._family + '」，共用同一套内核；本条只换了载体、触发方式或参数。';
      sameBtn.textContent = '打开《' + base.name + '》→';
      sameBtn.onclick = function () { openCode(base.id); };
      sameWrap.hidden = false;
    } else {
      sameWrap.hidden = true;
    }

    var cost = d.cost || {};
    var tier = document.getElementById('cm-cost-tier');
    tier.textContent = cost.tier || '—';
    tier.setAttribute('data-tier', cost.tier || '');
    document.getElementById('cm-cost-note').textContent = cost.note || '';
    document.getElementById('cm-avoid').textContent = d.avoid || '';

    codeBox.classList.remove('notes-on');
    notesBtn.setAttribute('aria-expanded', 'false');

    var ul = document.getElementById('cm-features');
    ul.textContent = '';
    e.features.forEach(function (f) { ul.appendChild(el('li', { text: f })); });
    var tags = document.getElementById('cm-tech');
    tags.textContent = '';
    (e.tech || []).forEach(function (t) { tags.appendChild(el('span', { text: t })); });
    document.getElementById('cm-open').href = viewHref(e.id);
    document.getElementById('cm-code').textContent = '载入源码…';
    document.getElementById('cm-lines').textContent = '';

    curSrc = '';
    curTab = 'all';
    getSource(e).then(function (src) {
      curSrc = src;
      setTab('all');
    }).catch(function (err) {
      document.getElementById('cm-code').textContent = '读不到源码（' + err.message + '）。\n请用 serve.py 打开本站，file:// 会被浏览器拦截 fetch。';
    });

    if (push !== false) history.pushState({ fx: id }, '', '#' + encodeURIComponent(id));
    setTimeout(function () { document.getElementById('cm-close').focus(); }, 30);
  }

  function closeCode() {
    if (!openId) return;
    var id = openId;
    openId = null;
    modal.hidden = true;
    codeBox.classList.remove('notes-on');
    notesBtn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('fx-lock');
    lockScroll(false);
    if (decodeURIComponent(location.hash.slice(1)) === id) {
      history.replaceState(null, '', location.pathname + location.search);
    }
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function copy(text, btn) {
    var done = function () {
      var old = btn.textContent;
      btn.textContent = '已复制 ✓';
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

  /* ------------------------------------------------------------ 交互绑定 */
  var q = document.getElementById('q'), qt = null;
  q.addEventListener('input', function () {
    clearTimeout(qt);
    qt = setTimeout(function () { state.q = q.value.trim(); render(); }, 120);
  });
  q.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { q.value = ''; state.q = ''; render(); }
  });

  document.getElementById('random').addEventListener('click', function () {
    var e = DATA.effects[Math.floor(Math.random() * DATA.effects.length)];
    state.q = ''; state.cat = ''; state.fav = false;
    q.value = '';
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
    b.addEventListener('click', function () { if (curSrc) setTab(b.dataset.tab); });
  });
  document.getElementById('cm-close').addEventListener('click', closeCode);
  notesBtn.addEventListener('click', function () {
    var on = codeBox.classList.toggle('notes-on');
    notesBtn.setAttribute('aria-expanded', on ? 'true' : 'false');
  });
  zoomFrame.addEventListener('load', function () {
    if (!zoomOpenId) return;
    zoomStage.classList.add('ready');
    tidy(zoomFrame);
    fitZoom();
  });
  document.getElementById('zm-close').addEventListener('click', closeZoom);
  document.getElementById('zm-code').addEventListener('click', function () {
    var id = zoomOpenId;
    closeZoom();
    if (id) openCode(id);
  });
  zoomModal.addEventListener('click', function (e) { if (e.target === zoomModal) closeZoom(); });
  document.getElementById('cm-copy').addEventListener('click', function () {
    var txt = currentText();
    if (txt) copy(txt, this);
  });
  modal.addEventListener('click', function (e) { if (e.target === modal) closeCode(); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !zoomModal.hidden) { closeZoom(); return; }
    if (e.key === 'Tab' && !zoomModal.hidden) {
      var zf = Array.prototype.filter.call(
        zoomModal.querySelectorAll('a[href],button:not([disabled]),iframe,[tabindex]:not([tabindex="-1"])'),
        function (n) { return n.offsetParent !== null; }
      );
      if (zf.length) {
        var zfirst = zf[0], zlast = zf[zf.length - 1];
        if (!zoomModal.contains(document.activeElement)) { e.preventDefault(); zfirst.focus(); }
        else if (e.shiftKey && document.activeElement === zfirst) { e.preventDefault(); zlast.focus(); }
        else if (!e.shiftKey && document.activeElement === zlast) { e.preventDefault(); zfirst.focus(); }
      }
    }
    if (e.key === 'Escape' && !modal.hidden) {
      if (codeBox.classList.contains('notes-on')) {
        codeBox.classList.remove('notes-on');
        notesBtn.setAttribute('aria-expanded', 'false');
        return;
      }
      closeCode();
      return;
    }
    if (e.key === '/' && document.activeElement !== q && modal.hidden) {
      e.preventDefault(); q.focus();
    }
    if (e.key === 'Tab' && !modal.hidden) {
      var f = Array.prototype.filter.call(
        modal.querySelectorAll('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])'),
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
    var t = hashTarget();
    if (t.zoom) {
      if (t.zoom && byId(t.zoom)) { openZoom(t.zoom, false); return; }
      closeZoom(false);
      closeCode();
      return;
    }
    closeZoom();
    if (t.code && byId(t.code)) openCode(t.code, false); else closeCode();
  });

  addEventListener('resize', function () {
    clearTimeout(window.__fxr);
    window.__fxr = setTimeout(function () {
      document.querySelectorAll('.fx-shot').forEach(function (s) {
        if (s.classList.contains('ready')) fitShot(s);
      });
      if (!zoomModal.hidden) fitZoom();
    }, 160);
  });

  /* ------------------------------------------------------------ 启动 */
  fetch('effects.json').then(function (r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }).then(function (d) {
    DATA = d;
    index();

    var counts = {};
    d.effects.forEach(function (e) { counts[e.cat] = (counts[e.cat] || 0) + 1; });

    var cats = document.getElementById('cats');
    cats.appendChild(el('button', { class: 'chip', type: 'button', 'data-cat': '', 'aria-pressed': 'true' },
      [document.createTextNode('全部'), el('small', { text: d.total })]));
    d.cats.forEach(function (c) {
      var b = el('button', { class: 'chip', type: 'button', 'data-cat': c.id, 'aria-pressed': 'false' },
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

    document.getElementById('n-sub').textContent = d.total;
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
        entries.forEach(function (en) {
          if (en.isIntersecting) return;
          unmount(en.target);
        });
      }, { rootMargin: '1400px 0px' });
    }

    render();

    var t = hashTarget();
    if (t.zoom && byId(t.zoom)) openZoom(t.zoom, false);
    else if (t.code && byId(t.code)) openCode(t.code, false);
  }).catch(function (err) {
    grid.appendChild(el('div', { class: 'empty' }, [
      el('h2', { text: '读不到 effects.json（' + err.message + '）' }),
      el('p', { text: '用 file:// 直接打开时浏览器会拦截 fetch；请运行 serve.py 或 启动预览.bat。' })
    ]));
  });
})();
