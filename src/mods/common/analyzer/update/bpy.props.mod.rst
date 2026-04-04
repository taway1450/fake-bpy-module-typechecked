.. mod-type:: update

.. module:: bpy.props

.. function:: BoolProperty(update, get, set, default, tags)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], bool] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, bool], None] | None
   :mod-option arg set: skip-refine

   :type default: bool
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: bool

.. function:: BoolVectorProperty(update, get, set, default, tags, size)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], :class:`bpy.types.bpy_prop_array`\ [bool]] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, :class:`bpy.types.bpy_prop_array`\ [bool]], None] | None
   :mod-option arg set: skip-refine

   :type default: :class:`bpy.types.bpy_prop_array`\ [bool] | None
   :mod-option arg default: skip-refine

   :type size: typing.Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31] | collections.abc.Sequence[int] | None
   :mod-option arg size: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: :class:`bpy.types.bpy_prop_array`\ [bool]
   :mod-option rtype: skip-refine

.. function:: EnumProperty(items, update, get, set, default, tags)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type items: collections.abc.Iterable[tuple[str, str, str] | tuple[str, str, str, int] | tuple[str, str, str, str, int] | None] | collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context` | None], collections.abc.Iterable[tuple[str, str, str] | tuple[str, str, str, int] | tuple[str, str, str, str, int] | None]]
   :mod-option arg items: skip-refine

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], int] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, int], None] | None
   :mod-option arg set: skip-refine

   :type default: str | int | set[str] | None
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: str

.. function:: FloatProperty(update, get, set, default, tags)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], float] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, float], None] | None
   :mod-option arg set: skip-refine

   :type default: float
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: float

.. function:: FloatVectorProperty(update, get, set, default, tags, size)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], :class:`bpy.types.bpy_prop_array`\ [float]] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, :class:`bpy.types.bpy_prop_array`\ [float]], None] | None
   :mod-option arg set: skip-refine

   :type default: :class:`bpy.types.bpy_prop_array`\ [float] | None
   :mod-option arg default: skip-refine

   :type size: typing.Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31] | collections.abc.Sequence[int] | None
   :mod-option arg size: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: :class:`bpy.types.bpy_prop_array`\ [float]
   :mod-option rtype: skip-refine

.. function:: IntProperty(update, get, set, default, tags)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], int] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, int], None] | None
   :mod-option arg set: skip-refine

   :type default: int
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: int

.. function:: IntVectorProperty(update, get, set, default, tags, size)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], :class:`bpy.types.bpy_prop_array`\ [int]] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, :class:`bpy.types.bpy_prop_array`\ [int]], None] | None
   :mod-option arg set: skip-refine

   :type default: :class:`bpy.types.bpy_prop_array`\ [int] | None
   :mod-option arg default: skip-refine

   :type size: typing.Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31] | collections.abc.Sequence[int] | None
   :mod-option arg size: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: :class:`bpy.types.bpy_prop_array`\ [int]
   :mod-option rtype: skip-refine

.. function:: PointerProperty(type, update, tags)

   :generic-types: _GenericType1: bpy.types.bpy_struct, _GenericType2: bpy.types.ID

   :type type: type[_GenericType2]
   :mod-option arg type: skip-refine

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: _GenericType2 | None
   :mod-option rtype: skip-refine

.. function:: CollectionProperty(type, tags)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type type: type[_GenericType1]
   :mod-option arg type: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: :class:`bpy.types.bpy_prop_collection_idprop`\ [_GenericType1]
   :mod-option rtype: skip-refine

.. function:: StringProperty(update, get, set, default, tags)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], str] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, str], None] | None
   :mod-option arg set: skip-refine

   :type default: str | None
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: str
