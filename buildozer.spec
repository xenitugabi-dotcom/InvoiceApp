[app]
# (str) Title of your application
title = InvoiceApp

# (str) Package name
package.name = invoiceapp

# (str) Package domain (unique reverse-domain format)
package.domain = org.xenitugabi

# (str) Source code directory
source.dir = .

# (list) Include these file types in the APK
source.include_exts = py,png,jpg,kv,json,txt

# (str) Application versioning
version = 1.0.0

# (str) Application entry point
main.py

# (list) Application requirements
requirements = python3,kivy,pillow,requests

# (str) Presplash and icon
icon.filename = assets/icons/product.png
presplash.filename = assets/icons/sales.png

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (list) Permissions your app needs
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (bool) Hide the title bar
android.hide_titlebar = 0

# (int) Target Android API (use stable one)
android.api = 33

# (int) Minimum supported Android API
android.minapi = 21

# (int) Android NDK API
android.ndk_api = 21

# (str) Android NDK version
android.ndk = 25b

# (str) Android SDK version
android.sdk = 33

# (str) Entry point for your app
entrypoint = main.py

# (str) Architecture(s)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable zlib support explicitly
android.add_libs_armeabi_v7a = /data/data/com.termux/files/usr/lib/libz.so
android.add_libs_arm64_v8a = /data/data/com.termux/files/usr/lib/libz.so

# (bool) Copy libraries into apk
android.copy_libs = 1

# (bool) Include source code in APK (debug mode)
android.debug = 1
