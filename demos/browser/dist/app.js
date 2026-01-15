var _pyfunc_create_dict = function () {
  const d = {};
  for (let i = 0; i < arguments.length; i += 2) {
    d[arguments[i]] = arguments[i + 1];
  }
  return d;
};
var _pyfunc_format = function (v, fmt) {
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
var _pyfunc_op_add = function (a, b) {
  // nargs: 2
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.concat(b);
  }
  return a + b;
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
var _pyfunc_op_getitem = function op_getitem(obj, key) {
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
var _pymeth_append = function (x) {
  // nargs: 1
  if (!Array.isArray(this)) {
    return this.append.apply(this, arguments);
  }

  this.push(x);
};
var _pymeth_format = function () {
  if (this.constructor !== String) return this.format.apply(this, arguments);
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
    let s = _pyfunc_format(arguments[index], fmt);
    parts.push(this.slice(i, i1), s);
    i = i2 + 1;
  }
  parts.push(this.slice(i));
  return parts.join("");
};
var _pymeth_strip = function (chars) {
  // nargs: 0 1
  if (this.constructor !== String) return this.strip.apply(this, arguments);
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
'Todo List Application\n\nA simple interactive todo app demonstrating Prescrypt browser capabilities:\n- DOM manipulation\n- Event handling\n- State management\n';


export let todos = [];
export let next_id = 1;

            export function add_todo(text) {
            'Add a new todo item.';

/* global next_id */

const todo = _pyfunc_create_dict('id', next_id, 'text', text, 'completed', false);
_pymeth_append.call(todos, todo);

next_id = _pyfunc_op_add(next_id, 1);
render();

            }


            export function toggle_todo(todo_id) {
            "Toggle a todo's completed status.";


let _pytmp_1_seq = todos;
if ((typeof _pytmp_1_seq === "object") && (!Array.isArray(_pytmp_1_seq))) { _pytmp_1_seq = Object.keys(_pytmp_1_seq);}
for (let _pytmp_2_itr = 0; _pytmp_2_itr < _pytmp_1_seq.length; _pytmp_2_itr += 1) {
    let todo = _pytmp_1_seq[_pytmp_2_itr];
    if ((_pyfunc_op_equals(_pyfunc_op_getitem(todo, 'id'), todo_id))) {_pyfunc_op_setitem(todo, 'completed', !_pyfunc_truthy(_pyfunc_op_getitem(todo, 'completed')));break;

    }
}
render();

            }


            export function delete_todo(todo_id) {
            'Delete a todo item.';

/* global todos */

todos = (function list_comprehension (iter0) {const res = [];if ((typeof iter0 === "object") && !Array.isArray(iter0)) {iter0 = Object.keys(iter0);}for (let i0=0; i0<iter0.length; i0++) {const t = iter0[i0];if (!((!_pyfunc_op_equals(_pyfunc_op_getitem(t, 'id'), todo_id)))) {continue;}{res.push(t);}}return res;}).call(this, todos);
render();

            }


            export function make_toggle_handler(todo_id) {
            'Create a toggle handler for a specific todo.';


let handler = (function handler(e) {
toggle_todo(todo_id);

}).bind(this);

return handler;

            }


            export function make_delete_handler(todo_id) {
            'Create a delete handler for a specific todo.';


let handler = (function handler(e) {
delete_todo(todo_id);

}).bind(this);

return handler;

            }


            export function render() {
            'Render the todo list to the DOM.';

const container = document.getElementById('todo-list');
container.innerHTML = '';

let _pytmp_3_seq = todos;
if ((typeof _pytmp_3_seq === "object") && (!Array.isArray(_pytmp_3_seq))) { _pytmp_3_seq = Object.keys(_pytmp_3_seq);}
for (let _pytmp_4_itr = 0; _pytmp_4_itr < _pytmp_3_seq.length; _pytmp_4_itr += 1) {
    let todo = _pytmp_3_seq[_pytmp_4_itr];const item = document.createElement('div');item.className = 'todo-item';
    if (_pyfunc_truthy(_pyfunc_op_getitem(todo, 'completed'))) {item.className = _pyfunc_op_add(item.className, ' completed');
    }const checkbox = document.createElement('input');checkbox.type = 'checkbox';checkbox.checked = _pyfunc_op_getitem(todo, 'completed');checkbox.addEventListener('change', make_toggle_handler(_pyfunc_op_getitem(todo, 'id')));
const span = document.createElement('span');span.textContent = _pyfunc_op_getitem(todo, 'text');const btn = document.createElement('button');btn.textContent = 'Delete';btn.className = 'delete-btn';btn.addEventListener('click', make_delete_handler(_pyfunc_op_getitem(todo, 'id')));
item.appendChild(checkbox);
item.appendChild(span);
item.appendChild(btn);
container.appendChild(item);

}
const completed = _pyfunc_op_len(((function list_comprehension (iter0) {const res = [];if ((typeof iter0 === "object") && !Array.isArray(iter0)) {iter0 = Object.keys(iter0);}for (let i0=0; i0<iter0.length; i0++) {const t = iter0[i0];if (!(_pyfunc_op_getitem(t, 'completed'))) {continue;}{res.push(t);}}return res;}).call(this, todos)));
const total = _pyfunc_op_len(todos);
document.getElementById('status').textContent = _pymeth_format.call("{}/{} completed", completed, total);
            }


            export function handle_submit(event) {
            'Handle form submission.';

event.preventDefault();

const input_el = document.getElementById('todo-input');
const text = _pymeth_strip.call(input_el.value);

if (_pyfunc_truthy(text)) {add_todo(text);
input_el.value = '';
}
            }


            export function handle_load(e) {
            'Handle page load.';

init();

            }


            export function init() {
            'Initialize the application.';

const form = document.getElementById('todo-form');
form.addEventListener('submit', handle_submit);

add_todo('Learn Prescrypt');

add_todo('Build something cool');

add_todo('Deploy to production');

            }

window.addEventListener('DOMContentLoaded', handle_load);
//# sourceMappingURL=app.js.map
