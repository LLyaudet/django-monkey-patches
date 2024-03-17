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
In current versions of Django, a prefetch use the ordering defined
on the class prefetched.
class Meta:
    ordering = ...
But when you prefetch and there is a single value per current object
that will recieve the prefetch in its cache,
then the ordering is totally useless.
It adds useless load on the DB server.
The goal of these patches is to remove this order by
for many versions of Django.
On very big prefetches I noticed a gain of 10 - 15 %,
since the rest of the DB query is mainly an index scan.
#ClimateChangeBrake
Note that I also submitted a ticket and a PR:
https://code.djangoproject.com/ticket/35309
https://github.com/django/django/pull/17984
So, we can hope for the better that future releases of Django
will not have this problem,
and maybe older versions if it is backported to some.
"""

from django.db.models.fields.related_descriptors import (
    ForwardManyToOneDescriptor,
    ReverseOneToOneDescriptor,
)


# In old versions of Django, the method is called get_prefetch_queryset().
# It is deprecated in Django 5 and will be removed in Django 6.
# Apply the patch that corresponds to your version.
original_forward_many_to_one_get_prefetch_queryset = None
if hasattr(ForwardManyToOneDescriptor, "get_prefetch_queryset"):
    original_forward_many_to_one_get_prefetch_queryset = (
        ForwardManyToOneDescriptor.get_prefetch_queryset
    )
original_reverse_one_to_one_get_prefetch_queryset = None
if hasattr(ReverseOneToOneDescriptor, "get_prefetch_queryset"):
    original_reverse_one_to_one_get_prefetch_queryset = (
        ReverseOneToOneDescriptor.get_prefetch_queryset
    )

original_forward_many_to_one_get_prefetch_querysets = None
if hasattr(ForwardManyToOneDescriptor, "get_prefetch_querysets"):
    original_forward_many_to_one_get_prefetch_querysets = (
        ForwardManyToOneDescriptor.get_prefetch_querysets
    )
original_reverse_one_to_one_get_prefetch_querysets = None
if hasattr(ReverseOneToOneDescriptor, "get_prefetch_querysets"):
    original_reverse_one_to_one_get_prefetch_querysets = (
        ReverseOneToOneDescriptor.get_prefetch_querysets
    )


def patched_forward_many_to_one_get_prefetch_queryset_v1(
    self, instances, queryset=None
):
    if queryset is None:
        queryset = self.get_queryset()
    queryset = queryset.order_by()
    return original_forward_many_to_one_get_prefetch_queryset(self, instances, queryset)


def patched_reverse_one_to_one_get_prefetch_queryset_v1(self, instances, queryset=None):
    if queryset is None:
        queryset = self.get_queryset()
    queryset = queryset.order_by()
    return original_reverse_one_to_one_get_prefetch_queryset(self, instances, queryset)


def apply_patched_get_prefetch_queryset_v1():
    ForwardManyToOneDescriptor.get_prefetch_queryset = (
        patched_forward_many_to_one_get_prefetch_queryset_v1
    )
    ReverseOneToOneDescriptor.get_prefetch_queryset = (
        patched_reverse_one_to_one_get_prefetch_queryset_v1
    )


def patched_forward_many_to_one_get_prefetch_querysets_v1(
    self, instances, querysets=None
):
    if querysets is None:
        querysets = [self.get_queryset()]
    if len(querysets) == 1:
        querysets[0] = querysets[0].order_by()
    return original_forward_many_to_one_get_prefetch_querysets(
        self, instances, querysets
    )


def patched_reverse_one_to_one_get_prefetch_querysets_v1(
    self, instances, querysets=None
):
    if querysets is None:
        querysets = [self.get_queryset()]
    if len(querysets) == 1:
        querysets[0] = querysets[0].order_by()
    return original_reverse_one_to_one_get_prefetch_querysets(
        self, instances, querysets
    )


def apply_patched_get_prefetch_querysets_v1():
    ForwardManyToOneDescriptor.get_prefetch_querysets = (
        patched_forward_many_to_one_get_prefetch_querysets_v1
    )
    ReverseOneToOneDescriptor.get_prefetch_querysets = (
        patched_reverse_one_to_one_get_prefetch_querysets_v1
    )
