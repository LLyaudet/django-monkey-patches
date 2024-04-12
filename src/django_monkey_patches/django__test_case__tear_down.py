r"""
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
Choose between flaky tests by default,
and slow tests by default.
The topic is complex,
because you may end up having tests
where most of the time is spent
on the same cache filling over and over.
But the good news is that you can apply or not this patch at will.

/!\/!\/!\ cache.clear() can do a lot of harm
if you have a cache infrastructure shared
between your test environment and your production environment,
or shared between your Django application and another application.
As the Django doc states at
https://docs.djangoproject.com/en/dev/topics/cache/:
> Finally, if you want to delete all the keys in the cache,
> use cache.clear().
> Be careful with this; clear() will remove everything from the cache,
> not just the keys set by your application.
Better solutions exist by searching for cache keys with some prefix,
and then using cache.delete_many().
But there is no uniform way yet, across cache backends,
to get cache keys with some prefix.
See:
https://stackoverflow.com/questions/9048257/\
  get-list-of-cache-keys-in-django
For this solution and Redis,
you will have to choose v2 and modify your caches settings
according to your use case.

/!\ Make sure you call super().tearDown()
in your custom tearDown() methods.
"""

import os
from typing import Dict

# pylint: disable-next=import-error
from django.conf import settings

# pylint: disable-next=import-error
from django.core.cache import cache, caches

# pylint: disable-next=import-error
from django.test import TestCase

from .django__base_cache__make_cache_key import (
    make_parallel_test_cache_key,
    make_test_cache_key,
)

# This function is a noop (pass).
original_tear_down = TestCase.tearDown


# pylint: disable-next=unused-argument
def patched_tear_down_v1(self, *args, **kwargs):
    """
    Not recommended,
    it will wipe out everything in the current cache.
    """
    cache.clear()


def apply_patched_tear_down_v1():
    """
    Apply a not recommended patch,
    it will wipe out everything in the current cache.
    """
    TestCase.tearDown = patched_tear_down_v1


# pylint: disable-next=unused-argument
def patched_tear_down_v2(self, *args, **kwargs):
    """
    This is the most flexible patch
    where you can define on a per cache basis
    the function you want to apply to clear the cache.
    The code of 4 possible callback functions is given after.
    """
    for cache_alias, cache_settings in settings.CACHES.items():
        test_clear_cache_callback = cache_settings.get(
            "TEST_CLEAR_CACHE_CALLBACK",
        )
        if test_clear_cache_callback is not None:
            test_clear_cache_callback(
                cache_alias,
                cache_settings,
                caches[cache_alias],
            )


def apply_patched_tear_down_v2():
    """
    Apply the recommended and flexible patch
    for cleaning cache in tests.
    """
    TestCase.tearDown = patched_tear_down_v2


def test_clear_cache_callback_v1(
    # pylint: disable-next=unused-argument
    cache_alias: str,
    # pylint: disable-next=unused-argument
    cache_settings: Dict,
    current_cache,
):
    """Probably not the best option"""
    current_cache.clear()


def test_clear_cache_callback_v2(
    # pylint: disable-next=unused-argument
    cache_alias: str,
    cache_settings: Dict,
    current_cache,
):
    """
    A nice possibility with Redis.
    See https://stackoverflow.com/a/55633767/5796086
    CC BY SA 4.0
    and see make_test_cache_key(), make_parallel_test_cache_key()
    in this package.
    And see v5...
    in case .keys() and .delete_many() apply KEY_FUNCTION
    and you want to cover all versions
    (the third parameter of KEY_FUNCTION)...
    """
    key_function = cache_settings.get("KEY_FUNCTION")
    key_prefix = cache_settings.get("KEY_PREFIX", "")
    if key_function is make_test_cache_key:
        query_key_prefix = f"test_cache:{key_prefix}:*"
    elif key_function is make_parallel_test_cache_key:
        query_key_prefix = f"test_cache{os.getpid()}:{key_prefix}:*"
    else:
        return
    cache_keys = current_cache.keys(query_key_prefix)
    if len(cache_keys) > 0:
        current_cache.delete_many(cache_keys)


def test_clear_cache_callback_v3(
    # pylint: disable-next=unused-argument
    cache_alias: str,
    cache_settings: Dict,
    current_cache,
):
    """
    Another possibility with other versions of Redis.
    See https://stackoverflow.com/a/71698532/5796086
    CC BY SA 4.0
    and see make_test_cache_key(), make_parallel_test_cache_key()
    in this package.
    """
    key_function = cache_settings.get("KEY_FUNCTION")
    key_prefix = cache_settings.get("KEY_PREFIX", "")
    if key_function is make_test_cache_key:
        query_key_prefix = f"test_cache:{key_prefix}:*"
    elif key_function is make_parallel_test_cache_key:
        query_key_prefix = f"test_cache{os.getpid()}:{key_prefix}:*"
    else:
        return
    cache_keys = current_cache.get_client(1).keys(query_key_prefix)
    if len(cache_keys) > 0:
        current_cache.delete_many(cache_keys)


def test_clear_cache_callback_v4(
    # pylint: disable-next=unused-argument
    cache_alias: str,
    cache_settings: Dict,
    current_cache,
):
    """
    Still another possibility with other versions of Redis.
    See https://stackoverflow.com/a/71698532/5796086
    CC BY SA 4.0
    and see make_test_cache_key(), make_parallel_test_cache_key()
    in this package.
    """
    key_function = cache_settings.get("KEY_FUNCTION")
    key_prefix = cache_settings.get("KEY_PREFIX", "")
    if key_function is make_test_cache_key:
        query_key_prefix = f"test_cache:{key_prefix}:*"
    elif key_function is make_parallel_test_cache_key:
        query_key_prefix = f"test_cache{os.getpid()}:{key_prefix}:*"
    else:
        return
    cache_keys = current_cache.get_client().keys(query_key_prefix)
    if len(cache_keys) > 0:
        current_cache.delete_many(cache_keys)


def test_clear_cache_callback_v5(
    # pylint: disable-next=unused-argument
    cache_alias: str,
    cache_settings: Dict,
    current_cache,
):
    """
    A nice possibility with Redis.
    """
    key_function = cache_settings.get("KEY_FUNCTION")
    key_prefix = cache_settings.get("KEY_PREFIX", "")
    if key_function is make_test_cache_key:
        query_key_prefix = f"test_cache:{key_prefix}:*"
    elif key_function is make_parallel_test_cache_key:
        query_key_prefix = f"test_cache{os.getpid()}:{key_prefix}:*"
    else:
        return
    cache_keys = current_cache.client.get_client(write=False).keys(
        query_key_prefix
    )
    if len(cache_keys) > 0:
        current_cache.client.get_client(write=True).delete(
            *cache_keys
        )
