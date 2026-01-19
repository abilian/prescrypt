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
var _pyfunc_op_error = function (etype, ...args) {
  // nargs: 1+
  let msg = args.join(", ");
  let e = new Error(etype + ": " + msg);
  e.name = etype;
  e.args = args;  // Store args for repr()
  return e;
};
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
  // Handle bytes (Uint8Array)
  if (x instanceof Uint8Array) {
    return _pyfunc_bytes_repr(x);
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
var _pyfunc_str = function (x) {
  // nargs: 0 1;
  if (x === undefined) {
    return "";
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

            function* f() {
            let n = 0;

while (true) {n = yield (n + 1);console.log(_pyfunc_str(n));

}
            }

let g = f();

try {_pymeth_send.call(g, 1);

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "TypeError" || err_1 instanceof _pyfunc_TypeError_py)) {console.log('caught');

    } else { throw err_1; }
}
console.log(_pyfunc_str(_pymeth_send.call(g, null)));

console.log(_pyfunc_str(_pymeth_send.call(g, 100)));

console.log(_pyfunc_str(_pymeth_send.call(g, 200)));


            function* f2() {
            console.log('entering');


let _pytmp_1_seq = _pyfunc_range(0, 3, 1);
if (!Array.isArray(_pytmp_1_seq) && typeof _pytmp_1_seq[Symbol.iterator] === 'function') { _pytmp_1_seq = [..._pytmp_1_seq];}
else if ((typeof _pytmp_1_seq === "object") && (!Array.isArray(_pytmp_1_seq))) { _pytmp_1_seq = Object.keys(_pytmp_1_seq);}
for (let _pytmp_2_itr = 0; _pytmp_2_itr < _pytmp_1_seq.length; _pytmp_2_itr += 1) {
    let i = _pytmp_1_seq[_pytmp_2_itr];console.log(_pyfunc_str(i));
yield;

}
console.log('returning 1');

console.log('returning 2');

            }

g = f2();
_pymeth_send.call(g, null);

_pymeth_send.call(g, 1);

_pymeth_send.call(g, 1);


try {_pymeth_send.call(g, 1);

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "StopIteration" || err_1 instanceof _pyfunc_StopIteration)) {console.log('caught');

    } else { throw err_1; }
}

try {_pymeth_send.call(g, 1);

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "StopIteration" || err_1 instanceof _pyfunc_StopIteration)) {console.log('caught');

    } else { throw err_1; }
}
