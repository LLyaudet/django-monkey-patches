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
Choose between flaky tests by default,
and slow tests by default.
The topic is complex,
because you may end up having tests
where most of the time is spent on the same cache filling over and over.
But the good news is that you can apply or not this patch at will.

/!\/!\/!\ cache.clear() can do a lot of harm
if you have a cache infrastructure shared between your test environment
and your production environment,
or shared between your Django application and another application.
As the Django doc states at https://docs.djangoproject.com/en/dev/topics/cache/ :
> Finally, if you want to delete all the keys in the cache, use cache.clear().
> Be careful with this; clear() will remove everything from the cache,
> not just the keys set by your application.
Better solutions exist by searching for cache keys with some prefix,
and then using cache.delete_many().
But there is no uniform way yet, across cache backends,
to get cache keys with some prefix.
See : https://stackoverflow.com/questions/9048257/get-list-of-cache-keys-in-django

/!\ Make sure you call super().tearDown() in your custom tearDown() methods.
"""
from django.core.cache import cache
from django.test import TestCase


# No original tearDown method


def patched_tear_down_v1(self, *args, **kwargs):
    cache.clear()


def apply_patched_tear_down_v1():
    TestCase.tearDown = patched_tear_down_v1
