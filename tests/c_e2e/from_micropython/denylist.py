from __future__ import annotations

ALLOW_LIST = {}
#     "decorator.py",
#     "slice_op.py",
#     # "try_except_break.py",
#     "try_reraise.py",
#     "try_reraise2.py",
# }
DENY_LIST = {
    # Another error
    "try_except_break.py",
    # Compilation timeouts (hangs or memory exhaustion)
    "string_format2.py",
    # Fails on Python 3.12+
    "slice_op.py",
    # Compilation timeouts (hangs or memory exhaustion)
    # "string_format2.py",
    #
    # Compilation errors
    # 10
    "io_iobase.py",  # 10:11: error: Base classes must be simple names
    # 11
    "class_super_multinherit.py",  # 11:0: error: Multiple inheritance not (yet) supported
    # 14
    "subclass_native_call.py",  # 14:10: error: Base classes must be simple names
    # 16
    "class_bases.py",  # 16:0: error: Multiple inheritance not (yet) supported
    # 17
    "io_stringio_base.py",  # 17:8: error: Base classes must be simple names
    # 20
    "builtin_property_inherit.py",  # 20:0: error: Multiple inheritance not (yet) supported
    # 21
    "class_store_class.py",  # 21:0: error: Multiple inheritance not (yet) supported
    "fun_code_lnotab.py",  # 21:11: error: Base classes must be simple names
    # 23
    "annotate_var.py",  # 23:4: error: Annotated assignment target must be a simple na...
    # 26
    "class_inherit_mul.py",  # 26:0: error: Multiple inheritance not (yet) supported
    "subclass_native1.py",  # 26:17: error: Base classes must be simple names
    # 33
    "io_buffered_writer.py",  # 33:11: error: Base classes must be simple names
    # 34
    "builtin_dir.py",  # 34:0: error: Multiple inheritance not (yet) supported
    # 5
    "subclass_native2_list.py",  # 5:0: error: Multiple inheritance not (yet) supported
    "subclass_native2_tuple.py",  # 5:0: error: Multiple inheritance not (yet) supported
    # 58
    "array1.py",  # 58:8: error: Base classes must be simple names
    # 59
    "subclass_native_init.py",  # 59:0: error: Multiple inheritance not (yet) supported
    # 9
    "subclass_native5.py",  # 9:0: error: Multiple inheritance not (yet) supported
    # Other
    "assign_expr_scope.py",  # no binding for nonlocal 'var5' found
    "async_await.py",  # gen_expr not implemented for <Await (AST node)>
    "async_await2.py",  # gen_expr not implemented for <Await (AST node)>
    "async_for.py",  # gen_stmt not implemented for <AsyncFor (AST node)>
    "async_for2.py",  # gen_expr not implemented for <Await (AST node)>
    "async_with.py",  # gen_stmt not implemented for <AsyncWith (AST node)>
    "async_with2.py",  # gen_expr not implemented for <Await (AST node)>
    "async_with_break.py",  # gen_stmt not implemented for <AsyncWith (AST node)>
    "async_with_return.py",  # gen_stmt not implemented for <AsyncWith (AST node)>
    "bytes_subscr.py",  # gen_assign not implemented for <Assign (AST node)>
    "op_error.py",  # gen_assign not implemented for <Assign (AST node)>
    # error
    "builtin_slice.py",  # error: Slice assignment with step is not supported
    # unhashable type
    "builtin_hash.py",  # unhashable type: 'list'
    #
    # QuickJS execution timeouts
    "builtin_range.py",
    "for_range.py",
    "memoryerror.py",
    #
    # QuickJS runtime errors
    # AttributeError
    "class_delattr_setattr.py",  # AttributeError: foo
    # Exception
    "exceptpoly.py",  # Exception: Exception:
    # NotImplementedError
    "exceptpoly2.py",  # NotImplementedError: NotImplementedError:
    # OverflowError
    "int_bytes_optional_args_cp311.py",  # OverflowError: OverflowError: int too big to convert
    # RangeError
    "string_mult.py",  # RangeError: invalid repeat count
    # ReferenceError
    "array_add.py",  # ReferenceError: 'array' is not defined
    "array_construct.py",  # ReferenceError: 'array' is not defined
    "array_construct2.py",  # ReferenceError: 'array' is not defined
    "array_construct_endian.py",  # ReferenceError: 'array' is not defined
    "array_intbig.py",  # ReferenceError: 'array' is not defined
    "array_micropython.py",  # ReferenceError: 'array' is not defined
    "async_syntaxerror.py",  # ReferenceError: 'exec' is not defined
    "attrtuple1.py",  # ReferenceError: 'sys' is not defined
    "attrtuple2.py",  # ReferenceError: 'os' is not defined
    "boundmeth1.py",  # ReferenceError: 'type' is not defined
    "builtin_bin.py",  # ReferenceError: 'bin' is not defined
    "builtin_bin_intbig.py",  # ReferenceError: 'bin' is not defined
    "builtin_compile.py",  # ReferenceError: 'compile' is not defined
    "builtin_ellipsis.py",  # ReferenceError: 'type' is not defined
    "builtin_exec.py",  # ReferenceError: 'exec' is not defined
    "builtin_getattr.py",  # ReferenceError: 'list' is not defined
    "builtin_hasattr.py",  # ReferenceError: 'list' is not defined
    "builtin_hash_gen.py",  # ReferenceError: 'type' is not defined
    "builtin_hash_intbig.py",  # ReferenceError: 'hash' is not defined
    "builtin_help.py",  # ReferenceError: 'help' is not defined
    "builtin_hex.py",  # ReferenceError: 'hex' is not defined
    "builtin_hex_intbig.py",  # ReferenceError: 'hex' is not defined
    "builtin_id.py",  # ReferenceError: 'id' is not defined
    "builtin_len1.py",  # ReferenceError: 'len' is not defined
    "builtin_locals.py",  # ReferenceError: 'locals' is not defined
    "builtin_map.py",  # ReferenceError: 'abs' is not defined
    "builtin_next_arg2.py",  # ReferenceError: 'next' is not defined
    "builtin_oct.py",  # ReferenceError: 'oct' is not defined
    "builtin_oct_intbig.py",  # ReferenceError: 'oct' is not defined
    "builtin_override.py",  # ReferenceError: 'builtins' is not defined
    "builtin_pow3_intbig.py",  # ReferenceError: 'hex' is not defined
    "builtin_range_maxsize.py",  # ReferenceError: 'maxsize' is not defined
    "builtin_setattr.py",  # ReferenceError: 'int' is not defined
    "builtin_str_hex.py",  # ReferenceError: 'bytes' is not defined
    "builtin_type.py",  # ReferenceError: 'type' is not defined
    "builtin_zip.py",  # ReferenceError: 'zip' is not defined
    "bytearray1.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_add.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_add_self.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_append.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_byte_operations.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_center.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_construct.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_construct_array.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_construct_endian.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_count.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_decode.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_intbig.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_partition.py",  # ReferenceError: 'bytearray' is not defined
    "bytearray_slice_assign.py",  # ReferenceError: 'bytearray' is not defined
    "bytes_add_array.py",  # ReferenceError: 'array' is not defined
    "bytes_add_bytearray.py",  # ReferenceError: 'bytearray' is not defined
    "bytes_add_endian.py",  # ReferenceError: 'array' is not defined
    "bytes_compare_array.py",  # ReferenceError: 'array' is not defined
    "bytes_compare_bytearray.py",  # ReferenceError: 'bytearray' is not defined
    "bytes_construct_array.py",  # ReferenceError: 'array' is not defined
    "bytes_construct_bytearray.py",  # ReferenceError: 'bytearray' is not defined
    "bytes_construct_endian.py",  # ReferenceError: 'array' is not defined
    "bytes_count.py",  # ReferenceError: 'bytes' is not defined
    "class2.py",  # ReferenceError: 'type' is not defined
    "class3.py",  # ReferenceError: 'type' is not defined
    "class_bind_self.py",  # ReferenceError: 'int' is not defined
    "class_dict.py",  # ReferenceError: 'int' is not defined
    "class_new.py",  # ReferenceError: 'object' is not defined
    "class_notimpl.py",  # ReferenceError: 'NotImplemented' is not defined
    "class_ordereddict.py",  # ReferenceError: 'int' is not defined
    "class_super_object.py",  # ReferenceError: 'object' is not defined
    "del_attr.py",  # ReferenceError: 'int' is not defined
    "deque1.py",  # ReferenceError: 'deque' is not defined
    "deque2.py",  # ReferenceError: 'deque' is not defined
    "deque_micropython.py",  # ReferenceError: 'deque' is not defined
    "deque_slice.py",  # ReferenceError: 'deque' is not defined
    "dict2.py",  # ReferenceError: 'id' is not defined
    "dict_fixed.py",  # ReferenceError: 'errno' is not defined
    "dict_fromkeys.py",  # ReferenceError: 'dict' is not defined
    "errno1.py",  # ReferenceError: 'type' is not defined
    "except_match_tuple.py",  # ReferenceError: 'fail' is not defined
    "exception1.py",  # ReferenceError: 'IndexError' is not defined
    "exception_chain.py",  # ReferenceError: 'sys' is not defined
    "frozenset1.py",  # ReferenceError: 'frozenset' is not defined
    "frozenset_add.py",  # ReferenceError: 'frozenset' is not defined
    "frozenset_binop.py",  # ReferenceError: 'frozenset' is not defined
    "frozenset_copy.py",  # ReferenceError: 'frozenset' is not defined
    "frozenset_difference.py",  # ReferenceError: 'frozenset' is not defined
    "frozenset_set.py",  # ReferenceError: 'frozenset' is not defined
    "fun_calldblstar.py",  # ReferenceError: 'len' is not defined
    "fun_calldblstar2.py",  # ReferenceError: 'exec' is not defined
    "fun_calldblstar3.py",  # ReferenceError: 'kw' is not defined
    "fun_callstardblstar.py",  # ReferenceError: 'kwargs' is not defined
    "fun_code.py",  # ReferenceError: 'type' is not defined
    "fun_kwonly.py",  # ReferenceError: 'x' is not defined
    "fun_kwonlydef.py",  # ReferenceError: 'a' is not defined
    "fun_kwvarargs.py",  # ReferenceError: 'kwargs' is not defined
    "gc1.py",  # ReferenceError: 'gc' is not defined
    "gen_yield_from_close.py",  # ReferenceError: 'next' is not defined
    "gen_yield_from_executing.py",  # ReferenceError: 'next' is not defined
    "gen_yield_from_send.py",  # ReferenceError: 'next' is not defined
    "gen_yield_from_stopped.py",  # ReferenceError: 'next' is not defined
    "gen_yield_from_throw.py",  # ReferenceError: 'next' is not defined
    "gen_yield_from_throw2.py",  # ReferenceError: 'next' is not defined
    "gen_yield_from_throw3.py",  # ReferenceError: 'next' is not defined
    "gen_yield_from_throw_multi_arg.py",  # ReferenceError: 'next' is not defined
    "generator_args.py",  # ReferenceError: 'kwargs' is not defined
    "generator_exc.py",  # ReferenceError: 'next' is not defined
    "generator_pend_throw.py",  # ReferenceError: 'next' is not defined
    "generator_pep479.py",  # ReferenceError: 'next' is not defined
    "generator_return.py",  # ReferenceError: 'next' is not defined
    "generator_throw.py",  # ReferenceError: 'next' is not defined
    "generator_throw_multi_arg.py",  # ReferenceError: 'next' is not defined
    "generator_throw_nested.py",  # ReferenceError: 'next' is not defined
    "getitem.py",  # ReferenceError: 'next' is not defined
    "globals_del.py",  # ReferenceError: 'type' is not defined
    "ifcond.py",  # ReferenceError: f2 is not initialized
    "import_instance_method.py",  # ReferenceError: 'sys' is not defined
    "int_64_basics.py",  # ReferenceError: 'sys' is not defined
    "int_big1.py",  # ReferenceError: 'sys' is not defined
    "int_big_error.py",  # ReferenceError: 'bytearray' is not defined
    "int_bytes.py",  # ReferenceError: 'sys' is not defined
    "int_bytes_int64.py",  # ReferenceError: 'hex' is not defined
    "int_bytes_intbig.py",  # ReferenceError: 'sys' is not defined
    "int_parse.py",  # ReferenceError: 'bytearray' is not defined
    "io_bytesio_cow.py",  # ReferenceError: 'io' is not defined
    "io_bytesio_ext.py",  # ReferenceError: 'io' is not defined
    "io_bytesio_ext2.py",  # ReferenceError: 'io' is not defined
    "io_stringio1.py",  # ReferenceError: 'io' is not defined
    "io_stringio_with.py",  # ReferenceError: 'io' is not defined
    "io_write_ext.py",  # ReferenceError: 'io' is not defined
    "iter1.py",  # ReferenceError: 'StopIteration' is not defined
    "iter2.py",  # ReferenceError: 'StopIteration' is not defined
    "lexer.py",  # ReferenceError: 'exec' is not defined
    "list_slice.py",  # ReferenceError: 'ValueError' is not defined
    "memoryview_slice_assign.py",  # ReferenceError: 'memoryview' is not defined
    "module1.py",  # ReferenceError: '__main__' is not defined
    "module2.py",  # ReferenceError: 'sys' is not defined
    "module_dict.py",  # ReferenceError: 'sys' is not defined
    "namedtuple1.py",  # ReferenceError: 'namedtuple' is not defined
    "namedtuple_asdict.py",  # ReferenceError: 'namedtuple' is not defined
    "nanbox_smallint.py",  # ReferenceError: 'micropython' is not defined
    "object1.py",  # ReferenceError: 'object' is not defined
    "object_new.py",  # ReferenceError: 'object' is not defined
    "op_error_bytearray.py",  # ReferenceError: 'bytearray' is not defined
    "ordereddict1.py",  # ReferenceError: 'OrderedDict' is not defined
    "ordereddict_eq.py",  # ReferenceError: 'OrderedDict' is not defined
    "parser.py",  # ReferenceError: 'compile' is not defined
    "python34.py",  # ReferenceError: 'exec' is not defined
    "scope_implicit.py",  # ReferenceError: x is not initialized
    "self_type_check.py",  # ReferenceError: 'sys' is not defined
    "set_type.py",  # ReferenceError: 'set' is not defined
    "set_unop.py",  # ReferenceError: 'hash' is not defined
    "special_methods2.py",  # ReferenceError: 'dir' is not defined
    "string_compare.py",  # ReferenceError: 'sys' is not defined
    "string_count.py",  # ReferenceError: 'str' is not defined
    "struct1.py",  # ReferenceError: 'struct' is not defined
    "struct1_intbig.py",  # ReferenceError: 'struct' is not defined
    "struct2.py",  # ReferenceError: 'struct' is not defined
    "struct_endian.py",  # ReferenceError: 'struct' is not defined
    "struct_micropython.py",  # ReferenceError: 'struct' is not defined
    "subclass_native3.py",  # ReferenceError: 'Exception' is not defined
    "subclass_native4.py",  # ReferenceError: 'list' is not defined
    "subclass_native_buffer.py",  # ReferenceError: 'bytes' is not defined
    "subclass_native_cmp.py",  # ReferenceError: 'tuple' is not defined
    "subclass_native_containment.py",  # ReferenceError: 'list' is not defined
    "subclass_native_exc_new.py",  # ReferenceError: 'BaseException' is not defined
    "subclass_native_iter.py",  # ReferenceError: 'map' is not defined
    "subclass_native_specmeth.py",  # ReferenceError: 'list' is not defined
    "subclass_native_str.py",  # ReferenceError: 'str' is not defined
    "syntaxerror.py",  # ReferenceError: 'exec' is not defined
    "syntaxerror_return.py",  # ReferenceError: 'exec' is not defined
    "sys1.py",  # ReferenceError: 'sys' is not defined
    "sys_exit.py",  # ReferenceError: 'sys' is not defined
    "sys_getsizeof.py",  # ReferenceError: 'sys' is not defined
    "sys_path.py",  # ReferenceError: 'globals' is not defined
    "sys_stdio.py",  # ReferenceError: 'sys' is not defined
    "sys_stdio_buffer.py",  # ReferenceError: 'sys' is not defined
    "try2.py",  # ReferenceError: 'foo' is not defined
    "try_as_var.py",  # ReferenceError: 'type' is not defined
    "try_error.py",  # ReferenceError: 'a' is not defined
    "try_finally1.py",  # ReferenceError: 'foo' is not defined
    "types1.py",  # ReferenceError: 'bool' is not defined
    "types2.py",  # ReferenceError: 'hash' is not defined
    "unary_op.py",  # ReferenceError: 'int' is not defined
    "unboundlocal.py",  # ReferenceError: x is not initialized
    # StopIteration
    "gen_yield_from.py",  # StopIteration: StopIteration: 444
    # SyntaxError
    "assign_expr.py",  # SyntaxError: unexpected token in expression: 'var'
    "builtin_eval.py",  # SyntaxError: unexpected token in expression: '#comment'
    "builtin_ord.py",  # SyntaxError: invalid number literal
    "builtin_super.py",  # SyntaxError: invalid number literal
    "bytes_partition.py",  # SyntaxError: invalid redefinition of lexical identifier
    "class_super.py",  # SyntaxError: invalid number literal
    "class_super_aslocal.py",  # SyntaxError: variable name expected
    "dict_del.py",  # SyntaxError: unexpected token in expression: 'if'
    "generator_closure.py",  # SyntaxError: expecting ')'
    "list_index.py",  # SyntaxError: invalid redefinition of lexical identifier
    "set_remove.py",  # SyntaxError: unexpected token in expression: 'if'
    "string_fstring.py",  # SyntaxError: expecting ';'
    "string_index.py",  # SyntaxError: invalid redefinition of lexical identifier
    "string_partition.py",  # SyntaxError: invalid redefinition of lexical identifier
    "string_rindex.py",  # SyntaxError: invalid redefinition of lexical identifier
    "string_rpartition.py",  # SyntaxError: invalid redefinition of lexical identifier
    "sys_tracebacklimit.py",  # SyntaxError: unexpected token in expression: 'if'
    "try_else.py",  # SyntaxError: invalid redefinition of lexical identifier
    "try_else_finally.py",  # SyntaxError: unexpected token in expression: 'finally'
    "try_finally_break.py",  # SyntaxError: unexpected token in expression: 'if'
    "tuple_index.py",  # SyntaxError: invalid redefinition of lexical identifier
    "unpack1.py",  # SyntaxError: invalid redefinition of lexical identifier
    "with1.py",  # SyntaxError: invalid redefinition of lexical identifier
    # SystemExit
    "builtin_delattr.py",  # SystemExit: SystemExit:
    "builtin_enumerate.py",  # SystemExit: SystemExit:
    "builtin_eval_buffer.py",  # SystemExit: SystemExit:
    "builtin_exec_buffer.py",  # SystemExit: SystemExit:
    "builtin_filter.py",  # SystemExit: SystemExit:
    "builtin_minmax.py",  # SystemExit: SystemExit:
    "builtin_property.py",  # SystemExit: SystemExit:
    "builtin_reversed.py",  # SystemExit: SystemExit:
    "builtin_sorted.py",  # SystemExit: SystemExit:
    "bytes_center.py",  # SystemExit: SystemExit:
    "class_descriptor.py",  # SystemExit: SystemExit:
    "class_setname_hazard.py",  # SystemExit: SystemExit:
    "class_setname_hazard_rand.py",  # SystemExit: SystemExit:
    "dict_fromkeys2.py",  # SystemExit: SystemExit:
    "fun_error2.py",  # SystemExit: SystemExit:
    "fun_globals.py",  # SystemExit: SystemExit:
    "int_big_to_small.py",  # SystemExit: SystemExit:
    "int_big_to_small_int29.py",  # SystemExit: SystemExit:
    "memoryview1.py",  # SystemExit: SystemExit:
    "memoryview2.py",  # SystemExit: SystemExit:
    "memoryview_gc.py",  # SystemExit: SystemExit:
    "memoryview_intbig.py",  # SystemExit: SystemExit:
    "memoryview_itemsize.py",  # SystemExit: SystemExit:
    "memoryview_slice_size.py",  # SystemExit: SystemExit:
    "object_dict.py",  # SystemExit: SystemExit:
    "op_error_memoryview.py",  # SystemExit: SystemExit:
    "slice_attrs.py",  # SystemExit: SystemExit:
    "slice_indices.py",  # SystemExit: SystemExit:
    "stopiteration.py",  # SystemExit: SystemExit:
    "string_center.py",  # SystemExit: SystemExit:
    "string_splitlines.py",  # SystemExit: SystemExit:
    # TypeError
    "async_def.py",  # TypeError: not a function
    "builtin_issubclass.py",  # TypeError: invalid 'instanceof' right operand
    "bytes_construct_intbig.py",  # TypeError: not a function
    "bytes_find.py",  # TypeError: not a function
    "bytes_replace.py",  # TypeError: cannot read property 'apply' of undefined
    "bytes_split.py",  # TypeError: cannot read property 'apply' of undefined
    "bytes_strip.py",  # TypeError: cannot read property 'apply' of undefined
    "class1.py",  # TypeError: not a function
    "class_call.py",  # TypeError: not a function
    "class_contains.py",  # TypeError: Not a container: [object Object]
    "class_inherit1.py",  # TypeError: not a function
    "class_inplace_op2.py",  # TypeError: cannot read property '__rmatmul__' of null
    "class_use_other.py",  # TypeError: not a function
    "containment.py",  # TypeError: Not a container: 49,50,51
    "dict_specialmeth.py",  # TypeError: not a function
    "dict_union.py",  # TypeError: cannot read property 'apply' of undefined
    "dict_update.py",  # TypeError: cannot convert to object
    "dict_views.py",  # TypeError: not a function
    "fun_code_colines.py",  # TypeError: cannot read property 'co_lines' of undefined
    "fun_code_full.py",  # TypeError: cannot read property 'co_code' of undefined
    "fun_name.py",  # TypeError: cannot read property '__name__' of undefined
    "fun_str.py",  # TypeError: cannot read property 'slice' of undefined
    "gen_yield_from_ducktype.py",  # TypeError: value is not iterable
    "gen_yield_from_throw_repeat.py",  # TypeError: not a function
    "generator_close.py",  # TypeError: not a function
    "generator_name.py",  # TypeError: cannot read property '__name__' of undefined
    "generator_send.py",  # TypeError: not a function
    "generator_throw_repeat.py",  # TypeError: not a function
    "iter0.py",  # TypeError: not a function
    "list1.py",  # TypeError: not a function
    "list_extend.py",  # TypeError: not a object
    "scope_class.py",  # TypeError: not a function
    "set_binop.py",  # TypeError: not a function
    "set_containment.py",  # TypeError: Not a container: [object Set]
    "set_copy.py",  # TypeError: cannot read property 'apply' of undefined
    "set_difference.py",  # TypeError: not a function
    "set_discard.py",  # TypeError: not a function
    "set_intersection.py",  # TypeError: not a function
    "set_isdisjoint.py",  # TypeError: not a function
    "set_isfooset.py",  # TypeError: not a function
    "set_pop.py",  # TypeError: cannot read property 'apply' of undefined
    "set_specialmeth.py",  # TypeError: not a function
    "set_symmetric_difference.py",  # TypeError: not a function
    "set_union.py",  # TypeError: not a function
    "set_update.py",  # TypeError: cannot read property 'apply' of undefined
    "slice_optimise.py",  # TypeError: not a function
    "string_rsplit.py",  # TypeError: cannot read property 'apply' of undefined
    "string_split.py",  # TypeError: cannot read property 'apply' of undefined
    "string_strip.py",  # TypeError: cannot read property 'apply' of undefined
    "subclass_classmethod.py",  # TypeError: not a function
    "try_return.py",  # TypeError: 'NoneType' object is not subscriptable
    #
    # Node.js runtime errors
    # ReferenceError
    "equal.py",  # ReferenceError: print is not defined
    #
    # Output mismatches (JS output differs from Python)
    "andor.py",
    "bool1.py",
    "builtin_abs_intbig.py",
    "builtin_callable.py",
    "builtin_chr.py",
    "builtin_divmod.py",
    "builtin_divmod_intbig.py",
    "builtin_eval_error.py",
    "builtin_pow3.py",
    "builtin_print.py",
    "builtin_range_attrs.py",
    "builtin_range_binop.py",
    "builtin_round_int.py",
    "builtin_round_intbig.py",
    "builtin_sum.py",
    "bytes_construct.py",
    "bytes_format_modulo.py",
    "bytes_mult.py",
    "class_binop.py",
    "class_getattr.py",
    "class_inplace_op.py",
    "class_item.py",
    "class_number.py",
    "class_reverse_op.py",
    "class_staticclassmethod.py",
    "class_store.py",
    "class_str.py",
    "closure_defargs.py",
    "closure_namedarg.py",
    "comprehension1.py",
    "del_deref.py",
    "del_global.py",
    "del_local.py",
    "del_name.py",
    "del_subscr.py",
    "dict1.py",
    "dict_clear.py",
    "dict_construct.py",
    "dict_from_iter.py",
    "dict_get.py",
    "dict_iterator.py",
    "dict_pop.py",
    "dict_popitem.py",
    "dict_setdefault.py",
    "floordivide_intbig.py",
    "for2.py",
    "fun_annotations.py",
    "fun_calldblstar4.py",
    "fun_callstar.py",
    "fun_defargs.py",
    "fun_defargs2.py",
    "fun_error.py",
    "fun_kwargs.py",
    "fun_varargs.py",
    "gen_yield_from_pending.py",
    "generator1.py",
    "getattr.py",
    "int1.py",
    "int_big_add.py",
    "int_big_and.py",
    "int_big_and2.py",
    "int_big_and3.py",
    "int_big_cmp.py",
    "int_big_div.py",
    "int_big_lshift.py",
    "int_big_mod.py",
    "int_big_mul.py",
    "int_big_or.py",
    "int_big_or2.py",
    "int_big_or3.py",
    "int_big_pow.py",
    "int_big_rshift.py",
    "int_big_unary.py",
    "int_big_xor.py",
    "int_big_xor2.py",
    "int_big_xor3.py",
    "int_big_zeroone.py",
    "int_constfolding.py",
    "int_constfolding_intbig.py",
    "int_divmod.py",
    "int_divmod_intbig.py",
    "int_divzero.py",
    "int_intbig.py",
    "int_small.py",
    "iter_of_iter.py",
    "lambda_defargs.py",
    "list_compare.py",
    "list_mult.py",
    "list_remove.py",
    "list_slice_3arg.py",
    "list_slice_assign.py",
    "list_sort.py",
    "op_error_literal.py",
    "return1.py",
    "scope.py",
    "seq_unpack.py",
    "set_add.py",
    "set_basic.py",
    "set_clear.py",
    "set_comprehension.py",
    "set_iter_of_iter.py",
    "slots_bool_len.py",
    "special_comparisons.py",
    "special_comparisons2.py",
    "special_methods.py",
    "special_methods_intbig.py",
    "string1.py",
    "string_cr_conversion.py",
    "string_crlf_conversion.py",
    "string_endswith.py",
    "string_find.py",
    "string_format.py",
    "string_format_cp310.py",
    "string_format_error.py",
    "string_format_intbig.py",
    "string_format_modulo.py",
    "string_format_sep.py",
    "string_fstring_debug.py",
    "string_join.py",
    "string_replace.py",
    "string_repr.py",
    "string_rfind.py",
    "string_startswith.py",
    "try_finally_break2.py",
    "try_finally_continue.py",
    "try_finally_return.py",
    "try_finally_return2.py",
    "try_finally_return3.py",
    "try_finally_return4.py",
    "tuple1.py",
    "tuple_compare.py",
    "tuple_mult.py",
    "tuple_slice.py",
    "with_break.py",
    "with_continue.py",
    "with_raise.py",
    "with_return.py",
}
