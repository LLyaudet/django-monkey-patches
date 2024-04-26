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
To optimize some queries, you may need to add prefetches
that apply only to some of the instances.
It is very convenient when you have some expensive prefetches
that concerns only a few instances.
Hence, I added a filter_callback argument to Prefetch.
#ClimateChangeBrake
Note that I also submitted a ticket and a PR:
https://code.djangoproject.com/ticket/35317
https://github.com/django/django/pull/17994
Unfortunately, it was rejected without really considering
the true value of it.
Moreover, I had very special use cases that needed also to add
a post_prefetch_callback argument to Prefetch.
Below is the code enabling all this.
You may not see the need for such things at first.
But if you have some time, here is a redacted real world example
of its use; at work, we use Django Rest Framework,
with lots of nested serializers.
In each model serializer, I add a static method enhance_queryset()
calling the methods enhance_queryset() of the nested serializers, etc.
So compare toy examples with production work...


class OModelSerializer(...):
    @staticmethod
    def enhance_queryset(
        query_set,
        prefix: str = "",
        c_id: Optional[CId] = None,
    ):
        query_set = SomeMixin1.enhance_queryset(query_set, prefix)

        def ventilate_ps_by_c_id(
            lookup,
            done_queries,
        ):
            prefetch_to = lookup.prefetch_to
            prefetch_before = get_previous_prefetch_to(prefetch_to)
            for obj in prefetch_before:
                if hasattr(obj, "needed_ps"):
                    if not hasattr(obj, "needed_p_by"):
                        obj.needed_p_by = {}
                    for obj2 in obj.needed_ps:
                        obj.needed_p_by[obj2.c_id] = obj2

        return query_set.prefetch_related(
            f"{prefix}p2",
            Prefetch(
                f"{prefix}s",
                post_prefetch_callback=(
                  create_post_prefetch_callback_add_backward_multiple(
                    retrieve_forward_cache_callback=lambda o: (
                        [o.s]
                        if o.s_id
                        else []
                    ),
                    backward_cache_name="current_o_ancestors",
                  )
                ),
            ),
            Prefetch(
                f"{prefix}c2",
                post_prefetch_callback=(
                  create_post_prefetch_callback_add_backward_multiple(
                    retrieve_forward_cache_callback=lambda o: (
                        [o.c2]
                        if o.c2_id
                        else []
                    ),
                    backward_cache_name="current_o_ancestors",
                  )
                ),
            ),
            Prefetch(
                f"{prefix}s__ps",
                queryset=(
                    P.objects.filter(c_id=c_id)
                    if c_id
                    else P.objects.all()
                ),
                to_attr="needed_ps",
                filter_callback=lambda p: (
                    hasattr(p, "_prefetched_objects_cache")
                    and p._prefetched_objects_cache.get(
                        "current_o_ancestors"
                    )
                    and any(
                        map(
                            lambda o: o.c2_id is not None,
                            p._prefetched_objects_cache.get(
                                 "current_o_ancestors"
                            ).values(),
                        )
                    )
                ),
                post_prefetch_callback=ventilate_ps_by_c_id,
            ),
            Prefetch(
                f"{prefix}c2__u",
                queryset=C2U.objects.filter(p2_id__isnull=False)
                .distinct("c2_id")
                .prefetch_related(
                    "p2",
                    Prefetch(
                        f"p2__ps",
                        queryset=(
                            P.objects.filter(c_id=c_id)
                            if c_id
                            else P.objects.all()
                        ),
                        to_attr="needed_ps",
                        post_prefetch_callback=ventilate_ps_by_c_id,
                    ),
                ),
                to_attr="needed_u",
                filter_callback=lambda c: (
                    hasattr(c2, "_prefetched_objects_cache")
                    and c2._prefetched_objects_cache.get(
                        "current_o_ancestors"
                    )
                    and any(
                        map(
                            lambda o: o.c2_id is not None
                            and o.s_id is None,
                            c._prefetched_objects_cache.get(
                                "current_o_ancestors"
                            ).values(),
                        )
                    )
                ),
            ),
        )


class DModelSerializer(...):
    ...

    @staticmethod
    def enhance_queryset(
        query_set,
        prefix: str = "",
        c_id: Optional[CId] = None,
    ):
        query_set = SomeMixin2.enhance_queryset(
            query_set,
            f"{prefix}l__",
        )
        query_set = OModelSerializer.enhance_queryset(
            query_set,
            f"{prefix}l__",
            c_id=c_id,
        )
        query_set = query_set.prefetch_related(
            f"{prefix}l__s2",
            f"{prefix}l__p3",
            f"{prefix}l2__s3__u",
            Prefetch(
                f"{prefix}l__r1",
                queryset=R1.objects.filter(
                    d_id=F("o__s2__d_id"),
                    r2__s4=SOME_CONSTANT,
                ).select_related("r2"),
                to_attr="pertinent_r3",
            ),
        )

        return query_set

So maybe now, you understand why
I do not understand framework maintainers
that block any new feature not coming from them.
I think we don't live in code of the same complexity.
I did a second PR,
mainly because it can help (but it was rejected as usual),
and because it can help for understanding this patch,
and see that the modifications needed are only minor:
https://github.com/django/django/pull/18003
"""

import importlib

# pylint: disable-next=import-error
from django.db.models import Prefetch, query

# See exec below for the need of these imports.
# pylint: disable-next=import-error,unused-import
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


# pylint: disable-next=too-many-arguments
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
        "                lookup.post_prefetch_callback("
        "lookup, done_queries)\n",
    )
    .replace(
        "obj_list = new_obj_list",
        "obj_list = new_obj_list\n"
        "        if lookup.post_prefetch_callback:\n"
        "            lookup.post_prefetch_callback("
        "lookup, done_queries)\n",
    )
)


# local value needed for the exec
prefetch_one_level = patched_prefetch_one_level_v1

# This line is not needed;
# in fact exec below will define the variable.
# But it is clearer.
# pylint: disable-next=invalid-name
patched_prefetch_related_objects_v1 = None

# pylint: disable-next=exec-used
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


def get_previous_prefetch_to(prefetch_to):
    """
    Going one step before in the order of prefetches.
    """
    if prefetch_to == "":
        raise ValueError(
            "get_previous_prefetch_to()"
            " You're going backward too much."
        )
    prefetch_before = ""
    index = prefetch_to.rfind(LOOKUP_SEP)
    if index != -1:
        prefetch_before = prefetch_to[:index]
    return prefetch_before


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
            prefetch_to = get_previous_prefetch_to(prefetch_to)
            backward_level -= 1
        prefetch_before = get_previous_prefetch_to(prefetch_to)
        for obj in done_queries[prefetch_before]:
            if obj is None:
                continue
            forward_objects = retrieve_forward_cache_callback(obj)
            if get_key_for_backward_object_callback is None:
                key = obj.pk
            else:
                key = get_key_for_backward_object_callback(obj)
            for obj2 in forward_objects:
                if obj2 is None:
                    continue
                if not hasattr(obj2, "_prefetched_objects_cache"):
                    # pylint: disable-next=protected-access
                    obj2._prefetched_objects_cache = {}
                if (
                    # pylint: disable-next=protected-access
                    obj2._prefetched_objects_cache.get(
                        backward_cache_name
                    )
                    is None
                ):
                    # pylint: disable-next=protected-access
                    obj2._prefetched_objects_cache[
                        backward_cache_name
                    ] = {}
                # pylint: disable-next=protected-access
                obj2._prefetched_objects_cache[backward_cache_name][
                    key
                ] = obj

    return post_prefetch_callback_add_backward_multiple


e = ()  # empty_tuple


def create_retrieve_forward_cache_callback_for_foreign_key(
    f,  # field_name
):
    """
    A function to obtain a retrieve_forward_cache_callback
    corresponding to a foreign key of a Django model.
    """
    g = f + "_id"

    def retrieve_forward_cache_callback_for_foreign_key(x):
        """
        The customized retrieve_forward_cache_callback function
        that will be returned.
        """

        return e if getattr(x, g) is None else (getattr(x, f),)

    return retrieve_forward_cache_callback_for_foreign_key


def create_retrieve_forward_cache_callback_for_prefetched_objects(
    c,  # cache_name
):
    """
    A function to obtain a retrieve_forward_cache_callback
    corresponding to an entry in _prefetched_objects_cache
    of a Django model.
    """

    def retrieve_forward_cache_callback_for_prefetched_objects(x):
        """
        The customized retrieve_forward_cache_callback function
        that will be returned.
        """

        if not hasattr(x, "_prefetched_objects_cache"):
            return e

        # pylint: disable-next=protected-access
        return x._prefetched_objects_cache.get(c, e)

    return retrieve_forward_cache_callback_for_prefetched_objects
