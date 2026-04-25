#!/usr/bin/env python
"""أداة Django لإدارة المشروع"""
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lawfirm.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("تعذّر استيراد Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
