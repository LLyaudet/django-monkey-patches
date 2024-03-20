"""
This file is part of django-monkey-patches library.

django-monkey-patches is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

django-monkey-patches is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with django-monkey-patches.
If not, see <http://www.gnu.org/licenses/>.

©Copyright 2023-2024 Laurent Lyaudet
-------------------------------------------------------------------------
To optimize some queries, you may need to add prefetches
that apply only to some of the instances.
It is very convenient when you have some expensive prefetches
that concerns only a few instances.
Hence, I added a filter_callback argument to Prefetch.
#ClimateChangeBrake
Note that I also submitted a ticket and a PR:
https://code.djangoproject.com/ticket/35317
https://github.com/django/django/pull/17994
So, we can hope for the better that future releases of Django
will have this feature,
and maybe older versions if it is backported to some.
"""

import importlib

# pylint: disable=import-error
from django.db.models import Prefetch, query

# See exec below for the need of these imports.
# pylint: disable=import-error,unused-import
from django.db.models.query import (
    LOOKUP_SEP,
    get_prefetcher,
    normalize_prefetch_lookups,
)

old_prefetch__init__ = Prefetch.__init__


def patched_prefetch__init__v1(
    self, lookup, queryset=None, to_attr=None, filter_callback=None
):
    """
    Patch for Prefetch.__init__ with filter_callback kwarg.
    """
    old_prefetch__init__(
        self, lookup, queryset=queryset, to_attr=to_attr
    )
    self.filter_callback = filter_callback


# pylint: disable=too-many-arguments
def patched_prefetch__init__v2(
    self,
    lookup,
    queryset=None,
    to_attr=None,
    filter_callback=None,
    post_prefetch_callback=None,
):
    """
    Patch for Prefetch.__init__ with filter_callback
    and post_prefetch_callback kwargs.
    """
    old_prefetch__init__(
        self, lookup, queryset=queryset, to_attr=to_attr
    )
    self.filter_callback = filter_callback
    self.post_prefetch_callback = post_prefetch_callback


old_prefetch_one_level = query.prefetch_one_level


def patched_prefetch_one_level_v1(
    instances, prefetcher, lookup, level
):
    """
    Patch for prefetch_one_level()
    applying Prefetch.filter_callback.
    """
    if lookup.filter_callback is not None:
        instances = [
            instance
            for instance in instances
            if lookup.filter_callback(instance)
        ]
    if len(instances) == 0:
        return [], ()
    return old_prefetch_one_level(
        instances, prefetcher, lookup, level
    )


def apply_patch_prefetch_with_filter_callback_v1():
    """
    Applying the patch for prefetches on subsets of instances.
    """
    Prefetch.__init__ = patched_prefetch__init__v1
    query.prefetch_one_level = patched_prefetch_one_level_v1


# Now things are starting to be amusing.
# We load the source code of the function prefetch_related_objects()
# in the installed version of Django and we patch its source code
# with string manipulations.
# First time for me in Python (not in PHP). :)
# It works with Django 2.2 and Django 5.0,
# probably also with versions in-between and after.
spec = importlib.util.find_spec("django.db.models.query", "django")
source = spec.loader.get_source("django.db.models.query")
source = source[
    source.find("def prefetch_related_objects") : source.find(
        "obj_list = new_obj_list"
    )
    + len("obj_list = new_obj_list")
]
source = (
    source.replace(
        "def prefetch_related_objects",
        "def patched_prefetch_related_objects_v1",
    )
    .replace(
        "done_queries = {}",
        'done_queries = {"": model_instances}',
    )
    .replace(
        "if lookup.prefetch_to in done_queries:",
        "if lookup.prefetch_to in done_queries:\n"
        "            if lookup.post_prefetch_callback:\n"
        "                lookup.post_prefetch_callback(lookup, done_queries)\n",
    )
    .replace(
        "obj_list = new_obj_list",
        "obj_list = new_obj_list\n"
        "        if lookup.post_prefetch_callback:\n"
        "            lookup.post_prefetch_callback(lookup, done_queries)\n",
    )
)


# local value needed for the exec
prefetch_one_level = patched_prefetch_one_level_v1

# This line is not needed;
# in fact exec below will define the variable.
# But it is clearer.
# pylint: disable=invalid-name
patched_prefetch_related_objects_v1 = None

# pylint: disable=exec-used
exec(
    source,
    globals(),
    locals(),
)


def apply_patch_prefetch_with_v2():
    """
    Applying the patch for prefetches with:
    - filter_callback,
    - post_prefetch_callback.
    """
    Prefetch.__init__ = patched_prefetch__init__v2
    query.prefetch_one_level = patched_prefetch_one_level_v1
    query.prefetch_related_objects = (
        patched_prefetch_related_objects_v1
    )


def create_post_prefetch_callback_add_backward_multiple(
    # Examples:
    # retrieve_forward_cache_callback=
    #   lambda x: [x.my_foreign_key] if x.my_foreign_key else []
    # retrieve_forward_cache_callback=
    #   lambda x: x._prefetched_objects_cache.get("toto", [])
    retrieve_forward_cache_callback,
    # backward_cache will always go
    # in x._prefetched_objects_cache as a dict
    # with a unique key to avoid repeating and the object.
    backward_cache_name,
    backward_level=0,
    # defaults to obj.pk
    get_key_for_backward_object_callback=None,
):
    """
    A function to obtain post_prefetch_callbacks
    filling backward relationships when multiple objects
    can prefetch the same object.
    Note that when the models relationships allow only
    one single object to prefetch the same object,
    then the framework already fills the backward cache.
    """

    def post_prefetch_callback_add_backward_multiple(
        lookup,
        done_queries,
    ):
        """
        The customized post_prefetch_callback function
        that will be returned.
        """
        nonlocal retrieve_forward_cache_callback
        nonlocal backward_cache_name
        nonlocal backward_level
        nonlocal get_key_for_backward_object_callback

        prefetch_to = lookup.prefetch_to
        while backward_level > 0:
            if prefetch_to == "":
                raise ValueError(
                    "post_prefetch_callback_add_backward_multiple()"
                    " You're going backward too much."
                )
            if prefetch_to.find(LOOKUP_SEP) == -1:
                raise ValueError(
                    "post_prefetch_callback_add_backward_multiple()"
                    " You're going backward too much."
                )
            prefetch_to = prefetch_to[: prefetch_to.rfind(LOOKUP_SEP)]
            backward_level -= 1
        prefetch_before = ""
        if prefetch_to.find(LOOKUP_SEP) != -1:
            prefetch_before = prefetch_to[
                : prefetch_to.rfind(LOOKUP_SEP)
            ]
        for obj in done_queries[prefetch_before]:
            forward_objects = retrieve_forward_cache_callback(obj)
            if get_key_for_backward_object_callback is None:
                key = obj.pk
            else:
                key = get_key_for_backward_object_callback(obj)
            for obj2 in forward_objects:
                # pylint: disable=protected-access
                if (
                    obj2._prefetched_objects_cache.get(
                        backward_cache_name
                    )
                    is None
                ):
                    # pylint: disable=protected-access
                    obj2._prefetched_objects_cache[
                        backward_cache_name
                    ] = {}
                # pylint: disable=protected-access
                obj2._prefetched_objects_cache[backward_cache_name][
                    key
                ] = obj

    return post_prefetch_callback_add_backward_multiple
