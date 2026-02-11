from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.graphics import Color, RoundedRectangle
import qrcode
from PIL import Image as PilImage, ImageDraw, ImageOps, ImageFilter
import io
import os
import base64
from kivy.utils import platform

# --- PERMISOS ANDROID ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

# ============================================================================
# 1. MOTOR GRÁFICO PRO (TU LÓGICA INTACTA)
# ============================================================================
# ... (Este bloque es idéntico al anterior, no lo toco) ...
def hex_to_rgb(hex_col):
    try:
        h = hex_col.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except:
        return (0, 0, 0)

def crear_fondo(w, h, mode, c1, c2, direction):
    if mode == "Transparente": return PilImage.new("RGBA", (w, h), (0, 0, 0, 0))
    elif mode == "Blanco (Default)": return PilImage.new("RGBA", (w, h), (255, 255, 255, 255))
    elif mode == "Sólido (Color)": return PilImage.new("RGBA", (w, h), c1 + (255,)) 
    elif mode == "Degradado":
        base = PilImage.new("RGB", (w, h), c1)
        draw = ImageDraw.Draw(base)
        if direction == "Vertical":
            for y in range(h):
                r = y / h
                col = tuple(int(c1[j] * (1 - r) + c2[j] * r) for j in range(3))
                draw.line([(0, y), (w, y)], fill=col)
        elif direction == "Horizontal":
            for x in range(w):
                r = x / w
                col = tuple(int(c1[j] * (1 - r) + c2[j] * r) for j in range(3))
                draw.line([(x, 0), (x, h)], fill=col)
        elif direction == "Diagonal":
            steps = w + h
            for i in range(steps):
                r = i / steps
                col = tuple(int(c1[j] * (1 - r) + c2[j] * r) for j in range(3))
                x0, y0 = 0, i; x1, y1 = i, 0
                if y0 > h: x0 = y0 - h; y0 = h
                if x1 > w: y1 = x1 - w; x1 = w
                draw.line([(x0, y0), (x1, y1)], fill=col, width=2)
        return base.convert("RGBA")
    return PilImage.new("RGBA", (w, h), (255, 255, 255, 255))

def generar_qr_full_engine(params, data_string):
    logo_path = params['logo_path']; estilo = params['estilo']
    modo_color_qr = params['modo_color_qr']
    qr_body_c1 = hex_to_rgb(params['c1']); qr_body_c2 = hex_to_rgb(params['c2'])
    usar_ojos = params['usar_ojos']
    eye_ext = hex_to_rgb(params['eye_ext']); eye_int = hex_to_rgb(params['eye_int'])
    modo_fondo = params['modo_fondo']
    bg_c1 = hex_to_rgb(params['bg_c1']); bg_c2 = hex_to_rgb(params['bg_c2'])
    grad_dir_bg = params['grad_dir_bg']; grad_dir_qr = params['grad_dir_qr']
    
    usar_logo = False
    if logo_path and os.path.exists(logo_path): usar_logo = True

    try:
        qr_temp = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=0)
        qr_temp.add_data(data_string); qr_temp.make(fit=True)
        matrix = qr_temp.get_matrix(); modules = len(matrix); size = modules * 40
        
        if usar_logo:
            logo_src = PilImage.open(logo_path).convert("RGBA")
            bbox = logo_src.getbbox()
            if bbox: logo_src = logo_src.crop(bbox)
            w_orig, h_orig = logo_src.size
            if w_orig > (h_orig * 1.4): logo_res = ImageOps.contain(logo_src, (int(size * 0.45), int(size * 0.20)))
            else: logo_res = ImageOps.contain(logo_src, (int(size * 0.23), int(size * 0.23)))
            l_pos = ((size - logo_res.width) // 2, (size - logo_res.height) // 2)
        else:
            logo_res = PilImage.new("RGBA", (1,1), (0,0,0,0)); l_pos = (0,0)

        base_mask = PilImage.new("L", (size, size), 0)
        if usar_logo:
            base_mask.paste(logo_res.split()[3], l_pos)
            ImageDraw.floodfill(base_mask, (0, 0), 128) 
            solid_mask = base_mask.point(lambda p: 0 if p == 128 else 255)
            aura_mask = solid_mask.filter(ImageFilter.MaxFilter((40 * 2) + 1)); aura_pixels = aura_mask.load()
        else: aura_pixels = base_mask.load()

        def get_m(r, c):
            if 0 <= r < modules and 0 <= c < modules:
                if usar_logo and aura_pixels[c * 40 + 20, r * 40 + 20] > 20: return False
                return matrix[r][c]
            return False

        def es_ojo_general(r, c): return (r<7 and c<7) or (r<7 and c>=modules-7) or (r>=modules-7 and c<7)
        def es_ojo_externo(r, c):
            if not es_ojo_general(r, c): return False
            if r<7 and c<7: lr,lc=r,c
            elif r<7 and c>=modules-7: lr,lc=r,c-(modules-7)
            else: lr,lc=r-(modules-7),c
            if 2<=lr<=4 and 2<=lc<=4: return False 
            return True 
        def es_ojo_interno(r, c):
            if not es_ojo_general(r, c): return False
            if r<7 and c<7: lr,lc=r,c
            elif r<7 and c>=modules-7: lr,lc=r,c-(modules-7)
            else: lr,lc=r-(modules-7),c
            if 2<=lr<=4 and 2<=lc<=4: return True
            return False

        mask_body = PilImage.new("L", (size, size), 0); draw_b = ImageDraw.Draw(mask_body)
        mask_ext = PilImage.new("L", (size, size), 0); draw_ext = ImageDraw.Draw(mask_ext)
        mask_int = PilImage.new("L", (size, size), 0); draw_int = ImageDraw.Draw(mask_int)
        RAD_LIQUID = 18; PAD = 2

        for r in range(modules):
            for c in range(modules):
                x, y = c * 40, r * 40
                
                if es_ojo_general(r, c):
                    if estilo == "Circular (Puntos)": 
                        continue 
                    if matrix[r][c]:
                        if es_ojo_interno(r,c): draw_int.rectangle([x, y, x+40, y+40], fill=255)
                        else: draw_ext.rectangle([x, y, x+40, y+40], fill=255)
                    continue

                if es_ojo_interno(r, c): draw = draw_int
                elif es_ojo_externo(r, c): draw = draw_ext
                else: draw = draw_b

                if estilo == "Liquid Pro (Gusano)":
                    if get_m(r, c):
                        draw.rounded_rectangle([x+PAD, y+PAD, x+40-PAD, y+40-PAD], radius=RAD_LIQUID, fill=255)
                        if get_m(r, c+1): draw.rounded_rectangle([x+PAD, y+PAD, x+80-PAD, y+40-PAD], radius=RAD_LIQUID, fill=255)
                        if get_m(r+1, c): draw.rounded_rectangle([x+PAD, y+PAD, x+40-PAD, y+80-PAD], radius=RAD_LIQUID, fill=255)
                        if get_m(r, c+1) and get_m(r+1, c) and get_m(r+1, c+1): draw.rectangle([x+20, y+20, x+60, y+60], fill=255)
                elif estilo == "Normal (Cuadrado)":
                    if get_m(r, c): draw.rectangle([x, y, x+40, y+40], fill=255)
                elif estilo == "Barras (Vertical)":
                    if get_m(r, c):
                        if es_ojo_general(r,c): draw.rectangle([x, y, x+40, y+40], fill=255)
                        else:
                            draw.rounded_rectangle([x+4, y, x+36, y+40], radius=10, fill=255)
                            if get_m(r+1, c) and not es_ojo_general(r+1, c): draw.rectangle([x+4, y+20, x+36, y+60], fill=255)
                elif estilo == "Circular (Puntos)":
                    if get_m(r, c): draw.ellipse([x+1, y+1, x+39, y+39], fill=255)

        if estilo == "Circular (Puntos)":
            def draw_geo_eye(r_start, c_start):
                x = c_start * 40; y = r_start * 40; s = 7 * 40
                draw_ext.ellipse([x, y, x+s, y+s], fill=255)
                draw_ext.ellipse([x+40, y+40, x+s-40, y+s-40], fill=0)
                draw_int.ellipse([x+80, y+80, x+s-80, y+s-80], fill=255)
            draw_geo_eye(0, 0); draw_geo_eye(0, modules-7); draw_geo_eye(modules-7, 0)

        img_body_color = PilImage.new("RGBA", (size, size), (0,0,0,0)); draw_grad = ImageDraw.Draw(img_body_color)
        color_final_1 = qr_body_c1; color_final_2 = qr_body_c2
        
        if modo_color_qr == "Automático (Logo)" and usar_logo:
            try: c_s = logo_res.resize((1,1)).getpixel((0,0))[:3]; color_final_1 = (0,0,0); color_final_2 = c_s
            except: pass

        if modo_color_qr == "Sólido (Un Color)": draw_grad.rectangle([0,0,size,size], fill=color_final_1 + (255,))
        else: 
            for i in range(size):
                r = i/size; col = tuple(int(color_final_1[j]*(1-r) + color_final_2[j]*r) for j in range(3)) + (255,)
                if grad_dir_qr == "Vertical": draw_grad.line([(0,i),(size,i)], fill=col)
                elif grad_dir_qr == "Horizontal": draw_grad.line([(i,0),(i,size)], fill=col)
                elif grad_dir_qr == "Diagonal": draw_grad.line([(i,0),(i,size)], fill=col) 

        if usar_ojos: img_ext_color = PilImage.new("RGBA", (size, size), eye_ext + (255,)); img_int_color = PilImage.new("RGBA", (size, size), eye_int + (255,))
        else: img_ext_color = img_body_color; img_int_color = img_body_color

        qr_layer = PilImage.new("RGBA", (size, size), (0,0,0,0))
        qr_layer.paste(img_body_color, (0,0), mask=mask_body)
        qr_layer.paste(img_ext_color, (0,0), mask=mask_ext)
        qr_layer.paste(img_int_color, (0,0), mask=mask_int)

        if usar_logo: qr_layer.paste(logo_res, l_pos, logo_res)

        BORDER = 40; full_size = size + (BORDER * 2)
        canvas_final = crear_fondo(full_size, full_size, modo_fondo, bg_c1, bg_c2, grad_dir_bg)
        canvas_final.paste(qr_layer, (BORDER, BORDER), mask=qr_layer)
        return canvas_final

    except Exception as e:
        print(f"Error: {e}")
        return None

# ============================================================================
# 2. INTERFAZ NATIVA MEJORADA
# ============================================================================

# Colores del Tema
BG_COLOR = get_color_from_hex("#121212")
CARD_COLOR = get_color_from_hex("#1E1E1E")
TEXT_COLOR = get_color_from_hex("#FFFFFF")
ACCENT_COLOR = get_color_from_hex("#00C853") # Verde moderno
INPUT_BG = get_color_from_hex("#2C2C2C")

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0,0,0,0) # Transparente para usar canvas
        self.bg_color_norm = ACCENT_COLOR

    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color_norm)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = INPUT_BG
        self.foreground_color = TEXT_COLOR
        self.cursor_color = ACCENT_COLOR
        self.hint_text_color = (0.6, 0.6, 0.6, 1)
        self.padding = [10, 10]
        self.background_normal = ''
        self.background_active = ''
        
class QRApp(App):
    def build(self):
        Window.clearcolor = BG_COLOR
        self.root = BoxLayout(orientation='vertical')
        
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20, padding=20)
        content.bind(minimum_height=content.setter('height'))

        # Header moderno
        header = Label(text="QR Pro Generator", font_size='28sp', size_hint_y=None, height=60, bold=True, color=TEXT_COLOR)
        content.add_widget(header)

        # --- SECCION 1: CONTENIDO ---
        self.add_section_title(content, "1. Contenido")
        
        self.spin_tipo = Spinner(text="Sitio Web (URL)", values=("Sitio Web (URL)", "Red WiFi", "Texto Libre", "Teléfono", "E-mail"), size_hint_y=None, height=50, background_color=CARD_COLOR, color=TEXT_COLOR)
        self.spin_tipo.bind(text=self.update_inputs)
        content.add_widget(self.spin_tipo)

        self.txt_1 = StyledTextInput(hint_text="Enlace (URL)", size_hint_y=None, height=50)
        content.add_widget(self.txt_1)

        self.txt_2 = StyledTextInput(hint_text="Campo 2", size_hint_y=None, height=0, opacity=0)
        content.add_widget(self.txt_2)

        self.txt_msg = StyledTextInput(hint_text="Mensaje", multiline=True, size_hint_y=None, height=0, opacity=0)
        content.add_widget(self.txt_msg)

        # --- SECCION 2: ESTILO ---
        self.add_section_title(content, "2. Estilo & Color")
        self.spin_estilo = Spinner(text="Liquid Pro (Gusano)", values=("Liquid Pro (Gusano)", "Normal (Cuadrado)", "Barras (Vertical)", "Circular (Puntos)"), size_hint_y=None, height=50, background_color=CARD_COLOR, color=TEXT_COLOR)
        content.add_widget(self.spin_estilo)

        self.spin_modo = Spinner(text="Automático (Logo)", values=("Automático (Logo)", "Sólido (Un Color)", "Degradado Custom"), size_hint_y=None, height=50, background_color=CARD_COLOR, color=TEXT_COLOR)
        content.add_widget(self.spin_modo)

        grid_colors = GridLayout(cols=2, spacing=10, size_hint_y=None, height=60)
        self.btn_c1 = Button(text="Color 1", background_color=get_color_from_hex("#000000"))
        self.btn_c1.bind(on_release=lambda x: self.open_color_picker(self.btn_c1))
        self.btn_c2 = Button(text="Color 2", background_color=get_color_from_hex("#3399ff"))
        self.btn_c2.bind(on_release=lambda x: self.open_color_picker(self.btn_c2))
        grid_colors.add_widget(self.btn_c1); grid_colors.add_widget(self.btn_c2)
        content.add_widget(grid_colors)

        # --- SECCION 3 & 4: OJOS Y FONDO (Simplificado visualmente) ---
        self.add_section_title(content, "3. Ojos y Fondo")
        self.spin_ojos = Spinner(text="Ojos: Igual al Cuerpo", values=("Ojos: Igual al Cuerpo", "Ojos: Personalizados"), size_hint_y=None, height=50, background_color=CARD_COLOR)
        content.add_widget(self.spin_ojos)
        
        self.spin_bg = Spinner(text="Fondo: Blanco", values=("Fondo: Blanco", "Fondo: Transparente", "Fondo: Sólido"), size_hint_y=None, height=50, background_color=CARD_COLOR)
        content.add_widget(self.spin_bg)

        # --- SECCION 5: LOGO ---
        self.add_section_title(content, "4. Logo Personalizado")
        self.btn_logo = Button(text="SELECCIONAR IMAGEN", size_hint_y=None, height=50, background_color=CARD_COLOR, color=TEXT_COLOR)
        self.btn_logo.bind(on_release=self.show_file_chooser)
        content.add_widget(self.btn_logo)
        self.logo_path_val = ""

        # --- GENERAR ---
        self.btn_gen = RoundedButton(text="GENERAR QR AHORA", size_hint_y=None, height=65, bold=True, font_size='18sp')
        self.btn_gen.bind(on_release=self.generar)
        content.add_widget(self.btn_gen)

        # --- IMAGEN RESULTADO ---
        self.img_container = BoxLayout(padding=10, size_hint_y=None, height=320)
        self.img_qr = Image(allow_stretch=True, keep_ratio=True)
        self.img_container.add_widget(self.img_qr)
        content.add_widget(self.img_container)

        # --- GUARDAR ---
        self.btn_save = Button(text="GUARDAR IMAGEN", disabled=True, size_hint_y=None, height=50, background_color=get_color_from_hex("#007BFF"))
        self.btn_save.bind(on_release=self.save_image)
        content.add_widget(self.btn_save)

        scroll.add_widget(content)
        self.root.add_widget(scroll)
        return self.root

    def add_section_title(self, layout, text):
        layout.add_widget(Label(text=text, color=ACCENT_COLOR, size_hint_y=None, height=35, halign='left', text_size=(Window.width-60, None), bold=True))

    # --- ARREGLO DEL SELECTOR DE ARCHIVOS ---
    def show_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # IMPORTANTE: Filtros para ver solo imágenes
        fc = FileChooserIconView(path='/storage/emulated/0/Download', filters=['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG'])
        
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_cancel = Button(text="Cancelar", background_color=(0.5,0,0,1))
        btn_select = Button(text="Seleccionar", background_color=(0,0.5,0,1))
        
        popup = Popup(title='Elige tu Logo (Imágenes)', content=content, size_hint=(0.95, 0.9))
        
        def select(instance):
            if fc.selection:
                self.logo_path_val = fc.selection[0]
                self.btn_logo.text = f"Logo: {os.path.basename(self.logo_path_val)}"
                self.btn_logo.background_color = get_color_from_hex("#006400")
                popup.dismiss()
        
        btn_cancel.bind(on_release=popup.dismiss)
        btn_select.bind(on_release=select)
        
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_select)
        content.add_widget(fc)
        content.add_widget(btn_box)
        popup.open()

    # --- LOGICA UI (Resto igual) ---
    def update_inputs(self, spinner, text):
        self.txt_2.height = 0; self.txt_2.opacity = 0; self.txt_msg.height = 0; self.txt_msg.opacity = 0
        self.txt_1.hint_text = "Texto"; self.txt_1.height = 50; self.txt_1.opacity = 1
        
        if text == "Sitio Web (URL)": self.txt_1.hint_text = "Enlace URL"
        elif text == "Red WiFi":
            self.txt_1.hint_text = "SSID (Nombre WiFi)"
            self.txt_2.height = 50; self.txt_2.opacity = 1; self.txt_2.hint_text = "Contraseña"
        elif text == "Texto Libre":
            self.txt_1.height = 0; self.txt_1.opacity = 0
            self.txt_msg.height = 100; self.txt_msg.opacity = 1
        elif text == "Teléfono": self.txt_1.hint_text = "Número (+595...)"
        elif text == "E-mail":
            self.txt_1.hint_text = "Correo"; self.txt_msg.height = 100; self.txt_msg.opacity = 1; self.txt_msg.hint_text = "Mensaje"

    def open_color_picker(self, target_btn):
        content = GridLayout(cols=4, spacing=5, padding=5)
        colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#333333", "#FFA500", "#800080", "#CCCCCC"]
        popup = Popup(title='Selecciona Color', size_hint=(0.8, 0.4), background_color=CARD_COLOR)
        def set_col(instance):
            target_btn.background_color = instance.background_color
            popup.dismiss()
        for c in colors:
            btn = Button(background_color=get_color_from_hex(c))
            btn.bind(on_release=set_col)
            content.add_widget(btn)
        popup.content = content; popup.open()

    def generar(self, instance):
        t = self.spin_tipo.text; data = ""
        if t == "Sitio Web (URL)": data = self.txt_1.text
        elif t == "Texto Libre": data = self.txt_msg.text
        elif t == "Red WiFi": data = f"WIFI:T:WPA;S:{self.txt_1.text};P:{self.txt_2.text};;"
        elif t == "Teléfono": data = f"tel:{self.txt_1.text}"
        elif t == "E-mail": data = f"mailto:{self.txt_1.text}?body={self.txt_msg.text}"
        if not data: return

        c1 = get_hex_from_color(self.btn_c1.background_color)
        c2 = get_hex_from_color(self.btn_c2.background_color)
        bg_mode = self.spin_bg.text.replace("Fondo: ", "")
        bg_mode = "Blanco (Default)" if bg_mode == "Blanco" else ("Sólido (Color)" if bg_mode == "Sólido" else bg_mode)

        params = {
            'logo_path': self.logo_path_val, 'estilo': self.spin_estilo.text,
            'modo_color_qr': self.spin_modo.text, 'c1': c1, 'c2': c2, 'grad_dir_qr': "Vertical",
            'usar_ojos': (self.spin_ojos.text == "Ojos: Personalizados"), 'eye_ext': c1, 'eye_int': c1,
            'modo_fondo': bg_mode, 'bg_c1': "#FFFFFF", 'bg_c2': "#FFFFFF", 'grad_dir_bg': "Vertical"
        }

        pil_image = generar_qr_full_engine(params, data)
        if pil_image:
            temp_path = os.path.join(App.get_running_app().user_data_dir, "temp_qr.png")
            pil_image.save(temp_path)
            self.img_qr.source = temp_path
            self.img_qr.reload()
            self.btn_save.disabled = False
            self.last_pil_image = pil_image

    def save_image(self, instance):
        if hasattr(self, 'last_pil_image'):
            path = "/storage/emulated/0/Download/qr_gen_pro.png"
            try:
                self.last_pil_image.save(path)
                self.btn_save.text = f"¡GUARDADO! (Ver Descargas)"
                self.btn_save.background_color = ACCENT_COLOR
            except Exception as e:
                self.btn_save.text = f"Error al guardar: {e}"

if __name__ == '__main__':
    QRApp().run()
