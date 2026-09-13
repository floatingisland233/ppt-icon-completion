# PPT 图标补全 Skill 设计方案

> 状态：**已按决议落地（P0+P1）**  
> 决议：半自动 iconfont + 无后端时询问一次旁路 + react-icons/builtin 优先自动 + 个人与项目双份安装。  
> 目标：为截图重建 / 可编辑 PPT 补齐语义小图标，支持从 [iconfont](https://www.iconfont.cn/) 等来源获取 SVG，按原图取色填色，并固化为可复用 skill 流程。

---

## 1. 背景与问题

当前 RO 成果汇报页重建结果中：

- 卡片 / 流程结构、文字已对象级可编辑；
- **部分语义小图标未复原**（流程步骤人物/电话/工具/同步、部分 header 图标等）；
- 环境常缺少 `image_gen` / Codex OAuth，导致 `image-to-editable-ppt` 的 asset-sheet 主路径不可用；
- 用圆+几何近似图标，观感弱且不符合「独立可替换图案对象」的交付标准。

用户诉求：

1. 在 [iconfont](https://www.iconfont.cn/) 寻找相近图标；
2. 下载 **SVG**；
3. 识别原图颜色，用相近色填充；
4. 将流程**内置进 skill**，下次直接调用。

---

## 2. 设计目标 / 非目标

### 2.1 目标

| ID | 目标 |
|----|------|
| G1 | 缺图标时可产出**独立、可移动**的图标图片对象（优先透明 PNG；保留 SVG 源文件） |
| G2 | 颜色贴近原图主题色（卡片蓝/绿/紫/青、流程灰/蓝等） |
| G3 | 流程可复用：下次重建同类页时按 skill 协议执行，少临场发挥 |
| G4 | 与现有 `image-to-editable-ppt`、`presentations` **协同**，不强行破坏前者主路径 |
| G5 | 保留图标来源与授权信息，便于审计 |

### 2.2 非目标（第一期不做）

| ID | 非目标 | 原因 |
|----|--------|------|
| N1 | 全自动爬取 iconfont 搜索/下载 API | 无稳定公开 API、登录/反爬、维护成本高 |
| N2 | PPT 内保留可编辑矢量路径（原生 SVG OOXML） | 兼容成本高；PNG 已满足「独立对象」 |
| N3 | 保证图标与原图像素级一致 | 库图标是「语义相近」，不是抠图复刻 |
| N4 | 替代复杂插画 / 照片 / 多色 Logo | 仍走 asset-sheet 或整体 PNG |

---

## 3. 总体策略（推荐）

采用 **「旁路 skill + 半自动协议」**，代号：

**`ppt-icon-completion`（PPT 图标补全）**

```text
┌─────────────────────────────────────────────────────────────┐
│  主重建路径                                                  │
│  image-to-editable-ppt（优先 asset-sheet 抠原图标）          │
│            │ 失败 / 无图片后端 / 用户显式要求图标库补全       │
│            ▼                                                 │
│  ppt-icon-completion（本方案）                               │
│            │                                                 │
│            ▼                                                 │
│  presentations / python-pptx / pptxgenjs 插入独立图片对象     │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 为何做成独立 skill，而不是直接改死 image-to-editable-ppt

`image-to-editable-ppt` 的 `page-decision-tree` 明确规定：

- 语义小图标属于 **foreground visual asset**；
- **禁止**用本地 Pillow/SVG/手绘近似替代；
- 主路径必须走 image backend 的 asset-sheet。

因此：

- **默认**：仍优先 asset-sheet（保真最高）；
- **旁路**：仅当用户声明「允许图标库补全」或主路径不可用时，启用 `ppt-icon-completion`；
- 在 `image-to-editable-ppt` 中只增加 **可选开关与交接协议**，不改写其「无降级」核心哲学（除非用户显式授权旁路）。

### 3.2 图标来源优先级（固定顺序）

1. **任务内已有合规 SVG/PNG**（`assets/icons/` 缓存命中）  
2. **程序化图标库**（`react-icons` / 项目内置 icon pack）— 可全自动  
3. **iconfont 半自动** — Agent 出检索词与候选；用户下载 SVG 放入约定目录，或粘贴 SVG 内容  
4. （最后）原生几何占位 — 仅 QA 标为 `icon_placeholder`，正式交付前应替换

---

## 4. 工作流设计

### Phase 0：触发条件

满足任一即触发图标补全：

- 用户说「补图标 / 用 iconfont / 图标库补全」；
- 重建预览中检测到语义图标位为空圆、几何占位、或与源图差异显著；
- `editppt doctor` 显示 image backend 不可用，且用户同意旁路。

### Phase 1：盘点（Inventory）

输出 `icon_inventory.json`：

```json
{
  "page_id": "page_001",
  "source_image": "input/source_slide.jpg",
  "icons": [
    {
      "id": "proc_asis_1",
      "role": "process_step_icon",
      "semantic": "人工巡检 / 人物",
      "search_terms_zh": ["人物", "用户", "巡检"],
      "search_terms_en": ["user", "person"],
      "bbox_norm": [0.14, 0.54, 0.18, 0.59],
      "theme_color_role": "process_blue",
      "status": "missing",
      "preferred_source": "iconfont|react-icons|cache"
    }
  ]
}
```

规则：

- 每个语义图标一条；
- `bbox_norm` 相对源图像素归一化，便于取色与定位；
- **不把**装饰线、纯色块、chevron 流程箭头算作图标（那些继续用原生形状）。

### Phase 2：色板（Palette）

从源图取样，生成 `color_palette.json`：

```json
{
  "roles": {
    "header_navy": "1A4A8C",
    "card_blue": "2B6CB0",
    "card_green": "2FA06E",
    "card_purple": "7A5CA8",
    "card_teal": "2A9B8F",
    "process_blue": "2F6FB8",
    "asis_gray": "7A8A9A",
    "alert_red": "D94545"
  },
  "sampling_notes": "从卡片色条/图标邻近非文字像素取中位色，映射到 role"
}
```

取色原则：

- 优先取 **色条 / 图标本体**，避开白底与文字；
- 映射到离散 role，避免每个图标一个噪声色；
- 同角色图标强制同色（As-Is 一排同灰蓝，To-Be 一排同蓝）。

### Phase 3：选型（Select）

对每条 inventory：

| 步骤 | 动作 |
|------|------|
| 3.1 | 查本地缓存 `~/.cursor/skills/ppt-icon-completion/icon-cache/` 与项目 `assets/icons/` |
| 3.2 | 未命中 → 生成 iconfont 检索建议（中文词为主）+ react-icons 候选名 |
| 3.3 | **半自动**：打开 [iconfont](https://www.iconfont.cn/)，用户选可商用图标，下载 SVG 到 `assets/icons/raw/{id}.svg` |
| 3.4 | 写入 `icon_selection.json`（含来源 URL、作者、授权备注） |

Agent 提示模板（内置 skill）：

```text
请在 iconfont 搜索：{search_terms_zh}
风格：扁平、线性或面性（与原图一致）、单色可填色
下载：SVG
保存为：assets/icons/raw/{id}.svg
授权：仅选可商用；在 selection 中注明项目名/作者
```

### Phase 4：填色与栅格化（Recolor & Rasterize）

确定性脚本（skill 内 `scripts/`，实现期再写）：

```text
recolor_svg.py  --in raw/x.svg --fill #2B6CB0 --out colored/x.svg
rasterize_svg.py --in colored/x.svg --size 256 --out png/x.png
```

规则：

- 默认把 SVG 中 `fill="#000"` / `currentColor` / 无 fill 的 path 统一为主题色；
- 保留 `fill="none"` 的描边结构；多色 SVG 第一期只支持「主色替换」；
- 输出 **透明底 PNG ≥256px**，插入 PPT 时再缩放到版式尺寸（避免拉伸变形）；
- **保留 colored SVG**，便于以后换色重导出。

### Phase 5：嵌入 PPT（Place）

- 每个图标 = **一张独立图片对象**；
- 禁止合并进大图；
- 先占位尺寸与源图 bbox 对齐，再微调；
- 更新对象统计：文本框 / 原生图形 / 图片 分开计数。

### Phase 6：QA

检查清单：

- [ ] 每个 `status=missing` 已变为 `placed` 或明确 `waived`
- [ ] 无整页截图
- [ ] 图标未裁切、未非等比拉伸
- [ ] 同排同角色颜色一致
- [ ] `icon_selection.json` 有来源与授权字段
- [ ] 预览图导出并目视对比源图

---

## 5. Skill 落位与目录结构

### 5.1 新建个人 skill（推荐）

路径：`~/.cursor/skills/ppt-icon-completion/`

```text
ppt-icon-completion/
├── SKILL.md                 # 触发词、工作流、与两大 skill 的交接
├── references/
│   ├── inventory-schema.md  # icon_inventory / palette / selection 字段
│   ├── iconfont-playbook.md # 半自动检索与授权注意事项
│   └── color-roles.md       # 常见企业汇报色角色约定
├── scripts/
│   ├── sample_palette.py    # 从源图+bbox 取样 → palette
│   ├── recolor_svg.py       # SVG 主色替换
│   ├── rasterize_svg.py     # SVG→PNG
│   └── validate_inventory.py
├── icon-cache/              # 可选：跨项目复用的已填色图标
└── examples/
    └── icon_inventory.example.json
```

### 5.2 项目侧约定目录

```text
{project}/
├── assets/
│   └── icons/
│       ├── raw/          # 用户/agent 放入的原始 SVG
│       ├── colored/      # 填色后 SVG
│       ├── png/          # 插入 PPT 用
│       ├── icon_inventory.json
│       ├── color_palette.json
│       └── icon_selection.json
└── output/
```

### 5.3 与现有 skill 的改动（实现期，小改）

| Skill | 改动类型 | 内容 |
|-------|----------|------|
| `ppt-icon-completion` | **新建** | 主流程与脚本 |
| `image-to-editable-ppt` | **小补丁** | SKILL.md 增加「旁路授权」条款：当 image backend 不可用且用户同意时，可调用 `ppt-icon-completion`，并在 manifest provenance 标注 `source=icon_library` |
| `presentations` | **小补丁** | Icons 一节增加：优先本协议资产；react-icons 作为自动源；插入须独立图片对象 |

**不建议**第一期大改 `page-decision-tree` 的「禁止本地近似」条文；改为「用户显式旁路时允许 icon library，禁止随意几何冒充」。

---

## 6. 与本页（RO 成果汇报）的实例映射

| icon id | 语义 | 检索词示例 | 颜色 role |
|---------|------|------------|-----------|
| card_bg | 文档 | 文档、列表 | card_blue |
| card_goal | 目标/靶心 | 目标、靶心 | card_green |
| card_benefit | 硬币/收益 | 硬币、金钱 | card_purple |
| card_soft | 星标 | 星星、星标 | card_teal |
| asis_1 | 人物巡检 | 用户、人物 | process_blue / asis_gray |
| asis_2 | 电话 | 电话、联系 | asis_gray |
| asis_3 | 工具 | 扳手、工具 | asis_gray |
| asis_4 | 同步 | 同步、刷新 | asis_gray |
| tobe_1 | 图表 | 柱状图、趋势 | process_blue |
| tobe_2 | 日历 | 日历、日程 | process_blue |
| tobe_3 | 扳手计划 | 扳手、维护 | process_blue |
| tobe_4 | 盾牌 | 盾牌、安全 | process_blue |
| header_team | 团队 | 团队、多人 | header_navy |

复杂插画（RO 膜组立体图、页眉工业照片）**不走本 skill**，继续整体图片或 asset-sheet。

---

## 7. 授权与合规

1. iconfont 图标授权因项目而异；skill 要求 `icon_selection.json` 必填：`license`、`author`、`project_url`、`commercial_ok`。  
2. `commercial_ok=false` 不得进入正式交付 PPT。  
3. 缓存图标时一并缓存授权元数据，禁止「只拷 PNG 丢来源」。  

参考站点：[iconfont 阿里巴巴矢量图标库](https://www.iconfont.cn/)

---

## 8. 分期实施计划

### P0 — 规范落地（0.5～1 天）
- 写入本设计；建 `ppt-icon-completion/SKILL.md` 骨架与 JSON schema；
- 为本项目补齐 `icon_inventory.json` 清单（可先手工）。

### P1 — 工具脚本（1～2 天）
- `sample_palette.py` / `recolor_svg.py` / `rasterize_svg.py`；
- 用本页 8～12 个图标跑通：人工下 SVG → 填色 → 插入 → 出预览。

### P2 — 接入两大 skill（0.5～1 天）
- presentations / image-to-editable-ppt 增加旁路说明与触发词；
- 交付检查清单写入 QA。

### P3 — 增强（可选，后续）
- react-icons 自动候选，减少手搜；
- 简单「缓存命中」复用历史项目图标；
- （不优先）探索 iconfont 官方/开放接口，仍保持半自动兜底。

---

## 9. 风险与对策

| 风险 | 对策 |
|------|------|
| 图标不像原图 | 允许多候选；验收看「语义+风格+颜色」，不追求同款 |
| 用户不愿每次手下 SVG | P2 加强 react-icons 自动路径；iconfont 仅补中文语义缺口 |
| 与 image-to-editable-ppt 规则冲突 | 旁路必须显式授权；provenance 标明来源 |
| SVG 结构奇葩填色失败 | 脚本失败时保留原 SVG，改用单色模板图标并标记 warning |
| 商用授权不清 | selection 缺字段则 QA 不通过 |

---

## 10. 成功标准

1. 调用 `/ppt-icon-completion`（或重建时启用旁路）后，本页流程步骤与卡片标题图标均为**独立图片对象**；  
2. 颜色与卡片/流程主题色目视一致；  
3. 全流程可在新项目按同一目录与 JSON 约定复用；  
4. 不引入整页截图；不破坏已有文本框/原生形状可编辑性。

---

## 11. 待你确认的决策点

实现前建议拍板：

1. **是否接受「用户从 iconfont 下载 SVG 到约定目录」的半自动**（推荐：接受）？  
2. **旁路默认**：仅手动开启，还是「无图片后端时自动询问一次」？  
3. **自动源**：是否第一期就加 `react-icons` 自动生成，iconfont 作补充？  
4. Skill 安装范围：仅个人 `~/.cursor/skills/`，还是同时放入本仓库 `.cursor/skills/`？

确认后即可按 P0→P1 开工（仍可按你要求分步，先只建 skill 文档不写脚本）。
