// method: append
export const append = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) {
    return this.KEY.apply(this, arguments);
  }

  this.push(x);
};

// ---

// method: extend
export const extend = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) {
    return this.KEY.apply(this, arguments);
  }

  this.push.apply(this, x);
};

// ---

// method: insert
export const insert = function (i, x) {
  // nargs: 2
  if (!Array.isArray(this)) {
    return this.KEY.apply(this, arguments);
  }

  i = i < 0 ? this.length + i : i;
  this.splice(i, 0, x);
};

// ---

// method: remove
export const remove = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) {
    return this.KEY.apply(this, arguments);
  }

  for (let i = 0; i < this.length; i++) {
    if (FUNCTION_PREFIXop_equals(this[i], x)) {
      this.splice(i, 1);
      return;
    }
  }
  const e = Error(x);
  e.name = "ValueError";
  throw e;
};

// ---

// method: reverse
export const reverse = function () {
  // nargs: 0
  this.reverse();
};

// ---

// method: sort
export const sort = function (key, reverse) {
  // nargs: 0 1 2
  if (!Array.isArray(this)) {
    return this.KEY.apply(this, arguments);
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

// ---

// method: clear
export const clear = function () {
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

  return this.KEY.apply(this, arguments);
};

// ---

// method: copy
export const copy = function () {
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

  return this.KEY.apply(this, arguments);
};

// ---

// method: pop
export const pop = function (i, d) {
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

  return this.KEY.apply(this, arguments);
};

// ---

// method: count
export const count = function (x, start, stop) {
  // nargs: 1 2 3
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  if (Array.isArray(this)) {
    let count = 0;
    for (let i = 0; i < this.length; i++) {
      if (FUNCTION_PREFIXop_equals(this[i], x)) {
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
  } else return this.KEY.apply(this, arguments);
};

// ---

// method: index
export const index = function (x, start, stop) {
  // nargs: 1 2 3
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  if (Array.isArray(this)) {
    for (let i = start; i < stop; i++) {
      if (FUNCTION_PREFIXop_equals(this[i], x)) {
        return i;
      } // indexOf cant
    }
  } else if (this.constructor === String) {
    let i = this.slice(start, stop).indexOf(x);
    if (i >= 0) return i + start;
  } else return this.KEY.apply(this, arguments);
  let e = Error(x);
  e.name = "ValueError";
  throw e;
};

// ---

// method: get
export const get = function (key, d) {
  // nargs: 1 2
  // If object has a native .get() method (like Map), use it
  // But check typeof to avoid calling this function recursively
  if (typeof this.KEY === 'function' && this.constructor !== Object) {
    return this.KEY.apply(this, arguments);
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

// ---

// method: items
export const items = function () {
  // nargs: 0
  // If object has native .items() method, use it
  if (typeof this.KEY === 'function' && this.constructor !== Object) {
    return this.KEY.apply(this, arguments);
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

// ---

// method: keys
export const keys = function () {
  // nargs: 0
  if (typeof this["KEY"] === "function") return this.KEY.apply(this, arguments);
  return Object.keys(this);
};

// ---

// method: popitem
export const popitem = function () {
  // nargs: 0
  if (typeof this.KEY === 'function' && this.constructor !== Object) {
    return this.KEY.apply(this, arguments);
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

// ---

// method: setdefault
export const setdefault = function (key, d) {
  // nargs: 1 2
  if (typeof this.KEY === 'function' && this.constructor !== Object) {
    return this.KEY.apply(this, arguments);
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

// ---

// method: update
export const update = function (other) {
  // nargs: 1
  if (typeof this.KEY === 'function' && this.constructor !== Object) {
    return this.KEY.apply(this, arguments);
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

// ---

// method: values
export const values = function () {
  // nargs: 0
  if (typeof this.KEY === 'function' && this.constructor !== Object) {
    return this.KEY.apply(this, arguments);
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

// ---

// method: repeat
export const repeat = function (count) {
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

// ---

// method: capitalize
export const capitalize = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  return this.slice(0, 1).toUpperCase() + this.slice(1).toLowerCase();
};

// ---

// method: casefold
export const casefold = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  return this.toLowerCase();
};

// ---

// method: center
export const center = function (w, fill) {
  // nargs: 1 2
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  fill = fill === undefined ? " " : fill;
  let tofill = Math.max(0, w - this.length);
  let left = Math.ceil(tofill / 2);
  let right = tofill - left;
  return (
    METHOD_PREFIXrepeat(fill, left) + this + METHOD_PREFIXrepeat(fill, right)
  );
};

// ---

// method: endswith
export const endswith = function (x) {
  // nargs: 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  let last_index = this.lastIndexOf(x);
  return last_index == this.length - x.length && last_index >= 0;
};

// ---

// method: expandtabs
export const expandtabs = function (tabsize) {
  // nargs: 0 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  tabsize = tabsize === undefined ? 8 : tabsize;
  return this.replace(/\t/g, METHOD_PREFIXrepeat(" ", tabsize));
};

// ---

// method: find
export const find = function (x, start, stop) {
  // nargs: 1 2 3
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  let i = this.slice(start, stop).indexOf(x);
  if (i >= 0) return i + start;
  return -1;
};

// ---

// method: format
export const format = function () {
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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
    let s = FUNCTION_PREFIXformat(arguments[index], fmt);
    parts.push(this.slice(i, i1), s);
    i = i2 + 1;
  }
  parts.push(this.slice(i));
  return parts.join("");
};

// ---

// method: isalnum
export const isalnum = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  return Boolean(/^[A-Za-z0-9]+$/.test(this));
};

// ---

// method: isalpha
export const isalpha = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  return Boolean(/^[A-Za-z]+$/.test(this));
};

// ---

// method: isidentifier
export const isidentifier = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  return Boolean(/^[A-Za-z_][A-Za-z0-9_]*$/.test(this));
};

// ---

// method: islower
export const islower = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  let low = this.toLowerCase(),
    high = this.toUpperCase();
  return low != high && low == this;
};

// ---

// method: isdecimal
export const isdecimal = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  return Boolean(/^[0-9]+$/.test(this));
};

// ---

// method: isnumeric
export const isnumeric = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  return Boolean(/^[0-9]+$/.test(this));
};

// ---

// method: isdigit
export const isdigit = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  return Boolean(/^[0-9]+$/.test(this));
};

// ---

// method: isspace
export const isspace = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  return Boolean(/^\s+$/.test(this));
};

// ---

// method: istitle
export const istitle = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  let low = this.toLowerCase(),
    title = METHOD_PREFIXtitle(this);
  return low != title && title == this;
};

// ---

// method: isupper
export const isupper = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  let low = this.toLowerCase(),
    high = this.toUpperCase();
  return low != high && high == this;
};

// ---

// method: join
export const join = function (x) {
  // nargs: 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  // Handle iterators/generators by converting to array first
  if (!Array.isArray(x) && typeof x[Symbol.iterator] === 'function') {
    x = [...x];
  }
  return x.join(this); // call join on the list instead of the string.
};

// ---

// method: ljust
export const ljust = function (w, fill) {
  // nargs: 1 2
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  fill = fill === undefined ? " " : fill;
  let tofill = Math.max(0, w - this.length);
  return this + METHOD_PREFIXrepeat(fill, tofill);
};

// ---

// method: lower
export const lower = function () {
  // nargs: 0
  if (this.constructor !== String) {
    return this.KEY.apply(this, arguments);
  }

  return this.toLowerCase();
};

// ---

// method: lstrip
export const lstrip = function (chars) {
  // nargs: 0 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);

  chars = chars === undefined ? " \t\r\n" : chars;
  for (let i = 0; i < this.length; i++) {
    if (chars.indexOf(this[i]) < 0) return this.slice(i);
  }
  return "";
};

// ---

// method: partition
export const partition = function (sep) {
  // nargs: 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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

// ---

// method: replace
export const replace = function (s1, s2, count) {
  // nargs: 2 3
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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

// ---

// method: rfind
export const rfind = function (x, start, stop) {
  // nargs: 1 2 3
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  start = start === undefined ? 0 : start;
  stop = stop === undefined ? this.length : stop;
  start = Math.max(0, start < 0 ? this.length + start : start);
  stop = Math.min(this.length, stop < 0 ? this.length + stop : stop);
  let i = this.slice(start, stop).lastIndexOf(x);
  if (i >= 0) return i + start;
  return -1;
};

// ---

// method: rindex
export const rindex = function (x, start, stop) {
  // nargs: 1 2 3
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  let i = METHOD_PREFIXrfind(this, x, start, stop);
  if (i >= 0) return i;
  let e = Error(x);
  e.name = "ValueError";
  throw e;
};

// ---

// method: rjust
export const rjust = function (w, fill) {
  // nargs: 1 2
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  fill = fill === undefined ? " " : fill;
  let tofill = Math.max(0, w - this.length);
  return METHOD_PREFIXrepeat(fill, tofill) + this;
};

// ---

// method: rpartition
export const rpartition = function (sep) {
  // nargs: 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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

// ---

// method: rsplit
export const rsplit = function (sep, count) {
  // nargs: 1 2
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  sep = sep === undefined ? /\s/ : sep;
  count = Math.max(0, count === undefined ? 1e20 : count);
  let parts = this.split(sep);
  let limit = Math.max(0, parts.length - count);
  let res = parts.slice(limit);
  if (count < parts.length) res.splice(0, 0, parts.slice(0, limit).join(sep));
  return res;
};

// ---

// method: rstrip
export const rstrip = function (chars) {
  // nargs: 0 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  chars = chars === undefined ? " \t\r\n" : chars;
  for (let i = this.length - 1; i >= 0; i--) {
    if (chars.indexOf(this[i]) < 0) return this.slice(0, i + 1);
  }
  return "";
};

// ---

// method: split
export const split = function (sep, count) {
  // nargs: 0, 1 2
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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

// ---

// method: splitlines
export const splitlines = function (keepends) {
  // nargs: 0 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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

// ---

// method: startswith
export const startswith = function (x) {
  // nargs: 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  return this.indexOf(x) == 0;
};

// ---

// method: strip
export const strip = function (chars) {
  // nargs: 0 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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

// ---

// method: swapcase
export const swapcase = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  let c,
    res = [];
  for (let i = 0; i < this.length; i++) {
    c = this[i];
    if (c.toUpperCase() == c) res.push(c.toLowerCase());
    else res.push(c.toUpperCase());
  }
  return res.join("");
};

// ---

// method: title
export const title = function () {
  // nargs: 0
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
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

// ---

// method: translate
export const translate = function (table) {
  // nargs: 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  let c,
    res = [];
  for (let i = 0; i < this.length; i++) {
    c = table[this[i]];
    if (c === undefined) res.push(this[i]);
    else if (c !== null) res.push(c);
  }
  return res.join("");
};

// ---

// method: upper
export const upper = function () {
  // nargs: 0
  if (this.constructor === String) {
    return this.toUpperCase();
  }
  return this.KEY.apply(this, arguments);
};

// ---

// method: zfill
export const zfill = function (width) {
  // nargs: 1
  if (this.constructor !== String) return this.KEY.apply(this, arguments);
  return METHOD_PREFIXrjust(this, width, "0");
};

// ---

// method: to_bytes
export const to_bytes = function (length, byteorder, signed) {
  // nargs: 2 3
  // int.to_bytes(length, byteorder, *, signed=False)
  // Converts an integer to a bytes object
  let n = typeof this === "number" ? this : Number(this);
  signed = signed === true || signed === "true";

  // Check for negative length
  if (length < 0) {
    throw FUNCTION_PREFIXop_error("ValueError", "length argument must be non-negative");
  }

  // Check for negative numbers when unsigned
  if (!signed && n < 0) {
    throw FUNCTION_PREFIXop_error("OverflowError", "can't convert negative int to unsigned");
  }

  // Special case: 0 can always be represented in 0 bytes
  if (length === 0) {
    if (n === 0) {
      return new Uint8Array(0);
    } else {
      throw FUNCTION_PREFIXop_error("OverflowError", "int too big to convert");
    }
  }

  // Calculate max value for given length
  let maxVal = signed ? Math.pow(2, length * 8 - 1) - 1 : Math.pow(2, length * 8) - 1;
  let minVal = signed ? -Math.pow(2, length * 8 - 1) : 0;

  if (n > maxVal || n < minVal) {
    throw FUNCTION_PREFIXop_error("OverflowError", "int too big to convert");
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

// ---

// method: send
export const send = function (value) {
  // nargs: 1
  // Python generator.send(value) implementation
  // - First call must send None (null) or TypeError is raised
  // - Returns the yielded value (unwraps JS {value, done} object)
  // - Raises StopIteration when generator is exhausted

  // Check if this is a generator (has .next method)
  if (typeof this.next !== "function") {
    throw FUNCTION_PREFIXop_error("AttributeError", "'object' has no attribute 'send'");
  }

  // Track if generator has been started using a hidden property
  if (!this._started) {
    // First call - must be None (null/undefined)
    if (value !== null && value !== undefined) {
      throw FUNCTION_PREFIXop_error(
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
    throw FUNCTION_PREFIXop_error("StopIteration", "");
  }

  return result.value;
};

// ---

// method: gen_throw
export const gen_throw = function (type, value, traceback) {
  // nargs: 1 2 3
  // Python generator.throw(type[, value[, traceback]]) implementation
  // Throws an exception at the yield point and returns next yielded value

  // Check if this is a generator (has .throw method)
  if (typeof this.throw !== "function") {
    throw FUNCTION_PREFIXop_error("AttributeError", "'generator' object has no attribute 'throw'");
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
    throw FUNCTION_PREFIXop_error("StopIteration", "");
  }

  return result.value;
};

// ---

// method: gen_close
export const gen_close = function () {
  // nargs: 0
  // Python generator.close() implementation
  // Throws GeneratorExit at the yield point
  // Silently handles StopIteration and GeneratorExit
  // Raises RuntimeError if generator yields a value

  // Check if this is a generator (has .return method)
  if (typeof this.return !== "function") {
    throw FUNCTION_PREFIXop_error("AttributeError", "'generator' object has no attribute 'close'");
  }

  // If generator hasn't started, just mark it as done
  if (!this._started) {
    this._closed = true;
    return;
  }

  // Try to close by throwing GeneratorExit
  try {
    // Create a GeneratorExit exception
    let genExit = FUNCTION_PREFIXop_error("GeneratorExit", "");

    // Try using .throw first (more Pythonic)
    if (typeof this.throw === "function") {
      let result = this.throw(genExit);
      // If generator yielded a value instead of exiting, that's an error
      if (!result.done) {
        throw FUNCTION_PREFIXop_error("RuntimeError", "generator ignored GeneratorExit");
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

// ---
