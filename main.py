import flet as ft
import qrcode
from PIL import Image, ImageDraw, ImageOps
import base64
import io
import os
import traceback

# --- MOTOR QR (Intacto) ---
def hex_to_rgb(h):
    try:
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    except: return (0, 0, 0)

def generar_qr(data, logo_path, estilo, c1_hex, c2_hex, bg_hex):
    try:
        # Colores
        c1 = hex_to_rgb(c1_hex)
        # Fondo
        bg_col = hex_to_rgb(bg_hex) + (255,)
        if bg_hex == "Transparente": bg_col = (0,0,0,0)

        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=0)
        qr.add_data(data); qr.make(fit=True)
        matrix = qr.get_matrix(); modules = len(matrix); size = modules * 40
        
        mask = Image.new("L", (size, size), 0); draw = ImageDraw.Draw(mask)
        
        for r in range(modules):
            for c in range(modules):
                if matrix[r][c]:
                    x, y = c * 40, r * 40
                    if estilo == "Circular": draw.ellipse([x, y, x+40, y+40], fill=255)
                    elif estilo == "Liquid": draw.rounded_rectangle([x+2, y+2, x+38, y+38], radius=15, fill=255)
                    else: draw.rectangle([x, y, x+40, y+40], fill=255)

        qr_img = Image.new("RGBA", (size, size), (0,0,0,0))
        qr_color = Image.new("RGBA", (size, size), c1 + (255,))
        qr_img.paste(qr_color, (0,0), mask)

        if logo_path and os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo = ImageOps.contain(logo, (int(size*0.25), int(size*0.25)))
            pos = ((size - logo.width)//2, (size - logo.height)//2)
            qr_img.paste(logo, pos, logo)

        final_bg = Image.new("RGBA", (size+80, size+80), bg_col)
        final_bg.paste(qr_img, (40, 40), qr_img)

        buf = io.BytesIO(); final_bg.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode(), buf.getvalue()
    except: return None, None

# --- APP ---
def main(page: ft.Page):
    page.title = "QR Generator"
    page.theme_mode = "dark"
    page.bgcolor = "#111111"
    page.padding = 20
    page.scroll = "auto"

    # 1. DEFINIR VARIABLES
    qr_data = {"bytes": None}
    logo_path = ft.Text(visible=False)
    
    # 2. DEFINIR PICKERS (SIN ARGUMENTOS)
    picker_logo = ft.FilePicker()
    picker_save = ft.FilePicker()
    
    # 3. AGREGAR A OVERLAY (CRUCIAL HACERLO ANTES DE USARLOS)
    page.overlay.extend([picker_logo, picker_save])

    # 4. DEFINIR FUNCIONES
    def on_logo(e):
        if e.files:
            logo_path.value = e.files[0].path
            btn_logo.text = "Logo Cargado!"
            btn_logo.bgcolor = "green"
            page.update()

    def on_save(e):
        if e.path and qr_data["bytes"]:
            with open(e.path, "wb") as f: f.write(qr_data["bytes"])
            page.snack_bar = ft.SnackBar(ft.Text("Guardado correctamente")); page.snack_bar.open = True
            page.update()

    # 5. ASIGNAR FUNCIONES (AHORA ES SEGURO)
    picker_logo.on_result = on_logo
    picker_save.on_result = on_save

    # 6. UI COMPONENTS
    txt_url = ft.TextField(label="Texto o URL", bgcolor="#222222")
    dd_style = ft.Dropdown(label="Estilo", value="Liquid", options=[
        ft.dropdown.Option("Liquid"), ft.dropdown.Option("Normal"), ft.dropdown.Option("Circular")
    ])
    
    # Colores simples para evitar errores
    color_qr = ft.Dropdown(label="Color QR", value="#000000", options=[
        ft.dropdown.Option("#000000", "Negro"), ft.dropdown.Option("#FFFFFF", "Blanco"), 
        ft.dropdown.Option("#0000FF", "Azul"), ft.dropdown.Option("#FF0000", "Rojo")
    ])
    
    btn_logo = ft.ElevatedButton("Subir Logo", icon="image", on_click=lambda _: picker_logo.pick_files())
    
    img_result = ft.Image(visible=False, fit="contain", width=280, height=280)
    
    btn_save = ft.ElevatedButton("Guardar", icon="save", disabled=True, on_click=lambda _: picker_save.save_file(file_name="qr.png"))

    def generar(e):
        if not txt_url.value: return
        
        b64, binary = generar_qr(txt_url.value, logo_path.value, dd_style.value, color_qr.value, None, "#FFFFFF")
        
        if b64:
            qr_data["bytes"] = binary
            img_result.src_base64 = b64
            img_result.visible = True
            btn_save.disabled = False
            page.update()

    btn_gen = ft.ElevatedButton("GENERAR", bgcolor="green", color="white", height=50, on_click=generar)

    # 7. AGREGAR A PÁGINA
    page.add(
        ft.Column([
            ft.Text("QR Creator Pro", size=24, weight="bold"),
            txt_url,
            ft.Row([dd_style, color_qr], alignment="spaceBetween"),
            btn_logo,
            ft.Divider(),
            btn_gen,
            ft.Container(content=img_result, alignment=ft.alignment.center),
            btn_save
        ], spacing=15)
    )

ft.app(target=main, assets_dir="assets")
