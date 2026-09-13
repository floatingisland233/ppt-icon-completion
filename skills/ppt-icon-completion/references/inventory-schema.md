# Inventory / palette / selection schemas

## icon_inventory.json

```json
{
  "page_id": "page_001",
  "source_image": "input/source_slide.jpg",
  "icons": [
    {
      "id": "asis_1",
      "role": "process_step_icon",
      "semantic": "人物巡检",
      "search_terms_zh": ["用户", "人物"],
      "search_terms_en": ["user", "person"],
      "builtin_name": "user",
      "bbox_norm": [0.14, 0.54, 0.18, 0.59],
      "theme_color_role": "asis_gray",
      "status": "missing"
    }
  ]
}
```

| Field | Required | Notes |
|-------|----------|-------|
| id | yes | filesystem-safe |
| semantic | yes | human label |
| search_terms_zh | yes | iconfont hints |
| builtin_name | no | maps to `builtin-icons/{name}.svg` |
| bbox_norm | no | `[l,t,r,b]` 0–1 for sampling / placement |
| theme_color_role | yes | key into palette.roles |
| status | yes | `missing` \| `resolved` \| `placed` \| `placeholder` \| `waived` |

## color_palette.json

```json
{
  "roles": {
    "card_blue": "2B6CB0",
    "process_blue": "2F6FB8"
  }
}
```

Hex without `#`.

## icon_selection.json

```json
{
  "items": [
    {
      "id": "asis_1",
      "source": "builtin|react-icons|iconfont|cache",
      "path": "assets/icons/raw/asis_1.svg",
      "license": "MIT|iconfont-project|unknown",
      "author": "",
      "project_url": "",
      "commercial_ok": true
    }
  ]
}
```

iconfont entries must set `commercial_ok` and `project_url` before formal delivery.
