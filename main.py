import flet as ft
import qrcode
from PIL import Image, ImageDraw, ImageOps
import base64
import io
import os
import traceback

def hex_to_rgb(h):
    try:
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except: return (0, 0, 0)

def generar_qr(data, logo_path, estilo):
    try:
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=0)
        qr.add_data(data); qr.make(fit=True)
        matrix = qr.get_matrix(); modules = len(matrix); size = modules * 40
        
        mask = Image.new("L", (size, size), 0); draw = ImageDraw.Draw(mask)
        
        for r in range(modules):
            for c in range(modules):
                if matrix[r][c]:
                    x, y = c * 40, r * 40
                    if estilo == "Circular (Puntos)": draw.ellipse([x, y, x+40, y+40], fill=255)
                    elif estilo == "Liquid Pro (Gusano)": draw.rounded_rectangle([x+2, y+2, x+38, y+38], radius=15, fill=255)
                    else: draw.rectangle([x, y, x+40, y+40], fill=255)

        qr_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        qr_color = Image.new("RGBA", (size, size), (0, 0, 0, 255))
        qr_img.paste(qr_color, (0, 0), mask)

        if logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo = ImageOps.contain(logo, (int(size * 0.25), int(size * 0.25)))
            pos = ((size - logo.width)//2, (size - logo.height)//2)
            qr_img.paste(logo, pos, logo)

        bg = Image.new("RGBA", (size + 80, size + 80), (255, 255, 255, 255))
        bg.paste(qr_img, (40, 40), qr_img)

        buf = io.BytesIO()
        bg.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode(), buf.getvalue()
    except: return None, None

def main(page: ft.Page):
    try:
        # --- CORRECCIÓN DE LA BARRA ROJA ---
        picker_logo = ft.FilePicker()
        picker_save = ft.FilePicker()
        
        # Primero al overlay
        page.overlay.append(picker_logo)
        page.overlay.append(picker_save)
        page.update() 

        page.title = "QR + Logo"
        page.theme_mode = "dark"
        page.bgcolor = "#111111"
        page.padding = 20
        page.scroll = "auto"

        qr_bytes = None
        logo_path = ft.Text(visible=False)

        # Funciones asignadas DESPUÉS de crear
        def on_logo_picked(e):
            if e.files:
                logo_path.value = e.files[0].path
                btn_logo.text = "Logo Cargado OK"
                btn_logo.bgcolor = "green"
                page.update()

        def on_save(e):
            if e.path and qr_bytes:
                with open(e.path, "wb") as f: f.write(qr_bytes)
                page.show_snack_bar(ft.SnackBar(ft.Text("¡Guardado!"), open=True))

        picker_logo.on_result = on_logo_picked
        picker_save.on_result = on_save

        txt_data = ft.TextField(label="Texto / Enlace", bgcolor="#222222")
        
        dd_style = ft.Dropdown(
            label="Estilo", value="Liquid Pro (Gusano)", bgcolor="#222222",
            options=[
                ft.dropdown.Option("Liquid Pro (Gusano)"),
                ft.dropdown.Option("Normal (Cuadrado)"),
                ft.dropdown.Option("Circular (Puntos)")
            ]
        )

        btn_logo = ft.ElevatedButton("Subir Logo", icon="image", bgcolor="#333333", color="white", on_click=lambda _: picker_logo.pick_files())
        
        img_preview = ft.Image(width=280, height=280, visible=False, fit="contain")
        
        btn_save = ft.ElevatedButton("Guardar", icon="save", disabled=True, bgcolor="blue", color="white", on_click=lambda _: picker_save.save_file(file_name="qr.png"))

        def generar(e):
            nonlocal qr_bytes
            if not txt_data.value: return
            b64, binary = generar_qr(txt_data.value, logo_path.value, dd_style.value)
            if b64:
                qr_bytes = binary
                img_preview.src_base64 = b64
                img_preview.visible = True
                btn_save.disabled = False
                page.update()

        btn_gen = ft.ElevatedButton("GENERAR QR", bgcolor="green", color="white", height=50, on_click=generar)

        page.add(ft.Column([
            ft.Text("QR + Logo Pro", size=24, weight="bold", color="white"),
            txt_data, dd_style, btn_logo, ft.Divider(), btn_gen, 
            ft.Container(content=img_preview, alignment=ft.alignment.center), btn_save
        ], spacing=15))

    except Exception as e:
        page.add(ft.Text(f"ERROR: {e}", color="red"))

ft.app(target=main, assets_dir="assets")
