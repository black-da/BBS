"""
复制前6行就可以创造一个测试py文件的脚本
"""
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BBS.settings")
    import django
    django.setup()
    import uuid
    for i in range(4):
        print(uuid.uuid4())