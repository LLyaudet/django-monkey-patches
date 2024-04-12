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
A collection of functions to make the key used by the cache.
As of now, it is only for tests.
"""

import os


def make_test_cache_key(key, key_prefix, version):
    """
    Add a simple "test_cache" prefix.

    For example, apply it in your settings file with:
    # if len(sys.argv) > 1 and sys.argv[1] == "test":
    if TESTING:
        for cache in CACHES.values():
            cache["KEY_FUNCTION"] = make_test_cache_key
    """
    return f"test_cache:{key_prefix}:{version}:{key}"


def make_parallel_test_cache_key(key, key_prefix, version):
    """
    Add a simple "test_cache" prefix plus the current pid.
    The local memory cache is isolated between processes.
    But it may not be the case of a Redis backend cache, for example.
    https://stackoverflow.com/questions/71583690/
    It may seem inefficient to call os.getpid() here,
    but Django loads settings only once even when multiple processes
    are used for parallel tests.
    And the BaseCache related objects are common.
    So setting KEY_PREFIX is not enough.

    For example, apply it in your settings file with:
    # if len(sys.argv) > 1 and sys.argv[1] == "test":
    if TESTING:
        for cache in CACHES.values():
            cache["KEY_FUNCTION"] = make_parallel_test_cache_key
    """

    return f"test_cache{os.getpid()}:{key_prefix}:{version}:{key}"
