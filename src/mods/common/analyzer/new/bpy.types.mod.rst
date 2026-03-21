.. mod-type:: new

.. module:: bpy.types

.. class:: bpy_prop_array

   :generic-types: _GenericType1

   .. method:: __get__(instance, owner)

      :rtype: :class:`bpy_prop_array`\ [_GenericType1]
      :mod-option rtype: skip-refine

   .. method:: __set__(instance, value)

      :type value: collections.abc.Iterable[_GenericType1]
      :mod-option arg value: skip-refine

   .. method:: foreach_get(seq)

      :type seq: collections.abc.MutableSequence[_GenericType1] | typing_extensions.Buffer | npt.NDArray
      :mod-option arg seq: skip-refine

   .. method:: foreach_set(seq)

      :type seq: collections.abc.Sequence[_GenericType1] | typing_extensions.Buffer | npt.NDArray
      :mod-option arg seq: skip-refine

   .. method:: __getitem__(key)

      :type key: int
      :mod-option arg key: skip-refine
      :rtype: _GenericType1
      :mod-option rtype: skip-refine
      :option function: overload

   .. method:: __getitem__(key)

      :type key: slice
      :mod-option arg key: skip-refine
      :rtype: tuple[_GenericType1, ...]
      :mod-option rtype: skip-refine
      :option function: overload

   .. method:: __setitem__(key, value)

      :type key: int
      :mod-option arg key: skip-refine
      :type value: _GenericType1
      :mod-option arg value: skip-refine
      :option function: overload

   .. method:: __setitem__(key, value)

      :type key: slice
      :mod-option arg key: skip-refine
      :type value: collections.abc.Iterable[_GenericType1]
      :mod-option arg value: skip-refine
      :option function: overload

   .. method:: __delitem__(key)

      :type key: int
      :mod-option arg key: skip-refine

   .. method:: __iter__()

      :rtype: collections.abc.Iterator[_GenericType1]
      :mod-option rtype: skip-refine

   .. method:: __next__()

      :rtype: _GenericType1
      :mod-option rtype: skip-refine

   .. method:: __len__()

      :rtype: int
      :mod-option rtype: skip-refine

.. class:: bpy_prop_collection_idprop

   built-in class used for user defined collections.

   :generic-types: _GenericType1

   .. base-class:: bpy_prop_collection[_GenericType1]

      :mod-option base-class: skip-refine

   .. method:: add()

      This is a function to add a new item to a collection.

      :rtype: _GenericType1
      :mod-option rtype: skip-refine

   .. method:: clear()

      This is a function to remove all items from a collection.

   .. method:: move(src_index, dst_index)

      This is a function to move an item in a collection.

      :type src_index: int
      :mod-option arg src_index: skip-refine
      :type dst_index: int
      :mod-option arg dst_index: skip-refine

   .. method:: remove(index)

      This is a function to remove an item from a collection.

      :type index: int
      :mod-option arg index: skip-refine

.. class:: ContextTempOverride

   .. method:: __enter__()

      :rtype: typing_extensions.Self
      :mod-option rtype: skip-refine

   .. method:: __exit__(exc_type, exc_val, exc_tb)

      :type exc_type: type[BaseException] | None
      :mod-option arg exc_type: skip-refine
      :type exc_val: BaseException | None
      :mod-option arg exc_val: skip-refine
