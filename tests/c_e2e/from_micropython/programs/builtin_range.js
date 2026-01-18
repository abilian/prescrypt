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
var _pyfunc_str = function (x) {
  // nargs: 0 1;
  if (x === undefined) {
    return "";
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
  // Default
  return JSON.stringify(x);
};
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
console.log(_pyfunc_str(_pyfunc_range(0, 4, 1)));

console.log((!!(_pyfunc_truthy(_pyfunc_range(0, 0, 1)))));

console.log((!!(_pyfunc_truthy(_pyfunc_range(0, 10, 1)))));

console.log((_pyfunc_op_len(_pyfunc_range(0, 0, 1))));

console.log((_pyfunc_op_len(_pyfunc_range(0, 4, 1))));

console.log((_pyfunc_op_len(_pyfunc_range(1, 4, 1))));

console.log((_pyfunc_op_len(_pyfunc_range(1, 4, 2))));

console.log((_pyfunc_op_len((_pyfunc_range(1, 4, (-1))))));

console.log((_pyfunc_op_len((_pyfunc_range(4, 1, (-1))))));

console.log((_pyfunc_op_len((_pyfunc_range(4, 1, (-2))))));

console.log(_pyfunc_str((_pyfunc_op_getitem(_pyfunc_range(0, 4, 1), 0))));

console.log(_pyfunc_str((_pyfunc_op_getitem(_pyfunc_range(0, 4, 1), 1))));

console.log(_pyfunc_str((_pyfunc_op_getitem(_pyfunc_range(0, 4, 1), -1))));

console.log(_pyfunc_str((_pyfunc_range(0, 4, 1).slice(0))));

console.log(_pyfunc_str((_pyfunc_range(0, 4, 1).slice(1))));

console.log(_pyfunc_str((_pyfunc_range(0, 4, 1).slice(1, 2))));

console.log(_pyfunc_str((_pyfunc_range(0, 4, 1).slice(1, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(0, 4, 1), 1, null, 2))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(0, 4, 1), 1, -2, 2))));

console.log(_pyfunc_str((_pyfunc_range(1, 4, 1).slice())));

console.log(_pyfunc_str((_pyfunc_range(1, 4, 1).slice(0))));

console.log(_pyfunc_str((_pyfunc_range(1, 4, 1).slice(1))));

console.log(_pyfunc_str((_pyfunc_range(1, 4, 1).slice(0, -1))));

console.log(_pyfunc_str((_pyfunc_range(4, 1, 1).slice())));

console.log(_pyfunc_str((_pyfunc_range(4, 1, 1).slice(0))));

console.log(_pyfunc_str((_pyfunc_range(4, 1, 1).slice(1))));

console.log(_pyfunc_str((_pyfunc_range(4, 1, 1).slice(0, -1))));

console.log(_pyfunc_str((_pyfunc_range(7, (-2), (-4)).slice())));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 5, 15, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 15, 5, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(100, 1, (-5)), 5, 15, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(100, 1, (-5)), 15, 5, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 5, 15, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 15, 5, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(100, 1, (-5)), 5, 15, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(100, 1, (-5)), 15, 5, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 5, 15, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 15, 5, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, (-5)), 5, 15, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, (-5)), 15, 5, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 5, 15, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, 5), 15, 5, 3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, (-5)), 5, 15, -3))));

console.log(_pyfunc_str((_pyfunc_slice(_pyfunc_range(1, 100, (-5)), 15, 5, 3))));

console.log(_pyfunc_str((_pyfunc_list((_pyfunc_range(7, (-2), (-4)).slice(2, -2))))));


try {_pyfunc_range(1, 2, 0);

} catch(err_1) {
    if (err_1 instanceof Error && err_1.name === "ValueError") {console.log('ValueError');

    } else { throw err_1; }
}

try {0 - _pyfunc_range(0, 1, 1);

} catch(err_1) {
    if (err_1 instanceof Error && err_1.name === "TypeError") {console.log('TypeError');

    } else { throw err_1; }
}

try {_pyfunc_op_setitem(_pyfunc_range(0, 1, 1), 0, 1);
} catch(err_1) {
    if (err_1 instanceof Error && err_1.name === "TypeError") {console.log('TypeError');

    } else { throw err_1; }
}
