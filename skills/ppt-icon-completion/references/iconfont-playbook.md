# iconfont 半自动手册

站点：[https://www.iconfont.cn/](https://www.iconfont.cn/)

## 步骤

1. 用 inventory 中的 `search_terms_zh` 搜索。
2. 优先选 **线性 / 面性扁平、单色、可改色** 的图标。
3. 确认授权为 **可商用**（或已购项目）。
4. 下载 **SVG**（不要 PNG）。
5. 保存为项目路径：`assets/icons/raw/{id}.svg`（`{id}` 与 inventory 一致）。
6. 在 `icon_selection.json` 填写 `author`、`project_url`、`license`、`commercial_ok`。

## 不要做

- 不要爬虫批量下载。
- 不要使用未标明可商用的图标进入正式交付。
- 不要把多色插画当小图标源（难以统一填色）。
