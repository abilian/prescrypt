import {op_add} from "./functions.js";

const assert = console.assert;

assert(op_add(1, 2) === 3);
assert(op_add(1, 2) !== 4);

// assert(false);
