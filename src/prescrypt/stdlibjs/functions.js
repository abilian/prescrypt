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
export const op_error = function (etype, msg) {
  // nargs: 2
  let e = new Error(etype + ": " + msg);
  e.name = etype;
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

// function: list
export const list = function (x) {
  const res = [];
  if (typeof x === "object" && !Array.isArray(x)) {
    x = Object.keys(x);
  }
  for (let i = 0; i < x.length; i++) {
    res.push(x[i]);
  }
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
  // nargs: 2
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
  return x.reduce(function (a, b) {
    return a + b;
  }, 0);
};

// ---

// function: round
export const round = Math.round; // nargs: 1;

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
  if (x === undefined) {
    return "";
  }
  if (Array.isArray(x)) {
    if (x.length == 0) {
      return "[]";
    }
    let result = "[" + FUNCTION_PREFIXstr(x[0]);
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
  // Default
  return JSON.stringify(x);
};

// ---

// function: repr
export const repr = function (x) {
  // nargs: 1
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
  for (let i = 0; i < x.length; i++) {
    if (!FUNCTION_PREFIXtruthy(x[i])) {
      return false;
    }
  }
  return true;
};

// ---

// function: any
export const any = function (x) {
  // nargs: 1
  for (let i = 0; i < x.length; i++) {
    if (FUNCTION_PREFIXtruthy(x[i])) {
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
  if (typeof iter === "object" && !Array.isArray(iter)) {
    iter = Object.keys(iter);
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
  if (obj.constructor === Object) {
    return Object.keys(obj).length;
  }
  throw new TypeError("object has no len()");
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
