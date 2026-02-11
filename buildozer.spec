[app]
title = QR Pro
package.name = qrlogopro
package.domain = com.comagro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# --- CAMBIOS AQUÍ (Icono y Precarga ACTIVADOS) ---
# El archivo icon.png debe existir en tu repositorio
icon.filename = icon.png
# Usamos el mismo icono para la pantalla de carga
presplash.filename = icon.png
presplash.background_color = #121212
# -----------------------------------------------

version = 1.1
requirements = python3,kivy==2.3.0,pillow,qrcode
orientation = portrait
osx.python_version = 3
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.copy_libs = 1
p4a.bootstrap = sdl2
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
