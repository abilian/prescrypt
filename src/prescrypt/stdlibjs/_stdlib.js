var _pyfunc_Ellipsis = Symbol.for('Ellipsis');
var _pyfunc_abs = Math.abs;;
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
var _pyfunc_create_dict = function () {
  const d = {};
  for (let i = 0; i < arguments.length; i += 2) {
    d[arguments[i]] = arguments[i + 1];
  }
  return d;
};
var _pyfunc_delattr = function (ob, name) {
  // nargs: 2
  delete ob[name];
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
var _pyfunc_format = function (v, fmt) {
  // nargs: 1 2
  if (fmt === undefined) {
    return String(v);
  }
  fmt = fmt.toLowerCase();
  let s = String(v);
  if (fmt.indexOf("!r") >= 0) {
    try {
      s = JSON.stringify(v);
    } catch (e) {
      s = undefined;
    }
    if (typeof s === "undefined") {
      s = v._IS_COMPONENT ? v.id : String(v);
    }
  }
  let fmt_type = "";
  if (
    fmt.slice(-1) == "i" ||
    fmt.slice(-1) == "f" ||
    fmt.slice(-1) == "e" ||
    fmt.slice(-1) == "g"
  ) {
    fmt_type = fmt[fmt.length - 1];
    fmt = fmt.slice(0, fmt.length - 1);
  }
  let i0 = fmt.indexOf(":");
  let i1 = fmt.indexOf(".");
  let spec1 = "",
    spec2 = ""; // before and after dot
  if (i0 >= 0) {
    if (i1 > i0) {
      spec1 = fmt.slice(i0 + 1, i1);
      spec2 = fmt.slice(i1 + 1);
    } else {
      spec1 = fmt.slice(i0 + 1);
    }
  } else if (i1 >= 0) {
    // No colon, but has dot (e.g., ".2f" after removing "f")
    spec1 = fmt.slice(0, i1);
    spec2 = fmt.slice(i1 + 1);
  }
  // Format numbers
  if (fmt_type == "") {
  } else if (fmt_type == "i") {
    // integer formatting, for %i
    s = parseInt(v).toFixed(0);
  } else if (fmt_type == "f") {
    // float formatting
    v = parseFloat(v);
    let decimals = spec2 ? Number(spec2) : 6;
    s = v.toFixed(decimals);
  } else if (fmt_type == "e") {
    // exp formatting
    v = parseFloat(v);
    let precision = (spec2 ? Number(spec2) : 6) || 1;
    s = v.toExponential(precision);
  } else if (fmt_type == "g") {
    // "general" formatting
    v = parseFloat(v);
    let precision = (spec2 ? Number(spec2) : 6) || 1;
    // Exp or decimal?
    s = v.toExponential(precision - 1);
    let s1 = s.slice(0, s.indexOf("e")),
      s2 = s.slice(s.indexOf("e"));
    if (s2.length == 3) {
      s2 = "e" + s2[1] + "0" + s2[2];
    }
    let exp = Number(s2.slice(1));
    if (exp >= -4 && exp < precision) {
      s1 = v.toPrecision(precision);
      s2 = "";
    }
    // Skip trailing zeros and dot
    let j = s1.length - 1;
    while (j > 0 && s1[j] == "0") {
      j -= 1;
    }
    s1 = s1.slice(0, j + 1);
    if (s1.slice(-1) == ".") {
      s1 = s1.slice(0, s1.length - 1);
    }
    s = s1 + s2;
  }
  // prefix/padding
  let prefix = "";
  if (spec1) {
    if (spec1[0] == "+" && v > 0) {
      prefix = "+";
      spec1 = spec1.slice(1);
    } else if (spec1[0] == " " && v > 0) {
      prefix = " ";
      spec1 = spec1.slice(1);
    }
  }
  if (spec1 && spec1[0] == "0") {
    let padding = Number(spec1.slice(1)) - (s.length + prefix.length);
    s = "0".repeat(Math.max(0, padding)) + s;
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
var _pyfunc_getattr = function (ob, name, deflt) {
  // nargs: 2 3
  let has_attr = ob !== undefined && ob !== null && ob[name] !== undefined;
  if (has_attr) {
    return ob[name];
  } else if (arguments.length == 3) {
    return deflt;
  } else {
    let e = Error(name);
    e.name = "AttributeError";
    throw e;
  }
};
var _pyfunc_hasattr = function (ob, name) {
  // nargs: 2
  return ob !== undefined && ob !== null && ob[name] !== undefined;
};
var _pyfunc_int = function (x, base) {
  // nargs: 1 2
  if (base !== undefined) {
    return parseInt(x, base);
  }
  return x < 0 ? Math.ceil(x) : Math.floor(x);
};
var _pyfunc_list = function (x) {
  // Handle iterators/generators using spread
  if (typeof x[Symbol.iterator] === 'function') {
    return [...x];
  }
  // Handle plain objects by converting to array of keys
  if (typeof x === "object" && !Array.isArray(x)) {
    return Object.keys(x);
  }
  // Fallback for array-like objects
  const res = [];
  for (let i = 0; i < x.length; i++) {
    res.push(x[i]);
  }
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
  return a + b;
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
var _pyfunc_op_error = function (etype, ...args) {
  // nargs: 1+
  let msg = args.join(", ");
  let e = new Error(etype + ": " + msg);
  e.name = etype;
  e.args = args;  // Store args for repr()
  return e;
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
  // Handle negative indices for arrays and strings
  if (typeof key === 'number' && key < 0 && (Array.isArray(obj) || typeof obj === 'string')) {
    key = obj.length + key;
  }
  return obj[key];
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
var _pyfunc_op_matmul = function (a, b) {
  // nargs: 2
  // Matrix multiplication operator @
  // Delegates to __matmul__ method if available
  if (typeof a.__matmul__ === 'function') {
    return a.__matmul__(b);
  }
  if (typeof b.__rmatmul__ === 'function') {
    return b.__rmatmul__(a);
  }
  throw new TypeError("unsupported operand type(s) for @");
};
var _pyfunc_op_mod = function (left, right) {
  // nargs: 2
  // Handles Python's % operator which can be either:
  // - String formatting: "hello %s" % "world"
  // - Numeric modulo: 7 % 3
  if (typeof left === 'string') {
    return _pyfunc_string_mod(left, right);
  }
  return left % right;
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
var _pyfunc_repr = function (x) {
  // nargs: 1
  // Handle Error objects (Python exceptions)
  if (x instanceof Error && x.name && x.args !== undefined) {
    let argsRepr = x.args.map(a => _pyfunc_repr(a)).join(", ");
    return x.name + "(" + argsRepr + ")";
  }
  // Handle booleans with Python-style capitalization
  if (typeof x === "boolean") {
    return x ? "True" : "False";
  }
  // Handle strings - use single quotes like Python
  if (typeof x === "string") {
    // Escape single quotes and backslashes, use single quotes
    return "'" + x.replace(/\\/g, "\\\\").replace(/'/g, "\\'") + "'";
  }
  // Handle null (None in Python)
  if (x === null) {
    return "None";
  }
  // Handle arrays (lists/tuples)
  if (Array.isArray(x)) {
    let items = x.map(e => _pyfunc_repr(e));
    return "[" + items.join(", ") + "]";
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
var _pyfunc_setattr = function (ob, name, value) {
  // nargs: 3
  ob[name] = value;
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
  if (typeof iter === "object" && !Array.isArray(iter)) {
    iter = Object.keys(iter);
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
var _pyfunc_str = function (x) {
  // nargs: 0 1;
  if (x === undefined) {
    return "";
  }
  // Handle booleans with Python-style capitalization
  if (typeof x === "boolean") {
    return x ? "True" : "False";
  }
  if (Array.isArray(x)) {
    if (x.length == 0) {
      return "[]";
    }
    let result = "[" + _pyfunc_str(x[0]);
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
  // Default
  return JSON.stringify(x);
};
var _pyfunc_str_decode = function (bytes, encoding) {
  // nargs: 2
  // Decode bytes/bytearray to string using specified encoding
  // Convert to Uint8Array if needed (handles both Array and TypedArray)
  let arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  // Use TextDecoder for proper encoding support
  let decoder = new TextDecoder(encoding || "utf-8");
  return decoder.decode(arr);
};
var _pyfunc_str_error_args = function () {
  // nargs: 0+
  // Called when str() has too many arguments - raises TypeError at runtime
  throw _pyfunc_op_error("TypeError", "str() takes at most 3 arguments");
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
  return new Proxy({}, {
    get: function(target, prop) {
      if (prop in base) {
        var val = base[prop];
        if (typeof val === 'function') {
          return val.bind(self);
        }
        return val;
      }
      return undefined;
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
var _pymeth_get = function (key, d) {
  // nargs: 1 2
  if (this.constructor !== Object) return this.get.apply(this, arguments);
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
  if (this.constructor !== Object) return this.items.apply(this, arguments);
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
  if (this.constructor !== Object) return this.popitem.apply(this, arguments);
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
var _pymeth_setdefault = function (key, d) {
  // nargs: 1 2
  if (this.constructor !== Object) return this.setdefault.apply(this, arguments);
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
  if (this.constructor !== Object) return this.update.apply(this, arguments);
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
  if (this.constructor !== Object) return this.values.apply(this, arguments);
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
