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
"""

# pylint: disable-next=import-error
from django.core.exceptions import FieldDoesNotExist

# pylint: disable-next=import-error
from django.db.models import ForeignKey


def put_filter_arg_in_field_cache(obj, kwargs):
    """
    Given an object and a dict of field-values/filtering-args
    put in the cache of ForeignKey/OneToOneField the given objects.
    """
    for key, value in kwargs.items():
        try:
            # pylint: disable-next=protected-access
            if isinstance(obj._meta.get_field(key), ForeignKey):
                # isinstance handles OneToOneField also.
                setattr(obj, key, value)
        except FieldDoesNotExist:
            pass
