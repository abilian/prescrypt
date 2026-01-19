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
var _pymeth_upper = function () {
  // nargs: 0
  if (this.constructor === String) {
    return this.toUpperCase();
  }
  return this.upper.apply(this, arguments);
};
'Test global and nonlocal declarations.';


let counter = 0;

            var increment = function increment() {
            /* global counter */

counter = (counter + 1);
            };

increment();

increment();

console.log(counter);

let total = 0;

            var outer = function outer() {

                    let inner = (function inner() {
                    /* global total */

total = (total + 10);
                    }).bind(this);

inner();

inner();

            };

outer();

console.log(total);

let x = 1;
let y = 2;

            var modify_both = function modify_both() {
            /* global x, y */

x = 10;
y = 20;
            };

modify_both();

console.log(x + " " + y);


            var make_counter = function make_counter() {
            let count = 0;

                    let inc = (function inc() {
                    /* nonlocal count */

count = (count + 1);
return count;

                    }).bind(this);

return inc;

            };

const counter_fn = make_counter();
console.log(_pyfunc_str(counter_fn()));

console.log(_pyfunc_str(counter_fn()));

console.log(_pyfunc_str(counter_fn()));


            var level1 = function level1() {
            let value = 'L1';

                    let level2 = (function level2() {

                    let level3 = (function level3() {
                    /* nonlocal value */

value = 'L3';
                    }).bind(this);

level3();

return value;

                    }).bind(this);

return level2();

            };

console.log(_pyfunc_str(level1()));


            var test_shadowing = function test_shadowing() {
            let x = 'outer';

                    let inner = (function inner() {
                    /* nonlocal x */

x = 'modified';
                    }).bind(this);

inner();

return x;

            };

console.log(_pyfunc_str(test_shadowing()));


            var multi_nonlocal = function multi_nonlocal() {
            let a = 1;
let b = 2;

                    let modify = (function modify() {
                    /* nonlocal a, b */

a = 10;
b = 20;
                    }).bind(this);

modify();

return (a + b);

            };

console.log(_pyfunc_str(multi_nonlocal()));


            var accumulator = function accumulator() {
            let total = 0;

                    let add = (function add(n) {
                    /* nonlocal total */

total = _pyfunc_op_add(total, n);
return total;

                    }).bind(this);

return add;

            };

const acc = accumulator();

let _pytmp_1_seq = _pyfunc_range(1, 6, 1);
if (!Array.isArray(_pytmp_1_seq) && typeof _pytmp_1_seq[Symbol.iterator] === 'function') { _pytmp_1_seq = [..._pytmp_1_seq];}
else if ((typeof _pytmp_1_seq === "object") && (!Array.isArray(_pytmp_1_seq))) { _pytmp_1_seq = Object.keys(_pytmp_1_seq);}
for (let _pytmp_2_itr = 0; _pytmp_2_itr < _pytmp_1_seq.length; _pytmp_2_itr += 1) {
    let i = _pytmp_1_seq[_pytmp_2_itr];const result = acc(i);
}
console.log(_pyfunc_str(result));

const message = 'hello';

var read_global = function read_global() {
return _pymeth_upper.call(message);

};

console.log(_pyfunc_str(read_global()));


            var closure_readonly = function closure_readonly() {
            const data = Object.assign([1, 2, 3], {_is_list: true});

let get_sum = (function get_sum() {
return _pyfunc_sum(data);

}).bind(this);

return get_sum;

            };

console.log(_pyfunc_str(((closure_readonly())())));

const value = 'global';

            var shadow_test = function shadow_test() {
            const value = 'local';
return value;

            };

console.log(_pyfunc_str(shadow_test()));

console.log(value);

console.log('global_nonlocal tests done');
