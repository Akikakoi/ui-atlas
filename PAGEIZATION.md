# 动效「原页」页面化 · 进度

> 进度：**100 / 100**，剩余 **0 条**。全部完成。
> 每条对应 `effects/<id>.html`；目标是把点击「原页」后的组件演示改成真实产品页面，同时保留原效果机制与可访问性。
> 三层密度：桌面完整页 / 600 × 450 紧凑首屏 / ≤560 手机单列；`.hint` 在紧凑层可见，手机隐藏。

## 进度概览

| 类别 | 已完成 | 剩余 |
| --- | ---: | ---: |
| 指针交互 | 13 | 0 |
| 滚动叙事 | 17 | 0 |
| 文字动效 | 18 | 0 |
| 布局与结构 | 15 | 0 |
| 状态反馈 | 16 | 0 |
| 背景氛围 | 10 | 0 |
| 转场与导航 | 11 | 0 |
| **合计** | **100** | **0** |

## 滚动叙事 · 9

- [x] 卡片堆叠 `stack`
- [x] 滚动吸附 `snap`
- [x] 图文随行 `sticky-figure`
- [x] 滚动描边 `scroll-draw`
- [x] 滚动点亮文字 `scroll-text-fill` · 变体（scrub）
- [x] 速度跑马灯 `velocity-marquee` · 变体（marquee）
- [x] 滚动序列帧 `scroll-sequence`
- [x] 滚动旋转 `scroll-rotate` · 变体（scroll-zoom）
- [x] 滚动换色 `scroll-hue` · 变体（scroll-zoom）

## 文字动效 · 18

- [x] 逐字上浮 `split`
- [x] 乱码解码 `scramble`
- [x] 打字机 `typewriter`
- [x] 双行跑马灯 `marquee`
- [x] 文字翻转替换 `flip`
- [x] 荧光笔划线 `highlight`
- [x] 模糊聚焦 `blur`
- [x] 渐变扫光 `gradient-text`
- [x] 文字波浪 `text-wave`
- [x] 数字里程表 `odometer`
- [x] 字符抖动 `text-jitter`
- [x] 描边填充文字 `text-outline` · 变体（gradient-text）
- [x] 弧线文字 `text-path`
- [x] 关键词轮换 `word-rotate` · 变体（marquee）
- [x] 故障文字 `text-glitch` · 变体（text-jitter）
- [x] 文字斥力 `text-repel` · 变体（点阵斥力）
- [x] 下划线展开 `text-underline`
- [x] 文字探照灯 `text-spotlight` · 变体（光斑卡片）

## 背景氛围 · 10

- [x] 流动网格渐变 `mesh`
- [x] 粒子连线 `particles`
- [x] 胶片颗粒 `grain`
- [x] 等高线波浪 `waves`
- [x] 星空穿越 `starfield`
- [x] 流光边框 `conic-border`
- [x] 透视网格 `perspective-grid`
- [x] 字符雨 `matrix-rain` · 变体（particles）
- [x] 液态熔岩灯 `lava-lamp` · 变体（mesh）
- [x] 体积光 `light-rays` · 变体（conic-border）

## 说明

- 带「变体」的 14 条可复用已页面化同源页的结构；`marquee`、`gradient-text`、`like`、`particles`、`mesh`、`conic-border` 及其变体均已页面化。
- 文字动效收尾 4 条全部完成：关键词轮换 → EMBER 烘焙所（豆单风味轮换）、故障文字 → TAPEHEAD 磁带修复所（磁带损伤故障）、文字斥力 → OFFGRID 隐私浏览器（追踪让开）、文字探照灯 → BLACKBOX 黑匣子剧场（舞台追光）。原效果参数与 `prefers-reduced-motion` 降级均保留。
- 100 条全部页面化，彩排完成：1440 桌面完整页 / 600 × 450 紧凑首屏 / ≤560 手机单列三档实测均通过。

## 已完成 100 条

- [x] 逐字上浮 `split`
- [x] 乱码解码 `scramble`
- [x] 打字机 `typewriter`
- [x] 双行跑马灯 `marquee`
- [x] 文字翻转替换 `flip`
- [x] 荧光笔划线 `highlight`
- [x] 模糊聚焦 `blur`
- [x] 渐变扫光 `gradient-text`
- [x] 文字波浪 `text-wave`
- [x] 光标裁切揭示 `clip`
- [x] 过滤网格 FLIP `filter`
- [x] 无缝手风琴 `accordion`
- [x] 滑动下划线标签页 `tabs`
- [x] 拖拽排序 `drag-sort`
- [x] 收缩顶栏 `sticky-header`
- [x] 可拖拽分栏 `split-pane`
- [x] 瀑布流重排 `masonry`
- [x] 侧栏收轨 `sidebar-rail`
- [x] 旋钮拖拽 `knob-drag`
- [x] 胶囊滑块 `segmented`
- [x] 表格行展开 `table-row-expand`
- [x] 滚动缩放 `scroll-zoom`
- [x] 磁吸按钮 `magnetic`
- [x] 光斑跟随卡片 `spotlight`
- [x] 3D 倾斜卡片 `tilt`
- [x] 自定义光标 `cursor`
- [x] 列表悬停预览 `hover-preview`
- [x] 点阵斥力 `dot-grid`
- [x] 悬停放大镜 `zoom-lens`
- [x] 逐段入场 `reveal`
- [x] 滚动钉住 `pin`
- [x] 错峰入场 `stagger-in`
- [x] 按钮展开搜索框 `morph-input`
- [x] 页面推入 `page-push`
- [x] 音频波形 `audio-wave`
- [x] 对勾描边 `check-draw`
- [x] Dock 邻近放大 `dock-hover`
- [x] 拖拽横滑 `drag-scroll`
- [x] 汉堡图标变形 `icon-morph`
- [x] 延迟提示气泡 `tooltip`
- [x] 步骤条 `stepper`
- [x] 底部导航 `bottom-nav`
- [x] 共享元素转场 `view-transition`
- [x] 遮罩擦除转场 `curtain`
- [x] 拖拽底部抽屉 `drawer`
- [x] 卡片展开 `expand`
- [x] 光标拖尾 `cursor-trail`
- [x] 拖拽惯性 `drag-inertia`
- [x] 拖拽擦洗 `scrub-drag`
- [x] 图片内平移 `image-pan`
- [x] 视差分层 `parallax`
- [x] 滚动擦亮文字 `scrub`
- [x] 阅读进度与章节 `progress`
- [x] 数字滚动 `counter`
- [x] 滚动速度倾斜 `skew`
- [x] 圆形主题切换 `theme-wipe`
- [x] 全屏菜单 `menu-overlay`
- [x] 顶部路由进度 `route-progress`
- [x] 3D 翻卡 `card-flip`
- [x] 点击涟漪 `ripple`
- [x] 堆叠提示 `toast`
- [x] 骨架屏到内容 `skeleton`
- [x] 点赞粒子 `like`
- [x] 长按确认 `hold`
- [x] 按钮加载 `button-loading`
- [x] 表单错误抖动 `shake`
- [x] 自动保存状态 `auto-save`
- [x] 复制成功反馈 `copy-feedback`
- [x] 角标弹跳 `badge-bump`
- [x] 下拉刷新 `pull-refresh`
- [x] 撤销删除 `undo-delete`
- [x] 成功纸屑 `confetti` · 变体（like）
- [x] 数字里程表 `odometer`
- [x] 字符抖动 `text-jitter`
- [x] 弧线文字 `text-path`
- [x] 下划线展开 `text-underline`
- [x] 描边填充文字 `text-outline` · 变体（gradient-text）
- [x] 关键词轮换 `word-rotate` · 变体（marquee）
- [x] 故障文字 `text-glitch` · 变体（text-jitter）
- [x] 文字斥力 `text-repel` · 变体（点阵斥力）
- [x] 文字探照灯 `text-spotlight` · 变体（光斑卡片）
- [x] 流动网格渐变 `mesh`
- [x] 粒子连线 `particles`
- [x] 胶片颗粒 `grain`
- [x] 等高线波浪 `waves`
- [x] 星空穿越 `starfield`
- [x] 流光边框 `conic-border`
- [x] 透视网格 `perspective-grid`
- [x] 字符雨 `matrix-rain`
- [x] 液态熔岩灯 `lava-lamp`
- [x] 体积光 `light-rays`
- [x] 卡片堆叠 `stack`
- [x] 滚动吸附 `snap`
- [x] 图文随行 `sticky-figure`
- [x] 滚动描边 `scroll-draw`
- [x] 滚动点亮文字 `scroll-text-fill`
- [x] 速度跑马灯 `velocity-marquee`
- [x] 滚动序列帧 `scroll-sequence`
- [x] 滚动旋转 `scroll-rotate`
- [x] 滚动换色 `scroll-hue`
