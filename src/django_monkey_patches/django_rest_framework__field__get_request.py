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
a "feature-complete" framework ;).
The goal of this patch is to shorten application code
with small helpers for accessing request in serializers.
https://github.com/encode/django-rest-framework/issues/8457
Field class introduces the context property,
and BaseSerializer inherits of Field,
so the right place to add this helper functions is Field.
"""

# pylint: disable-next=import-error
from rest_framework.fields import Field


def get_request_query_params(self):
    """
    Enables shorter code to access request query params
    from serializer.
    """
    request = self.context.get("request", None)
    if request is None:
        return {}
    if not hasattr(request, "query_params"):
        # True story, you may have a code base where, sometimes,
        # a Django HttpRequest is given instead of a DRF Request
        # to the context of the serializer.
        # (This is not an use of the serializer in a DRF view.)
        return request.GET
    return request.query_params


def get_request_data(self):
    """
    Enables shorter code to access request data
    from serializer.
    """
    request = self.context.get("request", None)
    if request is None or not hasattr(request, "data"):
        return {}
    return request.data


# pylint: disable-next=invalid-name
def get_request_POST(self):
    """
    Enables shorter code to access request POST
    from serializer.
    """
    request = self.context.get("request", None)
    if request is None:
        return {}
    return request.POST


def get_one_request_query_param(self, key, default=None):
    """
    Enables still shorter code to access one request query param
    from serializer.
    """
    return self.get_request_query_params().get(key, default)


def get_one_request_datum(self, key, default=None):
    """
    Enables still shorter code to access one request datum
    from serializer.
    """
    return self.get_request_data().get(key, default)


# pylint: disable-next=invalid-name
def get_one_request_POST_datum(self, key, default=None):
    """
    Enables still shorter code to access one request POST datum
    from serializer.
    """
    return self.get_request_POST().get(key, default)


def apply_get_request_patch_v1():
    """
    Add to Field (and Serializer) all the shortcuts.
    """

    Field.get_request_query_params = get_request_query_params
    Field.get_request_data = get_request_data
    Field.get_request_POST = get_request_POST
    Field.get_one_request_query_param = get_one_request_query_param
    Field.get_one_request_datum = get_one_request_datum
    Field.get_one_request_POST_datum = get_one_request_POST_datum
