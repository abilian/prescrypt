from pathlib import Path

from prescrypt.stdlib_js import StdlibJs

stdlib_js = StdlibJs().get_full_std_lib()
dst_file = Path(__file__).parent / ".." / "stdlibjs" / "_stdlib.js"
dst_file.write_text(stdlib_js)
