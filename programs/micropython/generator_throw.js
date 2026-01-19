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
var _pyfunc_ValueError = (function() {
  // nargs: 0 1
  function ValueError(message) {
    if (!(this instanceof ValueError)) {
      return new ValueError(message);
    }
    _pyfunc_Exception.call(this, message);
    this.name = "ValueError";
  }
  ValueError.prototype = Object.create(_pyfunc_Exception.prototype);
  ValueError.prototype.constructor = ValueError;
  return ValueError;
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
var _pyfunc_next = function (iterator, defaultValue) {
  // nargs: 1 2
  // Get next item from iterator
  let result = iterator.next();
  if (result.done) {
    if (arguments.length >= 2) {
      return defaultValue;
    }
    throw _pyfunc_op_error("StopIteration", "");
  }
  return result.value;
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

            var gen = function* gen() {
            yield 123;

yield 456;

            };

let g = gen();
console.log(_pyfunc_str(_pyfunc_next(g)));


try {_pymeth_gen_throw.call(g, _pyfunc_KeyError);

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "KeyError" || err_1 instanceof _pyfunc_KeyError)) {console.log('got KeyError from downstream!');

    } else { throw err_1; }
}

            var gen = function* gen() {

try {yield 1;
yield 2;

} catch(err_1) {
    {/* pass */

    }
}
            };

g = gen();
console.log(_pyfunc_str(_pyfunc_next(g)));


try {_pymeth_gen_throw.call(g, _pyfunc_ValueError);

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "StopIteration" || err_1 instanceof _pyfunc_StopIteration)) {console.log('got StopIteration');

    } else { throw err_1; }
}

            var gen = function* gen() {

try {yield 123;

} catch(err_1) {
    if (err_1 instanceof Error && (err_1.name === "GeneratorExit" || err_1 instanceof _pyfunc_GeneratorExit)) {
        e = err_1;console.log('GeneratorExit' + " " + _pyfunc_repr(e.args));

    } else { throw err_1; }
}
yield 456;

            };

g = gen();
console.log(_pyfunc_str(_pyfunc_next(g)));

console.log(_pyfunc_str(_pymeth_gen_throw.call(g, _pyfunc_GeneratorExit)));

g = gen();
console.log(_pyfunc_str(_pyfunc_next(g)));

console.log(_pyfunc_str((_pymeth_gen_throw.call(g, _pyfunc_GeneratorExit()))));
