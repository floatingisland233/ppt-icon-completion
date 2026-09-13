# ppt-icon-completion

Cursor Agent Skill：为「截图重建 / 可编辑 PPT」补齐语义小图标。

优先级：`本地缓存 → builtin SVG 包 → react-icons（可选）→ iconfont 半自动`。  
从源页色板取色填 SVG，栅格化为透明 PNG，以**独立图片对象**插入 PPT。

## 安装（Cursor）

将 `skills/ppt-icon-completion/` 复制到：

- 个人：`~/.cursor/skills/ppt-icon-completion/`
- 或项目：`.cursor/skills/ppt-icon-completion/`

重启 Cursor / 新开 Agent 会话后即可通过描述调用，例如：

> 用 ppt-icon-completion 给当前 PPT 补齐缺失小图标。

## 依赖

- Python 3 + `Pillow`、`numpy`、`pymupdf`（栅格化 SVG）
- 可选上游工作流（**请自行安装，本仓库不内嵌**）：
  - [ningzimu/image-to-editable-ppt-skill](https://github.com/ningzimu/image-to-editable-ppt-skill)（MIT）— 截图重建主路径
  - Anthropic document `pptx` / Presentations skill — 仅通过官方渠道获取，**请勿把其专有文件提交到本仓库**

## 快速使用

```bash
# 1) 准备 assets/icons/icon_inventory.json（见 skill examples）
# 2) 色板
python skills/ppt-icon-completion/scripts/sample_palette.py --use-defaults --out assets/icons/color_palette.json

# 3) 解析图标（builtin/cache）
python skills/ppt-icon-completion/scripts/resolve_icons.py \
  --inventory assets/icons/icon_inventory.json \
  --palette assets/icons/color_palette.json \
  --icons-root assets/icons \
  --skill-root skills/ppt-icon-completion

# 若 need_iconfont>0：按 references/iconfont-playbook.md 下载 SVG 到 assets/icons/raw/{id}.svg

# 4) 填色 + 栅格化
python skills/ppt-icon-completion/scripts/recolor_svg.py \
  --inventory assets/icons/icon_inventory.json \
  --palette assets/icons/color_palette.json \
  --icons-root assets/icons
python skills/ppt-icon-completion/scripts/rasterize_svg.py --icons-root assets/icons --size 256
```

将 `assets/icons/png/{id}.png` 作为独立图片插入 PPT 即可。

## 仓库内容

| 路径 | 说明 |
|------|------|
| `skills/ppt-icon-completion/` | Skill 本体（SKILL.md / scripts / builtin-icons / references） |
| `docs/` | 设计方案与决议 |

## 明确不包含

- Anthropic `presentations` / `pptx` skill 源码  
- 业务 PPT、源截图、预览大图  

## License

本仓库代码为 MIT（见 `LICENSE`）。  
使用 iconfont 等第三方图标时，请遵守对应图标的授权，并在 `icon_selection.json` 中记录来源。
