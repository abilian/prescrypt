// function: Ellipsis
export const Ellipsis = Symbol.for('Ellipsis')

// ---

// function: NotImplemented
export const NotImplemented = Symbol.for('NotImplemented');

// ---

// function: type_int
// Type identifiers - used for isinstance() and subclassing
export const type_int = Number;

// ---

// function: type_float
export const type_float = Number;

// ---

// function: type_str
export const type_str = String;

// ---

// function: type_bool
export const type_bool = Boolean;

// ---

// function: type_list
export const type_list = Array;

// ---

// function: type_tuple
export const type_tuple = Array;

// ---

// function: type_dict
export const type_dict = Object;

// ---

// function: type_set
export const type_set = Set;

// ---

// function: type_bytes
export const type_bytes = Uint8Array;

// ---

// function: type_object
// Base object class - all objects inherit from this
export const type_object = Object;

// ---

// function: type_type
// type() builtin - returns the type of an object
export const type_type = function (x) {
  // nargs: 1
  if (x === null) return "NoneType";
  if (x === undefined) return "NoneType";
  if (typeof x === "boolean") return FUNCTION_PREFIXtype_bool;
  if (typeof x === "number") {
    return Number.isInteger(x) ? FUNCTION_PREFIXtype_int : FUNCTION_PREFIXtype_float;
  }
  if (typeof x === "string") return FUNCTION_PREFIXtype_str;
  if (Array.isArray(x)) return FUNCTION_PREFIXtype_list;
  if (x instanceof Uint8Array) return FUNCTION_PREFIXtype_bytes;
  if (x instanceof Set) return FUNCTION_PREFIXtype_set;
  if (x instanceof Map) return FUNCTION_PREFIXtype_dict;
  if (typeof x === "function") return "function";
  if (typeof x === "object") {
    // Check for class instances
    if (x.constructor && x.constructor !== Object) {
      return x.constructor;
    }
    return FUNCTION_PREFIXtype_dict;
  }
  return typeof x;
};

// ---

// function: BaseException
// Exception types - using closure pattern to create proper exception classes
export const BaseException = (function() {
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

// ---

// function: Exception
export const Exception = (function() {
  // nargs: 0+
  function Exception(...args) {
    if (!(this instanceof Exception)) {
      return new Exception(...args);
    }
    FUNCTION_PREFIXBaseException.call(this, ...args);
    this.name = "Exception";
  }
  Exception.prototype = Object.create(FUNCTION_PREFIXBaseException.prototype);
  Exception.prototype.constructor = Exception;
  return Exception;
})();

// ---

// function: StopIteration
export const StopIteration = (function() {
  // nargs: 0 1
  function StopIteration(message) {
    if (!(this instanceof StopIteration)) {
      return new StopIteration(message);
    }
    FUNCTION_PREFIXException.call(this, message);
    this.name = "StopIteration";
  }
  StopIteration.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  StopIteration.prototype.constructor = StopIteration;
  return StopIteration;
})();

// ---

// function: GeneratorExit
export const GeneratorExit = (function() {
  // nargs: 0 1
  function GeneratorExit(message) {
    if (!(this instanceof GeneratorExit)) {
      return new GeneratorExit(message);
    }
    FUNCTION_PREFIXBaseException.call(this, message);
    this.name = "GeneratorExit";
  }
  GeneratorExit.prototype = Object.create(FUNCTION_PREFIXBaseException.prototype);
  GeneratorExit.prototype.constructor = GeneratorExit;
  return GeneratorExit;
})();

// ---

// function: ValueError
export const ValueError = (function() {
  // nargs: 0+
  function ValueError(...args) {
    if (!(this instanceof ValueError)) {
      return new ValueError(...args);
    }
    FUNCTION_PREFIXException.call(this, ...args);
    this.name = "ValueError";
  }
  ValueError.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  ValueError.prototype.constructor = ValueError;
  return ValueError;
})();

// ---

// function: IndexError
export const IndexError = (function() {
  // nargs: 0 1
  function IndexError(message) {
    if (!(this instanceof IndexError)) {
      return new IndexError(message);
    }
    FUNCTION_PREFIXException.call(this, message);
    this.name = "IndexError";
  }
  IndexError.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  IndexError.prototype.constructor = IndexError;
  return IndexError;
})();

// ---

// function: TypeError_py
export const TypeError_py = (function() {
  // nargs: 0 1
  function TypeError_py(message) {
    if (!(this instanceof TypeError_py)) {
      return new TypeError_py(message);
    }
    FUNCTION_PREFIXException.call(this, message);
    this.name = "TypeError";
  }
  TypeError_py.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  TypeError_py.prototype.constructor = TypeError_py;
  return TypeError_py;
})();

// ---

// function: KeyError
export const KeyError = (function() {
  // nargs: 0 1
  function KeyError(message) {
    if (!(this instanceof KeyError)) {
      return new KeyError(message);
    }
    FUNCTION_PREFIXException.call(this, message);
    this.name = "KeyError";
  }
  KeyError.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  KeyError.prototype.constructor = KeyError;
  return KeyError;
})();

// ---

// function: AttributeError
export const AttributeError = (function() {
  // nargs: 0 1
  function AttributeError(message) {
    if (!(this instanceof AttributeError)) {
      return new AttributeError(message);
    }
    FUNCTION_PREFIXException.call(this, message);
    this.name = "AttributeError";
  }
  AttributeError.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  AttributeError.prototype.constructor = AttributeError;
  return AttributeError;
})();

// ---

// function: RuntimeError
export const RuntimeError = (function() {
  // nargs: 0 1
  function RuntimeError(message) {
    if (!(this instanceof RuntimeError)) {
      return new RuntimeError(message);
    }
    FUNCTION_PREFIXException.call(this, message);
    this.name = "RuntimeError";
  }
  RuntimeError.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  RuntimeError.prototype.constructor = RuntimeError;
  return RuntimeError;
})();

// ---

// function: NameError
export const NameError = (function() {
  // nargs: 0 1
  function NameError(message) {
    if (!(this instanceof NameError)) {
      return new NameError(message);
    }
    FUNCTION_PREFIXException.call(this, message);
    this.name = "NameError";
  }
  NameError.prototype = Object.create(FUNCTION_PREFIXException.prototype);
  NameError.prototype.constructor = NameError;
  return NameError;
})();

// ---

// function: perf_counter
export const perf_counter = function () {
  // nargs: 0
  if (typeof process === "undefined") {
    return performance.now() * 1e-3;
  } else {
    const t = process.hrtime();
    return t[0] + t[1] * 1e-9;
  }
};

// ---

// function: time
export const time = function () {
  return Date.now() / 1000;
}; // nargs: 0;

// ---

// function: op_instantiate
export const op_instantiate = function (ob, args) {
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

// ---

// function: super_proxy
export const super_proxy = function (self, classProto) {
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

// ---

// function: create_dict
export const create_dict = function () {
  const d = {};
  for (let i = 0; i < arguments.length; i += 2) {
    d[arguments[i]] = arguments[i + 1];
  }
  return d;
};

// ---

// function: merge_dicts
export const merge_dicts = function () {
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

// ---

// function: op_parse_kwargs
export const op_parse_kwargs = function (
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
    throw FUNCTION_PREFIXop_error(
      "TypeError",
      "Function " + strict + " does not accept **kwargs."
    );
  }
  return kwargs;
};

// ---

// function: op_error
export const op_error = function (etype, ...args) {
  // nargs: 1+
  let msg = args.join(", ");
  let e = new Error(etype + ": " + msg);
  e.name = etype;
  e.args = args;  // Store args for repr()
  return e;
};

// ---

// function: hasattr
export const hasattr = function (ob, name) {
  // nargs: 2
  return ob !== undefined && ob !== null && ob[name] !== undefined;
};

// ---

// function: getattr
export const getattr = function (ob, name, deflt) {
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

// ---

// function: setattr
export const setattr = function (ob, name, value) {
  // nargs: 3
  ob[name] = value;
};

// ---

// function: delattr
export const delattr = function (ob, name) {
  // nargs: 2
  delete ob[name];
};

// ---

// function: dict
export const dict = function (x) {
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

// ---

// function: iter
export const iter = function (x) {
  // nargs: 1
  // Returns an iterator for the given iterable
  if (typeof x[Symbol.iterator] === "function") {
    return x[Symbol.iterator]();
  }
  // Handle plain objects by iterating over keys
  if (typeof x === "object" && x !== null) {
    return Object.keys(x)[Symbol.iterator]();
  }
  throw FUNCTION_PREFIXop_error("TypeError", "'" + typeof x + "' object is not iterable");
};

// ---

// function: next
export const next = function (iterator, defaultValue) {
  // nargs: 1 2
  // Get next item from iterator
  // Check if generator was closed
  if (iterator._closed) {
    if (arguments.length >= 2) {
      return defaultValue;
    }
    throw FUNCTION_PREFIXop_error("StopIteration", "");
  }
  // Mark generator as started for send/close methods
  iterator._started = true;
  let result = iterator.next();
  if (result.done) {
    if (arguments.length >= 2) {
      return defaultValue;
    }
    throw FUNCTION_PREFIXop_error("StopIteration", "");
  }
  return result.value;
};

// ---

// function: zip
export const zip = function (...iterables) {
  // nargs: 0+
  // Zip iterables together, yielding tuples
  if (iterables.length === 0) {
    return [];
  }
  // Convert all to arrays for simplicity
  let arrays = iterables.map(it => {
    if (Array.isArray(it)) return it;
    if (typeof it[Symbol.iterator] === "function") return [...it];
    return Array.from(it);
  });
  let minLen = Math.min(...arrays.map(a => a.length));
  let result = [];
  for (let i = 0; i < minLen; i++) {
    result.push(arrays.map(a => a[i]));
  }
  return result;
};

// ---

// function: map
export const map = function (func, ...iterables) {
  // nargs: 1+
  // Map function over iterable(s)
  if (iterables.length === 0) {
    throw FUNCTION_PREFIXop_error("TypeError", "map() must have at least two arguments");
  }
  if (iterables.length === 1) {
    // Single iterable - simple case
    let arr = iterables[0];
    if (!Array.isArray(arr)) {
      if (typeof arr[Symbol.iterator] === "function") {
        arr = [...arr];
      } else {
        arr = Array.from(arr);
      }
    }
    return arr.map(x => func(x));
  }
  // Multiple iterables - zip and apply
  let zipped = FUNCTION_PREFIXzip(...iterables);
  return zipped.map(args => func(...args));
};

// ---

// function: filter
export const filter = function (func, iterable) {
  // nargs: 2
  // Filter iterable by function
  let arr = iterable;
  if (!Array.isArray(arr)) {
    if (typeof arr[Symbol.iterator] === "function") {
      arr = [...arr];
    } else {
      arr = Array.from(arr);
    }
  }
  if (func === null || func === undefined) {
    // filter(None, iterable) filters out falsy values
    return arr.filter(x => FUNCTION_PREFIXtruthy(x));
  }
  return arr.filter(x => func(x));
};

// ---

// function: list
export const list = function (x) {
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

// ---

// function: range
export const range = function (start, end, step) {
  const res = [];
  let val = start;
  let n = (end - start) / step;
  for (let i = 0; i < n; i++) {
    res.push(val);
    val += step;
  }
  return res;
};

// ---

// function: format
export const format = function (v, fmt) {
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

// ---

// function: pow
export const pow = Math.pow; // nargs: 2;

// ---

// function: sum
export const sum = function (x) {
  // nargs: 1
  // Convert iterators/generators to array first
  if (!Array.isArray(x) && typeof x[Symbol.iterator] === 'function') {
    x = [...x];
  }
  return x.reduce(function (a, b) {
    return a + b;
  }, 0);
};

// ---

// function: round
export const round = function (x, ndigits) {
  // nargs: 1 2
  if (ndigits === undefined || ndigits === 0) {
    return Math.round(x);
  }
  const factor = Math.pow(10, ndigits);
  return Math.round(x * factor) / factor;
};

// ---

// function: hex
export const hex = function (x) {
  // nargs: 1
  // Convert integer to hexadecimal string with 0x prefix
  if (typeof x !== "number" || !Number.isInteger(x)) {
    if (typeof x.__index__ === "function") {
      x = x.__index__();
    } else {
      throw FUNCTION_PREFIXop_error("TypeError", "'float' object cannot be interpreted as an integer");
    }
  }
  if (x < 0) {
    return "-0x" + (-x).toString(16);
  }
  return "0x" + x.toString(16);
};

// ---

// function: bin
export const bin = function (x) {
  // nargs: 1
  // Convert integer to binary string with 0b prefix
  if (typeof x !== "number" || !Number.isInteger(x)) {
    if (typeof x.__index__ === "function") {
      x = x.__index__();
    } else {
      throw FUNCTION_PREFIXop_error("TypeError", "'float' object cannot be interpreted as an integer");
    }
  }
  if (x < 0) {
    return "-0b" + (-x).toString(2);
  }
  return "0b" + x.toString(2);
};

// ---

// function: oct
export const oct = function (x) {
  // nargs: 1
  // Convert integer to octal string with 0o prefix
  if (typeof x !== "number" || !Number.isInteger(x)) {
    if (typeof x.__index__ === "function") {
      x = x.__index__();
    } else {
      throw FUNCTION_PREFIXop_error("TypeError", "'float' object cannot be interpreted as an integer");
    }
  }
  if (x < 0) {
    return "-0o" + (-x).toString(8);
  }
  return "0o" + x.toString(8);
};

// ---

// function: abs
export const abs = function (x) {
  // nargs: 1
  // Return absolute value
  if (typeof x.__abs__ === "function") {
    return x.__abs__();
  }
  return Math.abs(x);
};

// ---

// function: hash
export const hash = function (x) {
  // nargs: 1
  // Return hash value of object
  if (typeof x.__hash__ === "function") {
    return x.__hash__();
  }
  if (x === null || x === undefined) {
    throw FUNCTION_PREFIXop_error("TypeError", "unhashable type: 'NoneType'");
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
    throw FUNCTION_PREFIXop_error("TypeError", "unhashable type: 'list'");
  }
  if (typeof x === "object" && x.constructor === Object) {
    throw FUNCTION_PREFIXop_error("TypeError", "unhashable type: 'dict'");
  }
  if (x instanceof Set) {
    throw FUNCTION_PREFIXop_error("TypeError", "unhashable type: 'set'");
  }
  // For other objects, use a unique id approach
  return FUNCTION_PREFIXid(x);
};

// ---

// function: id
export const id = function (x) {
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
  if (!FUNCTION_PREFIXid._map) {
    FUNCTION_PREFIXid._map = new WeakMap();
    FUNCTION_PREFIXid._counter = 1;
  }
  if (!FUNCTION_PREFIXid._map.has(x)) {
    FUNCTION_PREFIXid._map.set(x, FUNCTION_PREFIXid._counter++);
  }
  return FUNCTION_PREFIXid._map.get(x);
};

// ---

// function: int
export const int = function (x, base) {
  // nargs: 1 2
  if (base !== undefined) {
    return parseInt(x, base);
  }
  return x < 0 ? Math.ceil(x) : Math.floor(x);
};

// ---

// function: float
export const float = Number; // nargs: 1;

// ---

// function: str
// export const str = String // nargs: 0 1;
export const str = function (x) {
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
    return FUNCTION_PREFIXbytes_repr(x);
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
      firstStr = FUNCTION_PREFIXstr(first);
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
        const t = FUNCTION_PREFIXstr(e);
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
      let vStr = FUNCTION_PREFIXrepr(v);
      return kStr + ": " + vStr;
    });
    return "{" + parts.join(", ") + "}";
  }
  // Default - use String() for objects without __str__
  return String(x);
};

// ---

// function: bytes_repr
export const bytes_repr = function (bytes) {
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

// ---

// function: str_decode
export const str_decode = function (bytes, encoding) {
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
  throw FUNCTION_PREFIXop_error("LookupError", "unknown encoding: " + encoding);
};

// ---

// function: str_error_args
export const str_error_args = function () {
  // nargs: 0+
  // Called when str() has too many arguments - raises TypeError at runtime
  throw FUNCTION_PREFIXop_error("TypeError", "str() takes at most 3 arguments");
};

// ---

// function: bytes
export const bytes = function (source) {
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
    throw FUNCTION_PREFIXop_error("TypeError", "string argument without an encoding");
  }
  // If it's a number, create zero-filled bytes
  if (typeof source === "number") {
    if (source < 0) {
      throw FUNCTION_PREFIXop_error("ValueError", "negative count");
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
  throw FUNCTION_PREFIXop_error("TypeError", "cannot convert '" + typeof source + "' object to bytes");
};

// ---

// function: bytes_encode
export const bytes_encode = function (string, encoding) {
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
  throw FUNCTION_PREFIXop_error("LookupError", "unknown encoding: " + encoding);
};

// ---

// function: bytes_error_args
export const bytes_error_args = function () {
  // nargs: 0+
  // Called when bytes() has too many arguments - raises TypeError at runtime
  throw FUNCTION_PREFIXop_error("TypeError", "bytes() takes at most 3 arguments");
};

// ---

// function: int_from_bytes
export const int_from_bytes = function (bytes, byteorder, signed) {
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

// ---

// function: repr
export const repr = function (x) {
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
    let argsRepr = x.args.map(a => FUNCTION_PREFIXrepr(a)).join(", ");
    return x.name + "(" + argsRepr + ")";
  }
  // Handle bytes (Uint8Array)
  if (x instanceof Uint8Array) {
    return FUNCTION_PREFIXbytes_repr(x);
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
    let items = x.map(e => FUNCTION_PREFIXrepr(e));
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
      let kRepr = FUNCTION_PREFIXrepr(k);
      let vRepr = FUNCTION_PREFIXrepr(v);
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

// ---

// function: bool
export const bool = function (x) {
  // nargs: 1
  return Boolean(FUNCTION_PREFIXtruthy(x));
};

// ---

// function: abs
export const abs = Math.abs; // nargs: 1;

// ---

// function: divmod
export const divmod = function (x, y) {
  // nargs: 2
  const m = x % y;
  return [(x - m) / y, m];
};

// ---

// function: all
export const all = function (x) {
  // nargs: 1
  // Use for...of to handle both arrays and iterators/generators
  for (const item of x) {
    if (!FUNCTION_PREFIXtruthy(item)) {
      return false;
    }
  }
  return true;
};

// ---

// function: any
export const any = function (x) {
  // nargs: 1
  // Use for...of to handle both arrays and iterators/generators
  for (const item of x) {
    if (FUNCTION_PREFIXtruthy(item)) {
      return true;
    }
  }
  return false;
};

// ---

// function: enumerate
export const enumerate = function (iter) {
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

// ---

// function: zip
export const zip = function () {
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

// ---

// function: reversed
export const reversed = function (iter) {
  // nargs: 1
  if (typeof iter === "object" && !Array.isArray(iter)) {
    iter = Object.keys(iter);
  }
  return iter.slice().reverse();
};

// ---

// function: sorted
export const sorted = function (iter, key, reverse) {
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

// ---

// function: filter
export const filter = function (func, iter) {
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

// ---

// function: map
export const map = function (func, iter) {
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

// ---

// function: truthy
export const truthy = function (v) {
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

// ---

// function: op_len
export const op_len = function op_len(obj) {
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

// ---

// function: getattr
export const getattr = function (obj, name, defaultValue) {
  // nargs: 2 3
  // Get attribute from object
  if (obj == null) {
    if (arguments.length >= 3) {
      return defaultValue;
    }
    throw FUNCTION_PREFIXop_error("AttributeError", "'NoneType' object has no attribute '" + name + "'");
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
  throw FUNCTION_PREFIXop_error("AttributeError", "'" + typeName + "' object has no attribute '" + name + "'");
};

// ---

// function: hasattr
export const hasattr = function (obj, name) {
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

// ---

// function: setattr
export const setattr = function (obj, name, value) {
  // nargs: 3
  // Set attribute on object
  if (obj == null) {
    throw FUNCTION_PREFIXop_error("AttributeError", "'NoneType' object has no attribute '" + name + "'");
  }
  // Check for __setattr__
  if (typeof obj.__setattr__ === "function") {
    obj.__setattr__(name, value);
  } else {
    obj[name] = value;
  }
};

// ---

// function: delattr
export const delattr = function (obj, name) {
  // nargs: 2
  // Delete attribute from object
  if (obj == null) {
    throw FUNCTION_PREFIXop_error("AttributeError", "'NoneType' object has no attribute '" + name + "'");
  }
  // Check for __delattr__
  if (typeof obj.__delattr__ === "function") {
    obj.__delattr__(name);
  } else if (name in obj) {
    delete obj[name];
  } else {
    let typeName = obj.constructor ? obj.constructor.name : typeof obj;
    throw FUNCTION_PREFIXop_error("AttributeError", "'" + typeName + "' object has no attribute '" + name + "'");
  }
};

// ---

// function: dir
export const dir = function (obj) {
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

// ---

// function: callable
export const callable = function (obj) {
  // nargs: 1
  // Return True if object is callable
  return typeof obj === "function" || (typeof obj === "object" && obj !== null && typeof obj.__call__ === "function");
};

// ---

// function: op_getitem
export const op_getitem = function op_getitem(obj, key) {
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

// ---

// function: op_setitem
export const op_setitem = function op_setitem(obj, key, value) {
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

// ---

// function: op_equals
export const op_equals = function op_equals(a, b) {
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

// ---

// function: op_contains
export const op_contains = function op_contains(a, b) {
  // nargs: 2
  if (b == null) {
  } else if (Array.isArray(b)) {
    for (let i = 0; i < b.length; i++) {
      if (FUNCTION_PREFIXop_equals(a, b[i])) return true;
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

// ---

// function: op_add
export const op_add = function (a, b) {
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

// ---

// function: op_mul
export const op_mul = function (a, b) {
  // nargs: 2
  if ((typeof a === "number") + (typeof b === "number") === 1) {
    if (a.constructor === String) return METHOD_PREFIXrepeat(a, b);
    if (b.constructor === String) return METHOD_PREFIXrepeat(b, a);
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

// ---

// function: op_matmul
export const op_matmul = function (a, b) {
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

// ---

// function: string_mod
export const string_mod = function (format_str, args) {
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
          throw FUNCTION_PREFIXop_error("KeyError", name);
        }
        return FUNCTION_PREFIXformat_value(args[name], type, flags, width, precision);
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
      return FUNCTION_PREFIXformat_value(value, type, flags, actualWidth, actualPrecision);
    }
  );
};

// ---

// function: format_value
export const format_value = function (value, type, flags, width, precision) {
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
      result = FUNCTION_PREFIXstr(value);
      break;
    case 'r':
      result = FUNCTION_PREFIXrepr(value);
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

// ---

// function: op_mod
export const op_mod = function (left, right) {
  // nargs: 2
  // Handles Python's % operator which can be either:
  // - String formatting: "hello %s" % "world"
  // - Numeric modulo: 7 % 3
  if (typeof left === 'string') {
    return FUNCTION_PREFIXstring_mod(left, right);
  }
  return left % right;
};

// ---

// function: slice
export const slice = function (obj, start, stop, step) {
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

// ---

// function: call_kwargs
export const call_kwargs = function (func, args, kwargs) {
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

// ---
