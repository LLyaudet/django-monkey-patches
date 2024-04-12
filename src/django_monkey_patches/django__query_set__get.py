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
There is an inconsistency in behavior
of current QuerySet.get_or_create():
It avoids unnecessary DB query for related object given as argument
only if created is True.
I gave a script demonstrating this here:
https://code.djangoproject.com/ticket/34884
The patch of get_or_create() can be replaced by
a more general patch on QuerySet.get().
"""

# pylint: disable-next=import-error
from django.db.models import QuerySet

from .django__query_set import put_filter_arg_in_field_cache

original_get = QuerySet.get


def patched_get_v1(self, *args, **kwargs):
    """
    Patch for QuerySet.get() with foreign key cache.
    """
    result = original_get(self, *args, **kwargs)
    put_filter_arg_in_field_cache(result, kwargs)
    return result


def apply_patched_get_v1():
    """
    Apply the patch for QuerySet.get() with foreign key cache.
    """
    QuerySet.get = patched_get_v1
    return original_get
