# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['picCoder.py'],
             pathex=['C:\\Users\\michael.cvitanovich\\OneDrive - RCT\\MDC\\python\\picCoder'],
             binaries=[],
             datas=[('*.ui', '.'),('resources/*.png', 'resources')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('W ignore', None, 'OPTION')],
          name='picCoder',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          console=False,
		  icon='./picCoder.ico')
