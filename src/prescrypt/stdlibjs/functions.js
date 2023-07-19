// function: perf_counter
export const perf_counter = function() { // nargs: 0
    if (typeof(process) === "undefined"){return performance.now()*1e-3;}
    else {var t = process.hrtime(); return t[0] + t[1]*1e-9;}
};

// ---

// function: time
export const time = function () {return Date.now() / 1000;} // nargs: 0;

// ---

// function: op_instantiate
export const op_instantiate = function (ob, args) { // nargs: 2
    if ((typeof ob === "undefined") ||
            (typeof window !== "undefined" && window === ob) ||
            (typeof global !== "undefined" && global === ob))
            {throw "Class constructor is called as a function.";}
    for (var name in ob) {
        if (Object[name] === undefined &&
            typeof ob[name] === 'function' && !ob[name].nobind) {
            ob[name] = ob[name].bind(ob);
            ob[name].__name__ = name;
        }
    }
    if (ob.__init__) {
        ob.__init__.apply(ob, args);
    }
};

// ---

// function: create_dict
export const create_dict = function () {
    var d = {};
    for (var i=0; i<arguments.length; i+=2) { d[arguments[i]] = arguments[i+1]; }
    return d;
};

// ---

// function: merge_dicts
export const merge_dicts = function () {
    var res = {};
    for (var i=0; i<arguments.length; i++) {
        var d = arguments[i];
        var key, keys = Object.keys(d);
        for (var j=0; j<keys.length; j++) { key = keys[j]; res[key] = d[key]; }
    }
    return res;
};

// ---

// function: op_parse_kwargs
export const op_parse_kwargs = function (arg_names, arg_values, kwargs, strict) { // nargs: 3
    for (var i=0; i<arg_values.length; i++) {
        var name = arg_names[i];
        if (kwargs[name] !== undefined) {
            arg_values[i] = kwargs[name];
            delete kwargs[name];
        }
    }
    if (strict && Object.keys(kwargs).length > 0) {
        throw FUNCTION_PREFIXop_error('TypeError',
            'Function ' + strict + ' does not accept **kwargs.');
    }
    return kwargs;
};

// ---

// function: op_error
export const op_error = function (etype, msg) { // nargs: 2
    var e = new Error(etype + ': ' + msg);
    e.name = etype
    return e;
};

// ---

// function: hasattr
export const hasattr = function (ob, name) { // nargs: 2
    return (ob !== undefined) && (ob !== null) && (ob[name] !== undefined);
};

// ---

// function: getattr
export const getattr = function (ob, name, deflt) { // nargs: 2 3
    var has_attr = ob !== undefined && ob !== null && ob[name] !== undefined;
    if (has_attr) {return ob[name];}
    else if (arguments.length == 3) {return deflt;}
    else {var e = Error(name); e.name='AttributeError'; throw e;}
};

// ---

// function: setattr
export const setattr = function (ob, name, value) {  // nargs: 3
    ob[name] = value;
};

// ---

// function: delattr
export const delattr = function (ob, name) {  // nargs: 2
    delete ob[name];
};

// ---

// function: dict
export const dict = function (x) {
    var t, i, keys, r={};
    if (Array.isArray(x)) {
        for (i=0; i<x.length; i++) {
            t=x[i]; r[t[0]] = t[1];
        }
    } else {
        keys = Object.keys(x);
        for (i=0; i<keys.length; i++) {
            t=keys[i]; r[t] = x[t];
        }
    }
    return r;
};

// ---

// function: list
export const list = function (x) {
    var r=[];
    if (typeof x==="object" && !Array.isArray(x)) {x = Object.keys(x)}
    for (var i=0; i<x.length; i++) {
        r.push(x[i]);
    }
    return r;
};

// ---

// function: range
export const range = function (start, end, step) {
    var i, res = [];
    var val = start;
    var n = (end - start) / step;
    for (i=0; i<n; i++) {
        res.push(val);
        val += step;
    }
    return res;
};

// ---

// function: format
export const format = function (v, fmt) {  // nargs: 2
    fmt = fmt.toLowerCase();
    var s = String(v);
    if (fmt.indexOf('!r') >= 0) {
        try { s = JSON.stringify(v); } catch (e) { s = undefined; }
        if (typeof s === 'undefined') { s = v._IS_COMPONENT ? v.id : String(v); }
    }
    var fmt_type = '';
    if (fmt.slice(-1) == 'i' || fmt.slice(-1) == 'f' ||
        fmt.slice(-1) == 'e' || fmt.slice(-1) == 'g') {
            fmt_type = fmt[fmt.length-1]; fmt = fmt.slice(0, fmt.length-1);
    }
    var i0 = fmt.indexOf(':');
    var i1 = fmt.indexOf('.');
    var spec1 = '', spec2 = '';  // before and after dot
    if (i0 >= 0) {
        if (i1 > i0) { spec1 = fmt.slice(i0+1, i1); spec2 = fmt.slice(i1+1); }
        else { spec1 = fmt.slice(i0+1); }
    }
    // Format numbers
    if (fmt_type == '') {
    } else if (fmt_type == 'i') { // integer formatting, for %i
        s = parseInt(v).toFixed(0);
    } else if (fmt_type == 'f') {  // float formatting
        v = parseFloat(v);
        var decimals = spec2 ? Number(spec2) : 6;
        s = v.toFixed(decimals);
    } else if (fmt_type == 'e') {  // exp formatting
        v = parseFloat(v);
        var precision = (spec2 ? Number(spec2) : 6) || 1;
        s = v.toExponential(precision);
    } else if (fmt_type == 'g') {  // "general" formatting
        v = parseFloat(v);
        var precision = (spec2 ? Number(spec2) : 6) || 1;
        // Exp or decimal?
        s = v.toExponential(precision-1);
        var s1 = s.slice(0, s.indexOf('e')), s2 = s.slice(s.indexOf('e'));
        if (s2.length == 3) { s2 = 'e' + s2[1] + '0' + s2[2]; }
        var exp = Number(s2.slice(1));
        if (exp >= -4 && exp < precision) { s1=v.toPrecision(precision); s2=''; }
        // Skip trailing zeros and dot
        var j = s1.length-1;
        while (j>0 && s1[j] == '0') { j-=1; }
        s1 = s1.slice(0, j+1);
        if (s1.slice(-1) == '.') { s1 = s1.slice(0, s1.length-1); }
        s = s1 + s2;
    }
    // prefix/padding
    var prefix = '';
    if (spec1) {
        if (spec1[0] == '+' && v > 0) { prefix = '+'; spec1 = spec1.slice(1); }
        else if (spec1[0] == ' ' && v > 0) { prefix = ' '; spec1 = spec1.slice(1); }
    }
    if (spec1 && spec1[0] == '0') {
        var padding = Number(spec1.slice(1)) - (s.length + prefix.length);
        s = '0'.repeat(Math.max(0, padding)) + s;
    }
    return prefix + s;
};

// ---

// function: pow
export const pow = Math.pow // nargs: 2;

// ---

// function: sum
export const sum = function (x) {  // nargs: 1
    return x.reduce(function(a, b) {return a + b;});
};

// ---

// function: round
export const round = Math.round // nargs: 1;

// ---

// function: int
export const int = function (x, base) { // nargs: 1 2
    if(base !== undefined) return parseInt(x, base);
    return x<0 ? Math.ceil(x): Math.floor(x);
};

// ---

// function: float
export const float = Number // nargs: 1;

// ---

// function: str
export const str = String // nargs: 0 1;

// ---

// function: repr
export const repr = function (x) { // nargs: 1
    var res; try { res = JSON.stringify(x); } catch (e) { res = undefined; }
    if (typeof res === 'undefined') { res = x._IS_COMPONENT ? x.id : String(x); }
    return res;
};

// ---

// function: bool
export const bool = function (x) { // nargs: 1
    return Boolean(FUNCTION_PREFIXtruthy(x));
};

// ---

// function: abs
export const abs = Math.abs // nargs: 1;

// ---

// function: divmod
export const divmod = function (x, y) { // nargs: 2
    var m = x % y; return [(x-m)/y, m];
};

// ---

// function: all
export const all = function (x) { // nargs: 1
    for (var i=0; i<x.length; i++) {
        if (!FUNCTION_PREFIXtruthy(x[i])){return false;}
    } return true;
};

// ---

// function: any
export const any = function (x) { // nargs: 1
    for (var i=0; i<x.length; i++) {
        if (FUNCTION_PREFIXtruthy(x[i])){return true;}
    } return false;
};

// ---

// function: enumerate
export const enumerate = function (iter) { // nargs: 1
    var i, res=[];
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    for (i=0; i<iter.length; i++) {res.push([i, iter[i]]);}
    return res;
};

// ---

// function: zip
export const zip = function () { // nargs: 2 3 4 5 6 7 8 9
    var i, j, tup, arg, args = [], res = [], len = 1e20;
    for (i=0; i<arguments.length; i++) {
        arg = arguments[i];
        if ((typeof arg==="object") && (!Array.isArray(arg))) {arg = Object.keys(arg);}
        args.push(arg);
        len = Math.min(len, arg.length);
    }
    for (j=0; j<len; j++) {
        tup = []
        for (i=0; i<args.length; i++) {tup.push(args[i][j]);}
        res.push(tup);
    }
    return res;
};

// ---

// function: reversed
export const reversed = function (iter) { // nargs: 1
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    return iter.slice().reverse();
};

// ---

// function: sorted
export const sorted = function (iter, key, reverse) { // nargs: 1 2 3
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    var comp = function (a, b) {a = key(a); b = key(b);
        if (a<b) {return -1;} if (a>b) {return 1;} return 0;};
    comp = Boolean(key) ? comp : undefined;
    iter = iter.slice().sort(comp);
    if (reverse) iter.reverse();
    return iter;
};

// ---

// function: filter
export const filter = function (func, iter) { // nargs: 2
    if (typeof func === "undefined" || func === null) {func = function(x) {return x;}}
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    return iter.filter(func);
};

// ---

// function: map
export const map = function (func, iter) { // nargs: 2
    if (typeof func === "undefined" || func === null) {func = function(x) {return x;}}
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    return iter.map(func);
};

// ---

// function: truthy
export const truthy = function (v) {
    if (v === null || typeof v !== "object") {return v;}
    else if (v.length !== undefined) {return v.length ? v : false;}
    else if (v.byteLength !== undefined) {return v.byteLength ? v : false;}
    else if (v.constructor !== Object) {return true;}
    else {return Object.getOwnPropertyNames(v).length ? v : false;}
};

// ---

// function: op_equals
export const op_equals = function op_equals (a, b) { // nargs: 2
    var a_type = typeof a;
    // If a (or b actually) is of type string, number or boolean, we don't need
    // to do all the other type checking below.
    if (a_type === "string" || a_type === "boolean" || a_type === "number") {
        return a == b;
    }

    if (a == null || b == null) {
    } else if (Array.isArray(a) && Array.isArray(b)) {
        var i = 0, iseq = a.length == b.length;
        while (iseq && i < a.length) {iseq = op_equals(a[i], b[i]); i+=1;}
        return iseq;
    } else if (a.constructor === Object && b.constructor === Object) {
        var akeys = Object.keys(a), bkeys = Object.keys(b);
        akeys.sort(); bkeys.sort();
        var i=0, k, iseq = op_equals(akeys, bkeys);
        while (iseq && i < akeys.length)
            {k=akeys[i]; iseq = op_equals(a[k], b[k]); i+=1;}
        return iseq;
    } return a == b;
};

// ---

// function: op_contains
export const op_contains = function op_contains (a, b) { // nargs: 2
    if (b == null) {
    } else if (Array.isArray(b)) {
        for (var i=0; i<b.length; i++) {if (FUNCTION_PREFIXop_equals(a, b[i]))
                                           return true;}
        return false;
    } else if (b.constructor === Object) {
        for (var k in b) {if (a == k) return true;}
        return false;
    } else if (b.constructor == String) {
        return b.indexOf(a) >= 0;
    } var e = Error('Not a container: ' + b); e.name='TypeError'; throw e;
};

// ---

// function: op_add
export const op_add = function (a, b) { // nargs: 2
    if (Array.isArray(a) && Array.isArray(b)) {
        return a.concat(b);
    } return a + b;
};

// ---

// function: op_mult
export const op_mult = function (a, b) { // nargs: 2
    if ((typeof a === 'number') + (typeof b === 'number') === 1) {
        if (a.constructor === String) return METHOD_PREFIXrepeat(a, b);
        if (b.constructor === String) return METHOD_PREFIXrepeat(b, a);
        if (Array.isArray(b)) {var t=a; a=b; b=t;}
        if (Array.isArray(a)) {
            var res = []; for (var i=0; i<b; i++) res = res.concat(a);
            return res;
        }
    } return a * b;
};

// ---
