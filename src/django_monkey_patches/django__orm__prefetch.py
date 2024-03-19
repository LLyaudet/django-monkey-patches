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

from django.db.models import Prefetch, query

old_prefetch__init__ = Prefetch.__init__


def patched_prefetch__init__v1(
    self, lookup, queryset=None, to_attr=None, filter_callback=None
):
    result = old_prefetch__init__(self, lookup, queryset=queryset, to_attr=to_attr)
    self.filter_callback = filter_callback
    return result


old_prefetch_one_level = query.prefetch_one_level


def patched_prefetch_one_level_v1(instances, prefetcher, lookup, level):
    if lookup.filter_callback is not None:
        instances = [
            instance for instance in instances if lookup.filter_callback(instance)
        ]
    if len(instances) == 0:
        return [], ()
    return old_prefetch_one_level(instances, prefetcher, lookup, level)


query.prefetch_one_level = new_prefetch_one_level


def apply_patch_prefetch_with_filter_callback_v1():
    Prefetch.__init__ = patched_prefetch__init__v1
    query.prefetch_one_level = patched_prefetch_one_level_v1
