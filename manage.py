#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _disable_quickedit():
    """
    Отключает режим QuickEdit в Windows-консоли.
    QuickEdit позволяет выделять текст в консоли, но при этом блокирует
    запись в stdout, что приводит к зависанию сервера Django во время
    выделения текста в терминале.
    """
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        import ctypes.wintypes

        kernel32 = ctypes.windll.kernel32
        STD_INPUT_HANDLE = -10
        ENABLE_QUICK_EDIT_MODE = 0x0040
        ENABLE_EXTENDED_FLAGS = 0x0080

        handle = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        if handle == -1:
            return

        mode = ctypes.wintypes.DWORD()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return

        # Снимаем бит QuickEdit, выставляем EXTENDED_FLAGS
        new_mode = (mode.value & ~ENABLE_QUICK_EDIT_MODE) | ENABLE_EXTENDED_FLAGS
        kernel32.SetConsoleMode(handle, new_mode)
    except Exception:
        pass  # Игнорируем — не критично


def main():
    """Run administrative tasks."""
    _disable_quickedit()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SLEX_02.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
