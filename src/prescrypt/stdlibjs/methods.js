// method: append
export const append = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
  this.push(x);
};

// ---

// method: extend
export const extend = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
  this.push.apply(this, x);
};

// ---

// method: insert
export const insert = function (i, x) {
  // nargs: 2
  if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
  i = i < 0 ? this.length + i : i;
  this.splice(i, 0, x);
};

// ---

// method: remove
export const remove = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
  for (let i = 0; i < this.length; i++) {
    if (FUNCTION_PREFIXop_equals(this[i], x)) {
      this.splice(i, 1);
      return;
    }
  }
  let e = Error(x);
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
  if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
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
  if (reverse) this.reverse();
};

// ---

// method: clear
export const clear = function () {
  // nargs: 0
  if (Array.isArray(this)) {
    this.splice(0, this.length);
  } else if (this.constructor === Object) {
    let keys = Object.keys(this);
    for (let i = 0; i < keys.length; i++) delete this[keys[i]];
  } else return this.KEY.apply(this, arguments);
};

// ---

// method: copy
export const copy = function () {
  // nargs: 0
  if (Array.isArray(this)) {
    return this.slice(0);
  } else if (this.constructor === Object) {
    let key,
      keys = Object.keys(this),
      res = {};
    for (let i = 0; i < keys.length; i++) {
      key = keys[i];
      res[key] = this[key];
    }
    return res;
  } else return this.KEY.apply(this, arguments);
};

// ---

// method: pop
export const pop = function (i, d) {
  // nargs: 1 2
  if (Array.isArray(this)) {
    i = i === undefined ? -1 : i;
    i = i < 0 ? this.length + i : i;
    let popped = this.splice(i, 1);
    if (popped.length) return popped[0];
    let e = Error(i);
    e.name = "IndexError";
    throw e;
  } else if (this.constructor === Object) {
    let res = this[i];
    if (res !== undefined) {
      delete this[i];
      return res;
    } else if (d !== undefined) return d;
    let e = Error(i);
    e.name = "KeyError";
    throw e;
  } else return this.KEY.apply(this, arguments);
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
  if (this.constructor !== Object) return this.KEY.apply(this, arguments);
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
  if (this.constructor !== Object) return this.KEY.apply(this, arguments);
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
  if (this.constructor !== Object) return this.KEY.apply(this, arguments);
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
  if (this.constructor !== Object) return this.KEY.apply(this, arguments);
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
  if (this.constructor !== Object) return this.KEY.apply(this, arguments);
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
  if (this.constructor !== Object) return this.KEY.apply(this, arguments);
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
  let i = 0,
    i2,
    parts = [];
  count = count === undefined ? 1e20 : count;
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
