[app]
title = My Kivy App
package.name = mykivyapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# تثبيت إصدارات مستقرة ومتوافقة 100% مع الأندرويد والـ Cython
requirements = python3==3.10.11, hostpython3==3.10.11, kivy==2.3.0, opencv-python-headless, requests

orientation = portrait
fullscreen = 1

# هنركز على المعمارية الأحدث والمطلوبة حالياً عشان نسرع البناء ونمنع التضارب
android.archs = arm64-v8a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
