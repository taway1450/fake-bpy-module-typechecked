.. mod-type:: update

.. module:: bpy.props

.. function:: BoolProperty(update, get, set)

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

.. function:: BoolVectorProperty(update, get, set)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], collections.abc.Sequence[bool]] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, collections.abc.Sequence[bool]], None] | None
   :mod-option arg set: skip-refine

   :type default: collections.abc.Sequence[bool] | None
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: collections.abc.Sequence[bool]
   :mod-option rtype: skip-refine

.. function:: EnumProperty(items, update, get, set)

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

.. function:: FloatProperty(update, get, set)

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

.. function:: FloatVectorProperty(update, get, set)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], collections.abc.Sequence[float]] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, collections.abc.Sequence[float]], None] | None
   :mod-option arg set: skip-refine

   :type default: collections.abc.Sequence[float] | None
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: collections.abc.Sequence[float]
   :mod-option rtype: skip-refine

.. function:: IntProperty(update, get, set)

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

.. function:: IntVectorProperty(update, get, set)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type get: collections.abc.Callable[[_GenericType1], collections.abc.Sequence[int]] | None
   :mod-option arg get: skip-refine

   :type set: collections.abc.Callable[[_GenericType1, collections.abc.Sequence[int]], None] | None
   :mod-option arg set: skip-refine

   :type default: collections.abc.Sequence[int] | None
   :mod-option arg default: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: collections.abc.Sequence[int]
   :mod-option rtype: skip-refine

.. function:: PointerProperty(type, update)

   :generic-types: _GenericType1: bpy.types.bpy_struct, _GenericType2: bpy.types.ID

   :type type: type[_GenericType2]
   :mod-option arg type: skip-refine

   :type update: collections.abc.Callable[[_GenericType1, :class:`bpy.types.Context`], None] | None
   :mod-option arg update: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: _GenericType2 | None
   :mod-option rtype: skip-refine

.. function:: CollectionProperty(type)

   :generic-types: _GenericType1: bpy.types.bpy_struct

   :type type: type[_GenericType1]
   :mod-option arg type: skip-refine

   :type tags: set[str] | None
   :mod-option arg tags: skip-refine

   :rtype: :class:`bpy.types.bpy_prop_collection`\ [_GenericType1]
   :mod-option rtype: skip-refine

.. function:: StringProperty(update, get, set)

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
