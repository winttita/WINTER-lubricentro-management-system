"""Genera build/icon.ico para LubricantroWinter.exe.

Diseno: bidon de aceite minimalista (cilindro con tapa y mango) en azul
petroleo (#1B4F72), con una gota dorada (#E8A21C) como marca sobre el
cuerpo del bidon. Fondo transparente.

Salida: build/icon.ico multi-resolucion (16, 32, 48, 64, 128, 256, 512).
Ejecutar: python build/make_icon.py
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw

OUTPUT_ICO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

# Paleta
BIDON_FILL = (27, 79, 114, 255)      # #1B4F72 azul petroleo
BIDON_DARK = (21, 68, 92, 255)       # #15445C azul marino (sombras/tapa)
BIDON_HIGHLIGHT = (52, 113, 154, 255)  # lighten para brillo lateral
GOTA_GOLD = (232, 162, 28, 255)      # #E8A21C dorado
GOTA_GOLD_DARK = (191, 130, 16, 255)  # sombra de la gota


def _draw_bidon(d: ImageDraw.ImageDraw, size: int) -> None:
    """Dibuja un bidon de aceite centrado en un canvas cuadrado de lado `size`."""
    # Coordenadas clave en proporcion del canvas
    margin = size * 0.18
    left = int(margin)
    right = int(size - margin)
    body_top = int(size * 0.30)
    body_bottom = int(size * 0.86)
    body_w = right - left
    radius = max(int(size * 0.10), 6)  # esquinas redondeadas del bidon

    # --- Cuerpo del bidon (rectangulo con esquinas redondeadas) ---
    d.rounded_rectangle(
        [(left, body_top), (right, body_bottom)],
        radius=radius,
        fill=BIDON_FILL,
    )

    # --- Brillo lateral izquierdo ---
    highlight_w = max(int(body_w * 0.12), 3)
    d.rounded_rectangle(
        [(left + int(body_w * 0.08), body_top + int(size * 0.04)),
         (left + int(body_w * 0.08) + highlight_w, body_bottom - int(size * 0.04))],
        radius=max(highlight_w // 2, 2),
        fill=BIDON_HIGHLIGHT,
    )

    # --- Tapa superior (cilindro chico) ---
    cap_w = int(body_w * 0.42)
    cap_h = int(size * 0.10)
    cap_x0 = left + (body_w - cap_w) // 2
    cap_y0 = body_top - cap_h + max(2, cap_h // 6)  # leve solapamiento
    d.rounded_rectangle(
        [(cap_x0, cap_y0), (cap_x0 + cap_w, cap_y0 + cap_h)],
        radius=max(cap_h // 3, 3),
        fill=BIDON_DARK,
    )

    # --- Mango superior (arco) ---
    handle_w = int(body_w * 0.55)
    handle_h = int(size * 0.12)
    handle_x0 = left + (body_w - handle_w) // 2
    handle_y0 = cap_y0 - handle_h + max(2, handle_h // 6)
    handle_thickness = max(int(size * 0.025), 3)
    # Dibujamos el mango como rounded rectangle hueco
    d.rounded_rectangle(
        [(handle_x0, handle_y0), (handle_x0 + handle_w, handle_y0 + handle_h)],
        radius=handle_thickness,
        outline=BIDON_DARK,
        width=handle_thickness,
    )

    # --- Linea de la etiqueta (franja horizontal clara) ---
    label_y0 = int(body_top + (body_bottom - body_top) * 0.42)
    label_y1 = int(body_top + (body_bottom - body_top) * 0.70)
    # Fondo de la etiqueta: un sub-rectangulo mas claro
    label_pad = max(int(body_w * 0.06), 3)
    d.rounded_rectangle(
        [(left + label_pad, label_y0), (right - label_pad, label_y1)],
        radius=max((label_y1 - label_y0) // 4, 2),
        fill=BIDON_DARK,
    )

    # --- Gota dorada centrada en la etiqueta como marca ---
    gota_cx = size // 2
    gota_cy = (label_y0 + label_y1) // 2
    gota_h = max(int((label_y1 - label_y0) * 0.78), 6)
    gota_w = max(int(gota_h * 0.66), 4)
    _draw_drop(d, gota_cx, gota_cy, gota_w, gota_h, GOTA_GOLD, GOTA_GOLD_DARK)


def _draw_drop(d: ImageDraw.ImageDraw, cx: int, cy: int, w: int, h: int,
               fill: tuple, outline: tuple) -> None:
    """Dibuja una gota (lagrima) de ancho w y alto h centrada en (cx, cy).

    Forma: punta arriba, parte redonda abajo. Construida como un arco
    superior (punta) + un ovalo inferior.
    """
    half_w = w / 2.0
    top_y = cy - h / 2
    bot_y = cy + h / 2

    # Parte inferior: elipse
    ellipse_radius = w / 2
    ellipse_h = h * 0.70
    ellipse_cy = cy + h * 0.10
    e_left = cx - ellipse_radius
    e_top = ellipse_cy - ellipse_h / 2
    e_right = cx + ellipse_radius
    e_bot = ellipse_cy + ellipse_h / 2

    # Puntero de puntos para la parte de la punta (triangulo curvo)
    # Usamos un poligono que aproxima la parte superior de la gota
    points = [(cx, top_y)]
    steps = 16
    for i in range(1, steps + 1):
        t = i / steps
        # ancho maximo a mitad de camino
        span = ellipse_radius * (1 - (2 * t - 1) ** 2)
        y = top_y + (ellipse_cy - ellipse_h / 2 - top_y) * t
        points.append((cx - span, y))
    for i in range(steps, -1, -1):
        t = i / steps
        span = ellipse_radius * (1 - (2 * t - 1) ** 2)
        y = top_y + (ellipse_cy - ellipse_h / 2 - top_y) * t
        points.append((cx + span, y))
    points.append((cx, top_y))

    # Dibujar elipse (cuerpo)
    d.ellipse([(e_left, e_top), (e_right, e_bot)], fill=fill, outline=outline, width=max(1, w // 24))
    # Dibujar cabeza (punta)
    d.polygon(points, fill=fill)


def render_master(size: int = 512) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _draw_bidon(d, size)
    return img


def main() -> None:
    img = render_master(512)
    sizes = [16, 32, 48, 64, 128, 256, 512]
    img.save(OUTPUT_ICO, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"Icono generado: {OUTPUT_ICO}")
    print(f"Tamano archivo: {os.path.getsize(OUTPUT_ICO)} bytes")
    print(f"Resoluciones embebidas: {sizes}")


if __name__ == "__main__":
    main()
