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
In my tests, this patch yields a speed up of almost 10 %,
since it avoids many unnecessary queries.
"""
from django.core.exceptions import FieldDoesNotExist
from django.db.models import QuerySet, ForeignKey


original_get_or_create = QuerySet.get_or_create


def patched_get_or_create_v1(self, defaults=None, **kwargs):
    result, created = original_get_or_create(self, defaults=defaults, **kwargs)
    if not created:
        for key, value in kwargs.items():
            try:
                if isinstance(result._meta.get_field(key), ForeignKey):
                    # isinstance handles OneToOneField also.
                    setattr(result, key, value)
            except FieldDoesNotExist:
                pass
    return result, created


def apply_patched_get_or_create_v1():
    QuerySet.get_or_create = patched_get_or_create_v1
    return original_get_or_create
