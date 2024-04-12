"""
This file is part of django-monkey-patches library.

django-monkey-patches is free software:
you can redistribute it and/or modify it under the terms
of the GNU Lesser General Public License
as published by the Free Software Foundation,
either version 3 of the License,
or (at your option) any later version.

django-monkey-patches is distributed in the hope
that it will be useful,
but WITHOUT ANY WARRANTY;
without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of
the GNU Lesser General Public License
along with django-monkey-patches.
If not, see <http://www.gnu.org/licenses/>.

©Copyright 2023-2024 Laurent Lyaudet
----------------------------------------------------------------------
The goal of dev_side_code files is to keep code
that should not be used
but was used to create the best code possible in some patches.
Below, is the code for micro-optimisations of
retrieve_forward_cache_callback_for_foreign_key.
"""

# pylint: disable=too-many-lines

import functools
import random
import timeit

# pylint: disable-next=invalid-name
instance_with_fk = None
# pylint: disable-next=invalid-name
instance_without_fk = None
e = ()  # empty_tuple


# l = lambda
# c = callback
# cc = create_callback
# Dict of callbacks to test
callbacks = {
    "l_field_list_list": lambda x: (
        [x.field_name] if x.field_name else []
    ),
    "l_field_id_list_list": lambda x: (
        [x.field_name] if x.field_name_id else []
    ),
    "l_field_not_none_list_list": lambda x: (
        [x.field_name] if x.field_name is not None else []
    ),
    "l_field_id_not_none_list_list": lambda x: (
        [x.field_name] if x.field_name_id is not None else []
    ),
    "l_field_none_list_list": lambda x: (
        [] if x.field_name is None else [x.field_name]
    ),
    "l_field_id_none_list_list": lambda x: (
        [] if x.field_name_id is None else [x.field_name]
    ),
    "l_field_tuple_tuple": lambda x: (
        (x.field_name,) if x.field_name else ()
    ),
    "l_field_id_tuple_tuple": lambda x: (
        (x.field_name,) if x.field_name_id else ()
    ),
    "l_field_not_none_tuple_tuple": lambda x: (
        (x.field_name,) if x.field_name is not None else ()
    ),
    "l_field_id_not_none_tuple_tuple": lambda x: (
        (x.field_name,) if x.field_name_id is not None else ()
    ),
    "l_field_none_tuple_tuple": lambda x: (
        () if x.field_name is None else (x.field_name,)
    ),
    "l_field_id_none_tuple_tuple": lambda x: (
        () if x.field_name_id is None else (x.field_name,)
    ),
    "l_field_list_tuple": lambda x: (
        [x.field_name] if x.field_name else ()
    ),
    "l_field_id_list_tuple": lambda x: (
        [x.field_name] if x.field_name_id else ()
    ),
    "l_field_not_none_list_tuple": lambda x: (
        [x.field_name] if x.field_name is not None else ()
    ),
    "l_field_id_not_none_list_tuple": lambda x: (
        [x.field_name] if x.field_name_id is not None else ()
    ),
    "l_field_none_list_tuple": lambda x: (
        () if x.field_name is None else [x.field_name]
    ),
    "l_field_id_none_list_tuple": lambda x: (
        () if x.field_name_id is None else [x.field_name]
    ),
    "l_field_tuple_list": lambda x: (
        (x.field_name,) if x.field_name else []
    ),
    "l_field_id_tuple_list": lambda x: (
        (x.field_name,) if x.field_name_id else []
    ),
    "l_field_not_none_tuple_list": lambda x: (
        (x.field_name,) if x.field_name is not None else []
    ),
    "l_field_id_not_none_tuple_list": lambda x: (
        (x.field_name,) if x.field_name_id is not None else []
    ),
    "l_field_none_tuple_list": lambda x: (
        [] if x.field_name is None else (x.field_name,)
    ),
    "l_field_id_none_tuple_list": lambda x: (
        [] if x.field_name_id is None else (x.field_name,)
    ),
    "l_field_tuple_empty": lambda x: (
        (x.field_name,) if x.field_name else e
    ),
    "l_field_id_tuple_empty": lambda x: (
        (x.field_name,) if x.field_name_id else e
    ),
    "l_field_not_none_tuple_empty": lambda x: (
        (x.field_name,) if x.field_name is not None else e
    ),
    "l_field_id_not_none_tuple_empty": lambda x: (
        (x.field_name,) if x.field_name_id is not None else e
    ),
    "l_field_none_tuple_empty": lambda x: (
        e if x.field_name is None else (x.field_name,)
    ),
    "l_field_id_none_tuple_empty": lambda x: (
        e if x.field_name_id is None else (x.field_name,)
    ),
    "l_field_list_empty": lambda x: (
        [x.field_name] if x.field_name else e
    ),
    "l_field_id_list_empty": lambda x: (
        [x.field_name] if x.field_name_id else e
    ),
    "l_field_not_none_list_empty": lambda x: (
        [x.field_name] if x.field_name is not None else e
    ),
    "l_field_id_not_none_list_empty": lambda x: (
        [x.field_name] if x.field_name_id is not None else e
    ),
    "l_field_none_list_empty": lambda x: (
        e if x.field_name is None else [x.field_name]
    ),
    "l_field_id_none_list_empty": lambda x: (
        e if x.field_name_id is None else [x.field_name]
    ),
}


def cc_field_list_list(f):
    """
    A function to obtain a c_field_list_list.
    """

    def c_field_list_list(x):
        """
        The customized c_field_list_list.
        """
        nonlocal f

        return [getattr(x, f)] if getattr(x, f) else []

    return c_field_list_list


def cc_field_id_list_list(f):
    """
    A function to obtain a c_field_id_list_list.
    """
    g = f + "_id"

    def c_field_id_list_list(x):
        """
        The customized c_field_id_list_list.
        """
        nonlocal f
        nonlocal g

        return [getattr(x, f)] if getattr(x, g) else []

    return c_field_id_list_list


def cc_field_not_none_list_list(f):
    """
    A function to obtain a c_field_not_none_list_list.
    """

    def c_field_not_none_list_list(x):
        """
        The customized c_field_not_none_list_list.
        """
        nonlocal f

        return [getattr(x, f)] if getattr(x, f) is not None else []

    return c_field_not_none_list_list


def cc_field_id_not_none_list_list(f):
    """
    A function to obtain a c_field_id_not_none_list_list.
    """
    g = f + "_id"

    def c_field_id_not_none_list_list(x):
        """
        The customized c_field_id_not_none_list_list.
        """
        nonlocal f
        nonlocal g

        return [getattr(x, f)] if getattr(x, g) is not None else []

    return c_field_id_not_none_list_list


def cc_field_none_list_list(f):
    """
    A function to obtain a c_field_none_list_list.
    """

    def c_field_none_list_list(x):
        """
        The customized c_field_none_list_list.
        """
        nonlocal f

        return [] if getattr(x, f) is None else [getattr(x, f)]

    return c_field_none_list_list


def cc_field_id_none_list_list(f):
    """
    A function to obtain a c_field_id_none_list_list.
    """
    g = f + "_id"

    def c_field_id_none_list_list(x):
        """
        The customized c_field_id_none_list_list.
        """
        nonlocal f
        nonlocal g

        return [] if getattr(x, g) is None else [getattr(x, f)]

    return c_field_id_none_list_list


def cc_field_tuple_tuple(f):
    """
    A function to obtain a c_field_tuple_tuple.
    """

    def c_field_tuple_tuple(x):
        """
        The customized c_field_tuple_tuple.
        """
        nonlocal f

        return (getattr(x, f),) if getattr(x, f) else ()

    return c_field_tuple_tuple


def cc_field_id_tuple_tuple(f):
    """
    A function to obtain a c_field_id_tuple_tuple.
    """
    g = f + "_id"

    def c_field_id_tuple_tuple(x):
        """
        The customized c_field_id_tuple_tuple.
        """
        nonlocal f
        nonlocal g

        return (getattr(x, f),) if getattr(x, g) else ()

    return c_field_id_tuple_tuple


def cc_field_not_none_tuple_tuple(f):
    """
    A function to obtain a c_field_not_none_tuple_tuple.
    """

    def c_field_not_none_tuple_tuple(x):
        """
        The customized c_field_not_none_tuple_tuple.
        """
        nonlocal f

        return (getattr(x, f),) if getattr(x, f) is not None else ()

    return c_field_not_none_tuple_tuple


def cc_field_id_not_none_tuple_tuple(f):
    """
    A function to obtain a c_field_id_not_none_tuple_tuple.
    """
    g = f + "_id"

    def c_field_id_not_none_tuple_tuple(x):
        """
        The customized c_field_id_not_none_tuple_tuple.
        """
        nonlocal f
        nonlocal g

        return (getattr(x, f),) if getattr(x, g) is not None else ()

    return c_field_id_not_none_tuple_tuple


def cc_field_none_tuple_tuple(f):
    """
    A function to obtain a c_field_none_tuple_tuple.
    """

    def c_field_none_tuple_tuple(x):
        """
        The customized c_field_none_tuple_tuple.
        """
        nonlocal f

        return () if getattr(x, f) is None else (getattr(x, f),)

    return c_field_none_tuple_tuple


def cc_field_id_none_tuple_tuple(f):
    """
    A function to obtain a c_field_id_none_tuple_tuple.
    """
    g = f + "_id"

    def c_field_id_none_tuple_tuple(x):
        """
        The customized c_field_id_none_tuple_tuple.
        """
        nonlocal f
        nonlocal g

        return () if getattr(x, g) is None else (getattr(x, f),)

    return c_field_id_none_tuple_tuple


def cc_field_list_tuple(f):
    """
    A function to obtain a c_field_list_tuple.
    """

    def c_field_list_tuple(x):
        """
        The customized c_field_list_tuple.
        """
        nonlocal f

        return [getattr(x, f)] if getattr(x, f) else ()

    return c_field_list_tuple


def cc_field_id_list_tuple(f):
    """
    A function to obtain a c_field_id_list_tuple.
    """
    g = f + "_id"

    def c_field_id_list_tuple(x):
        """
        The customized c_field_id_list_tuple.
        """
        nonlocal f
        nonlocal g

        return [getattr(x, f)] if getattr(x, g) else ()

    return c_field_id_list_tuple


def cc_field_not_none_list_tuple(f):
    """
    A function to obtain a c_field_not_none_list_tuple.
    """

    def c_field_not_none_list_tuple(x):
        """
        The customized c_field_not_none_list_tuple.
        """
        nonlocal f

        return [getattr(x, f)] if getattr(x, f) is not None else ()

    return c_field_not_none_list_tuple


def cc_field_id_not_none_list_tuple(f):
    """
    A function to obtain a c_field_id_not_none_list_tuple.
    """
    g = f + "_id"

    def c_field_id_not_none_list_tuple(x):
        """
        The customized c_field_id_not_none_list_tuple.
        """
        nonlocal f
        nonlocal g

        return [getattr(x, f)] if getattr(x, g) is not None else ()

    return c_field_id_not_none_list_tuple


def cc_field_none_list_tuple(f):
    """
    A function to obtain a c_field_none_list_tuple.
    """

    def c_field_none_list_tuple(x):
        """
        The customized c_field_none_list_tuple.
        """
        nonlocal f

        return () if getattr(x, f) is None else [getattr(x, f)]

    return c_field_none_list_tuple


def cc_field_id_none_list_tuple(f):
    """
    A function to obtain a c_field_id_none_list_tuple.
    """
    g = f + "_id"

    def c_field_id_none_list_tuple(x):
        """
        The customized c_field_id_none_list_tuple.
        """
        nonlocal f
        nonlocal g

        return () if getattr(x, g) is None else [getattr(x, f)]

    return c_field_id_none_list_tuple


def cc_field_tuple_list(f):
    """
    A function to obtain a c_field_tuple_list.
    """

    def c_field_tuple_list(x):
        """
        The customized c_field_tuple_list.
        """
        nonlocal f

        return (getattr(x, f),) if getattr(x, f) else []

    return c_field_tuple_list


def cc_field_id_tuple_list(f):
    """
    A function to obtain a c_field_id_tuple_list.
    """
    g = f + "_id"

    def c_field_id_tuple_list(x):
        """
        The customized c_field_id_tuple_list.
        """
        nonlocal f
        nonlocal g

        return (getattr(x, f),) if getattr(x, g) else []

    return c_field_id_tuple_list


def cc_field_not_none_tuple_list(f):
    """
    A function to obtain a c_field_not_none_tuple_list.
    """

    def c_field_not_none_tuple_list(x):
        """
        The customized c_field_not_none_tuple_list.
        """
        nonlocal f

        return (getattr(x, f),) if getattr(x, f) is not None else []

    return c_field_not_none_tuple_list


def cc_field_id_not_none_tuple_list(f):
    """
    A function to obtain a c_field_id_not_none_tuple_list.
    """
    g = f + "_id"

    def c_field_id_not_none_tuple_list(x):
        """
        The customized c_field_id_not_none_tuple_list.
        """
        nonlocal f
        nonlocal g

        return (getattr(x, f),) if getattr(x, g) is not None else []

    return c_field_id_not_none_tuple_list


def cc_field_none_tuple_list(f):
    """
    A function to obtain a c_field_none_tuple_list.
    """

    def c_field_none_tuple_list(x):
        """
        The customized c_field_none_tuple_list.
        """
        nonlocal f

        return [] if getattr(x, f) is None else (getattr(x, f),)

    return c_field_none_tuple_list


def cc_field_id_none_tuple_list(f):
    """
    A function to obtain a c_field_id_none_tuple_list.
    """
    g = f + "_id"

    def c_field_id_none_tuple_list(x):
        """
        The customized c_field_id_none_tuple_list.
        """
        nonlocal f
        nonlocal g

        return [] if getattr(x, g) is None else (getattr(x, f),)

    return c_field_id_none_tuple_list


def cc_field_tuple_empty(f):
    """
    A function to obtain a c_field_tuple_empty.
    """

    def c_field_tuple_empty(x):
        """
        The customized c_field_tuple_empty.
        """
        nonlocal f

        return (getattr(x, f),) if getattr(x, f) else e

    return c_field_tuple_empty


def cc_field_id_tuple_empty(f):
    """
    A function to obtain a c_field_id_tuple_empty.
    """
    g = f + "_id"

    def c_field_id_tuple_empty(x):
        """
        The customized c_field_id_tuple_empty.
        """
        nonlocal f
        nonlocal g

        return (getattr(x, f),) if getattr(x, g) else e

    return c_field_id_tuple_empty


def cc_field_not_none_tuple_empty(f):
    """
    A function to obtain a c_field_not_none_tuple_empty.
    """

    def c_field_not_none_tuple_empty(x):
        """
        The customized c_field_not_none_tuple_empty.
        """
        nonlocal f

        return (getattr(x, f),) if getattr(x, f) is not None else e

    return c_field_not_none_tuple_empty


def cc_field_id_not_none_tuple_empty(f):
    """
    A function to obtain a c_field_id_not_none_tuple_empty.
    """
    g = f + "_id"

    def c_field_id_not_none_tuple_empty(x):
        """
        The customized c_field_id_not_none_tuple_empty.
        """
        nonlocal f
        nonlocal g

        return (getattr(x, f),) if getattr(x, g) is not None else e

    return c_field_id_not_none_tuple_empty


def cc_field_none_tuple_empty(f):
    """
    A function to obtain a c_field_none_tuple_empty.
    """

    def c_field_none_tuple_empty(x):
        """
        The customized c_field_none_tuple_empty.
        """
        nonlocal f

        return e if getattr(x, f) is None else (getattr(x, f),)

    return c_field_none_tuple_empty


def cc_field_id_none_tuple_empty(f):
    """
    A function to obtain a c_field_id_none_tuple_empty.
    """
    g = f + "_id"

    def c_field_id_none_tuple_empty(x):
        """
        The customized c_field_id_none_tuple_empty.
        """
        nonlocal f
        nonlocal g

        return e if getattr(x, g) is None else (getattr(x, f),)

    return c_field_id_none_tuple_empty


def cc_field_list_empty(f):
    """
    A function to obtain a c_field_list_empty.
    """

    def c_field_list_empty(x):
        """
        The customized c_field_list_empty.
        """
        nonlocal f

        return [getattr(x, f)] if getattr(x, f) else e

    return c_field_list_empty


def cc_field_id_list_empty(f):
    """
    A function to obtain a c_field_id_list_empty.
    """
    g = f + "_id"

    def c_field_id_list_empty(x):
        """
        The customized c_field_id_list_empty.
        """
        nonlocal f
        nonlocal g

        return [getattr(x, f)] if getattr(x, g) else e

    return c_field_id_list_empty


def cc_field_not_none_list_empty(f):
    """
    A function to obtain a c_field_not_none_list_empty.
    """

    def c_field_not_none_list_empty(x):
        """
        The customized c_field_not_none_list_empty.
        """
        nonlocal f

        return [getattr(x, f)] if getattr(x, f) is not None else e

    return c_field_not_none_list_empty


def cc_field_id_not_none_list_empty(f):
    """
    A function to obtain a c_field_id_not_none_list_empty.
    """
    g = f + "_id"

    def c_field_id_not_none_list_empty(x):
        """
        The customized c_field_id_not_none_list_empty.
        """
        nonlocal f
        nonlocal g

        return [getattr(x, f)] if getattr(x, g) is not None else e

    return c_field_id_not_none_list_empty


def cc_field_none_list_empty(f):
    """
    A function to obtain a c_field_none_list_empty.
    """

    def c_field_none_list_empty(x):
        """
        The customized c_field_none_list_empty.
        """
        nonlocal f

        return e if getattr(x, f) is None else [getattr(x, f)]

    return c_field_none_list_empty


def cc_field_id_none_list_empty(f):
    """
    A function to obtain a c_field_id_none_list_empty.
    """
    g = f + "_id"

    def c_field_id_none_list_empty(x):
        """
        The customized c_field_id_none_list_empty.
        """
        nonlocal f
        nonlocal g

        return e if getattr(x, g) is None else [getattr(x, f)]

    return c_field_id_none_list_empty


def cc_field_list_list_nnl(f):
    """
    A function to obtain a c_field_list_list_nnl.
    """

    def c_field_list_list_nnl(x):
        """
        The customized c_field_list_list_nnl.
        """

        return [getattr(x, f)] if getattr(x, f) else []

    return c_field_list_list_nnl


def cc_field_id_list_list_nnl(f):
    """
    A function to obtain a c_field_id_list_list_nnl.
    """
    g = f + "_id"

    def c_field_id_list_list_nnl(x):
        """
        The customized c_field_id_list_list_nnl.
        """

        return [getattr(x, f)] if getattr(x, g) else []

    return c_field_id_list_list_nnl


def cc_field_not_none_list_list_nnl(f):
    """
    A function to obtain a c_field_not_none_list_list_nnl.
    """

    def c_field_not_none_list_list_nnl(x):
        """
        The customized c_field_not_none_list_list_nnl.
        """

        return [getattr(x, f)] if getattr(x, f) is not None else []

    return c_field_not_none_list_list_nnl


def cc_field_id_not_none_list_list_nnl(f):
    """
    A function to obtain a c_field_id_not_none_list_list_nnl.
    """
    g = f + "_id"

    def c_field_id_not_none_list_list_nnl(x):
        """
        The customized c_field_id_not_none_list_list_nnl.
        """

        return [getattr(x, f)] if getattr(x, g) is not None else []

    return c_field_id_not_none_list_list_nnl


def cc_field_none_list_list_nnl(f):
    """
    A function to obtain a c_field_none_list_list_nnl.
    """

    def c_field_none_list_list_nnl(x):
        """
        The customized c_field_none_list_list_nnl.
        """

        return [] if getattr(x, f) is None else [getattr(x, f)]

    return c_field_none_list_list_nnl


def cc_field_id_none_list_list_nnl(f):
    """
    A function to obtain a c_field_id_none_list_list_nnl.
    """
    g = f + "_id"

    def c_field_id_none_list_list_nnl(x):
        """
        The customized c_field_id_none_list_list_nnl.
        """

        return [] if getattr(x, g) is None else [getattr(x, f)]

    return c_field_id_none_list_list_nnl


def cc_field_tuple_tuple_nnl(f):
    """
    A function to obtain a c_field_tuple_tuple_nnl.
    """

    def c_field_tuple_tuple_nnl(x):
        """
        The customized c_field_tuple_tuple_nnl.
        """

        return (getattr(x, f),) if getattr(x, f) else ()

    return c_field_tuple_tuple_nnl


def cc_field_id_tuple_tuple_nnl(f):
    """
    A function to obtain a c_field_id_tuple_tuple_nnl.
    """
    g = f + "_id"

    def c_field_id_tuple_tuple_nnl(x):
        """
        The customized c_field_id_tuple_tuple_nnl.
        """

        return (getattr(x, f),) if getattr(x, g) else ()

    return c_field_id_tuple_tuple_nnl


def cc_field_not_none_tuple_tuple_nnl(f):
    """
    A function to obtain a c_field_not_none_tuple_tuple_nnl.
    """

    def c_field_not_none_tuple_tuple_nnl(x):
        """
        The customized c_field_not_none_tuple_tuple_nnl.
        """

        return (getattr(x, f),) if getattr(x, f) is not None else ()

    return c_field_not_none_tuple_tuple_nnl


def cc_field_id_not_none_tuple_tuple_nnl(f):
    """
    A function to obtain a c_field_id_not_none_tuple_tuple_nnl.
    """
    g = f + "_id"

    def c_field_id_not_none_tuple_tuple_nnl(x):
        """
        The customized c_field_id_not_none_tuple_tuple_nnl.
        """

        return (getattr(x, f),) if getattr(x, g) is not None else ()

    return c_field_id_not_none_tuple_tuple_nnl


def cc_field_none_tuple_tuple_nnl(f):
    """
    A function to obtain a c_field_none_tuple_tuple_nnl.
    """

    def c_field_none_tuple_tuple_nnl(x):
        """
        The customized c_field_none_tuple_tuple_nnl.
        """

        return () if getattr(x, f) is None else (getattr(x, f),)

    return c_field_none_tuple_tuple_nnl


def cc_field_id_none_tuple_tuple_nnl(f):
    """
    A function to obtain a c_field_id_none_tuple_tuple_nnl.
    """
    g = f + "_id"

    def c_field_id_none_tuple_tuple_nnl(x):
        """
        The customized c_field_id_none_tuple_tuple_nnl.
        """

        return () if getattr(x, g) is None else (getattr(x, f),)

    return c_field_id_none_tuple_tuple_nnl


def cc_field_list_tuple_nnl(f):
    """
    A function to obtain a c_field_list_tuple_nnl.
    """

    def c_field_list_tuple_nnl(x):
        """
        The customized c_field_list_tuple_nnl.
        """

        return [getattr(x, f)] if getattr(x, f) else ()

    return c_field_list_tuple_nnl


def cc_field_id_list_tuple_nnl(f):
    """
    A function to obtain a c_field_id_list_tuple_nnl.
    """
    g = f + "_id"

    def c_field_id_list_tuple_nnl(x):
        """
        The customized c_field_id_list_tuple_nnl.
        """

        return [getattr(x, f)] if getattr(x, g) else ()

    return c_field_id_list_tuple_nnl


def cc_field_not_none_list_tuple_nnl(f):
    """
    A function to obtain a c_field_not_none_list_tuple_nnl.
    """

    def c_field_not_none_list_tuple_nnl(x):
        """
        The customized c_field_not_none_list_tuple_nnl.
        """

        return [getattr(x, f)] if getattr(x, f) is not None else ()

    return c_field_not_none_list_tuple_nnl


def cc_field_id_not_none_list_tuple_nnl(f):
    """
    A function to obtain a c_field_id_not_none_list_tuple_nnl.
    """
    g = f + "_id"

    def c_field_id_not_none_list_tuple_nnl(x):
        """
        The customized c_field_id_not_none_list_tuple_nnl.
        """

        return [getattr(x, f)] if getattr(x, g) is not None else ()

    return c_field_id_not_none_list_tuple_nnl


def cc_field_none_list_tuple_nnl(f):
    """
    A function to obtain a c_field_none_list_tuple_nnl.
    """

    def c_field_none_list_tuple_nnl(x):
        """
        The customized c_field_none_list_tuple_nnl.
        """

        return () if getattr(x, f) is None else [getattr(x, f)]

    return c_field_none_list_tuple_nnl


def cc_field_id_none_list_tuple_nnl(f):
    """
    A function to obtain a c_field_id_none_list_tuple_nnl.
    """
    g = f + "_id"

    def c_field_id_none_list_tuple_nnl(x):
        """
        The customized c_field_id_none_list_tuple_nnl.
        """

        return () if getattr(x, g) is None else [getattr(x, f)]

    return c_field_id_none_list_tuple_nnl


def cc_field_tuple_list_nnl(f):
    """
    A function to obtain a c_field_tuple_list_nnl.
    """

    def c_field_tuple_list_nnl(x):
        """
        The customized c_field_tuple_list_nnl.
        """

        return (getattr(x, f),) if getattr(x, f) else []

    return c_field_tuple_list_nnl


def cc_field_id_tuple_list_nnl(f):
    """
    A function to obtain a c_field_id_tuple_list_nnl.
    """
    g = f + "_id"

    def c_field_id_tuple_list_nnl(x):
        """
        The customized c_field_id_tuple_list_nnl.
        """

        return (getattr(x, f),) if getattr(x, g) else []

    return c_field_id_tuple_list_nnl


def cc_field_not_none_tuple_list_nnl(f):
    """
    A function to obtain a c_field_not_none_tuple_list_nnl.
    """

    def c_field_not_none_tuple_list_nnl(x):
        """
        The customized c_field_not_none_tuple_list_nnl.
        """

        return (getattr(x, f),) if getattr(x, f) is not None else []

    return c_field_not_none_tuple_list_nnl


def cc_field_id_not_none_tuple_list_nnl(f):
    """
    A function to obtain a c_field_id_not_none_tuple_list_nnl.
    """
    g = f + "_id"

    def c_field_id_not_none_tuple_list_nnl(x):
        """
        The customized c_field_id_not_none_tuple_list_nnl.
        """

        return (getattr(x, f),) if getattr(x, g) is not None else []

    return c_field_id_not_none_tuple_list_nnl


def cc_field_none_tuple_list_nnl(f):
    """
    A function to obtain a c_field_none_tuple_list_nnl.
    """

    def c_field_none_tuple_list_nnl(x):
        """
        The customized c_field_none_tuple_list_nnl.
        """

        return [] if getattr(x, f) is None else (getattr(x, f),)

    return c_field_none_tuple_list_nnl


def cc_field_id_none_tuple_list_nnl(f):
    """
    A function to obtain a c_field_id_none_tuple_list_nnl.
    """
    g = f + "_id"

    def c_field_id_none_tuple_list_nnl(x):
        """
        The customized c_field_id_none_tuple_list_nnl.
        """

        return [] if getattr(x, g) is None else (getattr(x, f),)

    return c_field_id_none_tuple_list_nnl


def cc_field_tuple_empty_nnl(f):
    """
    A function to obtain a c_field_tuple_empty_nnl.
    """

    def c_field_tuple_empty_nnl(x):
        """
        The customized c_field_tuple_empty_nnl.
        """

        return (getattr(x, f),) if getattr(x, f) else e

    return c_field_tuple_empty_nnl


def cc_field_id_tuple_empty_nnl(f):
    """
    A function to obtain a c_field_id_tuple_empty_nnl.
    """
    g = f + "_id"

    def c_field_id_tuple_empty_nnl(x):
        """
        The customized c_field_id_tuple_empty_nnl.
        """

        return (getattr(x, f),) if getattr(x, g) else e

    return c_field_id_tuple_empty_nnl


def cc_field_not_none_tuple_empty_nnl(f):
    """
    A function to obtain a c_field_not_none_tuple_empty_nnl.
    """

    def c_field_not_none_tuple_empty_nnl(x):
        """
        The customized c_field_not_none_tuple_empty_nnl.
        """

        return (getattr(x, f),) if getattr(x, f) is not None else e

    return c_field_not_none_tuple_empty_nnl


def cc_field_id_not_none_tuple_empty_nnl(f):
    """
    A function to obtain a c_field_id_not_none_tuple_empty_nnl.
    """
    g = f + "_id"

    def c_field_id_not_none_tuple_empty_nnl(x):
        """
        The customized c_field_id_not_none_tuple_empty_nnl.
        """

        return (getattr(x, f),) if getattr(x, g) is not None else e

    return c_field_id_not_none_tuple_empty_nnl


def cc_field_none_tuple_empty_nnl(f):
    """
    A function to obtain a c_field_none_tuple_empty_nnl.
    """

    def c_field_none_tuple_empty_nnl(x):
        """
        The customized c_field_none_tuple_empty_nnl.
        """

        return e if getattr(x, f) is None else (getattr(x, f),)

    return c_field_none_tuple_empty_nnl


def cc_field_id_none_tuple_empty_nnl(f):
    """
    A function to obtain a c_field_id_none_tuple_empty_nnl.
    """
    g = f + "_id"

    def c_field_id_none_tuple_empty_nnl(x):
        """
        The customized c_field_id_none_tuple_empty_nnl.
        """

        return e if getattr(x, g) is None else (getattr(x, f),)

    return c_field_id_none_tuple_empty_nnl


def cc_field_list_empty_nnl(f):
    """
    A function to obtain a c_field_list_empty_nnl.
    """

    def c_field_list_empty_nnl(x):
        """
        The customized c_field_list_empty_nnl.
        """

        return [getattr(x, f)] if getattr(x, f) else e

    return c_field_list_empty_nnl


def cc_field_id_list_empty_nnl(f):
    """
    A function to obtain a c_field_id_list_empty_nnl.
    """
    g = f + "_id"

    def c_field_id_list_empty_nnl(x):
        """
        The customized c_field_id_list_empty_nnl.
        """

        return [getattr(x, f)] if getattr(x, g) else e

    return c_field_id_list_empty_nnl


def cc_field_not_none_list_empty_nnl(f):
    """
    A function to obtain a c_field_not_none_list_empty_nnl.
    """

    def c_field_not_none_list_empty_nnl(x):
        """
        The customized c_field_not_none_list_empty_nnl.
        """

        return [getattr(x, f)] if getattr(x, f) is not None else e

    return c_field_not_none_list_empty_nnl


def cc_field_id_not_none_list_empty_nnl(f):
    """
    A function to obtain a c_field_id_not_none_list_empty_nnl.
    """
    g = f + "_id"

    def c_field_id_not_none_list_empty_nnl(x):
        """
        The customized c_field_id_not_none_list_empty_nnl.
        """

        return [getattr(x, f)] if getattr(x, g) is not None else e

    return c_field_id_not_none_list_empty_nnl


def cc_field_none_list_empty_nnl(f):
    """
    A function to obtain a c_field_none_list_empty_nnl.
    """

    def c_field_none_list_empty_nnl(x):
        """
        The customized c_field_none_list_empty_nnl.
        """

        return e if getattr(x, f) is None else [getattr(x, f)]

    return c_field_none_list_empty_nnl


def cc_field_id_none_list_empty_nnl(f):
    """
    A function to obtain a c_field_id_none_list_empty_nnl.
    """
    g = f + "_id"

    def c_field_id_none_list_empty_nnl(x):
        """
        The customized c_field_id_none_list_empty_nnl.
        """

        return e if getattr(x, g) is None else [getattr(x, f)]

    return c_field_id_none_list_empty_nnl


callbacks.update(
    {
        "c_field_list_list": cc_field_list_list("field_name"),
        "c_field_id_list_list": cc_field_id_list_list("field_name"),
        "c_field_not_none_list_list": cc_field_not_none_list_list(
            "field_name"
        ),
        "c_field_id_not_none_list_list": (
            cc_field_id_not_none_list_list("field_name")
        ),
        "c_field_none_list_list": cc_field_none_list_list(
            "field_name"
        ),
        "c_field_id_none_list_list": cc_field_id_none_list_list(
            "field_name"
        ),
        "c_field_tuple_tuple": cc_field_tuple_tuple("field_name"),
        "c_field_id_tuple_tuple": cc_field_id_tuple_tuple(
            "field_name"
        ),
        "c_field_not_none_tuple_tuple": cc_field_not_none_tuple_tuple(
            "field_name"
        ),
        "c_field_id_not_none_tuple_tuple": (
            cc_field_id_not_none_tuple_tuple("field_name")
        ),
        "c_field_none_tuple_tuple": cc_field_none_tuple_tuple(
            "field_name"
        ),
        "c_field_id_none_tuple_tuple": cc_field_id_none_tuple_tuple(
            "field_name"
        ),
        "c_field_list_tuple": cc_field_list_tuple("field_name"),
        "c_field_id_list_tuple": cc_field_id_list_tuple("field_name"),
        "c_field_not_none_list_tuple": cc_field_not_none_list_tuple(
            "field_name"
        ),
        "c_field_id_not_none_list_tuple": (
            cc_field_id_not_none_list_tuple("field_name")
        ),
        "c_field_none_list_tuple": cc_field_none_list_tuple(
            "field_name"
        ),
        "c_field_id_none_list_tuple": cc_field_id_none_list_tuple(
            "field_name"
        ),
        "c_field_tuple_list": cc_field_tuple_list("field_name"),
        "c_field_id_tuple_list": cc_field_id_tuple_list("field_name"),
        "c_field_not_none_tuple_list": cc_field_not_none_tuple_list(
            "field_name"
        ),
        "c_field_id_not_none_tuple_list": (
            cc_field_id_not_none_tuple_list("field_name")
        ),
        "c_field_none_tuple_list": cc_field_none_tuple_list(
            "field_name"
        ),
        "c_field_id_none_tuple_list": cc_field_id_none_tuple_list(
            "field_name"
        ),
        "c_field_tuple_empty": cc_field_tuple_empty("field_name"),
        "c_field_id_tuple_empty": cc_field_id_tuple_empty(
            "field_name"
        ),
        "c_field_not_none_tuple_empty": cc_field_not_none_tuple_empty(
            "field_name"
        ),
        "c_field_id_not_none_tuple_empty": (
            cc_field_id_not_none_tuple_empty("field_name")
        ),
        "c_field_none_tuple_empty": cc_field_none_tuple_empty(
            "field_name"
        ),
        "c_field_id_none_tuple_empty": cc_field_id_none_tuple_empty(
            "field_name"
        ),
        "c_field_list_empty": cc_field_list_empty("field_name"),
        "c_field_id_list_empty": cc_field_id_list_empty("field_name"),
        "c_field_not_none_list_empty": cc_field_not_none_list_empty(
            "field_name"
        ),
        "c_field_id_not_none_list_empty": (
            cc_field_id_not_none_list_empty("field_name")
        ),
        "c_field_none_list_empty": cc_field_none_list_empty(
            "field_name"
        ),
        "c_field_id_none_list_empty": cc_field_id_none_list_empty(
            "field_name"
        ),
        "c_field_list_list_nnl": cc_field_list_list_nnl("field_name"),
        "c_field_id_list_list_nnl": cc_field_id_list_list_nnl(
            "field_name"
        ),
        "c_field_not_none_list_list_nnl": (
            cc_field_not_none_list_list_nnl("field_name")
        ),
        "c_field_id_not_none_list_list_nnl": (
            cc_field_id_not_none_list_list_nnl("field_name")
        ),
        "c_field_none_list_list_nnl": cc_field_none_list_list_nnl(
            "field_name"
        ),
        "c_field_id_none_list_list_nnl": (
            cc_field_id_none_list_list_nnl("field_name")
        ),
        "c_field_tuple_tuple_nnl": cc_field_tuple_tuple_nnl(
            "field_name"
        ),
        "c_field_id_tuple_tuple_nnl": cc_field_id_tuple_tuple_nnl(
            "field_name"
        ),
        "c_field_not_none_tuple_tuple_nnl": (
            cc_field_not_none_tuple_tuple_nnl("field_name")
        ),
        "c_field_id_not_none_tuple_tuple_nnl": (
            cc_field_id_not_none_tuple_tuple_nnl("field_name")
        ),
        "c_field_none_tuple_tuple_nnl": (
            cc_field_none_tuple_tuple_nnl("field_name")
        ),
        "c_field_id_none_tuple_tuple_nnl": (
            cc_field_id_none_tuple_tuple_nnl("field_name")
        ),
        "c_field_list_tuple_nnl": (
            cc_field_list_tuple_nnl("field_name")
        ),
        "c_field_id_list_tuple_nnl": cc_field_id_list_tuple_nnl(
            "field_name"
        ),
        "c_field_not_none_list_tuple_nnl": (
            cc_field_not_none_list_tuple_nnl("field_name")
        ),
        "c_field_id_not_none_list_tuple_nnl": (
            cc_field_id_not_none_list_tuple_nnl("field_name")
        ),
        "c_field_none_list_tuple_nnl": cc_field_none_list_tuple_nnl(
            "field_name"
        ),
        "c_field_id_none_list_tuple_nnl": (
            cc_field_id_none_list_tuple_nnl("field_name")
        ),
        "c_field_tuple_list_nnl": cc_field_tuple_list_nnl(
            "field_name"
        ),
        "c_field_id_tuple_list_nnl": cc_field_id_tuple_list_nnl(
            "field_name"
        ),
        "c_field_not_none_tuple_list_nnl": (
            cc_field_not_none_tuple_list_nnl("field_name")
        ),
        "c_field_id_not_none_tuple_list_nnl": (
            cc_field_id_not_none_tuple_list_nnl("field_name")
        ),
        "c_field_none_tuple_list_nnl": cc_field_none_tuple_list_nnl(
            "field_name"
        ),
        "c_field_id_none_tuple_list_nnl": (
            cc_field_id_none_tuple_list_nnl("field_name")
        ),
        "c_field_tuple_empty_nnl": cc_field_tuple_empty_nnl(
            "field_name"
        ),
        "c_field_id_tuple_empty_nnl": cc_field_id_tuple_empty_nnl(
            "field_name"
        ),
        "c_field_not_none_tuple_empty_nnl": (
            cc_field_not_none_tuple_empty_nnl("field_name")
        ),
        "c_field_id_not_none_tuple_empty_nnl": (
            cc_field_id_not_none_tuple_empty_nnl("field_name")
        ),
        "c_field_none_tuple_empty_nnl": cc_field_none_tuple_empty_nnl(
            "field_name"
        ),
        "c_field_id_none_tuple_empty_nnl": (
            cc_field_id_none_tuple_empty_nnl("field_name")
        ),
        "c_field_list_empty_nnl": cc_field_list_empty_nnl(
            "field_name"
        ),
        "c_field_id_list_empty_nnl": cc_field_id_list_empty_nnl(
            "field_name"
        ),
        "c_field_not_none_list_empty_nnl": (
            cc_field_not_none_list_empty_nnl("field_name")
        ),
        "c_field_id_not_none_list_empty_nnl": (
            cc_field_id_not_none_list_empty_nnl("field_name")
        ),
        "c_field_none_list_empty_nnl": cc_field_none_list_empty_nnl(
            "field_name"
        ),
        "c_field_id_none_list_empty_nnl": (
            cc_field_id_none_list_empty_nnl("field_name")
        ),
    }
)

NUMBER_OF_ITERATIONS = 1000000


def benchmark(callbacks_to_benchmark):
    """
    Benchmark all the callbacks in the argument dict.
    """

    result = []
    for name, callback in callbacks_to_benchmark.items():
        time_with_fk = timeit.timeit(
            functools.partial(callback, instance_with_fk),
            number=NUMBER_OF_ITERATIONS,
        )
        time_without_fk = timeit.timeit(
            functools.partial(callback, instance_without_fk),
            number=NUMBER_OF_ITERATIONS,
        )
        result.append(
            {
                "name": name,
                "time_with_fk": time_with_fk,
                "time_without_fk": time_without_fk,
            }
        )
    result.sort(key=lambda x: x["time_without_fk"])
    result.sort(key=lambda x: x["time_with_fk"])
    for data in result:
        print(
            f"{data['name']}:"
            f" Avec FK: {data['time_with_fk']},"
            f" Sans FK: {data['time_without_fk']}"
        )


# Benchmark each callback.
benchmark(callbacks)

print("-------------------------------------------------------------")

# Benchmark each callback in random order.
keys = list(callbacks.keys())
random.shuffle(keys)
callbacks_2 = {key: callbacks[key] for key in keys}
benchmark(callbacks_2)
