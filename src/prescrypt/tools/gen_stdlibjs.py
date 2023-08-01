from pathlib import Path

from prescrypt.stdlib_js import (FUNCTION_PREFIX, METHOD_PREFIX,
                                 get_full_std_lib)

stdlib_js = get_full_std_lib()

# functions = Path(__file__).parent / ".." / "stdlibjs" / "functions.js"
# methods = Path(__file__).parent / ".." / "stdlibjs" / "methods.js"
#
# functions_js = functions.read_text()
# methods_js = methods.read_text()
#
# functions_js = functions_js.replace("FUNCTION_PREFIX", FUNCTION_PREFIX)
# methods_js = methods_js.replace("METHOD_PREFIX", METHOD_PREFIX)
#
# stdlib_js = functions_js + "\n\n" + methods_js

(Path(__file__).parent / ".." / "stdlibjs" / "_stdlib.js").write_text(stdlib_js)
