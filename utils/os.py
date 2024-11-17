# ⚠️ USE AT YOUR OWN RISK
# first: pip install pysqlite3-binary
# then in settings.py:

# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package

import platform
import os

def fix_trouble():
    if "Linux" in str(platform.system()):
        __import__('pysqlite3')
        import sys
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')