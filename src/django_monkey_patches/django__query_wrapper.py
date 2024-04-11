"""
This file is part of django-monkey-patches library.

django-monkey-patches is free software:
you can redistribute it and/or modify it under the terms
of the GNU Lesser General Public License
as published by the Free Software Foundation,
either version 3 of the License,
or (at your option) any later version.

django-monkey-patches is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY;
without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with django-monkey-patches.
If not, see <http://www.gnu.org/licenses/>.

©Copyright 2023-2024 Laurent Lyaudet
-------------------------------------------------------------------------
A full-featured custom query wrapper and constants to control it,
plus functions to customize part of its behavior.
The goal is to give back full control to the developper
by enabling debug, etc. that will be localized to a problem to solve
without making the whole application unusable in production.
"""

import time
import traceback

# Remind that you can modify the constants below during execution:
# import django__query_wrapper
# django__query_wrapper.COUNT_QUERIES = True
# ... the code I'm looking at closely
# django__query_wrapper.COUNT_QUERIES = False
# logger.info(f"Number of queries : {...}")

# Why you may want to throttle queries?
# To see the impact of some conditions,
# like when you have an n-tier architecture
# and you always have a penalty of approximately 3 ms per query.
# You can somehow reproduce this in your development environment
# to see where you may have a problem later.
THROTTLE_QUERIES = False
QUERY_PENALTY_MILLISECONDS = 3
# When the number of queries "scales" too closely
# with the number of objects processed...
# The count will be saved on connection object
# (django_monkey_patches_query_count).
COUNT_QUERIES = False
# When you have some particular queries that are too slow.
# If you can control settings.DEBUG,
# you may want to use a log filter on django.db.backends.
# But settings.DEBUG activates too many things
# (bad frameworks use global constants that do everything,
# good frameworks have atomic constants for anything to work in isolation,
# better frameworks choose carefully
# the intermediate switches to add to the good frameworks.)
TIME_QUERIES = False
# Activate the dump of the calls stack to process or log it.
COMPUTE_CALLS_STACK = False
# Execute a callback before executing the query on the DBMS.
PRE_EXECUTION_CALLBACK = None
# Execute a callback after executing the query on the DBMS.
POST_EXECUTION_CALLBACK = None


def custom_query_wrapper_v1(execute, sql, params, many, context):
    """
    This custom query wrapper features many options
    to help debug and profile database queries.
    """
    if THROTTLE_QUERIES:
        time.sleep(QUERY_PENALTY_MILLISECONDS / 1000)

    stack = None
    if COMPUTE_CALLS_STACK:
         stack = traceback.format_stack()

    if PRE_EXECUTION_CALLBACK is not None:
        (
            execute,
            sql,
            params,
            many,
            context,
            stack,
        ) = PRE_EXECUTION_CALLBACK(execute, sql, params, many, context, stack)

    start_time = None
    if TIME_QUERIES:
        start_time = time.time()

    result = execute(sql, params, many, context)

    end_time = None
    duration = None
    if TIME_QUERIES:
        end_time = time.time()
        duration = end_time - start-time

    connection = context["connection"]
    if COUNT_QUERIES:
        if not hasattr(connection, "django_monkey_patches_query_count"):
            connection.django_monkey_patches_query_count = 0
        connection.django_monkey_patches_query_count += 1

    if POST_EXECUTION_CALLBACK is not None:
        result = POST_EXECUTION_CALLBACK(
            execute,
            sql,
            params,
            many,
            context,
            stack,
            start_time,
            result,
            end_time,
            duration,
        )

    return result


def get_full_query_v1(sql, params, context):
    """
    An helper function to see the request
    as it will be transmitted to the DBMS.
    """
    connection = context["connection"]
    return  connection.cursor().mogrify(sql, params)

