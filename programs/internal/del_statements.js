var _pyfunc_BaseException = (function() {
  // nargs: 0 1
  function BaseException(message) {
    if (!(this instanceof BaseException)) {
      return new BaseException(message);
    }
    Error.call(this, message);
    this.name = "BaseException";
    this.message = message || "";
    this.args = message !== undefined ? [message] : [];
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, BaseException);
    }
  }
  BaseException.prototype = Object.create(Error.prototype);
  BaseException.prototype.constructor = BaseException;
  return BaseException;
})();
var _pyfunc_Exception = (function() {
  // nargs: 0 1
  function Exception(message) {
    if (!(this instanceof Exception)) {
      return new Exception(message);
    }
    _pyfunc_BaseException.call(this, message);
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
var _pyfunc_create_dict = function () {
  const d = {};
  for (let i = 0; i < arguments.length; i += 2) {
    d[arguments[i]] = arguments[i + 1];
  }
  return d;
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
  // Handle bytes (Uint8Array)
  if (x instanceof Uint8Array) {
    return _pyfunc_bytes_repr(x);
  }
  // Handle strings - use single quotes like Python
  if (typeof x === "string") {
    // Escape single quotes and backslashes, use single quotes
    return "'" + x.replace(/\\/g, "\\\\").replace(/'/g, "\\'") + "'";
  }
  // Handle null/undefined (None in Python)
  if (x === null || x === undefined) {
    return "None";
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
  // Handle bytes (Uint8Array) - output like b'...'
  if (x instanceof Uint8Array) {
    return _pyfunc_bytes_repr(x);
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
var _pymeth_keys = function () {
  // nargs: 0
  if (typeof this["keys"] === "function") return this.keys.apply(this, arguments);
  return Object.keys(this);
};
'Test del statements for variables, list items, dict keys, and attributes.';


const x = 10;
console.log(x);


delete x;

try {console.log(x);

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "NameError" || err_1 instanceof _pyfunc_NameError)) {console.log('x deleted');

    } else { throw err_1; }
}
const lst = Object.assign([1, 2, 3, 4, 5], {_is_list: true});

delete _pyfunc_op_getitem(lst, 2);
console.log(_pyfunc_str(lst));

const lst2 = Object.assign([0, 1, 2, 3, 4, 5, 6], {_is_list: true});

delete lst2.slice(1, 4);
console.log(_pyfunc_str(lst2));

const lst3 = Object.assign([10, 20, 30], {_is_list: true});

delete _pyfunc_op_getitem(lst3, -1);
console.log(_pyfunc_str(lst3));

const d = _pyfunc_create_dict('a', 1, 'b', 2, 'c', 3);

delete _pyfunc_op_getitem(d, 'b');
console.log(_pyfunc_str((_pyfunc_sorted(_pymeth_keys.call(d), undefined, false))));

console.log(_pyfunc_str(_pyfunc_op_getitem(d, 'a')));

const key = 'a';

delete _pyfunc_op_getitem(d, key);
console.log(_pyfunc_str((_pyfunc_list(_pymeth_keys.call(d)))));

Point = function () {
    if (!(this instanceof Point)) {
        return new Point(...arguments);
    }
    _pyfunc_op_instantiate(this, arguments);
}
Point.prototype._base_class = Object;
Point.prototype.__name__ = "Point";

                Point.prototype.__init__ = function (x, y) {
                this.x = x;
this.y = y;
                };


const p = Point(10, 20);
console.log(_pyfunc_str(p.x));


delete p.x;

try {console.log(_pyfunc_str(p.x));

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "AttributeError" || err_1 instanceof _pyfunc_AttributeError)) {console.log('p.x deleted');

    } else { throw err_1; }
}
console.log(_pyfunc_str(p.y));

let [a, b, c] = [1, 2, 3];

delete a;
delete b;

try {console.log(_pyfunc_str(a));

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "NameError" || err_1 instanceof _pyfunc_NameError)) {console.log('a deleted');

    } else { throw err_1; }
}
console.log(_pyfunc_str(c));

const items = _pyfunc_create_dict('x', 1, 'y', 2, 'z', 3);
const to_delete = Object.assign(['x', 'z'], {_is_list: true});

let _pytmp_1_seq = to_delete;
if (!Array.isArray(_pytmp_1_seq) && typeof _pytmp_1_seq[Symbol.iterator] === 'function') { _pytmp_1_seq = [..._pytmp_1_seq];}
else if ((typeof _pytmp_1_seq === "object") && (!Array.isArray(_pytmp_1_seq))) { _pytmp_1_seq = Object.keys(_pytmp_1_seq);}
for (let _pytmp_2_itr = 0; _pytmp_2_itr < _pytmp_1_seq.length; _pytmp_2_itr += 1) {
    let k = _pytmp_1_seq[_pytmp_2_itr];
    delete _pyfunc_op_getitem(items, k);
}
console.log(_pyfunc_str((_pyfunc_list(_pymeth_keys.call(items)))));

const nested = _pyfunc_create_dict('outer', _pyfunc_create_dict('inner', 42));

delete _pyfunc_op_getitem(_pyfunc_op_getitem(nested, 'outer'), 'inner');
console.log(_pyfunc_str(nested));

console.log('del_statements tests done');
