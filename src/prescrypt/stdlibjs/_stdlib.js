var _pyfunc_BaseException = (function() {
  // nargs: 0+
  function BaseException(...args) {
    if (!(this instanceof BaseException)) {
      return new BaseException(...args);
    }
    let message = args.length > 0 ? String(args[0]) : "";
    Error.call(this, message);
    this.name = "BaseException";
    this.message = message;
    // args is always a tuple (array without _is_list) containing all constructor arguments
    this.args = args;
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, BaseException);
    }
  }
  BaseException.prototype = Object.create(Error.prototype);
  BaseException.prototype.constructor = BaseException;
  return BaseException;
})();
var _pyfunc_Ellipsis = Symbol.for('Ellipsis');
var _pyfunc_Exception = (function() {
  // nargs: 0+
  function Exception(...args) {
    if (!(this instanceof Exception)) {
      return new Exception(...args);
    }
    _pyfunc_BaseException.call(this, ...args);
    this.name = "Exception";
  }
  Exception.prototype = Object.create(_pyfunc_BaseException.prototype);
  Exception.prototype.constructor = Exception;
  return Exception;
})();
var _pyfunc_AttributeError = (function() {
  // nargs: 0 1
  function AttributeError(message) {
    if (!(this instanceof AttributeError)) {
      return new AttributeError(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "AttributeError";
  }
  AttributeError.prototype = Object.create(_pyfunc_Exception.prototype);
  AttributeError.prototype.constructor = AttributeError;
  return AttributeError;
})();
var _pyfunc_GeneratorExit = (function() {
  // nargs: 0 1
  function GeneratorExit(message) {
    if (!(this instanceof GeneratorExit)) {
      return new GeneratorExit(message);
    }
    _pyfunc_BaseException.call(this, message);
    this.name = "GeneratorExit";
  }
  GeneratorExit.prototype = Object.create(_pyfunc_BaseException.prototype);
  GeneratorExit.prototype.constructor = GeneratorExit;
  return GeneratorExit;
})();
var _pyfunc_IndexError = (function() {
  // nargs: 0 1
  function IndexError(message) {
    if (!(this instanceof IndexError)) {
      return new IndexError(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "IndexError";
  }
  IndexError.prototype = Object.create(_pyfunc_Exception.prototype);
  IndexError.prototype.constructor = IndexError;
  return IndexError;
})();
var _pyfunc_KeyError = (function() {
  // nargs: 0 1
  function KeyError(message) {
    if (!(this instanceof KeyError)) {
      return new KeyError(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "KeyError";
  }
  KeyError.prototype = Object.create(_pyfunc_Exception.prototype);
  KeyError.prototype.constructor = KeyError;
  return KeyError;
})();
var _pyfunc_NameError = (function() {
  // nargs: 0 1
  function NameError(message) {
    if (!(this instanceof NameError)) {
      return new NameError(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "NameError";
  }
  NameError.prototype = Object.create(_pyfunc_Exception.prototype);
  NameError.prototype.constructor = NameError;
  return NameError;
})();
var _pyfunc_NotImplemented = Symbol.for('NotImplemented');
var _pyfunc_RuntimeError = (function() {
  // nargs: 0 1
  function RuntimeError(message) {
    if (!(this instanceof RuntimeError)) {
      return new RuntimeError(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "RuntimeError";
  }
  RuntimeError.prototype = Object.create(_pyfunc_Exception.prototype);
  RuntimeError.prototype.constructor = RuntimeError;
  return RuntimeError;
})();
var _pyfunc_StopIteration = (function() {
  // nargs: 0 1
  function StopIteration(message) {
    if (!(this instanceof StopIteration)) {
      return new StopIteration(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "StopIteration";
  }
  StopIteration.prototype = Object.create(_pyfunc_Exception.prototype);
  StopIteration.prototype.constructor = StopIteration;
  return StopIteration;
})();
var _pyfunc_TypeError_py = (function() {
  // nargs: 0 1
  function TypeError_py(message) {
    if (!(this instanceof TypeError_py)) {
      return new TypeError_py(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "TypeError";
  }
  TypeError_py.prototype = Object.create(_pyfunc_Exception.prototype);
  TypeError_py.prototype.constructor = TypeError_py;
  return TypeError_py;
})();
var _pyfunc_ValueError = (function() {
  // nargs: 0+
  function ValueError(...args) {
    if (!(this instanceof ValueError)) {
      return new ValueError(...args);
    }
    _pyfunc_Exception.call(this, ...args);
    this.name = "ValueError";
  }
  ValueError.prototype = Object.create(_pyfunc_Exception.prototype);
  ValueError.prototype.constructor = ValueError;
  return ValueError;
})();
var _pyfunc_abs = Math.abs;;
var _pyfunc_bytes_repr = function (bytes) {
  // nargs: 1
  // Return Python-style repr for bytes: b'...'
  let result = "b'";
  for (let i = 0; i < bytes.length; i++) {
    let b = bytes[i];
    if (b === 92) {  // backslash
      result += "\\\\";
    } else if (b === 39) {  // single quote
      result += "\\'";
    } else if (b === 10) {  // newline
      result += "\\n";
    } else if (b === 13) {  // carriage return
      result += "\\r";
    } else if (b === 9) {  // tab
      result += "\\t";
    } else if (b >= 32 && b < 127) {
      // Printable ASCII
      result += String.fromCharCode(b);
    } else {
      // Non-printable: use \xNN format
      result += "\\x" + b.toString(16).padStart(2, "0");
    }
  }
  result += "'";
  return result;
};
var _pyfunc_call_kwargs = function (func, args, kwargs) {
  // nargs: 3
  // Call a function with positional args and keyword args.
  // If the function has __args__ metadata (parameter names), use them to
  // map kwargs to positional arguments. Otherwise, try to call with
  // kwargs as a single argument (for functions expecting {flx_args, flx_kwargs}).

  // Get function's parameter names if available
  const paramNames = func.__args__;

  if (paramNames && Array.isArray(paramNames)) {
    // We have parameter metadata - map kwargs to positional args
    const positional = args.slice();  // Copy positional args

    // Fill in remaining parameters from kwargs
    for (let i = positional.length; i < paramNames.length; i++) {
      const paramName = paramNames[i];
      if (kwargs.hasOwnProperty(paramName)) {
        positional.push(kwargs[paramName]);
      } else {
        // Parameter not provided - let JS handle the default
        positional.push(undefined);
      }
    }

    return func.apply(null, positional);
  } else {
    // No metadata - fall back to passing kwargs object
    // This handles functions that expect {flx_args, flx_kwargs} format
    if (args.length === 0 && Object.keys(kwargs).length > 0) {
      return func({flx_args: args, flx_kwargs: kwargs});
    }
    return func.apply(null, args);
  }
};
var _pyfunc_callable = function (obj) {
  // nargs: 1
  // Return True if object is callable
  return typeof obj === "function" || (typeof obj === "object" && obj !== null && typeof obj.__call__ === "function");
};
var _pyfunc_create_dict = function () {
  const d = {};
  for (let i = 0; i < arguments.length; i += 2) {
    d[arguments[i]] = arguments[i + 1];
  }
  return d;
};
var _pyfunc_dict = function (x) {
  const res = {};
  if (Array.isArray(x)) {
    for (let i = 0; i < x.length; i++) {
      let t = x[i];
      res[t[0]] = t[1];
    }
  } else {
    const keys = Object.keys(x);
    for (let i = 0; i < keys.length; i++) {
      let t = keys[i];
      res[t] = x[t];
    }
  }
  return res;
};
var _pyfunc_dir = function (obj) {
  // nargs: 0 1
  // Return list of names in scope or object attributes
  if (obj === undefined) {
    // Without argument, return names in current scope
    // This is hard to do correctly in JS, return empty list
    return [];
  }
  let names = new Set();
  // Add own properties
  if (typeof obj === "object" && obj !== null) {
    for (let key of Object.keys(obj)) {
      names.add(key);
    }
    // Add prototype properties
    let proto = Object.getPrototypeOf(obj);
    while (proto && proto !== Object.prototype) {
      for (let key of Object.getOwnPropertyNames(proto)) {
        if (!key.startsWith("_") || key.startsWith("__")) {
          names.add(key);
        }
      }
      proto = Object.getPrototypeOf(proto);
    }
  }
  // For primitives, add type methods
  if (typeof obj === "string") {
    names.add("upper");
    names.add("lower");
    names.add("strip");
    names.add("split");
    // ... add more as needed
  }
  // Check for __dir__ method
  if (obj && typeof obj.__dir__ === "function") {
    return obj.__dir__();
  }
  return Array.from(names).sort();
};
var _pyfunc_divmod = function (x, y) {
  // nargs: 2
  const m = x % y;
  return [(x - m) / y, m];
};
var _pyfunc_enumerate = function (iter) {
  // nargs: 1
  const res = [];
  // Handle iterators/generators
  if (!Array.isArray(iter) && typeof iter[Symbol.iterator] === 'function') {
    let i = 0;
    for (const item of iter) {
      res.push([i++, item]);
    }
    return res;
  }
  // Handle plain objects
  if (typeof iter === "object" && !Array.isArray(iter)) {
    iter = Object.keys(iter);
  }
  for (let i = 0; i < iter.length; i++) {
    res.push([i, iter[i]]);
  }
  return res;
};
var _pyfunc_filter = function (func, iter) {
  // nargs: 2
  if (typeof func === "undefined" || func === null) {
    func = function (x) {
      return x;
    };
  }
  if (typeof iter === "object" && !Array.isArray(iter)) {
    iter = Object.keys(iter);
  }
  return iter.filter(func);
};
var _pyfunc_float = Number;;
var _pyfunc_hasattr = function (obj, name) {
  // nargs: 2
  // Check if object has attribute
  if (obj == null) {
    return false;
  }
  // Check for __getattr__
  if (typeof obj.__getattr__ === "function") {
    try {
      obj.__getattr__(name);
      return true;
    } catch (e) {
      return false;
    }
  }
  return name in obj || obj[name] !== undefined;
};
var _pyfunc_int = function (x, base) {
  // nargs: 1 2
  if (base !== undefined) {
    return parseInt(x, base);
  }
  return x < 0 ? Math.ceil(x) : Math.floor(x);
};
var _pyfunc_int_from_bytes = function (bytes, byteorder, signed) {
  // nargs: 2 3
  // int.from_bytes(bytes, byteorder, *, signed=False)
  // Converts bytes to an integer
  signed = signed === true || signed === "true";
  let isLittle = byteorder === "little";

  // Convert to array if needed
  let arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let length = arr.length;

  if (length === 0) {
    return 0;
  }

  // Build the integer value
  let result = 0;
  for (let i = 0; i < length; i++) {
    let idx = isLittle ? length - 1 - i : i;
    result = result * 256 + arr[idx];
  }

  // Handle signed conversion (two's complement)
  if (signed && arr[isLittle ? length - 1 : 0] >= 128) {
    result = result - Math.pow(2, length * 8);
  }

  return result;
};
var _pyfunc_list = function (x) {
  let res;
  // Handle iterators/generators using spread
  if (typeof x[Symbol.iterator] === 'function') {
    res = [...x];
  }
  // Handle plain objects by converting to array of keys
  else if (typeof x === "object" && !Array.isArray(x)) {
    res = Object.keys(x);
  }
  // Fallback for array-like objects
  else {
    res = [];
    for (let i = 0; i < x.length; i++) {
      res.push(x[i]);
    }
  }
  // Mark as list for repr() to display as [] not ()
  res._is_list = true;
  return res;
};
var _pyfunc_map = function (func, iter) {
  // nargs: 2
  if (typeof func === "undefined" || func === null) {
    func = function (x) {
      return x;
    };
  }
  if (typeof iter === "object" && !Array.isArray(iter)) {
    iter = Object.keys(iter);
  }
  return iter.map(func);
};
var _pyfunc_merge_dicts = function () {
  const res = {};
  for (let i = 0; i < arguments.length; i++) {
    const d = arguments[i];
    const keys = Object.keys(d);
    for (let j = 0; j < keys.length; j++) {
      let key = keys[j];
      res[key] = d[key];
    }
  }
  return res;
};
var _pyfunc_op_add = function (a, b) {
  // nargs: 2
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.concat(b);
  }
  // Handle bytes (Uint8Array) concatenation
  if (a instanceof Uint8Array && b instanceof Uint8Array) {
    let result = new Uint8Array(a.length + b.length);
    result.set(a, 0);
    result.set(b, a.length);
    return result;
  }
  return a + b;
};
var _pyfunc_op_delitem = function op_delitem(obj, key) {
  // nargs: 2
  // Python del obj[key] - checks for __delitem__ method first
  if (obj == null) {
    throw new TypeError("'NoneType' object does not support item deletion");
  }
  if (typeof obj.__delitem__ === 'function') {
    obj.__delitem__(key);
  } else if (Array.isArray(obj)) {
    // For arrays, use splice to remove element
    obj.splice(key, 1);
  } else {
    // For objects, use delete
    delete obj[key];
  }
};
var _pyfunc_op_equals = function op_equals(a, b) {
  // nargs: 2
  let a_type = typeof a;
  // If a (or b actually) is of type string, number or boolean, we don't need
  // to do all the other type checking below.
  if (a_type === "string" || a_type === "boolean" || a_type === "number") {
    return a == b;
  }

  if (a == null || b == null) {
    return a == b;
  }

  // Check for __eq__ method on either object
  if (typeof a.__eq__ === 'function') {
    return a.__eq__(b);
  }
  if (typeof b.__eq__ === 'function') {
    return b.__eq__(a);
  }

  if (Array.isArray(a) && Array.isArray(b)) {
    let i = 0,
      iseq = a.length == b.length;
    while (iseq && i < a.length) {
      iseq = op_equals(a[i], b[i]);
      i += 1;
    }
    return iseq;
  }

  if (a.constructor === Object && b.constructor === Object) {
    const akeys = Object.keys(a),
      bkeys = Object.keys(b);
    akeys.sort();
    bkeys.sort();
    let i = 0,
      iseq = op_equals(akeys, bkeys);
    while (iseq && i < akeys.length) {
      const k = akeys[i];
      iseq = op_equals(a[k], b[k]);
      i += 1;
    }
    return iseq;
  }

  return a == b;
};
var _pyfunc_op_contains = function op_contains(a, b) {
  // nargs: 2
  if (b == null) {
  } else if (Array.isArray(b)) {
    for (let i = 0; i < b.length; i++) {
      if (_pyfunc_op_equals(a, b[i])) return true;
    }
    return false;
  } else if (b.constructor === Object) {
    for (let k in b) {
      if (a == k) return true;
    }
    return false;
  } else if (b.constructor == String) {
    return b.indexOf(a) >= 0;
  }
  let e = Error("Not a container: " + b);
  e.name = "TypeError";
  throw e;
};
var _pyfunc_op_error = function (etype, ...args) {
  // nargs: 1+
  let msg = args.join(", ");
  let e = new Error(etype + ": " + msg);
  e.name = etype;
  e.args = args;  // Store args for repr()
  return e;
};
var _pyfunc_bin = function (x) {
  // nargs: 1
  // Convert integer to binary string with 0b prefix
  if (typeof x !== "number" || !Number.isInteger(x)) {
    if (typeof x.__index__ === "function") {
      x = x.__index__();
    } else {
      throw _pyfunc_op_error("TypeError", "'float' object cannot be interpreted as an integer");
    }
  }
  if (x < 0) {
    return "-0b" + (-x).toString(2);
  }
  return "0b" + x.toString(2);
};
var _pyfunc_bytes = function (source) {
  // nargs: 0 1
  // bytes() constructor - single argument form
  // - bytes(int) -> n zero bytes
  // - bytes(iterable) -> bytes from iterable of ints
  // - bytes(bytes) -> copy of bytes
  if (source === undefined) {
    return new Uint8Array();
  }
  // If it's a string without encoding, raise TypeError (like Python)
  if (typeof source === "string") {
    throw _pyfunc_op_error("TypeError", "string argument without an encoding");
  }
  // If it's a number, create zero-filled bytes
  if (typeof source === "number") {
    if (source < 0) {
      throw _pyfunc_op_error("ValueError", "negative count");
    }
    return new Uint8Array(source);
  }
  // If it's already a Uint8Array, copy it
  if (source instanceof Uint8Array) {
    return new Uint8Array(source);
  }
  // If it's an array or iterable, convert to bytes
  if (Array.isArray(source)) {
    return new Uint8Array(source);
  }
  // Handle iterators/generators
  if (typeof source[Symbol.iterator] === "function") {
    return new Uint8Array([...source]);
  }
  throw _pyfunc_op_error("TypeError", "cannot convert '" + typeof source + "' object to bytes");
};
var _pyfunc_bytes_encode = function (string, encoding) {
  // nargs: 2
  // Encode string to bytes using specified encoding
  let enc = (encoding || "utf-8").toLowerCase().replace("-", "");
  // Use TextEncoder if available
  if (typeof TextEncoder !== "undefined") {
    let encoder = new TextEncoder();
    return encoder.encode(string);
  }
  // Fallback: manual UTF-8 encoding for QuickJS
  if (enc === "utf8" || enc === "utf-8") {
    let bytes = [];
    for (let i = 0; i < string.length; i++) {
      let cp = string.codePointAt(i);
      if (cp < 0x80) {
        bytes.push(cp);
      } else if (cp < 0x800) {
        bytes.push(0xc0 | (cp >> 6));
        bytes.push(0x80 | (cp & 0x3f));
      } else if (cp < 0x10000) {
        bytes.push(0xe0 | (cp >> 12));
        bytes.push(0x80 | ((cp >> 6) & 0x3f));
        bytes.push(0x80 | (cp & 0x3f));
      } else {
        bytes.push(0xf0 | (cp >> 18));
        bytes.push(0x80 | ((cp >> 12) & 0x3f));
        bytes.push(0x80 | ((cp >> 6) & 0x3f));
        bytes.push(0x80 | (cp & 0x3f));
        i++; // Skip surrogate pair
      }
    }
    return new Uint8Array(bytes);
  }
  // ASCII/latin-1
  if (enc === "ascii" || enc === "latin1" || enc === "iso88591") {
    let bytes = new Uint8Array(string.length);
    for (let i = 0; i < string.length; i++) {
      bytes[i] = string.charCodeAt(i);
    }
    return bytes;
  }
  throw _pyfunc_op_error("LookupError", "unknown encoding: " + encoding);
};
var _pyfunc_bytes_error_args = function () {
  // nargs: 0+
  // Called when bytes() has too many arguments - raises TypeError at runtime
  throw _pyfunc_op_error("TypeError", "bytes() takes at most 3 arguments");
};
var _pyfunc_delattr = function (obj, name) {
  // nargs: 2
  // Delete attribute from object
  if (obj == null) {
    throw _pyfunc_op_error("AttributeError", "'NoneType' object has no attribute '" + name + "'");
  }
  // Check for __delattr__
  if (typeof obj.__delattr__ === "function") {
    obj.__delattr__(name);
  } else if (name in obj) {
    delete obj[name];
  } else {
    let typeName = obj.constructor ? obj.constructor.name : typeof obj;
    throw _pyfunc_op_error("AttributeError", "'" + typeName + "' object has no attribute '" + name + "'");
  }
};
var _pyfunc_getattr = function (obj, name, defaultValue) {
  // nargs: 2 3
  // Get attribute from object
  if (obj == null) {
    if (arguments.length >= 3) {
      return defaultValue;
    }
    throw _pyfunc_op_error("AttributeError", "'NoneType' object has no attribute '" + name + "'");
  }
  // Check for __getattr__ first
  if (typeof obj.__getattr__ === "function") {
    try {
      return obj.__getattr__(name);
    } catch (e) {
      if (arguments.length >= 3 && e.name === "AttributeError") {
        return defaultValue;
      }
      throw e;
    }
  }
  // Direct property access
  if (name in obj) {
    return obj[name];
  }
  // Check prototype chain
  if (obj[name] !== undefined) {
    return obj[name];
  }
  if (arguments.length >= 3) {
    return defaultValue;
  }
  let typeName = obj.constructor ? obj.constructor.name : typeof obj;
  throw _pyfunc_op_error("AttributeError", "'" + typeName + "' object has no attribute '" + name + "'");
};
var _pyfunc_hex = function (x) {
  // nargs: 1
  // Convert integer to hexadecimal string with 0x prefix
  if (typeof x !== "number" || !Number.isInteger(x)) {
    if (typeof x.__index__ === "function") {
      x = x.__index__();
    } else {
      throw _pyfunc_op_error("TypeError", "'float' object cannot be interpreted as an integer");
    }
  }
  if (x < 0) {
    return "-0x" + (-x).toString(16);
  }
  return "0x" + x.toString(16);
};
var _pyfunc_iter = function (x) {
  // nargs: 1
  // Returns an iterator for the given iterable
  if (typeof x[Symbol.iterator] === "function") {
    return x[Symbol.iterator]();
  }
  // Handle plain objects by iterating over keys
  if (typeof x === "object" && x !== null) {
    return Object.keys(x)[Symbol.iterator]();
  }
  throw _pyfunc_op_error("TypeError", "'" + typeof x + "' object is not iterable");
};
var _pyfunc_next = function (iterator, defaultValue) {
  // nargs: 1 2
  // Get next item from iterator
  // Check if generator was closed
  if (iterator._closed) {
    if (arguments.length >= 2) {
      return defaultValue;
    }
    throw _pyfunc_op_error("StopIteration", "");
  }
  // Mark generator as started for send/close methods
  iterator._started = true;
  let result = iterator.next();
  if (result.done) {
    if (arguments.length >= 2) {
      return defaultValue;
    }
    throw _pyfunc_op_error("StopIteration", "");
  }
  return result.value;
};
var _pyfunc_oct = function (x) {
  // nargs: 1
  // Convert integer to octal string with 0o prefix
  if (typeof x !== "number" || !Number.isInteger(x)) {
    if (typeof x.__index__ === "function") {
      x = x.__index__();
    } else {
      throw _pyfunc_op_error("TypeError", "'float' object cannot be interpreted as an integer");
    }
  }
  if (x < 0) {
    return "-0o" + (-x).toString(8);
  }
  return "0o" + x.toString(8);
};
var _pyfunc_op_delattr = function op_delattr(obj, name) {
  // nargs: 2
  // Python del obj.attr - checks for property deleters first
  if (obj == null) {
    throw _pyfunc_op_error('AttributeError', "'NoneType' object has no attribute '" + name + "'");
  }
  // Check for property deleter (__deleter_propname__ method on prototype)
  var deleterName = '__deleter_' + name + '__';
  var proto = Object.getPrototypeOf(obj);
  if (proto && typeof proto[deleterName] === 'function') {
    proto[deleterName].call(obj);
    return;
  }
  // Check for __delattr__ method
  if (typeof obj.__delattr__ === 'function') {
    obj.__delattr__(name);
    return;
  }
  // Fall back to regular delete
  if (name in obj) {
    delete obj[name];
  } else {
    var typeName = obj.constructor ? obj.constructor.name : typeof obj;
    throw _pyfunc_op_error('AttributeError', "'" + typeName + "' object has no attribute '" + name + "'");
  }
};
var _pyfunc_op_ge = function op_ge(a, b) {
  // nargs: 2
  // Check for __ge__ method on the left operand
  if (a != null && typeof a.__ge__ === 'function') {
    return a.__ge__(b);
  }
  return a >= b;
};
var _pyfunc_op_getitem = function op_getitem(obj, key) {
  // nargs: 2
  // Python obj[key] - checks for __getitem__ method first
  if (obj == null) {
    throw new TypeError("'NoneType' object is not subscriptable");
  }
  if (typeof obj.__getitem__ === 'function') {
    return obj.__getitem__(key);
  }
  // Handle negative indices for arrays, strings, and typed arrays (bytes)
  if (typeof key === 'number' && key < 0 && (Array.isArray(obj) || typeof obj === 'string' || obj instanceof Uint8Array)) {
    key = obj.length + key;
  }
  return obj[key];
};
var _pyfunc_op_gt = function op_gt(a, b) {
  // nargs: 2
  // Check for __gt__ method on the left operand
  if (a != null && typeof a.__gt__ === 'function') {
    return a.__gt__(b);
  }
  return a > b;
};
var _pyfunc_op_instantiate = function (ob, args) {
  // nargs: 2
  if (
    typeof ob === "undefined" ||
    (typeof window !== "undefined" && window === ob) ||
    (typeof global !== "undefined" && global === ob)
  ) {
    throw "Class constructor is called as a function.";
  }
  for (let name in ob) {
    if (
      Object[name] === undefined &&
      typeof ob[name] === "function" &&
      !ob[name].nobind
    ) {
      ob[name] = ob[name].bind(ob);
      ob[name].__name__ = name;
    }
  }
  if (ob.__init__) {
    ob.__init__.apply(ob, args);
  }
  // Seal object if __slots__ is defined (prevents adding new properties)
  if (ob.__slots__ !== undefined) {
    Object.seal(ob);
  }
};
var _pyfunc_op_le = function op_le(a, b) {
  // nargs: 2
  // Check for __le__ method on the left operand
  if (a != null && typeof a.__le__ === 'function') {
    return a.__le__(b);
  }
  return a <= b;
};
var _pyfunc_op_len = function op_len(obj) {
  // nargs: 1
  // Python len() - checks for __len__ method first, then falls back to .length
  if (obj == null) {
    throw new TypeError("object of type 'NoneType' has no len()");
  }
  if (typeof obj.__len__ === 'function') {
    return obj.__len__();
  }
  if (obj.length !== undefined) {
    return obj.length;
  }
  // JavaScript Set and Map use .size instead of .length
  if (obj.size !== undefined) {
    return obj.size;
  }
  if (obj.constructor === Object) {
    return Object.keys(obj).length;
  }
  throw new TypeError("object has no len()");
};
var _pyfunc_op_lt = function op_lt(a, b) {
  // nargs: 2
  // Check for __lt__ method on the left operand
  if (a != null && typeof a.__lt__ === 'function') {
    return a.__lt__(b);
  }
  return a < b;
};
var _pyfunc_op_matmul = function (a, b) {
  // nargs: 2
  // Matrix multiplication operator @
  // Delegates to __matmul__ method if available, then __rmatmul__
  if (typeof a.__matmul__ === 'function') {
    const result = a.__matmul__(b);
    if (result !== Symbol.for('NotImplemented')) {
      return result;
    }
  }
  if (typeof b.__rmatmul__ === 'function') {
    const result = b.__rmatmul__(a);
    if (result !== Symbol.for('NotImplemented')) {
      return result;
    }
  }
  throw new TypeError("unsupported operand type(s) for @");
};
var _pyfunc_op_mul = function (a, b) {
  // nargs: 2
  if ((typeof a === "number") + (typeof b === "number") === 1) {
    if (a.constructor === String) return _pymeth_repeat.call(a, b);
    if (b.constructor === String) return _pymeth_repeat.call(b, a);
    if (Array.isArray(b)) {
      let t = a;
      a = b;
      b = t;
    }
    if (Array.isArray(a)) {
      let res = [];
      for (let i = 0; i < b; i++) res = res.concat(a);
      return res;
    }
  }
  return a * b;
};
var _pyfunc_op_parse_kwargs = function (
  arg_names,
  arg_values,
  kwargs,
  strict
) {
  // nargs: 3
  for (let i = 0; i < arg_values.length; i++) {
    let name = arg_names[i];
    if (kwargs[name] !== undefined) {
      arg_values[i] = kwargs[name];
      delete kwargs[name];
    }
  }
  if (strict && Object.keys(kwargs).length > 0) {
    throw _pyfunc_op_error(
      "TypeError",
      "Function " + strict + " does not accept **kwargs."
    );
  }
  return kwargs;
};
var _pyfunc_op_setitem = function op_setitem(obj, key, value) {
  // nargs: 3
  // Python obj[key] = value - checks for __setitem__ method first
  if (obj == null) {
    throw new TypeError("'NoneType' object does not support item assignment");
  }
  if (typeof obj.__setitem__ === 'function') {
    obj.__setitem__(key, value);
  } else {
    obj[key] = value;
  }
};
var _pyfunc_perf_counter = function () {
  // nargs: 0
  if (typeof process === "undefined") {
    return performance.now() * 1e-3;
  } else {
    const t = process.hrtime();
    return t[0] + t[1] * 1e-9;
  }
};
var _pyfunc_pow = Math.pow;;
var _pyfunc_range = function (start, end, step) {
  const res = [];
  let val = start;
  let n = (end - start) / step;
  for (let i = 0; i < n; i++) {
    res.push(val);
    val += step;
  }
  return res;
};
var _pyfunc_reversed = function (iter) {
  // nargs: 1
  if (typeof iter === "object" && !Array.isArray(iter)) {
    iter = Object.keys(iter);
  }
  return iter.slice().reverse();
};
var _pyfunc_round = function (x, ndigits) {
  // nargs: 1 2
  if (ndigits === undefined || ndigits === 0) {
    return Math.round(x);
  }
  const factor = Math.pow(10, ndigits);
  return Math.round(x * factor) / factor;
};
var _pyfunc_setattr = function (obj, name, value) {
  // nargs: 3
  // Set attribute on object
  if (obj == null) {
    throw _pyfunc_op_error("AttributeError", "'NoneType' object has no attribute '" + name + "'");
  }
  // Check for __setattr__
  if (typeof obj.__setattr__ === "function") {
    obj.__setattr__(name, value);
  } else {
    obj[name] = value;
  }
};
var _pyfunc_slice = function (obj, start, stop, step) {
  // nargs: 4
  // Slice with step: handles a[::2], a[::-1], a[1:5:2], etc.
  const len = obj.length;

  // Normalize step
  if (step === 0) {
    throw new ValueError("slice step cannot be zero");
  }

  // Normalize start
  if (start === null) {
    start = step < 0 ? len - 1 : 0;
  } else if (start < 0) {
    start = Math.max(0, len + start);
  } else {
    start = Math.min(start, step < 0 ? len - 1 : len);
  }

  // Normalize stop
  if (stop === null) {
    stop = step < 0 ? -1 : len;
  } else if (stop < 0) {
    stop = Math.max(-1, len + stop);
  } else {
    stop = Math.min(stop, len);
  }

  // Collect elements
  const result = [];
  if (step > 0) {
    for (let i = start; i < stop; i += step) {
      result.push(obj[i]);
    }
  } else {
    for (let i = start; i > stop; i += step) {
      result.push(obj[i]);
    }
  }

  // Return same type as input
  if (typeof obj === "string") {
    return result.join("");
  }
  return result;
};
var _pyfunc_sorted = function (iter, key, reverse) {
  // nargs: 1 2 3
  // Handle iterators/generators - convert to array first
  if (!Array.isArray(iter)) {
    if (typeof iter[Symbol.iterator] === 'function') {
      iter = [...iter];
    } else if (typeof iter === "object") {
      iter = Object.keys(iter);
    }
  }
  let comp;
  if (key) {
    // Custom key function provided
    comp = function (a, b) {
      a = key(a);
      b = key(b);
      if (a < b) return -1;
      if (a > b) return 1;
      return 0;
    };
  } else {
    // Default comparison - Python-like behavior (works correctly for numbers and strings)
    comp = function (a, b) {
      if (a < b) return -1;
      if (a > b) return 1;
      return 0;
    };
  }
  iter = iter.slice().sort(comp);
  if (reverse) iter.reverse();
  return iter;
};
var _pyfunc_str_decode = function (bytes, encoding) {
  // nargs: 2
  // Decode bytes/bytearray to string using specified encoding
  // Convert to Uint8Array if needed (handles both Array and TypedArray)
  let arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let enc = (encoding || "utf-8").toLowerCase().replace("-", "");
  // Use TextDecoder if available
  if (typeof TextDecoder !== "undefined") {
    let decoder = new TextDecoder(enc);
    return decoder.decode(arr);
  }
  // Fallback: manual UTF-8 decoding for QuickJS
  if (enc === "utf8" || enc === "utf-8") {
    let result = "";
    let i = 0;
    while (i < arr.length) {
      let b = arr[i];
      if (b < 0x80) {
        result += String.fromCharCode(b);
        i++;
      } else if ((b & 0xe0) === 0xc0) {
        result += String.fromCharCode(((b & 0x1f) << 6) | (arr[i + 1] & 0x3f));
        i += 2;
      } else if ((b & 0xf0) === 0xe0) {
        result += String.fromCharCode(
          ((b & 0x0f) << 12) | ((arr[i + 1] & 0x3f) << 6) | (arr[i + 2] & 0x3f),
        );
        i += 3;
      } else if ((b & 0xf8) === 0xf0) {
        // 4-byte sequence (surrogate pairs for chars > 0xFFFF)
        let cp =
          ((b & 0x07) << 18) |
          ((arr[i + 1] & 0x3f) << 12) |
          ((arr[i + 2] & 0x3f) << 6) |
          (arr[i + 3] & 0x3f);
        cp -= 0x10000;
        result += String.fromCharCode(0xd800 + (cp >> 10), 0xdc00 + (cp & 0x3ff));
        i += 4;
      } else {
        i++;
      }
    }
    return result;
  }
  // ASCII/latin-1
  if (enc === "ascii" || enc === "latin1" || enc === "iso88591") {
    let result = "";
    for (let i = 0; i < arr.length; i++) {
      result += String.fromCharCode(arr[i]);
    }
    return result;
  }
  throw _pyfunc_op_error("LookupError", "unknown encoding: " + encoding);
};
var _pyfunc_str_error_args = function () {
  // nargs: 0+
  // Called when str() has too many arguments - raises TypeError at runtime
  throw _pyfunc_op_error("TypeError", "str() takes at most 3 arguments");
};
var _pyfunc_sum = function (x) {
  // nargs: 1
  // Convert iterators/generators to array first
  if (!Array.isArray(x) && typeof x[Symbol.iterator] === 'function') {
    x = [...x];
  }
  return x.reduce(function (a, b) {
    return a + b;
  }, 0);
};
var _pyfunc_super_proxy = function (self, classProto) {
  // nargs: 2
  // Creates a proxy object for super() that accesses parent class methods/attributes
  // and binds methods to the current instance.
  // classProto is the prototype of the class where super() is called from (not the instance's class)
  // This is needed for multi-level inheritance to work correctly.
  var base = classProto ? classProto._base_class : self._base_class;
  if (!base) {
    throw new TypeError("super(): no base class");
  }
  var className = classProto ? classProto.__name__ : (self.__name__ || 'object');
  return new Proxy({}, {
    get: function(target, prop) {
      // Handle string conversion
      if (prop === '__str__' || prop === 'toString') {
        return function() {
          return '<super: <class \'' + className + '\'>, <' + className + ' object>>';
        };
      }
      if (prop === Symbol.toStringTag) {
        return 'super';
      }
      // Handle hasattr-style checks
      if (prop === '__class__') {
        return 'super';
      }
      if (prop in base) {
        var val = base[prop];
        if (typeof val === 'function') {
          return val.bind(self);
        }
        return val;
      }
      // Special case: __init__ on Object base class is a no-op
      // This allows super().__init__() to work when inheriting from object
      if (prop === '__init__' && (base === Object || base === Object.prototype)) {
        return function() {};
      }
      return undefined;
    },
    set: function(target, prop, value) {
      throw _pyfunc_op_error('AttributeError', "'super' object attribute '" + prop + "' is read-only");
    },
    deleteProperty: function(target, prop) {
      throw _pyfunc_op_error('AttributeError', "'super' object attribute '" + prop + "' is read-only");
    },
    has: function(target, prop) {
      // Support 'in' operator and hasattr()
      if (prop === '__str__' || prop === 'toString' || prop === '__class__') {
        return true;
      }
      return prop in base;
    }
  });
};
var _pyfunc_time = function () {
  return Date.now() / 1000;
}; // nargs: 0;
var _pyfunc_truthy = function (v) {
  if (v === null || typeof v !== "object") {
    return v;
  } else if (v.length !== undefined) {
    return v.length ? v : false;
  } else if (v.byteLength !== undefined) {
    return v.byteLength ? v : false;
  } else if (v.constructor !== Object) {
    return true;
  } else {
    return Object.getOwnPropertyNames(v).length ? v : false;
  }
};
var _pyfunc_all = function (x) {
  // nargs: 1
  // Use for...of to handle both arrays and iterators/generators
  for (const item of x) {
    if (!_pyfunc_truthy(item)) {
      return false;
    }
  }
  return true;
};
var _pyfunc_any = function (x) {
  // nargs: 1
  // Use for...of to handle both arrays and iterators/generators
  for (const item of x) {
    if (_pyfunc_truthy(item)) {
      return true;
    }
  }
  return false;
};
var _pyfunc_bool = function (x) {
  // nargs: 1
  return Boolean(_pyfunc_truthy(x));
};
var _pyfunc_type_bool = Boolean;
var _pyfunc_type_bytes = Uint8Array;
var _pyfunc_type_dict = Object;
var _pyfunc_type_float = Number;
var _pyfunc_type_int = Number;
var _pyfunc_type_list = Array;
var _pyfunc_type_object = Object;
var _pyfunc_type_set = Set;
var _pyfunc_type_str = String;
var _pyfunc_type_tuple = Array;
var _pyfunc_type_type = function (x) {
  // nargs: 1
  if (x === null) return "NoneType";
  if (x === undefined) return "NoneType";
  if (typeof x === "boolean") return _pyfunc_type_bool;
  if (typeof x === "number") {
    return Number.isInteger(x) ? _pyfunc_type_int : _pyfunc_type_float;
  }
  if (typeof x === "string") return _pyfunc_type_str;
  if (Array.isArray(x)) return _pyfunc_type_list;
  if (x instanceof Uint8Array) return _pyfunc_type_bytes;
  if (x instanceof Set) return _pyfunc_type_set;
  if (x instanceof Map) return _pyfunc_type_dict;
  if (typeof x === "function") return "function";
  if (typeof x === "object") {
    // Check for class instances
    if (x.constructor && x.constructor !== Object) {
      return x.constructor;
    }
    return _pyfunc_type_dict;
  }
  return typeof x;
};
var _pyfunc_zip = function () {
  // nargs: 2 3 4 5 6 7 8 9
  let len = 1e20;
  const args = [],
    res = [];

  for (let i = 0; i < arguments.length; i++) {
    let arg = arguments[i];
    if (typeof arg === "object" && !Array.isArray(arg)) {
      arg = Object.keys(arg);
    }
    args.push(arg);
    len = Math.min(len, arg.length);
  }
  for (let j = 0; j < len; j++) {
    const tup = [];
    for (let i = 0; i < args.length; i++) {
      tup.push(args[i][j]);
    }
    res.push(tup);
  }
  return res;
};
var _pyfunc_format = function (v, fmt) {
  // nargs: 1 2
  if (fmt === undefined) {
    return String(v);
  }
  let s = String(v);

  // Handle !r conversion (repr)
  if (fmt.indexOf("!r") >= 0) {
    try {
      s = JSON.stringify(v);
    } catch (e) {
      s = undefined;
    }
    if (typeof s === "undefined") {
      s = v._IS_COMPONENT ? v.id : String(v);
    }
    fmt = fmt.replace("!r", "");
  }

  // Parse format spec: [[fill]align][sign][#][0][width][,][.precision][type]
  // The format can be either ":spec" (from f-strings) or just "spec" (from format() builtin)
  let i0 = fmt.indexOf(":");
  let spec = i0 >= 0 ? fmt.slice(i0 + 1) : fmt;

  // Parse fill and alignment
  let fill = ' ';
  let align = '';
  if (spec.length >= 2 && ['<', '>', '^', '='].includes(spec[1])) {
    fill = spec[0];
    align = spec[1];
    spec = spec.slice(2);
  } else if (spec.length >= 1 && ['<', '>', '^', '='].includes(spec[0])) {
    align = spec[0];
    spec = spec.slice(1);
  }

  // Parse sign
  let prefix = "";
  if (spec.length > 0 && ['+', '-', ' '].includes(spec[0])) {
    if (spec[0] === '+' && typeof v === 'number' && v >= 0) {
      prefix = '+';
    } else if (spec[0] === ' ' && typeof v === 'number' && v >= 0) {
      prefix = ' ';
    }
    spec = spec.slice(1);
  }

  // Parse # (alternate form) - skip for now
  if (spec.length > 0 && spec[0] === '#') {
    spec = spec.slice(1);
  }

  // Check for thousands separator
  let useThousands = false;
  if (spec.indexOf(',') >= 0) {
    useThousands = true;
    spec = spec.replace(',', '');
  }

  // Handle zero-fill shorthand: 05 means 0>5 for numbers
  if (spec.length > 0 && spec[0] === '0' && !align) {
    fill = '0';
    align = '>';
    spec = spec.slice(1);
  }

  // Parse width
  let width = 0;
  let widthMatch = spec.match(/^(\d+)/);
  if (widthMatch) {
    width = parseInt(widthMatch[1], 10);
    spec = spec.slice(widthMatch[1].length);
  }

  // Parse precision
  let precision = null;
  if (spec.length > 0 && spec[0] === '.') {
    spec = spec.slice(1);
    let precMatch = spec.match(/^(\d+)/);
    if (precMatch) {
      precision = parseInt(precMatch[1], 10);
      spec = spec.slice(precMatch[1].length);
    }
  }

  // Parse type (remaining characters)
  let fmt_type = spec.toLowerCase();

  // Format the value based on type
  if (fmt_type === 'd' || fmt_type === 'i') {
    s = parseInt(v).toFixed(0);
  } else if (fmt_type === 'f') {
    v = parseFloat(v);
    let decimals = precision !== null ? precision : 6;
    s = v.toFixed(decimals);
  } else if (fmt_type === 'e') {
    v = parseFloat(v);
    let prec = precision !== null ? precision : 6;
    s = v.toExponential(prec);
  } else if (fmt_type === 'g') {
    v = parseFloat(v);
    let prec = (precision !== null ? precision : 6) || 1;
    s = v.toExponential(prec - 1);
    let s1 = s.slice(0, s.indexOf("e")),
      s2 = s.slice(s.indexOf("e"));
    if (s2.length == 3) {
      s2 = "e" + s2[1] + "0" + s2[2];
    }
    let exp = Number(s2.slice(1));
    if (exp >= -4 && exp < prec) {
      s1 = v.toPrecision(prec);
      s2 = "";
    }
    let j = s1.length - 1;
    while (j > 0 && s1[j] == "0") {
      j -= 1;
    }
    s1 = s1.slice(0, j + 1);
    if (s1.slice(-1) == ".") {
      s1 = s1.slice(0, s1.length - 1);
    }
    s = s1 + s2;
  } else if (fmt_type === '' && precision !== null && typeof v === 'number') {
    // No type but has precision - treat as float
    s = parseFloat(v).toFixed(precision);
  }

  // Apply thousands separator
  if (useThousands && !isNaN(parseFloat(v))) {
    let parts = s.split('.');
    let intPart = parts[0];
    let sign = '';
    if (intPart[0] === '-') {
      sign = '-';
      intPart = intPart.slice(1);
    }
    // Add commas to integer part using regex
    intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    parts[0] = sign + intPart;
    s = parts.join('.');
  }

  // Apply width and alignment padding
  if (width > 0) {
    let totalLen = s.length + prefix.length;
    if (totalLen < width) {
      let padLen = width - totalLen;
      let padding = fill.repeat(padLen);
      if (align === '<') {
        // Left align - padding on right
        s = prefix + s + padding;
        prefix = '';
      } else if (align === '^') {
        // Center align
        let left = Math.floor(padLen / 2);
        let right = padLen - left;
        s = fill.repeat(left) + prefix + s + fill.repeat(right);
        prefix = '';
      } else if (align === '=' && prefix) {
        // Sign-aware padding (padding between sign and digits)
        s = prefix + padding + s;
        prefix = '';
      } else {
        // Default: right align ('>') - padding on left
        if (fill === '0' && prefix) {
          // Zero padding goes after sign
          s = prefix + padding + s;
          prefix = '';
        } else {
          s = padding + s;
        }
      }
    }
  }

  return prefix + s;
};
var _pyfunc_format_value = function (value, type, flags, width, precision) {
  // nargs: 5
  // Format a single value according to % format specifier
  let result;
  let sign = '';
  const useAltForm = flags && flags.indexOf('#') >= 0;
  const forceSign = flags && flags.indexOf('+') >= 0;
  const spaceSign = flags && flags.indexOf(' ') >= 0;
  const zeroPad = flags && flags.indexOf('0') >= 0;
  const leftAlign = flags && flags.indexOf('-') >= 0;

  // Convert value to number for numeric formats
  let numValue = value;
  if (typeof value === 'boolean') {
    numValue = value ? 1 : 0;
  } else if (typeof value === 'object' && value !== null && typeof value.__int__ === 'function') {
    numValue = value.__int__();
  } else {
    numValue = Number(value);
  }

  // Handle different types
  switch (type) {
    case 's':
      result = _pyfunc_str(value);
      break;
    case 'r':
      result = _pyfunc_repr(value);
      break;
    case 'd':
    case 'i':
    case 'u':
      // Integer (u is deprecated in Python 3, same as d)
      let intVal = Math.floor(numValue);
      if (intVal < 0) {
        sign = '-';
        intVal = -intVal;
      } else if (forceSign) {
        sign = '+';
      } else if (spaceSign) {
        sign = ' ';
      }
      result = String(intVal);
      // Handle precision for integers (minimum digits)
      if (precision !== undefined && precision !== '') {
        const prec = Number(precision);
        while (result.length < prec) {
          result = '0' + result;
        }
      }
      result = sign + result;
      break;
    case 'o':
      result = Math.floor(Math.abs(numValue)).toString(8);
      if (useAltForm && result !== '0') {
        result = '0o' + result;
      }
      break;
    case 'x':
      result = Math.floor(Math.abs(numValue)).toString(16);
      if (useAltForm) {
        result = '0x' + result;
      }
      break;
    case 'X':
      result = Math.floor(Math.abs(numValue)).toString(16).toUpperCase();
      if (useAltForm) {
        result = '0X' + result;
      }
      break;
    case 'e':
      result = numValue.toExponential(precision !== undefined && precision !== '' ? Number(precision) : 6);
      break;
    case 'E':
      result = numValue.toExponential(precision !== undefined && precision !== '' ? Number(precision) : 6).toUpperCase();
      break;
    case 'f':
    case 'F':
      result = numValue.toFixed(precision !== undefined && precision !== '' ? Number(precision) : 6);
      break;
    case 'g':
    case 'G':
      result = numValue.toPrecision(precision !== undefined && precision !== '' ? Number(precision) : 6);
      if (type === 'G') result = result.toUpperCase();
      break;
    case 'c':
      // Character
      if (typeof value === 'number') {
        result = String.fromCharCode(value);
      } else if (typeof value === 'string' && value.length === 1) {
        result = value;
      } else if (typeof value === 'boolean') {
        result = String.fromCharCode(value ? 1 : 0);
      } else {
        throw new TypeError("%c requires int or char");
      }
      break;
    default:
      result = String(value);
  }

  // Handle precision for strings
  if ((type === 's' || type === 'r') && precision !== undefined && precision !== '') {
    result = result.slice(0, Number(precision));
  }

  // Handle width padding
  if (width !== undefined && width !== '') {
    const w = Number(width);
    if (result.length < w) {
      const padLen = w - result.length;
      if (leftAlign) {
        result = result + ' '.repeat(padLen);
      } else if (zeroPad && !leftAlign && 'diuoxXeEfFgG'.indexOf(type) >= 0) {
        // Zero padding goes after the sign
        if (sign && result.startsWith(sign)) {
          result = sign + '0'.repeat(padLen) + result.slice(sign.length);
        } else if (result.startsWith('0x') || result.startsWith('0X') || result.startsWith('0o')) {
          const prefix = result.slice(0, 2);
          result = prefix + '0'.repeat(padLen) + result.slice(2);
        } else {
          result = '0'.repeat(padLen) + result;
        }
      } else {
        result = ' '.repeat(padLen) + result;
      }
    }
  }

  return result;
};
var _pyfunc_hash = function (x) {
  // nargs: 1
  // Return hash value of object
  if (typeof x.__hash__ === "function") {
    return x.__hash__();
  }
  if (x === null || x === undefined) {
    throw _pyfunc_op_error("TypeError", "unhashable type: 'NoneType'");
  }
  if (typeof x === "number") {
    // For integers, hash is the integer itself (for small ints)
    if (Number.isInteger(x)) {
      return x;
    }
    // For floats, use a simple hash
    return Math.floor(x * 1000000) | 0;
  }
  if (typeof x === "string") {
    // Simple string hash (djb2 algorithm)
    let hash = 5381;
    for (let i = 0; i < x.length; i++) {
      hash = ((hash << 5) + hash) + x.charCodeAt(i);
      hash = hash | 0; // Convert to 32-bit integer
    }
    return hash;
  }
  if (typeof x === "boolean") {
    return x ? 1 : 0;
  }
  if (x instanceof Uint8Array) {
    // Hash bytes
    let hash = 5381;
    for (let i = 0; i < x.length; i++) {
      hash = ((hash << 5) + hash) + x[i];
      hash = hash | 0;
    }
    return hash;
  }
  // For objects, check if they're hashable
  if (Array.isArray(x)) {
    throw _pyfunc_op_error("TypeError", "unhashable type: 'list'");
  }
  if (typeof x === "object" && x.constructor === Object) {
    throw _pyfunc_op_error("TypeError", "unhashable type: 'dict'");
  }
  if (x instanceof Set) {
    throw _pyfunc_op_error("TypeError", "unhashable type: 'set'");
  }
  // For other objects, use a unique id approach
  return _pyfunc_id(x);
};
var _pyfunc_id = function (x) {
  // nargs: 1
  // Return unique identity for object
  // Use a WeakMap to assign unique IDs to objects
  if (typeof x !== "object" || x === null) {
    // For primitives, use a simple hash approach
    if (typeof x === "number") return x | 0;
    if (typeof x === "string") {
      // Simple string hash (inline to avoid circular dep with hash())
      let h = 5381;
      for (let i = 0; i < x.length; i++) {
        h = ((h << 5) + h) + x.charCodeAt(i);
        h = h | 0;
      }
      return h;
    }
    if (typeof x === "boolean") return x ? 1 : 0;
    if (x === undefined) return 0;
    return 0;
  }
  // For objects, use WeakMap to track IDs
  if (!_pyfunc_id._map) {
    _pyfunc_id._map = new WeakMap();
    _pyfunc_id._counter = 1;
  }
  if (!_pyfunc_id._map.has(x)) {
    _pyfunc_id._map.set(x, _pyfunc_id._counter++);
  }
  return _pyfunc_id._map.get(x);
};
var _pyfunc_op_mod = function (left, right) {
  // nargs: 2
  // Handles Python's % operator which can be either:
  // - String formatting: "hello %s" % "world"
  // - Numeric modulo: 7 % 3
  // Note: Python's modulo always has the same sign as the divisor,
  // while JavaScript's % has the same sign as the dividend.
  // Python: -2 % 17 = 15, JS: -2 % 17 = -2
  if (typeof left === 'string') {
    return _pyfunc_string_mod(left, right);
  }
  // Use Python-style modulo: ((a % b) + b) % b
  return ((left % right) + right) % right;
};
var _pyfunc_property = function (fget, fset, fdel, doc) {
  // nargs: 0 1 2 3 4
  // Python property builtin - creates a property descriptor
  var prop = {
    __class__: 'property',
    fget: fget || null,
    fset: fset || null,
    fdel: fdel || null,
    __doc__: doc || null,
    getter: function(fn) {
      return _pyfunc_property(fn, this.fset, this.fdel, this.__doc__);
    },
    setter: function(fn) {
      return _pyfunc_property(this.fget, fn, this.fdel, this.__doc__);
    },
    deleter: function(fn) {
      return _pyfunc_property(this.fget, this.fset, fn, this.__doc__);
    }
  };
  return prop;
};
var _pyfunc_repr = function (x) {
  // nargs: 1
  // Handle null/undefined (None in Python) first
  if (x === null || x === undefined) {
    return "None";
  }
  // Handle booleans with Python-style capitalization
  if (typeof x === "boolean") {
    return x ? "True" : "False";
  }
  // Check for __repr__ method on objects (custom classes)
  if (typeof x === "object" && x !== null && typeof x.__repr__ === "function") {
    return x.__repr__();
  }
  // Handle Error objects (Python exceptions)
  if (x instanceof Error && x.name && x.args !== undefined) {
    let argsRepr = x.args.map(a => _pyfunc_repr(a)).join(", ");
    return x.name + "(" + argsRepr + ")";
  }
  // Handle bytes (Uint8Array)
  if (x instanceof Uint8Array) {
    return _pyfunc_bytes_repr(x);
  }
  // Handle strings - use quotes like Python
  if (typeof x === "string") {
    // Python uses single quotes by default, but uses double quotes
    // if the string contains single quotes but no double quotes
    const hasSingle = x.indexOf("'") >= 0;
    const hasDouble = x.indexOf('"') >= 0;
    if (hasSingle && !hasDouble) {
      // Use double quotes to avoid escaping
      return '"' + x.replace(/\\/g, "\\\\") + '"';
    }
    // Default: use single quotes with escaping
    return "'" + x.replace(/\\/g, "\\\\").replace(/'/g, "\\'") + "'";
  }
  // Handle arrays (lists/tuples)
  if (Array.isArray(x)) {
    let items = x.map(e => _pyfunc_repr(e));
    // Arrays marked with _is_list are lists (use [])
    // Unmarked arrays are tuples (use ())
    if (x._is_list) {
      return "[" + items.join(", ") + "]";
    } else {
      // Tuple representation - need trailing comma for single-element tuples
      if (items.length === 1) {
        return "(" + items[0] + ",)";
      }
      return "(" + items.join(", ") + ")";
    }
  }
  // Handle dicts (plain objects)
  if (typeof x === "object" && x !== null && x.constructor === Object) {
    let entries = Object.entries(x);
    if (entries.length === 0) {
      return "{}";
    }
    let parts = entries.map(function([k, v]) {
      let kRepr = _pyfunc_repr(k);
      let vRepr = _pyfunc_repr(v);
      return kRepr + ": " + vRepr;
    });
    return "{" + parts.join(", ") + "}";
  }
  // Handle numbers
  if (typeof x === "number") {
    return String(x);
  }
  let res;
  try {
    res = JSON.stringify(x);
  } catch (e) {
    res = undefined;
  }
  if (typeof res === "undefined") {
    res = x._IS_COMPONENT ? x.id : String(x);
  }
  return res;
};
var _pyfunc_str = function (x) {
  // nargs: 0 1;
  // str() with no args returns empty string, str(None) returns "None"
  if (arguments.length === 0) {
    return "";
  }
  if (x === null || x === undefined) {
    return "None";
  }
  // Handle booleans with Python-style capitalization
  if (typeof x === "boolean") {
    return x ? "True" : "False";
  }
  // Check for __str__ method on objects (custom classes)
  if (typeof x === "object" && x !== null && typeof x.__str__ === "function") {
    return x.__str__();
  }
  // Handle bytes (Uint8Array) - output like b'...'
  if (x instanceof Uint8Array) {
    return _pyfunc_bytes_repr(x);
  }
  // Handle floats - preserve .0 for whole numbers
  if (typeof x === "number") {
    if (Number.isFinite(x) && !Number.isInteger(x)) {
      return String(x);
    }
    // Check if it was created as a float (has decimal point in source)
    // For runtime, we check if it's a whole number that should display with .0
    if (Number.isInteger(x)) {
      return String(x);
    }
    return String(x);
  }
  if (Array.isArray(x)) {
    if (x.length == 0) {
      return "[]";
    }
    // Quote first element if it's a string (same as other elements)
    let first = x[0];
    let firstStr;
    if (typeof first === "string") {
      if (first.indexOf("'") == -1) {
        firstStr = "'" + first + "'";
      } else {
        firstStr = JSON.stringify(first);
      }
    } else {
      firstStr = _pyfunc_str(first);
    }
    let result = "[" + firstStr;
    for (let i = 1; i < x.length; i++) {
      const e = x[i];
      if (typeof e === "string") {
        if (e.indexOf("'") == -1) {
          result = result.concat(", " + "'" + e + "'");
        } else {
          result = result.concat(", " + JSON.stringify(e));
        }
      } else {
        const t = _pyfunc_str(e);
        result = result.concat(", " + t);
      }
    }
    return result + "]";
  }
  if (typeof x === "string") {
    return x;
  }
  // Handle dicts (plain objects)
  if (typeof x === "object" && x !== null && !Array.isArray(x) && x.constructor === Object) {
    let entries = Object.entries(x);
    if (entries.length === 0) {
      return "{}";
    }
    let parts = entries.map(function([k, v]) {
      let kStr = typeof k === "string" ? "'" + k + "'" : String(k);
      let vStr = _pyfunc_repr(v);
      return kStr + ": " + vStr;
    });
    return "{" + parts.join(", ") + "}";
  }
  // Default - use String() for objects without __str__
  return String(x);
};
var _pyfunc_string_mod = function (format_str, args) {
  // nargs: 2
  // Python-style % string formatting with runtime tuple unpacking
  // format_str: the format string with %s, %d, %r, etc. placeholders
  // args: either a single value or a tuple/array of values

  // Check for named placeholders like %(name)s
  const hasNamedPlaceholders = /%\([^)]+\)/.test(format_str);

  if (hasNamedPlaceholders) {
    // Handle named placeholders - args should be a dict
    if (typeof args !== 'object' || Array.isArray(args)) {
      throw new TypeError("format requires a mapping");
    }
    return format_str.replace(/%\(([^)]+)\)([-+0 #]*)?(\d+)?(?:\.(\d+))?([srdeEfgGioxXcu])|%%/g,
      function(match, name, flags, width, precision, type) {
        if (match === "%%") return "%";
        if (!(name in args)) {
          throw _pyfunc_op_error("KeyError", name);
        }
        return _pyfunc_format_value(args[name], type, flags, width, precision);
      }
    );
  }

  // Count value slots needed (placeholders + * for dynamic width/precision)
  // This regex matches: %[-+0 #]*[*]?[\d]*[.]?[*]?[\d]*[type]
  const slot_re = /%(?:[-+0 #]*)?(\*)?(?:\d*)?(?:\.(\*)?\d*)?[srdeEfgGioxXcu]/g;
  let slots = 0;
  let m;
  while ((m = slot_re.exec(format_str)) !== null) {
    slots++; // The value itself
    if (m[1] === '*') slots++; // Dynamic width
    if (m[2] === '*') slots++; // Dynamic precision
  }

  // Normalize args to an array
  // In Python, only tuples are unpacked for % formatting
  // Non-tuple sequences (lists, etc.) are treated as single values
  let values;
  // Check if args is a tuple (unmarked array or explicitly marked)
  // Arrays marked with _is_list are NOT tuples
  const isList = args && args._is_list === true;
  const isTuple = Array.isArray(args) && !isList;

  if (slots === 0) {
    values = [];
  } else if (slots === 1 && !isTuple) {
    // Single placeholder with non-tuple (list, scalar, etc.) - treat as single value
    values = [args];
  } else if (slots === 1 && isTuple && args.length === 1) {
    // Single placeholder with single-element tuple - unpack
    values = args;
  } else if (slots === 1 && isTuple && args.length > 1) {
    // Single placeholder with multi-element tuple - too many values
    throw new TypeError("not all arguments converted during string formatting");
  } else if (isTuple) {
    // Multiple placeholders with tuple - unpack
    values = args;
  } else {
    // Multiple placeholders but args is not a tuple - TypeError
    throw new TypeError("not enough arguments for format string");
  }

  // Validate count
  if (values.length < slots) {
    throw new TypeError("not enough arguments for format string");
  }
  if (values.length > slots) {
    throw new TypeError("not all arguments converted during string formatting");
  }

  // Replace placeholders
  let valueIndex = 0;
  return format_str.replace(/%(?:([-+0 #]*))?(\*)?(\d*)(?:\.(\*)?(\d*))?([srdeEfgGioxXcu])|%%/g,
    function(match, flags, dynWidth, width, dynPrec, precision, type) {
      if (match === "%%") return "%";
      // Handle dynamic width
      let actualWidth = width;
      if (dynWidth === '*') {
        actualWidth = String(values[valueIndex++]);
      }
      // Handle dynamic precision
      let actualPrecision = precision;
      if (dynPrec === '*') {
        actualPrecision = String(values[valueIndex++]);
      }
      const value = values[valueIndex++];
      return _pyfunc_format_value(value, type, flags, actualWidth, actualPrecision);
    }
  );
};
var _pymeth_append = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) {
    return this.append.apply(this, arguments);
  }

  this.push(x);
};
var _pymeth_capitalize = function () {
  // nargs: 0
  if (this.constructor !== String) return this.capitalize.apply(this, arguments);
  return this.slice(0, 1).toUpperCase() + this.slice(1).toLowerCase();
};
var _pymeth_casefold = function () {
  // nargs: 0
  if (this.constructor !== String) return this.casefold.apply(this, arguments);
  return this.toLowerCase();
};
var _pymeth_center = function (w, fill) {
  // nargs: 1 2
  if (this.constructor !== String) return this.center.apply(this, arguments);
  fill = fill === undefined ? " " : fill;
  let tofill = Math.max(0, w - this.length);
  let left = Math.ceil(tofill / 2);
  let right = tofill - left;
  return (
    _pymeth_repeat.call(fill, left) + this + _pymeth_repeat.call(fill, right)
  );
};
var _pymeth_clear = function () {
  // nargs: 0
  if (Array.isArray(this)) {
    this.splice(0, this.length);
    return;
  }

  if (this.constructor === Object) {
    const keys = Object.keys(this);
    for (let i = 0; i < keys.length; i++) {
      delete this[keys[i]];
    }
    return;
  }

  return this.clear.apply(this, arguments);
};
var _pymeth_copy = function () {
  // nargs: 0
  if (Array.isArray(this)) {
    return this.slice(0);
  }

  if (this.constructor === Object) {
    const keys = Object.keys(this),
      res = {};
    for (let i = 0; i < keys.length; i++) {
      let key = keys[i];
      res[key] = this[key];
    }
    return res;
  }

  return this.copy.apply(this, arguments);
};
var _pymeth_count = function (x, start, stop) {
  // nargs: 1 2 3
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  if (Array.isArray(this)) {
    let count = 0;
    for (let i = 0; i < this.length; i++) {
      if (_pyfunc_op_equals(this[i], x)) {
        count += 1;
      }
    }
    return count;
  } else if (this.constructor == String) {
    let count = 0,
      i = start;
    while (i >= 0 && i < stop) {
      i = this.indexOf(x, i);
      if (i < 0) break;
      count += 1;
      i += Math.max(1, x.length);
    }
    return count;
  } else return this.count.apply(this, arguments);
};
var _pymeth_endswith = function (x) {
  // nargs: 1
  if (this.constructor !== String) return this.endswith.apply(this, arguments);
  let last_index = this.lastIndexOf(x);
  return last_index == this.length - x.length && last_index >= 0;
};
var _pymeth_expandtabs = function (tabsize) {
  // nargs: 0 1
  if (this.constructor !== String) return this.expandtabs.apply(this, arguments);
  tabsize = tabsize === undefined ? 8 : tabsize;
  return this.replace(/\t/g, _pymeth_repeat.call(" ", tabsize));
};
var _pymeth_extend = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) {
    return this.extend.apply(this, arguments);
  }

  this.push.apply(this, x);
};
var _pymeth_find = function (x, start, stop) {
  // nargs: 1 2 3
  if (this.constructor !== String) return this.find.apply(this, arguments);
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  let i = this.slice(start, stop).indexOf(x);
  if (i >= 0) return i + start;
  return -1;
};
var _pymeth_format = function () {
  if (this.constructor !== String) return this.format.apply(this, arguments);
  let parts = [],
    i = 0,
    i1,
    i2;
  let itemnr = -1;
  while (i < this.length) {
    // find opening
    i1 = this.indexOf("{", i);
    if (i1 < 0 || i1 == this.length - 1) {
      break;
    }
    if (this[i1 + 1] == "{") {
      parts.push(this.slice(i, i1 + 1));
      i = i1 + 2;
      continue;
    }
    // find closing
    i2 = this.indexOf("}", i1);
    if (i2 < 0) {
      break;
    }
    // parse
    itemnr += 1;
    let fmt = this.slice(i1 + 1, i2);
    let index = fmt.split(":")[0].split("!")[0];
    index = index ? Number(index) : itemnr;
    let s = _pyfunc_format(arguments[index], fmt);
    parts.push(this.slice(i, i1), s);
    i = i2 + 1;
  }
  parts.push(this.slice(i));
  return parts.join("");
};
var _pymeth_gen_close = function () {
  // nargs: 0
  // Python generator.close() implementation
  // Throws GeneratorExit at the yield point
  // Silently handles StopIteration and GeneratorExit
  // Raises RuntimeError if generator yields a value

  // Check if this is a generator (has .return method)
  if (typeof this.return !== "function") {
    throw _pyfunc_op_error("AttributeError", "'generator' object has no attribute 'close'");
  }

  // If generator hasn't started, just mark it as done
  if (!this._started) {
    this._closed = true;
    return;
  }

  // Try to close by throwing GeneratorExit
  try {
    // Create a GeneratorExit exception
    let genExit = _pyfunc_op_error("GeneratorExit", "");

    // Try using .throw first (more Pythonic)
    if (typeof this.throw === "function") {
      let result = this.throw(genExit);
      // If generator yielded a value instead of exiting, that's an error
      if (!result.done) {
        throw _pyfunc_op_error("RuntimeError", "generator ignored GeneratorExit");
      }
    } else {
      // Fall back to .return() which terminates the generator
      this.return();
    }
  } catch (e) {
    // StopIteration and GeneratorExit are expected and should be ignored
    if (e.name === "StopIteration" || e.name === "GeneratorExit") {
      return;
    }
    // Other exceptions propagate
    throw e;
  }

  this._closed = true;
};
var _pymeth_gen_throw = function (type, value, traceback) {
  // nargs: 1 2 3
  // Python generator.throw(type[, value[, traceback]]) implementation
  // Throws an exception at the yield point and returns next yielded value

  // Check if this is a generator (has .throw method)
  if (typeof this.throw !== "function") {
    throw _pyfunc_op_error("AttributeError", "'generator' object has no attribute 'throw'");
  }

  // Create the exception to throw
  let exc;
  if (type instanceof Error) {
    // Already an exception instance
    exc = type;
  } else if (typeof type === "function") {
    // Exception class - instantiate it
    if (value !== undefined) {
      exc = type(value);
    } else {
      exc = type();
    }
  } else {
    // type is the exception value itself
    exc = type;
  }

  // Mark generator as started (throw can start a generator)
  this._started = true;

  // Call the underlying JS generator's .throw(exception)
  let result;
  try {
    result = this.throw(exc);
  } catch (e) {
    // Exception was not caught by generator - re-throw
    throw e;
  }

  // If generator is done after handling the exception, raise StopIteration
  if (result.done) {
    throw _pyfunc_op_error("StopIteration", "");
  }

  return result.value;
};
var _pymeth_get = function (key, d) {
  // nargs: 1 2
  // If object has a native .get() method (like Map), use it
  // But check typeof to avoid calling this function recursively
  if (typeof this.get === 'function' && this.constructor !== Object) {
    return this.get.apply(this, arguments);
  }
  // Python dict-like behavior: get key with optional default
  // This works for plain objects and any object without native .get()
  if (this[key] !== undefined) {
    return this[key];
  } else if (d !== undefined) {
    return d;
  } else {
    return null;
  }
};
var _pymeth_index = function (x, start, stop) {
  // nargs: 1 2 3
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  if (Array.isArray(this)) {
    for (let i = start; i < stop; i++) {
      if (_pyfunc_op_equals(this[i], x)) {
        return i;
      } // indexOf cant
    }
  } else if (this.constructor === String) {
    let i = this.slice(start, stop).indexOf(x);
    if (i >= 0) return i + start;
  } else return this.index.apply(this, arguments);
  let e = Error(x);
  e.name = "ValueError";
  throw e;
};
var _pymeth_insert = function (i, x) {
  // nargs: 2
  if (!Array.isArray(this)) {
    return this.insert.apply(this, arguments);
  }

  i = i < 0 ? this.length + i : i;
  this.splice(i, 0, x);
};
var _pymeth_isalnum = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isalnum.apply(this, arguments);
  return Boolean(/^[A-Za-z0-9]+$/.test(this));
};
var _pymeth_isalpha = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isalpha.apply(this, arguments);
  return Boolean(/^[A-Za-z]+$/.test(this));
};
var _pymeth_isdecimal = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isdecimal.apply(this, arguments);

  return Boolean(/^[0-9]+$/.test(this));
};
var _pymeth_isdigit = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isdigit.apply(this, arguments);

  return Boolean(/^[0-9]+$/.test(this));
};
var _pymeth_isidentifier = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isidentifier.apply(this, arguments);

  return Boolean(/^[A-Za-z_][A-Za-z0-9_]*$/.test(this));
};
var _pymeth_islower = function () {
  // nargs: 0
  if (this.constructor !== String) return this.islower.apply(this, arguments);

  let low = this.toLowerCase(),
    high = this.toUpperCase();
  return low != high && low == this;
};
var _pymeth_isnumeric = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isnumeric.apply(this, arguments);

  return Boolean(/^[0-9]+$/.test(this));
};
var _pymeth_isspace = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isspace.apply(this, arguments);

  return Boolean(/^\s+$/.test(this));
};
var _pymeth_istitle = function () {
  // nargs: 0
  if (this.constructor !== String) return this.istitle.apply(this, arguments);

  let low = this.toLowerCase(),
    title = _pymeth_title.call(this);
  return low != title && title == this;
};
var _pymeth_isupper = function () {
  // nargs: 0
  if (this.constructor !== String) return this.isupper.apply(this, arguments);

  let low = this.toLowerCase(),
    high = this.toUpperCase();
  return low != high && high == this;
};
var _pymeth_items = function () {
  // nargs: 0
  // If object has native .items() method, use it
  if (typeof this.items === 'function' && this.constructor !== Object) {
    return this.items.apply(this, arguments);
  }
  // Python dict-like behavior
  let key,
    keys = Object.keys(this),
    res = [];
  for (let i = 0; i < keys.length; i++) {
    key = keys[i];
    res.push([key, this[key]]);
  }
  return res;
};
var _pymeth_join = function (x) {
  // nargs: 1
  if (this.constructor !== String) return this.join.apply(this, arguments);

  // Handle iterators/generators by converting to array first
  if (!Array.isArray(x) && typeof x[Symbol.iterator] === 'function') {
    x = [...x];
  }
  return x.join(this); // call join on the list instead of the string.
};
var _pymeth_keys = function () {
  // nargs: 0
  if (typeof this["keys"] === "function") return this.keys.apply(this, arguments);
  return Object.keys(this);
};
var _pymeth_ljust = function (w, fill) {
  // nargs: 1 2
  if (this.constructor !== String) return this.ljust.apply(this, arguments);

  fill = fill === undefined ? " " : fill;
  let tofill = Math.max(0, w - this.length);
  return this + _pymeth_repeat.call(fill, tofill);
};
var _pymeth_lower = function () {
  // nargs: 0
  if (this.constructor !== String) {
    return this.lower.apply(this, arguments);
  }

  return this.toLowerCase();
};
var _pymeth_lstrip = function (chars) {
  // nargs: 0 1
  if (this.constructor !== String) return this.lstrip.apply(this, arguments);

  chars = chars === undefined ? " \t\r\n" : chars;
  for (let i = 0; i < this.length; i++) {
    if (chars.indexOf(this[i]) < 0) return this.slice(i);
  }
  return "";
};
var _pymeth_partition = function (sep) {
  // nargs: 1
  if (this.constructor !== String) return this.partition.apply(this, arguments);
  if (sep === "") {
    let e = Error("empty sep");
    e.name = "ValueError";
    throw e;
  }
  let i1 = this.indexOf(sep);
  if (i1 < 0) return [this.slice(0), "", ""];
  let i2 = i1 + sep.length;
  return [this.slice(0, i1), this.slice(i1, i2), this.slice(i2)];
};
var _pymeth_pop = function (i, d) {
  // nargs: 1 2
  if (Array.isArray(this)) {
    i = i === undefined ? -1 : i;
    i = i < 0 ? this.length + i : i;
    const popped = this.splice(i, 1);
    if (popped.length) {
      return popped[0];
    }
    const e = Error(i);
    e.name = "IndexError";
    throw e;
  }

  if (this.constructor === Object) {
    let res = this[i];
    if (res !== undefined) {
      delete this[i];
      return res;
    } else if (d !== undefined) {
      return d;
    }
    const e = Error(i);
    e.name = "KeyError";
    throw e;
  }

  return this.pop.apply(this, arguments);
};
var _pymeth_popitem = function () {
  // nargs: 0
  if (typeof this.popitem === 'function' && this.constructor !== Object) {
    return this.popitem.apply(this, arguments);
  }
  // Python dict-like behavior
  let keys, key, val;
  keys = Object.keys(this);
  if (keys.length == 0) {
    let e = Error();
    e.name = "KeyError";
    throw e;
  }
  key = keys[0];
  val = this[key];
  delete this[key];
  return [key, val];
};
var _pymeth_remove = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) {
    return this.remove.apply(this, arguments);
  }

  for (let i = 0; i < this.length; i++) {
    if (_pyfunc_op_equals(this[i], x)) {
      this.splice(i, 1);
      return;
    }
  }
  const e = Error(x);
  e.name = "ValueError";
  throw e;
};
var _pymeth_repeat = function (count) {
  // nargs: 0
  if (this.repeat) return this.repeat(count);
  if (count < 1) return "";
  let result = "",
    pattern = this.valueOf();
  while (count > 1) {
    if (count & 1) result += pattern;
    (count >>= 1), (pattern += pattern);
  }
  return result + pattern;
};
var _pymeth_replace = function (s1, s2, count) {
  // nargs: 2 3
  if (this.constructor !== String) return this.replace.apply(this, arguments);
  count = count === undefined ? 1e20 : count;

  // Special case: empty string replacement inserts between every character
  if (s1.length === 0) {
    if (count <= 0) return this;
    let parts = [];
    let replacements = 0;
    for (let i = 0; i <= this.length; i++) {
      if (replacements < count) {
        parts.push(s2);
        replacements++;
      }
      if (i < this.length) {
        parts.push(this[i]);
      }
    }
    return parts.join("");
  }

  // Normal case: non-empty search string
  let i = 0,
    i2,
    parts = [];
  while (count > 0) {
    i2 = this.indexOf(s1, i);
    if (i2 >= 0) {
      parts.push(this.slice(i, i2));
      parts.push(s2);
      i = i2 + s1.length;
      count -= 1;
    } else break;
  }
  parts.push(this.slice(i));
  return parts.join("");
};
var _pymeth_reverse = function () {
  // nargs: 0
  this.reverse();
};
var _pymeth_rfind = function (x, start, stop) {
  // nargs: 1 2 3
  if (this.constructor !== String) return this.rfind.apply(this, arguments);
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  let i = this.slice(start, stop).lastIndexOf(x);
  if (i >= 0) return i + start;
  return -1;
};
var _pymeth_rindex = function (x, start, stop) {
  // nargs: 1 2 3
  if (this.constructor !== String) return this.rindex.apply(this, arguments);
  let i = _pymeth_rfind.call(this, x, start, stop);
  if (i >= 0) return i;
  let e = Error(x);
  e.name = "ValueError";
  throw e;
};
var _pymeth_rjust = function (w, fill) {
  // nargs: 1 2
  if (this.constructor !== String) return this.rjust.apply(this, arguments);
  fill = fill === undefined ? " " : fill;
  let tofill = Math.max(0, w - this.length);
  return _pymeth_repeat.call(fill, tofill) + this;
};
var _pymeth_rpartition = function (sep) {
  // nargs: 1
  if (this.constructor !== String) return this.rpartition.apply(this, arguments);
  if (sep === "") {
    let e = Error("empty sep");
    e.name = "ValueError";
    throw e;
  }
  let i1 = this.lastIndexOf(sep);
  if (i1 < 0) return ["", "", this.slice(0)];
  let i2 = i1 + sep.length;
  return [this.slice(0, i1), this.slice(i1, i2), this.slice(i2)];
};
var _pymeth_rsplit = function (sep, count) {
  // nargs: 1 2
  if (this.constructor !== String) return this.rsplit.apply(this, arguments);
  sep = sep === undefined ? /\s/ : sep;
  count = Math.max(0, count === undefined ? 1e20 : count);
  let parts = this.split(sep);
  let limit = Math.max(0, parts.length - count);
  let res = parts.slice(limit);
  if (count < parts.length) res.splice(0, 0, parts.slice(0, limit).join(sep));
  return res;
};
var _pymeth_rstrip = function (chars) {
  // nargs: 0 1
  if (this.constructor !== String) return this.rstrip.apply(this, arguments);
  chars = chars === undefined ? " \t\r\n" : chars;
  for (let i = this.length - 1; i >= 0; i--) {
    if (chars.indexOf(this[i]) < 0) return this.slice(0, i + 1);
  }
  return "";
};
var _pymeth_send = function (value) {
  // nargs: 1
  // Python generator.send(value) implementation
  // - First call must send None (null) or TypeError is raised
  // - Returns the yielded value (unwraps JS {value, done} object)
  // - Raises StopIteration when generator is exhausted

  // Check if this is a generator (has .next method)
  if (typeof this.next !== "function") {
    throw _pyfunc_op_error("AttributeError", "'object' has no attribute 'send'");
  }

  // Track if generator has been started using a hidden property
  if (!this._started) {
    // First call - must be None (null/undefined)
    if (value !== null && value !== undefined) {
      throw _pyfunc_op_error(
        "TypeError",
        "can't send non-None value to a just-started generator"
      );
    }
    this._started = true;
  }

  // Call the underlying JS generator's .next(value)
  let result = this.next(value);

  // If generator is done, raise StopIteration
  if (result.done) {
    throw _pyfunc_op_error("StopIteration", "");
  }

  return result.value;
};
var _pymeth_setdefault = function (key, d) {
  // nargs: 1 2
  if (typeof this.setdefault === 'function' && this.constructor !== Object) {
    return this.setdefault.apply(this, arguments);
  }
  // Python dict-like behavior
  if (this[key] !== undefined) {
    return this[key];
  } else if (d !== undefined) {
    this[key] = d;
    return d;
  } else {
    return null;
  }
};
var _pymeth_sort = function (key, reverse) {
  // nargs: 0 1 2
  if (!Array.isArray(this)) {
    return this.sort.apply(this, arguments);
  }

  let comp = function (a, b) {
    a = key(a);
    b = key(b);
    if (a < b) {
      return -1;
    }
    if (a > b) {
      return 1;
    }
    return 0;
  };
  comp = Boolean(key) ? comp : undefined;
  this.sort(comp);
  if (reverse) {
    this.reverse();
  }
};
var _pymeth_split = function (sep, count) {
  // nargs: 0, 1 2
  if (this.constructor !== String) return this.split.apply(this, arguments);
  if (sep === "") {
    let e = Error("empty sep");
    e.name = "ValueError";
    throw e;
  }
  sep = sep === undefined ? /\s/ : sep;
  if (count === undefined) {
    return this.split(sep);
  }
  let res = [],
    i = 0,
    index1 = 0,
    index2 = 0;
  while (i < count && index1 < this.length) {
    index2 = this.indexOf(sep, index1);
    if (index2 < 0) {
      break;
    }
    res.push(this.slice(index1, index2));
    index1 = index2 + sep.length || 1;
    i += 1;
  }
  res.push(this.slice(index1));
  return res;
};
var _pymeth_splitlines = function (keepends) {
  // nargs: 0 1
  if (this.constructor !== String) return this.splitlines.apply(this, arguments);
  keepends = keepends ? 1 : 0;
  let finder = /\r\n|\r|\n/g;
  let i = 0,
    i2,
    isrn,
    parts = [];
  while (finder.exec(this) !== null) {
    i2 = finder.lastIndex - 1;
    isrn = i2 > 0 && this[i2 - 1] == "\r" && this[i2] == "\n";
    if (keepends) parts.push(this.slice(i, finder.lastIndex));
    else parts.push(this.slice(i, i2 - isrn));
    i = finder.lastIndex;
  }
  if (i < this.length) parts.push(this.slice(i));
  else if (!parts.length) parts.push("");
  return parts;
};
var _pymeth_startswith = function (x) {
  // nargs: 1
  if (this.constructor !== String) return this.startswith.apply(this, arguments);
  return this.indexOf(x) == 0;
};
var _pymeth_strip = function (chars) {
  // nargs: 0 1
  if (this.constructor !== String) return this.strip.apply(this, arguments);
  chars = chars === undefined ? " \t\r\n" : chars;
  let i,
    s1 = this,
    s2 = "",
    s3 = "";
  for (i = 0; i < s1.length; i++) {
    if (chars.indexOf(s1[i]) < 0) {
      s2 = s1.slice(i);
      break;
    }
  }
  for (i = s2.length - 1; i >= 0; i--) {
    if (chars.indexOf(s2[i]) < 0) {
      s3 = s2.slice(0, i + 1);
      break;
    }
  }
  return s3;
};
var _pymeth_swapcase = function () {
  // nargs: 0
  if (this.constructor !== String) return this.swapcase.apply(this, arguments);
  let c,
    res = [];
  for (let i = 0; i < this.length; i++) {
    c = this[i];
    if (c.toUpperCase() == c) res.push(c.toLowerCase());
    else res.push(c.toUpperCase());
  }
  return res.join("");
};
var _pymeth_title = function () {
  // nargs: 0
  if (this.constructor !== String) return this.title.apply(this, arguments);
  let i0,
    res = [],
    tester = /^[^A-Za-z]?[A-Za-z]$/;
  for (let i = 0; i < this.length; i++) {
    i0 = Math.max(0, i - 1);
    if (tester.test(this.slice(i0, i + 1))) res.push(this[i].toUpperCase());
    else res.push(this[i].toLowerCase());
  }
  return res.join("");
};
var _pymeth_to_bytes = function (length, byteorder, signed) {
  // nargs: 2 3
  // int.to_bytes(length, byteorder, *, signed=False)
  // Converts an integer to a bytes object
  let n = typeof this === "number" ? this : Number(this);
  signed = signed === true || signed === "true";

  // Check for negative length
  if (length < 0) {
    throw _pyfunc_op_error("ValueError", "length argument must be non-negative");
  }

  // Check for negative numbers when unsigned
  if (!signed && n < 0) {
    throw _pyfunc_op_error("OverflowError", "can't convert negative int to unsigned");
  }

  // Special case: 0 can always be represented in 0 bytes
  if (length === 0) {
    if (n === 0) {
      return new Uint8Array(0);
    } else {
      throw _pyfunc_op_error("OverflowError", "int too big to convert");
    }
  }

  // Calculate max value for given length
  let maxVal = signed ? Math.pow(2, length * 8 - 1) - 1 : Math.pow(2, length * 8) - 1;
  let minVal = signed ? -Math.pow(2, length * 8 - 1) : 0;

  if (n > maxVal || n < minVal) {
    throw _pyfunc_op_error("OverflowError", "int too big to convert");
  }

  // Handle signed negative numbers (two's complement)
  if (signed && n < 0) {
    n = Math.pow(2, length * 8) + n;
  }

  let bytes = new Uint8Array(length);
  let isLittle = byteorder === "little";

  for (let i = 0; i < length; i++) {
    let idx = isLittle ? i : length - 1 - i;
    bytes[idx] = n & 0xff;
    n = Math.floor(n / 256);
  }

  return bytes;
};
var _pymeth_translate = function (table) {
  // nargs: 1
  if (this.constructor !== String) return this.translate.apply(this, arguments);
  let c,
    res = [];
  for (let i = 0; i < this.length; i++) {
    c = table[this[i]];
    if (c === undefined) res.push(this[i]);
    else if (c !== null) res.push(c);
  }
  return res.join("");
};
var _pymeth_update = function (other) {
  // nargs: 1
  if (typeof this.update === 'function' && this.constructor !== Object) {
    return this.update.apply(this, arguments);
  }
  // Python dict-like behavior
  let key,
    keys = Object.keys(other);
  for (let i = 0; i < keys.length; i++) {
    key = keys[i];
    this[key] = other[key];
  }
  return null;
};
var _pymeth_upper = function () {
  // nargs: 0
  if (this.constructor === String) {
    return this.toUpperCase();
  }
  return this.upper.apply(this, arguments);
};
var _pymeth_values = function () {
  // nargs: 0
  if (typeof this.values === 'function' && this.constructor !== Object) {
    return this.values.apply(this, arguments);
  }
  // Python dict-like behavior
  let key,
    keys = Object.keys(this),
    res = [];
  for (let i = 0; i < keys.length; i++) {
    key = keys[i];
    res.push(this[key]);
  }
  return res;
};
var _pymeth_zfill = function (width) {
  // nargs: 1
  if (this.constructor !== String) return this.zfill.apply(this, arguments);
  return _pymeth_rjust.call(this, width, "0");
};
