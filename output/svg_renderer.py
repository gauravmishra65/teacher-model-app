"""
Pure-Python SVG → PNG renderer using Pillow only.
Handles the shapes AI generates for educational diagrams:
rect, circle, ellipse, line, polyline, polygon, path (M/L/Z), text, tspan.
No Cairo, no native DLLs required.
"""

import io
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

NS = re.compile(r'\{[^}]*\}')          # strip XML namespaces
HEX3 = re.compile(r'^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$')

NAMED_COLORS = {
    "red":"#ff0000","green":"#008000","blue":"#0000ff","black":"#000000",
    "white":"#ffffff","yellow":"#ffff00","orange":"#ffa500","purple":"#800080",
    "pink":"#ffc0cb","brown":"#a52a2a","grey":"#808080","gray":"#808080",
    "cyan":"#00ffff","magenta":"#ff00ff","lime":"#00ff00","navy":"#000080",
    "teal":"#008080","maroon":"#800000","olive":"#808000","silver":"#c0c0c0",
    "none": None, "transparent": None,
}


def _parse_color(val: str | None, default=None):
    if not val or val.strip() in ("", "none", "transparent"):
        return default
    val = val.strip()
    if val in NAMED_COLORS:
        c = NAMED_COLORS[val]
        return default if c is None else _hex_to_rgb(c)
    if val.startswith("#"):
        m = HEX3.match(val)
        if m:
            val = f"#{m.group(1)*2}{m.group(2)*2}{m.group(3)*2}"
        return _hex_to_rgb(val)
    if val.startswith("rgb"):
        nums = re.findall(r'\d+', val)
        if len(nums) >= 3:
            return tuple(int(n) for n in nums[:3])
    return default


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return (0, 0, 0)


def _f(val, default=0.0) -> float:
    try:
        return float(re.sub(r'[^0-9.\-]', '', str(val))) if val else default
    except Exception:
        return default


def _style_dict(style_str: str) -> dict:
    d = {}
    for part in (style_str or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def _get(elem, attr, default=None):
    """Get attribute, falling back to inline style."""
    val = elem.get(attr)
    if val is not None:
        return val
    style = _style_dict(elem.get("style", ""))
    return style.get(attr, default)


def _draw_elem(draw: ImageDraw.ImageDraw, elem, scale=1.0):
    tag = NS.sub('', elem.tag)
    fill_raw  = _get(elem, "fill", "black")
    stroke_raw = _get(elem, "stroke", "none")
    sw = max(1, int(_f(_get(elem, "stroke-width", "1")) * scale))
    fill   = _parse_color(fill_raw,  (0, 0, 0))
    stroke = _parse_color(stroke_raw, None)

    def s(v, d=0.0):  # scale a coordinate
        return _f(v, d) * scale

    if tag == "rect":
        x, y = s(elem.get("x", 0)), s(elem.get("y", 0))
        w, h = s(elem.get("width", 10)), s(elem.get("height", 10))
        rx = s(elem.get("rx", 0))
        box = [x, y, x + w, y + h]
        if fill:
            draw.rounded_rectangle(box, radius=rx, fill=fill)
        if stroke:
            draw.rounded_rectangle(box, radius=rx, outline=stroke, width=sw)

    elif tag in ("circle", "ellipse"):
        cx, cy = s(elem.get("cx", 0)), s(elem.get("cy", 0))
        rx = s(elem.get("r") or elem.get("rx", 10))
        ry = s(elem.get("r") or elem.get("ry", 10))
        box = [cx - rx, cy - ry, cx + rx, cy + ry]
        if fill:
            draw.ellipse(box, fill=fill)
        if stroke:
            draw.ellipse(box, outline=stroke, width=sw)

    elif tag == "line":
        x1, y1 = s(elem.get("x1", 0)), s(elem.get("y1", 0))
        x2, y2 = s(elem.get("x2", 0)), s(elem.get("y2", 0))
        col = stroke or fill or (0, 0, 0)
        draw.line([x1, y1, x2, y2], fill=col, width=sw)

    elif tag in ("polyline", "polygon"):
        pts_str = elem.get("points", "")
        nums = [float(n) for n in re.findall(r'[-+]?\d*\.?\d+', pts_str)]
        pts = [(nums[i] * scale, nums[i+1] * scale) for i in range(0, len(nums)-1, 2)]
        if len(pts) >= 2:
            if tag == "polygon" and fill:
                draw.polygon(pts, fill=fill)
            col = stroke or fill or (0, 0, 0)
            draw.line(pts + ([pts[0]] if tag == "polygon" else []), fill=col, width=sw)

    elif tag == "path":
        d = elem.get("d", "")
        pts = _parse_path(d, scale)
        if len(pts) >= 2:
            if fill and len(pts) >= 3:
                draw.polygon(pts, fill=fill)
            col = stroke or fill or (0, 0, 0)
            draw.line(pts, fill=col, width=sw)

    elif tag in ("text", "tspan"):
        x, y = s(elem.get("x", 0)), s(elem.get("y", 0))
        fs = max(8, int(_f(_get(elem, "font-size", "12")) * scale))
        col = fill or (0, 0, 0)
        text = (elem.text or "").strip()
        if text:
            try:
                font = ImageFont.truetype("arial.ttf", fs)
            except Exception:
                font = ImageFont.load_default()
            anchor = _get(elem, "text-anchor", "start")
            if anchor == "middle":
                bbox = draw.textbbox((0, 0), text, font=font)
                x -= (bbox[2] - bbox[0]) / 2
            elif anchor == "end":
                bbox = draw.textbbox((0, 0), text, font=font)
                x -= (bbox[2] - bbox[0])
            draw.text((x, y - fs * 0.8), text, fill=col, font=font)

    # Recurse into groups / nested elements
    if tag in ("g", "svg", "a"):
        for child in elem:
            _draw_elem(draw, child, scale)


def _parse_path(d: str, scale: float) -> list:
    """Minimal M/L/H/V/Z path parser — enough for simple educational diagrams."""
    pts = []
    cx, cy = 0.0, 0.0
    tokens = re.findall(r'[MmLlHhVvZzCcSsQqTtAa]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d)
    cmd = "M"
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            continue
        if cmd in "Mm":
            cx, cy = float(tokens[i]) * scale, float(tokens[i+1]) * scale
            pts.append((cx, cy))
            i += 2
        elif cmd in "Ll":
            cx, cy = float(tokens[i]) * scale, float(tokens[i+1]) * scale
            pts.append((cx, cy))
            i += 2
        elif cmd == "H":
            cx = float(tokens[i]) * scale; pts.append((cx, cy)); i += 1
        elif cmd == "h":
            cx += float(tokens[i]) * scale; pts.append((cx, cy)); i += 1
        elif cmd == "V":
            cy = float(tokens[i]) * scale; pts.append((cx, cy)); i += 1
        elif cmd == "v":
            cy += float(tokens[i]) * scale; pts.append((cx, cy)); i += 1
        elif cmd in "Zz":
            if pts:
                pts.append(pts[0])
        else:
            i += 1  # skip unsupported params
    return pts


def svg_to_png_bytes(svg_string: str, max_width: int = 600) -> bytes:
    """Convert an SVG string to PNG bytes using Pillow. Returns None on failure."""
    try:
        # Clean up common AI SVG issues
        svg_string = svg_string.strip()
        if not svg_string.startswith("<"):
            return None

        root = ET.fromstring(svg_string)
        tag = NS.sub('', root.tag)
        if tag != "svg":
            # Wrap bare elements in svg tag
            svg_string = f'<svg xmlns="http://www.w3.org/2000/svg">{svg_string}</svg>'
            root = ET.fromstring(svg_string)

        w_raw = root.get("width", "400")
        h_raw = root.get("height", "300")
        # Handle viewBox fallback
        vb = root.get("viewBox")
        if vb:
            parts = re.findall(r'[\d.]+', vb)
            if len(parts) == 4 and _f(w_raw) == 0:
                w_raw, h_raw = parts[2], parts[3]

        orig_w = max(1, _f(w_raw, 400))
        orig_h = max(1, _f(h_raw, 300))
        scale = min(1.0, max_width / orig_w) * 2  # 2x for retina
        W, H = max(1, int(orig_w * scale)), max(1, int(orig_h * scale))

        bg_raw = _style_dict(root.get("style", "")).get("background", None)
        bg = _parse_color(root.get("background") or bg_raw or "white", (255, 255, 255))
        img = Image.new("RGB", (W, H), bg or (255, 255, 255))
        draw = ImageDraw.Draw(img)

        for child in root:
            _draw_elem(draw, child, scale)

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()
    except Exception as e:
        return None  # caller handles fallback
