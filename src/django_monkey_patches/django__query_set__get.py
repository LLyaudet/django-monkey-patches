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

©Copyright 2023 Laurent Lyaudet
"""
"""
There is an inconsistency in behavior of current QuerySet.get_or_create():
It avoids unnecessary DB query for related object given as argument
only if created is True.
I gave a script demonstrating this here:
https://code.djangoproject.com/ticket/34884
The patch of get_or_create() can be replaced by
a more general patch on QuerySet.get().
"""
from django.core.exceptions import FieldDoesNotExist
from django.db.models import QuerySet, ForeignKey


original_get = QuerySet.get


def patched_get_v1(self, *args, **kwargs):
    result = original_get(self, *args, **kwargs)
    for key, value in kwargs.items():
        try:
            if isinstance(result._meta.get_field(key), ForeignKey):
                # isinstance handles OneToOneField also.
                setattr(result, key, value)
        except FieldDoesNotExist:
            pass
    return result


def apply_patched_get_or_create_v1():
    QuerySet.get = patched_get_v1
    return original_get
