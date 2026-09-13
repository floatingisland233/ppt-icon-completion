# -*- coding: utf-8 -*-
"""Object-level editable rebuild of RO membrane prediction report slide."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

ROOT = Path(r"C:\Users\Xiaomi\Desktop\StudyProject\PPTTest1")
ASSETS = ROOT / "assets" / "cropped"
ICONS = ROOT / "assets" / "icons" / "png"
OUT = ROOT / "output"

# Standard 16:9 widescreen — closer to corporate PPT usage
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

NAVY = RGBColor(0x1A, 0x4A, 0x8C)
BLUE = RGBColor(0x2B, 0x6C, 0xB0)
BLUE_MID = RGBColor(0x3A, 0x7B, 0xC8)
BLUE_LT = RGBColor(0xE8, 0xF1, 0xFB)
GREEN = RGBColor(0x2F, 0xA0, 0x6E)
GREEN_LT = RGBColor(0xE6, 0xF6, 0xEE)
PURPLE = RGBColor(0x7A, 0x5C, 0xA8)
PURPLE_LT = RGBColor(0xF1, 0xEB, 0xF8)
TEAL = RGBColor(0x2A, 0x9B, 0x8F)
TEAL_LT = RGBColor(0xE5, 0xF6, 0xF4)
RED = RGBColor(0xD9, 0x45, 0x45)
RED_LT = RGBColor(0xFD, 0xEE, 0xEE)
GRAY = RGBColor(0x5A, 0x6A, 0x7A)
GRAY_BOX = RGBColor(0x7A, 0x8A, 0x9A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x22, 0x2A, 0x33)
BG = RGBColor(0xF4, 0xF7, 0xFB)
LINE = RGBColor(0xD0, 0xDA, 0xE6)


def set_run(run, text, size=11, bold=False, color=BLACK, font="微软雅黑"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = etree.SubElement(rPr, qn("a:ea"))
    ea.set("typeface", font)


def _anchor(tf, anchor):
    mapping = {MSO_ANCHOR.TOP: "t", MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.BOTTOM: "b"}
    try:
        tf._txBody.bodyPr.set("anchor", mapping.get(anchor, "t"))
        for a in ("lIns", "tIns", "rIns", "bIns"):
            tf._txBody.bodyPr.set(a, "0")
    except Exception:
        pass


def add_text(slide, left, top, width, height, text, size=11, bold=False, color=BLACK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    _anchor(tf, anchor)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.runs[0] if p.runs else p.add_run()
    set_run(run, text, size, bold, color)
    return box


def add_rich(slide, left, top, width, height, segments, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    _anchor(tf, anchor)
    p = tf.paragraphs[0]
    p.alignment = align
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    for text, size, bold, color in segments:
        set_run(p.add_run(), text, size, bold, color)
    return box


def fill(shape, color, line=None, lw=1.25):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(lw)


def rounded(slide, left, top, width, height, color, line=None, adj=0.1):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    fill(sh, color, line)
    try:
        sh.adjustments[0] = adj
    except Exception:
        pass
    return sh


def rect(slide, left, top, width, height, color, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    fill(sh, color, line)
    return sh


def oval(slide, left, top, width, height, color, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, width, height)
    fill(sh, color, line)
    return sh


def chevron(slide, left, top, width, height, color):
    sh = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, left, top, width, height)
    fill(sh, color)
    return sh


def shadow(shape):
    spPr = shape._element.spPr
    effectLst = spPr.find(qn("a:effectLst"))
    if effectLst is None:
        effectLst = etree.SubElement(spPr, qn("a:effectLst"))
    outer = etree.SubElement(effectLst, qn("a:outerShdw"))
    outer.set("blurRad", "50800")
    outer.set("dist", "25400")
    outer.set("dir", "2700000")
    outer.set("algn", "tl")
    outer.set("rotWithShape", "0")
    srgb = etree.SubElement(outer, qn("a:srgbClr"))
    srgb.set("val", "1A3A5C")
    etree.SubElement(srgb, qn("a:alpha")).set("val", "16000")


def add_img(slide, name, left, top, width=None, height=None, root=None):
    path = (root or ASSETS) / name
    if not path.exists():
        return None
    kw = {}
    if width is not None:
        kw["width"] = width
    if height is not None:
        kw["height"] = height
    return slide.shapes.add_picture(str(path), left, top, **kw)


def add_icon(slide, icon_id, left, top, size):
    """Independent PNG icon from ppt-icon-completion pipeline."""
    return add_img(slide, f"{icon_id}.png", left, top, width=size, height=size, root=ICONS)


def draw_ro_unit(slide, x, y):
    """Native RO membrane rack illustration (no text)."""
    # frame
    rounded(slide, x, y, Inches(0.72), Inches(1.35), BLUE_LT, line=BLUE, adj=0.08)
    for i, yy in enumerate([0.12, 0.45, 0.78]):
        rounded(slide, x + Inches(0.1), y + Inches(yy), Inches(0.52), Inches(0.28), WHITE, line=BLUE_MID, adj=0.35)
        oval(slide, x + Inches(0.14), y + Inches(yy + 0.06), Inches(0.16), Inches(0.16), BLUE_LT, line=BLUE)
    # clock
    oval(slide, x + Inches(0.78), y + Inches(0.15), Inches(0.32), Inches(0.32), WHITE, line=BLUE)
    oval(slide, x + Inches(0.92), y + Inches(0.28), Inches(0.04), Inches(0.04), BLUE)
    # warning triangle
    tri = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, x + Inches(0.82), y + Inches(0.55), Inches(0.28), Inches(0.26))
    fill(tri, RED)
    add_text(slide, x + Inches(0.82), y + Inches(0.6), Inches(0.28), Inches(0.2),
             "!", size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def pill_label(slide, x, y, w, h, color, icon_id, title):
    rounded(slide, x, y, w, h, color, adj=0.5)
    icon_sz = h - Inches(0.08)
    add_icon(slide, icon_id, x + Inches(0.08), y + Inches(0.04), icon_sz)
    add_text(slide, x + Inches(0.36), y, w - Inches(0.42), h, title, size=11, bold=True,
             color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, SLIDE_W, SLIDE_H, BG)

    # ===== HEADER =====
    hh = Inches(0.78)
    rect(slide, 0, 0, SLIDE_W, hh, NAVY)
    # pipes as right-side photo under navy (full-bleed right)
    pic = add_img(slide, "header_pipes.png", Inches(9.4), Inches(0.0), height=hh)
    # navy gradient cover strip
    rect(slide, Inches(8.7), 0, Inches(1.0), hh, NAVY)
    add_text(slide, Inches(0.25), Inches(0.08), Inches(8.5), Inches(0.38),
             "RO 膜组压差预测与预警 | 成果汇报", size=20, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(0.25), Inches(0.42), Inches(6.5), Inches(0.28),
             "厂务智能运维 · 提前安排清洗", size=11, color=RGBColor(0xC5, 0xD8, 0xF0), anchor=MSO_ANCHOR.MIDDLE)
    # team pill on photo
    rounded(slide, Inches(10.0), Inches(0.42), Inches(3.05), Inches(0.28), RGBColor(0x24, 0x58, 0x9E), adj=0.5)
    add_icon(slide, "header_team", Inches(10.12), Inches(0.46), Inches(0.2))
    add_text(slide, Inches(10.35), Inches(0.42), Inches(2.6), Inches(0.28),
             "项目团队：XXX、XXX、XXX", size=9, color=WHITE, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

    # ===== 4 CARDS =====
    cy = Inches(0.95)
    ch = Inches(2.28)
    m = Inches(0.2)
    g = Inches(0.12)
    cw = (SLIDE_W - m * 2 - g * 3) / 4
    xs = [m + i * (cw + g) for i in range(4)]

    meta = [
        (BLUE, "card_bg", "背景"),
        (GREEN, "card_goal", "目标"),
        (PURPLE, "card_benefit", "量化效益"),
        (TEAL, "card_soft", "非量化效益"),
    ]
    for i, (accent, icon, title) in enumerate(meta):
        card = rounded(slide, xs[i], cy, cw, ch, WHITE, line=LINE, adj=0.06)
        shadow(card)
        pill_label(slide, xs[i] + Inches(0.12), cy + Inches(0.1), Inches(1.35 if i < 2 else 1.55), Inches(0.3), accent, icon, title)

    # Card1
    x = xs[0]
    draw_ro_unit(slide, x + Inches(0.1), cy + Inches(0.5))
    add_rich(slide, x + Inches(1.25), cy + Inches(0.5), cw - Inches(1.35), Inches(1.6), [
        ("RO 膜压差达清洗阀值后，才联系厂商安排清洗；发现到清洗完成约 ", 9, False, BLACK),
        ("18 天", 9, True, BLUE),
        ("。期间常靠加压或备用膜组保产，运维成本高、响应被动。", 9, False, BLACK),
    ])

    # Card2
    x = xs[1]
    rounded(slide, x + Inches(0.15), cy + Inches(0.52), Inches(0.78), Inches(0.78), GREEN_LT, adj=0.12)
    for j, h in enumerate([0.22, 0.35, 0.48]):
        rect(slide, x + Inches(0.28 + j * 0.16), cy + Inches(1.15 - h), Inches(0.11), Inches(h), GREEN)
    ar = slide.shapes.add_shape(MSO_SHAPE.UP_ARROW, x + Inches(0.7), cy + Inches(0.58), Inches(0.16), Inches(0.3))
    fill(ar, GREEN)
    add_rich(slide, x + Inches(1.05), cy + Inches(0.52), cw - Inches(1.15), Inches(0.95), [
        ("建设压差趋势预测与自动预警，提前约 ", 9, False, BLACK),
        ("7 天", 9, True, GREEN),
        (" 发现超阀风险，支撑计划性清洗。", 9, False, BLACK),
    ])
    rounded(slide, x + Inches(0.15), cy + Inches(1.75), cw - Inches(0.3), Inches(0.38), GREEN_LT, adj=0.15)
    add_text(slide, x + Inches(0.2), cy + Inches(1.75), cw - Inches(0.4), Inches(0.38),
             "目标上线 / 验收时间：2025 年 12 月", size=9, bold=True, color=GREEN, anchor=MSO_ANCHOR.MIDDLE)

    # Card3
    x = xs[2]
    add_text(slide, x + Inches(0.1), cy + Inches(0.48), cw - Inches(0.2), Inches(0.24),
             "年运维收益预估约", size=10, color=GRAY, align=PP_ALIGN.CENTER)
    add_text(slide, x + Inches(0.1), cy + Inches(0.68), cw - Inches(0.2), Inches(0.48),
             "24 万元", size=26, bold=True, color=PURPLE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, x + Inches(0.1), cy + Inches(1.15), cw - Inches(0.2), Inches(0.22),
             "(投入约 2.1 万元，回收期 ≤ 1 年)", size=8, color=GRAY, align=PP_ALIGN.CENTER)
    rounded(slide, x + Inches(0.15), cy + Inches(1.45), cw - Inches(0.3), Inches(0.68), PURPLE_LT, adj=0.1)
    add_rich(slide, x + Inches(0.2), cy + Inches(1.5), cw - Inches(0.4), Inches(0.58), [
        ("预警窗口：0 天 → 约 ", 9, False, BLACK),
        ("7 天\n", 9, True, PURPLE),
        ("响应从「事后抢修」变为「提前准备」", 8, False, GRAY),
    ], align=PP_ALIGN.CENTER)

    # Card4
    x = xs[3]
    items = [
        ("soft_1", "设备状态可视化 | 正常 / 预警 / 待清洗 / 维护中，减少纯靠经验判断"),
        ("soft_2", "通知闭环 | 超阀或波动自动告警，企微/邮件触达责任人"),
        ("soft_3", "数据可沉淀 | 历史压差、预测、告警可追溯，支撑后续厂务智能化扩展"),
    ]
    iy = cy + Inches(0.5)
    for idx, (iid, txt) in enumerate(items, 1):
        oval(slide, x + Inches(0.14), iy + Inches(0.02), Inches(0.24), Inches(0.24), TEAL)
        add_text(slide, x + Inches(0.14), iy + Inches(0.02), Inches(0.24), Inches(0.24),
                 str(idx), size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_icon(slide, iid, x + Inches(0.42), iy + Inches(0.02), Inches(0.22))
        add_text(slide, x + Inches(0.68), iy, cw - Inches(0.78), Inches(0.5), txt, size=8, color=BLACK)
        iy += Inches(0.52)

    # ===== PROCESS BAR =====
    by = Inches(3.35)
    rounded(slide, m, by, SLIDE_W - m * 2, Inches(0.34), BLUE_MID, adj=0.1)
    add_text(slide, m + Inches(0.3), by, SLIDE_W - m * 2 - Inches(0.4), Inches(0.34),
             "流程对比 | 从发现到恢复，效率与成本的双重优化", size=12, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

    # Chevrons
    left_w = Inches(1.35)
    right_w = Inches(1.7)
    mid_l = m + left_w + Inches(0.08)
    mid_r = SLIDE_W - m - right_w - Inches(0.08)
    mid_w = mid_r - mid_l
    sg = Inches(0.06)
    sw = (mid_w - sg * 3) / 4
    chy = Inches(3.8)
    for i, lab in enumerate(["发现异常", "联系厂商", "到场清洗", "恢复运行"]):
        sx = mid_l + i * (sw + sg)
        chevron(slide, sx, chy, sw, Inches(0.3), BLUE)
        add_text(slide, sx + Inches(0.02), chy, sw - Inches(0.18), Inches(0.3),
                 lab, size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Rows
    r1 = Inches(4.2)
    r2 = Inches(5.85)
    rh = Inches(1.35)

    rounded(slide, m, r1, left_w, rh, GRAY_BOX, adj=0.08)
    add_text(slide, m, r1 + Inches(0.35), left_w, Inches(0.3), "As-Is 现状", size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, m, r1 + Inches(0.7), left_w, Inches(0.3), "巡检 + 超限", size=9, color=RGBColor(0xE8, 0xEE, 0xF4), align=PP_ALIGN.CENTER)

    rounded(slide, m, r2, left_w, rh, BLUE, adj=0.08)
    add_text(slide, m, r2 + Inches(0.35), left_w, Inches(0.3), "To-Be 改善后", size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, m, r2 + Inches(0.7), left_w, Inches(0.3), "预测 + 预警中心", size=9, color=RGBColor(0xD0, 0xE4, 0xFF), align=PP_ALIGN.CENTER)

    asis = [
        "人工巡检 / 超限才告警\n依赖人工发现，存在滞后性",
        "达阀后才联系\n准备窗口不足",
        "≥ 15 天清洗作业\n整体 ≥ 18 天链路",
        "期间或加压耗电 / 启用备用\n运维成本高、供水有风险",
    ]
    tobe = [
        "系统日更 7 日压差预测\n超阀 / 波动自动预警",
        "提前约 7 天联系\n把等待变成备料 / 排人",
        "仍按厂商节奏清洗\n可纳入计划窗口",
        "减少应急手段\n降低供水与成本风险",
    ]
    asis_ids = ["asis_1", "asis_2", "asis_3", "asis_4"]
    tobe_ids = ["tobe_1", "tobe_2", "tobe_3", "tobe_4"]

    def step_icon_png(slide, cx, top, icon_id, ring_blue=True):
        oval(
            slide,
            cx - Inches(0.18),
            top,
            Inches(0.36),
            Inches(0.36),
            BLUE_LT if ring_blue else RGBColor(0xEE, 0xF1, 0xF5),
            line=BLUE if ring_blue else GRAY,
        )
        add_icon(slide, icon_id, cx - Inches(0.12), top + Inches(0.06), Inches(0.24))

    for i, txt in enumerate(asis):
        sx = mid_l + i * (sw + sg)
        rounded(slide, sx, r1, sw, rh, WHITE, line=LINE, adj=0.08)
        step_icon_png(slide, sx + sw / 2, r1 + Inches(0.1), asis_ids[i], ring_blue=False)
        add_text(slide, sx + Inches(0.06), r1 + Inches(0.5), sw - Inches(0.12), Inches(0.75),
                 txt, size=8, color=BLACK, align=PP_ALIGN.CENTER)
        if i < 3:
            ar = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, sx + sw + Inches(0.005), r1 + rh / 2 - Inches(0.06), Inches(0.05), Inches(0.12))
            fill(ar, BLUE_MID)

    for i, txt in enumerate(tobe):
        sx = mid_l + i * (sw + sg)
        rounded(slide, sx, r2, sw, rh, BLUE_LT, line=RGBColor(0xB5, 0xCE, 0xE8), adj=0.08)
        step_icon_png(slide, sx + sw / 2, r2 + Inches(0.1), tobe_ids[i], ring_blue=True)
        add_text(slide, sx + Inches(0.06), r2 + Inches(0.5), sw - Inches(0.12), Inches(0.75),
                 txt, size=8, color=BLACK, align=PP_ALIGN.CENTER)
        if i < 3:
            ar = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, sx + sw + Inches(0.005), r2 + rh / 2 - Inches(0.06), Inches(0.05), Inches(0.12))
            fill(ar, BLUE_MID)

    # down arrows between rows
    for i in range(4):
        sx = mid_l + i * (sw + sg) + sw / 2 - Inches(0.08)
        ar = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, sx, r1 + rh + Inches(0.05), Inches(0.16), Inches(0.22))
        fill(ar, BLUE)

    # summaries
    sx = SLIDE_W - m - right_w
    rounded(slide, sx, r1, right_w, rh, WHITE, line=RED, adj=0.08)
    add_text(slide, sx + Inches(0.05), r1 + Inches(0.08), right_w - Inches(0.1), Inches(0.28),
             "从发现到具备清洗准备", size=8, color=GRAY, align=PP_ALIGN.CENTER)
    add_text(slide, sx + Inches(0.05), r1 + Inches(0.35), right_w - Inches(0.1), Inches(0.45),
             "≥18 天", size=20, bold=True, color=RED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rounded(slide, sx + Inches(0.12), r1 + Inches(0.95), right_w - Inches(0.24), Inches(0.28), RED_LT, adj=0.4)
    add_text(slide, sx + Inches(0.12), r1 + Inches(0.95), right_w - Inches(0.24), Inches(0.28),
             "运维模式：应急抢修", size=8, bold=True, color=RED, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    rounded(slide, sx, r2, right_w, rh, WHITE, line=GREEN, adj=0.08)
    add_text(slide, sx + Inches(0.05), r2 + Inches(0.08), right_w - Inches(0.1), Inches(0.28),
             "提前预警约", size=8, color=GRAY, align=PP_ALIGN.CENTER)
    add_text(slide, sx + Inches(0.05), r2 + Inches(0.35), right_w - Inches(0.1), Inches(0.45),
             "7 天", size=20, bold=True, color=GREEN, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rounded(slide, sx + Inches(0.12), r2 + Inches(0.95), right_w - Inches(0.24), Inches(0.28), GREEN_LT, adj=0.4)
    add_text(slide, sx + Inches(0.12), r2 + Inches(0.95), right_w - Inches(0.24), Inches(0.28),
             "运维模式：计划维护", size=8, bold=True, color=GREEN, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    out1 = OUT / "RO_membrane_prediction_editable.pptx"
    page = ROOT / "output/image-to-editable-ppt/job001/20260913-172412-source_slide/pages/page_001/page.pptx"
    prs.save(str(out1))
    prs.save(str(page))
    # Chinese filename alias
    out2 = OUT / "RO膜组压差预测与预警_成果汇报_可编辑.pptx"
    prs.save(str(out2))
    print("OK", out1)
    return out1


if __name__ == "__main__":
    build()
