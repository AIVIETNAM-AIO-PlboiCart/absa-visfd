"""Gọi setup_console() ở đầu main() của MỌI script in tiếng Việt.

Console Windows mặc định dùng cp1252 -> print tiếng Việt có dấu sẽ lỗi UnicodeEncodeError.
"""
import sys


def setup_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
