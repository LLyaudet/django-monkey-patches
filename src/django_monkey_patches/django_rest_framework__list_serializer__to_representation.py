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
Django Rest Framework is considered "feature-complete".
But if you had the chance to work with an in-house framework
like I did in PHP for 8,5 years,
you know that there is no such thing as
a "feature-complete" framework :(.
The goal of this patch is to have a sensible place
to add unconventional prefetches.
You may apply the patch,
or use patched_to_representation_v1
in a class inheriting from ListSerializer.
"""

# pylint: disable-next=import-error
from django.db import models

# pylint: disable-next=import-error
from rest_framework.serializers import ListSerializer

original_to_representation = ListSerializer.to_representation


def patched_to_representation_v1(self, data):
    """
    List of object instances -> List of dicts of primitive datatypes.
    """
    # Dealing with nested relationships, data can be a Manager,
    # so, first get a queryset from the Manager if needed
    iterable = (
        data.all()
        if isinstance(data, models.manager.BaseManager)
        else data
    )

    if self.context.get("list_before_representation_callback"):
        self.context.get("list_before_representation_callback")(
            iterable
        )
    elif self.child.context.get(
        "list_before_representation_callback"
    ):
        self.child.context.get("list_before_representation_callback")(
            iterable
        )
    elif hasattr(self, "list_before_representation_callback"):
        self.list_before_representation_callback(iterable)
    elif hasattr(self.child, "list_before_representation_callback"):
        self.child.list_before_representation_callback(iterable)

    return [self.child.to_representation(item) for item in iterable]


def apply_patched_to_representation_v1():
    """
    Apply the patch to enable custom computation before the end of
    the list serializer to_representation().
    """
    ListSerializer.to_representation = patched_to_representation_v1
    return original_to_representation
