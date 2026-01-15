# Module System

Prescrypt supports Python's import system and generates ES6 modules for multi-file projects.

## Enabling Module Mode

For multi-file projects, enable module mode:

```bash
# Single file with exports
py2js app.py -m

# Directory (module mode automatic)
py2js src/ -o dist/
```

## Import Syntax

### Importing Local Modules

```python
# Import entire module
import utils
utils.helper()

# Import specific names
from utils import helper, process
helper()

# Import with alias
from utils import helper as h
h()

# Import all (discouraged)
from utils import *
```

**Compiles to ES6:**

```javascript
import * as utils from './utils.js';
utils.helper();

import { helper, process } from './utils.js';
helper();

import { helper as h } from './utils.js';
h();

import * as _star from './utils.js';
// names merged into scope
```

### Relative Imports

```python
# From parent package
from .. import config
from ..utils import helper

# From sibling module
from . import constants
from .helpers import format_date
```

**Compiles to:**

```javascript
import * as config from '../config.js';
import { helper } from '../utils.js';

import * as constants from './constants.js';
import { format_date } from './helpers.js';
```

## Exports

In module mode (`-m`), top-level definitions are exported:

```python
# config.py
VERSION = "1.0.0"
DEBUG = True

def configure(options):
    pass

class Settings:
    pass
```

**Compiles to:**

```javascript
// config.js
export const VERSION = "1.0.0";
export const DEBUG = true;

export function configure(options) {
    // ...
}

export const Settings = function() {
    // ...
};
```

### Controlling Exports

Use `__all__` to control what gets exported:

```python
__all__ = ["public_func", "PublicClass"]

def public_func():
    pass

def _private_func():  # Not exported (leading underscore)
    pass

class PublicClass:
    pass
```

!!! note "Leading Underscore Convention"
    Names starting with `_` are not exported by default, matching Python convention.

## Module Search Path

Prescrypt searches for modules in:

1. The directory containing the source file
2. Directories specified with `-M`/`--module-path`
3. The project source directory (for directory compilation)

```bash
# Add additional module paths
py2js src/ -o dist/ -M lib/ -M vendor/
```

## Package Structure

### `__init__.py` Files

`__init__.py` files become `index.js`:

```
mypackage/
├── __init__.py    → index.js
├── core.py        → core.js
└── utils.py       → utils.js
```

### Importing Packages

```python
# Import package (uses __init__.py)
import mypackage
mypackage.main()

# Import from package
from mypackage import core
from mypackage.utils import helper
```

**Compiles to:**

```javascript
import * as mypackage from './mypackage/index.js';
mypackage.main();

import * as core from './mypackage/core.js';
import { helper } from './mypackage/utils.js';
```

## Running Generated Modules

### Node.js

Create a `package.json` with ES6 modules enabled:

```json
{
  "type": "module"
}
```

Then run:

```bash
node dist/main.js
```

### Browser

Use ES6 module script tags:

```html
<script type="module" src="dist/main.js"></script>
```

Or with import maps:

```html
<script type="importmap">
{
  "imports": {
    "myapp/": "./dist/"
  }
}
</script>
<script type="module">
import { main } from 'myapp/main.js';
main();
</script>
```

## Circular Imports

Prescrypt handles circular imports the same way JavaScript does:

```python
# a.py
from b import func_b

def func_a():
    return func_b()

# b.py
from a import func_a

def func_b():
    return func_a()
```

!!! warning "Circular Import Limitations"
    Circular imports can cause issues if you try to use imported values at module initialization time. Call imported functions inside other functions to avoid problems.

## Best Practices

!!! tip "Organize by Feature"
    Group related code in packages:
    ```
    myapp/
    ├── models/
    │   ├── __init__.py
    │   └── user.py
    ├── views/
    │   ├── __init__.py
    │   └── home.py
    └── main.py
    ```

!!! tip "Use Explicit Imports"
    Prefer `from module import name` over `import module` for clearer dependencies and better tree-shaking.

!!! tip "Avoid `from x import *`"
    Star imports make it hard to track where names come from and can cause naming conflicts.

## See Also

- [CLI Reference](cli.md) - Module path options
- [JavaScript Interop](js-interop.md) - Importing JavaScript modules
- [Multi-file Example](../examples/multi-file.md) - Complete project example
