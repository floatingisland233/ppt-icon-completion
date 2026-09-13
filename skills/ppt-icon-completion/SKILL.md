---
name: ppt-icon-completion
description: >-
  Completes missing semantic icons on editable PPT reconstructions using a
  cache → react-icons/builtin pack → iconfont semi-manual pipeline, recolors
  SVGs from source slide palettes, and inserts independent transparent PNGs.
  Use when rebuilding slides from screenshots, when small icons are missing or
  placeholder geometry, when image-to-editable-ppt asset-sheet is unavailable,
  or when the user asks for iconfont / 图标补全 / 补图标.
---

# PPT Icon Completion

## Locked decisions (this project)

1. **iconfont**: semi-manual — user downloads SVG into `assets/icons/raw/{id}.svg`.
2. **Bypass**: ask once when image backend is unavailable; otherwise off unless user requests.
3. **Auto source**: try cache → react-icons / builtin pack before iconfont.
4. **Install**: personal `~/.cursor/skills/ppt-icon-completion/` and project `.cursor/skills/ppt-icon-completion/`.

## When to run

- User asks to 补图标 / iconfont / 图标库补全.
- Preview shows empty circles or crude geometry where semantic icons belong.
- `editppt doctor` shows image backend missing and user accepts the bypass (ask once).

Do **not** use for complex illustrations, photos, or multi-color logos — keep asset-sheet or whole PNG.

## Source priority

1. Project `assets/icons/` or skill `icon-cache/` hit  
2. Auto: `react-icons` (Node) or skill `builtin-icons/` SVG pack  
3. Semi-manual: [iconfont](https://www.iconfont.cn/) → save as `assets/icons/raw/{id}.svg`  
4. Placeholder only with `status=placeholder` (must replace before formal delivery)

## Workflow

### 1. Inventory

Create/update `assets/icons/icon_inventory.json` (schema in `references/inventory-schema.md`).

### 2. Palette

```bash
python scripts/sample_palette.py --source <source.png|jpg> --inventory assets/icons/icon_inventory.json --out assets/icons/color_palette.json
```

Or copy role colors from the slide theme when sampling is noisy.

### 3. Resolve icons

```bash
python scripts/resolve_icons.py --inventory assets/icons/icon_inventory.json --palette assets/icons/color_palette.json --icons-root assets/icons --skill-root <this-skill>
```

- Fills `raw/` from builtin/react-icons when possible.
- Lists remaining ids that need iconfont download.
- Writes `icon_selection.json`.

For each remaining id, tell the user:

```text
请在 https://www.iconfont.cn/ 搜索：{search_terms_zh}
风格：扁平单色；下载 SVG；仅选可商用
保存为：assets/icons/raw/{id}.svg
```

### 4. Recolor + rasterize

```bash
python scripts/recolor_svg.py --inventory assets/icons/icon_inventory.json --palette assets/icons/color_palette.json --icons-root assets/icons
python scripts/rasterize_svg.py --icons-root assets/icons --size 256
```

### 5. Place into PPT

Insert each `assets/icons/png/{id}.png` as an **independent** picture object (python-pptx / pptxgenjs). Never merge into a full-slide image.

### 6. QA

- [ ] Every inventory icon is `placed` or explicitly `waived`
- [ ] No full-slide source screenshot
- [ ] No non-uniform stretch; transparent PNG
- [ ] Same role → same fill color
- [ ] `icon_selection.json` has license fields for iconfont items

## Integration

- **image-to-editable-ppt**: preferred path remains asset-sheet. This skill is an **authorized bypass** when backend is down or user opts in; mark provenance `source=icon_library`.
- **presentations**: prefer assets from this pipeline over empty shape decoys.

## References

- [inventory-schema.md](references/inventory-schema.md)
- [iconfont-playbook.md](references/iconfont-playbook.md)
- [color-roles.md](references/color-roles.md)
