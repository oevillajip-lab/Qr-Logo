[app]
title = QR Logo Pro
package.name = qrlogopro
package.domain = com.comagro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.3.0,pillow,qrcode
orientation = portrait
osx.python_version = 3
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

# ESTO ES LO NUEVO PARA ARREGLAR EL ERROR:
# Forzamos la rama master de p4a que tiene los parches arreglados
p4a.branch = master
# Forzamos una versión de NDK que sabemos que funciona con Kivy
android.ndk = 25b
# Desactivamos la copia de librerias que a veces falla
android.copy_libs = 1
# Usamos SDL2 como bootstrap (motor)
p4a.bootstrap = sdl2
