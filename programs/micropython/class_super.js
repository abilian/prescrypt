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
Base = function () {
    if (!(this instanceof Base)) {
        return new Base(...arguments);
    }
    _pyfunc_op_instantiate(this, arguments);
}
Base.prototype._base_class = Object;
Base.prototype.__name__ = "Base";

Base.prototype.__init__ = function () {
this.a = 1;
};

                Base.prototype.meth = function () {
                console.log('in Base meth' + " " + _pyfunc_str(this.a));

return null;
                };


Sub = function () {
    if (!(this instanceof Sub)) {
        return new Sub(...arguments);
    }
    _pyfunc_op_instantiate(this, arguments);
}
Sub.prototype = Object.create(Base.prototype);
Sub.prototype._base_class = Base.prototype;
Sub.prototype.__name__ = "Sub";

                Sub.prototype.meth = function () {
                console.log('in Sub meth');

return _pyfunc_super_proxy(this, Sub.prototype).meth();

                };


const a = Sub();
a.meth();

A = function () {
    if (!(this instanceof A)) {
        return new A(...arguments);
    }
    _pyfunc_op_instantiate(this, arguments);
}
A.prototype._base_class = Object;
A.prototype.__name__ = "A";

                A.prototype.p = function () {
                console.log(_pyfunc_str((_pyfunc_str(_pyfunc_super_proxy(this, A.prototype)).slice(0, 18))));

return null;
                };


A().p();

A = function () {
    if (!(this instanceof A)) {
        return new A(...arguments);
    }
    _pyfunc_op_instantiate(this, arguments);
}
A.prototype._base_class = Object;
A.prototype.__name__ = "A";
A.bar = A.prototype.bar = 123;
                A.prototype.foo = function () {
                console.log('A foo');

return Object.assign([1, 2, 3], {_is_list: true});

                };


B = function () {
    if (!(this instanceof B)) {
        return new B(...arguments);
    }
    _pyfunc_op_instantiate(this, arguments);
}
B.prototype = Object.create(A.prototype);
B.prototype._base_class = A.prototype;
B.prototype.__name__ = "B";

                B.prototype.foo = function () {
                console.log('B foo');

console.log(_pyfunc_str((_pyfunc_super_proxy(this, B.prototype).bar)));

return _pymeth_count.call((_pyfunc_super_proxy(this, B.prototype).foo()), 2);

                };


console.log(_pyfunc_str((B().foo())));


try {_pyfunc_super_proxy(1, (1).prototype);

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "TypeError" || err_1 instanceof _pyfunc_TypeError_py)) {console.log('TypeError');

    } else { throw err_1; }
}

if ((_pyfunc_hasattr((_pyfunc_super_proxy(B(), (B).prototype)), 'foo'))) {
} else {
    throw _pyfunc_op_error('AssertionError');
}

try {(_pyfunc_super_proxy(B(), (B).prototype)).foo = 1;
} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "AttributeError" || err_1 instanceof _pyfunc_AttributeError)) {console.log('AttributeError');

    } else { throw err_1; }
}

try {
    delete (_pyfunc_super_proxy(B(), (B).prototype)).foo;
} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "AttributeError" || err_1 instanceof _pyfunc_AttributeError)) {console.log('AttributeError');

    } else { throw err_1; }
}
