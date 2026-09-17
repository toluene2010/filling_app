[app]
title = Filling Daily Entry
package.name = fillingsentry
package.domain = com.fillingerentry
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

android.api = 31
android.minapi = 21
android.archs = arm64-v8a

android.allow_backup = True
android.accept_sdk_license = True
android.permissions = INTERNET

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
