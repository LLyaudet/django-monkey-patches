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
A full-featured custom query wrapper and constants to control it,
plus functions to customize part of its behavior.
The goal is to give back full control to the developper
by enabling debug, etc. that will be localized to a problem to solve
without making the whole application unusable/slow in production.
"""

import re
import time
import traceback

# pylint: disable-next=import-error
from django.db import connections

# Remind that you can modify the constants below during execution:
# from django_monkey_patches import django__query_wrapper
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
# The count will be saved on connection(s) object(s).
COUNT_QUERIES = False
# When you have some particular queries that are too slow.
# If you can control settings.DEBUG,
# you may want to use a log filter on django.db.backends.
# But settings.DEBUG activates too many things
# (bad frameworks use global constants that do everything,
# good frameworks have atomic constants for anything to work
# in isolation,
# better frameworks choose carefully
# the intermediate switches to add to the good frameworks.)
# Bizarre, il me semblait déjà avoir écrit ça en commençant
# à faire ce patch en novembre ou décembre 2023 ?
# Mais là, plus de trace sur mon ordi.
# Je me fais laver le cerveau un peu trop souvent.
# Autre truc marrant, la recherche GitHub sur le mot atomic
# ne trouve rien dans mon repo django-monkey-patches,
# alors que le push a plus de 5 heures d'ancienneté
# (grep c'est compliqué comme feature ?).
TIME_QUERIES = False
# Activate the dump of the call stack to process or log it.
COMPUTE_CALL_STACK = False
# Execute a callback before executing the query on the DBMS.
PRE_EXECUTION_CALLBACK = None
# Execute a callback after executing the query on the DBMS.
POST_EXECUTION_CALLBACK = None

# All functions below are suffixed with _v1.
# Beware, that I may not use the strictest interpretation
# of backward compatible, because it would need to duplicate
# hundreds of lines of code each time.
# If you understand the logic, you will see that
# the backward compatible problems I don't want to handle
# is about adding custom "fields" in the data structure.
# Please, look at the message at the beginning of
# get_extra_data_template_for_set_of_queries_v1(),
# and submit an issue if needed.
# Otherwise, there may be a "new v1" that will break your code.
# The other backward compatible problems should normally be adressed.


def custom_query_wrapper_v1(execute, sql, params, many, context):
    """
    This custom query wrapper features many options
    to help debug and profile database queries.
    You should be able to do anything you want with it.
    Below, are given data structures and a POST_EXECUTION_CALLBACK
    that should handle most of your use cases.

    Here is an example of how to use it with a middleware:

    class CustomQueryWrapperMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            # Optional but recommended, see below.
            # At least an equivalent is needed,
            # if you activate COUNT_QUERIES.
            init_connections_extra_data_v1()

            # See at end of file to wrap all connections.
            with connection.execute_wrapper(custom_query_wrapper_v1):
                return self.get_response(request)

    In settings.py, add:
    # ######### MIDDLEWARE CONFIGURATION
    MIDDLEWARE = (
        ...
        "path_to.middlewares.CustomQueryWrapperMiddleware",
        ...
    )

    If you want to use it in your commands, there is more work.
    I recommend to define your own class:
    class CustomBaseCommand(BaseCommand):
        ...
        def execute(self, *args, **options):
            # Copy the code of BaseCommand.execute()
            # And in it replace at least:
            #   output = self.handle(*args, **options)
            # with:
            with connection.execute_wrapper(custom_query_wrapper_v1):
                # See at end of file to wrap all connections.
                output = self.handle(*args, **options)
        ...
    And then, make all your commands inherit from CustomBaseCommand.
    You can go way further
    in this line of customization and monitoring.
    """

    if THROTTLE_QUERIES:
        time.sleep(QUERY_PENALTY_MILLISECONDS / 1000)

    call_stack = None
    if COMPUTE_CALL_STACK:
        call_stack = traceback.format_stack()

    if PRE_EXECUTION_CALLBACK is not None:
        (
            execute,
            sql,
            params,
            many,
            context,
            call_stack,
        ) = PRE_EXECUTION_CALLBACK(
            execute, sql, params, many, context, call_stack
        )

    start_time = None
    if TIME_QUERIES:
        start_time = time.time()

    result = execute(sql, params, many, context)

    end_time = None
    duration = None
    if TIME_QUERIES:
        end_time = time.time()
        duration = end_time - start_time

    if COUNT_QUERIES:
        connections.django_monkey_patches_dict["query_count"] += 1
        connection = context["connection"]
        connection.django_monkey_patches_dict["query_count"] += 1

    if POST_EXECUTION_CALLBACK is not None:
        result = POST_EXECUTION_CALLBACK(
            execute,
            sql,
            params,
            many,
            context,
            call_stack,
            start_time,
            result,
            end_time,
            duration,
        )

    return result


# pylint: disable-next=unused-argument
def get_full_query_v1(extra_data_dict, data):
    """
    An helper function to see the request
    as it will be transmitted to the DBMS.
    """

    connection = data["context"]["connection"]
    return connection.cursor().mogrify(data["sql"], data["params"])


get_full_query_v1.field_name = "full_query_v1"


params_placeholders_regexp = re.compile("%s(,%s)*")


# pylint: disable-next=unused-argument
def get_sql_signature_v1(extra_data_dict, data):
    """
    An helper function to get an SQL signature
    where the params have no impact.
    It is somewhat similar to a technique we used at Teliae.
    Jérôme Petit added an activable dump of all queries
    and progressively improved the profiling tool,
    with help of other team members including me,
    this kind of signature was used to group requests together.
    But since our in-house framework was rarely using
    prepared statements,
    the code to obtain an "SQL signature" was different.
    All the code in this file is more general and flexible than
    what we had at Teliae when I was working there.
    But the ideas here both stem from my work at Teliae and Deleev.
    """

    return params_placeholders_regexp.sub("", data["sql"])


get_sql_signature_v1.field_name = "sql_signature_v1"


# pylint: disable-next=unused-argument
def get_light_call_stack_v1(extra_data_dict, data):
    """
    An helper function to remove framework code from the call stack.
    Usually, you want to know where you generate a DB request
    in your own code.
    """

    return [
        line
        for line in data["call_stack"]
        if "site-packages/" not in line
    ]


get_light_call_stack_v1.field_name = "light_call_stack_v1"


def get_managed_list(manager):
    """
    Smaller with auto-completion:
    get_managed_list(manager)
    [] if manager is None else manager.list()
    """

    if manager is None:
        return []
    return manager.list()


def get_managed_dict(manager):
    """
    Smaller with auto-completion:
    get_managed_dict(manager)
    {} if manager is None else manager.dict()
    """

    if manager is None:
        return {}
    return manager.dict()


# Unfortunately, there is no "inline" function or macro in Python.
# Another strange fact, C has inline functions,
# but no keyword to inline only at some spot.
# And sometimes, you know where is the spot
# where it MUST-epsilon be inlined.
# In theory, the compiler is supposed to know better than you...
# Search for examples.
# Of course, you can add assembly in C code instead.
# Much more convenient.
# Or you can use ORDER or CHAOS C "macros engines",
# and recently Zig, but I would prefer more keywords
# and less limited base macro rules for C,
# instead of learning something totally new.
# There may be more advantages to Zig that I don't see,
# since I only read news about it.
# And there is Rust with partial memory-safety.
# But since I almost never do multi-threaded code,
# I'm more looking at C and languages enabling very fast code,
# than more safe code.
# https://github.com/google/comprehensive-rust/issues
# Something disappeared : I have no "issue",
# but I still have some memory and a brain and a shiny armor
# and a sword in the hands of God:
# Let's hope it is just my tongue
# to tell the Truth in the name of Jesus.
# Let's hope I shall use my tongue more frequently aligned/adjusted
# with God's intention. I have no pretention of perfection.
# fn main() {
#   for x in 1..5 {
#     println!("x: {x}");
#   }
#   let bla = [1, 2, 3, 4, 5];
#   // La bonne excuse,
#   // c'est l'indécidabilité du problème de l'arrêt
#   // (cf. le film Didier, certains ne savent pas s'arrêter),
#   // style Collatz conjecture,
#   // c'est clair qu'on fait ce genre de blagues
#   // dans le code tout le temps...
#   // Non mais sérieux... 99 % du code,
#   // il doit y avoir des règles simples
#   // pour ne pas avoir à gérer de problème indécidable...
#   // Enfin, ce n'est que mon avis.
#   // Mais je ne bosse pas trop sur des compilateurs ;
#   // peut-être que c'est un peu plus au niveau méta
#   // qu'il y a des trucs "amusants" sur le plan scientifique,
#   // et encore ce n'est pas une certitude.
#
#   for elem in 1..10 {
#     let truc = bla[elem];
#     println!("elem: {truc}");
#   }
# }


# pylint: disable-next=too-many-arguments
def get_extra_data_template_for_set_of_queries_v1(
    query_fields=None,
    min_seconds_threshold=0,
    max_seconds_threshold=float("inf"),
    filter_callback=None,
    insertion_callback=None,
    subsets_extra_data=None,
    allocated_subsets_extra_data=None,
    allocated_subsets_key_callback=None,
    allocated_subsets_init_callback=None,
    top_down_post_processing_callback=None,
    bottom_up_post_processing_callback=None,
    # You may need that with django-rq or other multiprocesses code:
    manager=None,
):
    """
    Obtain a default extra_data_dict with most of
    the interesting "fields" regarding DB queries analysis.
    If you see something that may be interesting to add here,
    with a good example of why you need it, please,
    submit an issue on my GitHub repository.
    That's the goal of the LGPL: if you improve this library code,
    please share with anyone.
    I will not sue you if you don't, since it is a border-line case.
    Just adding "fields" and then using other functions
    without my code
    or eventually wrapping mines may be subject to interpretation.
    Basically, I think that if you use your own additional "fields"
    and your own callbacks to fill/use the "fields" below,
    you have no obligation at all.
    But it would be nice to contribute anyway.
    """

    if query_fields is None:
        query_fields = get_managed_list(manager)
    if subsets_extra_data is None:
        subsets_extra_data = get_managed_dict(manager)
    if allocated_subsets_extra_data is None:
        allocated_subsets_extra_data = get_managed_dict(manager)
    if allocated_subsets_key_callback is None:
        allocated_subsets_key_callback = get_managed_dict(manager)
    if allocated_subsets_init_callback is None:
        allocated_subsets_init_callback = get_managed_dict(manager)

    result = get_managed_dict(manager)
    result_content = {
        "query_count": 0,
        "query_fields": query_fields,  # [
        #     "execute",
        #     "sql",
        #     "params",
        #     "many",
        #     "context",
        #     "call_stack",
        #     "start_time",
        #     "result",
        #     "end_time",
        #     "duration",
        #     get_full_query_v1,  # This is a function
        # ],
        "query_list": get_managed_list(manager),  # [
        # {
        #     "execute": None,
        #     "sql": None,
        #     "params": None,
        #     "many": None,
        #     "context": None,
        #     "call_stack": None,
        #     "start_time": None,
        #     "result": None,
        #     "end_time": None,
        #     "duration": None,
        #     "full_query_v1": None,
        # },
        # ],
        "total_duration": 0,
        "average_duration": 0,
        "min_duration": float("inf"),
        "max_duration": 0,
        # ------------------------------------------------------------
        # These fields could be at the top,
        # but it would be less didactic I think.
        # Two floats that will be compared to query duration
        # for any query in ancestor subset;
        # in case a comparison fails,
        # the query is not counted in this subset.
        "min_seconds_threshold": min_seconds_threshold,  # 0,
        # float("inf"),
        "max_seconds_threshold": max_seconds_threshold,
        "filter_callback": filter_callback,  # None,
        # Default will be to use query_fields, update total,
        # min, max, and recurse on nested dicts.
        "insertion_callback": insertion_callback,  # None,
        # ------------------------------------------------------------
        "subsets_extra_data": subsets_extra_data,  # {
        #     "main": get_extra_data_template_for_set_of_queries(),
        # },
        "allocated_subsets_extra_data": allocated_subsets_extra_data,
        # {
        #   Beware of recursive calls
        #   https://stackoverflow.com/questions/
        #   22464900/do-dictionaries-have-a-key-length-limit
        #   Value of dict can be the count or a full nested dict.
        #   "distinct_call_stacks": {
        #     f"{some_call_stack}": (
        #       get_extra_data_template_for_set_of_queries(),
        #     )
        #   },
        # },
        "allocated_subsets_key_callback": (
            allocated_subsets_key_callback
            # {
            #   "distinct_call_stacks": lambda x, y: y["call_stack"],
            # },
        ),
        "allocated_subsets_init_callback": (
            allocated_subsets_init_callback
            # {
            #   "distinct_call_stacks": (
            #     get_extra_data_template_for_set_of_queries
            #   ),
            # },
        ),
        # If you want an allocated_subsets_filter_callback,
        # because you want to allocate only a subset of queries,
        # then you're invited to use one more nesting level
        # with subsets_extra_data.
        # Because it will avoid duplicating
        # the, currently, three fields
        # used for filtering above.
        # With the following callbacks, you can sort query_list,
        # for example.
        # But you may also reorder the nested dicts, etc.,
        # and you can control if you want to synthetize
        # bottom-up or top_down.
        "top_down_post_processing_callback": (
            top_down_post_processing_callback  # None
        ),
        "bottom_up_post_processing_callback": (
            bottom_up_post_processing_callback  # None
        ),
        # If you need a mix of both,
        # you should rewrite the top-down one.
        # Thus, you can do things in the order that pleases you,
        # recurse when you want, etc.,
        # and you can add flags in the dicts
        # to avoid multi-post-processings
        # on recursed dicts.
        # But clearly, in most cases,
        # the bottom-up post-processing makes more sense.
        # (Think sorting sub-results, etc.)
    }
    result.update(result_content)
    return result


def init_connections_extra_data(
    get_extra_data_template_callback,
    manager=None,
    empty_stash_stack=False,
):
    """
    You should call this function or a custom one
    before using the custom query wrapper.
    """

    connections.django_monkey_patches_dict = (
        get_extra_data_template_callback()
    )
    if empty_stash_stack or not hasattr(
        connections, "django_monkey_patches_stash_stack"
    ):
        connections.django_monkey_patches_stash_stack = (
            get_managed_list(manager)
        )

    for connection_key in connections:
        connection = connections[connection_key]
        connection.django_monkey_patches_dict = (
            get_extra_data_template_callback()
        )
        if empty_stash_stack or not hasattr(
            connection, "django_monkey_patches_stash_stack"
        ):
            connection.django_monkey_patches_stash_stack = (
                get_managed_list(manager)
            )


# pylint: disable-next=too-many-arguments
def init_connections_extra_data_v1(
    manager=None,
    empty_stash_stack=False,
    query_fields=None,
    min_seconds_threshold=0,
    max_seconds_threshold=float("inf"),
    filter_callback=None,
    insertion_callback=None,
    subsets_extra_data=None,
    allocated_subsets_extra_data=None,
    allocated_subsets_key_callback=None,
    allocated_subsets_init_callback=None,
    top_down_post_processing_callback=None,
    bottom_up_post_processing_callback=None,
):
    """
    A simple default function providing the
    get_extra_data_template_callback argument
    to init_connections_extra_data().
    """

    def lambda_get_extra_data_template_for_set_of_queries_v1():
        return get_extra_data_template_for_set_of_queries_v1(
            query_fields=query_fields,
            min_seconds_threshold=min_seconds_threshold,
            max_seconds_threshold=max_seconds_threshold,
            filter_callback=filter_callback,
            insertion_callback=insertion_callback,
            subsets_extra_data=subsets_extra_data,
            allocated_subsets_extra_data=allocated_subsets_extra_data,
            allocated_subsets_key_callback=(
                allocated_subsets_key_callback
            ),
            allocated_subsets_init_callback=(
                allocated_subsets_init_callback
            ),
            top_down_post_processing_callback=(
                top_down_post_processing_callback
            ),
            bottom_up_post_processing_callback=(
                bottom_up_post_processing_callback
            ),
            manager=manager,
        )

    init_connections_extra_data(
        lambda_get_extra_data_template_for_set_of_queries_v1,
        manager=manager,
        empty_stash_stack=empty_stash_stack,
    )


# pylint: disable-next=too-many-arguments
def insert_in_connections_extra_data_v1(
    execute,
    sql,
    params,
    many,
    context,
    call_stack,
    start_time,
    result,
    end_time,
    duration,
):
    """
    The entry-point function to insert query data in relevant dicts.
    It should be your default POST_EXECUTION_CALLBACK.
    """

    all_dicts = [
        connections.django_monkey_patches_dict,
        context["connection"].django_monkey_patches_dict,
    ]
    data = {
        "execute": execute,
        "sql": sql,
        "params": params,
        "many": many,
        "context": context,
        "call_stack": call_stack,
        "start_time": start_time,
        "result": result,
        "end_time": end_time,
        "duration": duration,
    }
    for extra_data_dict in all_dicts:
        insert_in_extra_data_dict_v1(extra_data_dict, data)
    return result


# pylint: disable-next=too-many-branches
def insert_in_extra_data_dict_v1(extra_data_dict, data):
    """
    The recursive function used to insert the data of a query
    in all relevant dicts.
    """

    # Filtering part -------------------------------------------------
    if data["duration"] is not None:
        # /!\ check list: you did activate TIME_QUERIES?
        if (
            extra_data_dict["min_seconds_threshold"]
            > data["duration"]
        ):
            return
        if (
            extra_data_dict["max_seconds_threshold"]
            < data["duration"]
        ):
            return

    filter_callback = extra_data_dict["filter_callback"]
    if filter_callback is not None and not filter_callback(
        extra_data_dict, data
    ):
        return
    # ----------------------------------------------------------------

    # Insertion part -------------------------------------------------
    extra_data_dict["query_count"] += 1
    fields = extra_data_dict["query_fields"]
    if len(fields) > 0:
        local_data = {}
        for field in fields:
            # pylint: disable-next=unidiomatic-typecheck
            if type(field) is str:
                local_data[field] = data[field]
            else:
                # It is a function.
                local_data[field.field_name] = field(
                    extra_data_dict, data
                )
        extra_data_dict["query_list"].append(local_data)
    if data["duration"] is not None:
        extra_data_dict["total_duration"] += data["duration"]
        extra_data_dict["min_duration"] = min(
            extra_data_dict["min_duration"], data["duration"]
        )
        extra_data_dict["max_duration"] = max(
            extra_data_dict["max_duration"], data["duration"]
        )
    insertion_callback = extra_data_dict["insertion_callback"]
    if insertion_callback is not None:
        # You can keep track of nesting
        # by altering data in this callback.
        insertion_callback(extra_data_dict, data)
    # ----------------------------------------------------------------

    # Recursion part -------------------------------------------------
    for some_dict in extra_data_dict["subsets_extra_data"]:
        insert_in_extra_data_dict_v1(some_dict, data)
    for (
        allocated_subset_key,
        key_generator,
    ) in extra_data_dict["allocated_subsets_key_callback"].items():
        if key_generator is None:
            continue
        sub_dict = extra_data_dict["allocated_subsets_extra_data"][
            allocated_subset_key
        ]
        if sub_dict is None:
            raise ValueError(
                "allocated_subsets error:"
                f" no sub_dict for {allocated_subset_key}"
            )
        init_callback = extra_data_dict[
            "allocated_subsets_init_callback"
        ][allocated_subset_key]
        if init_callback is None:
            raise ValueError(
                "allocated_subsets error:"
                f" no init_callback for {allocated_subset_key}"
            )
        some_key = key_generator(extra_data_dict, data)
        if sub_dict.get(some_key) is None:
            sub_dict[some_key] = init_callback(extra_data_dict, data)
        insert_in_extra_data_dict_v1(sub_dict[some_key], data)
    # ----------------------------------------------------------------


def synthetize_connections_extra_data_v1():
    """
    The entry-point function to call synthetize_extra_data_dict_v1()
    on all root extra data dicts.
    """

    extra_data_dicts = [connections.django_monkey_patches_dict]
    extra_data_dicts.extend(
        connections[connection_key].django_monkey_patches_dict
        for connection_key in connections
    )
    for extra_data_dict in extra_data_dicts:
        synthetize_extra_data_dict_v1(extra_data_dict)


def synthetize_extra_data_dict_v1(extra_data_dict):
    """
    The recursive function used to synthetize
    the results at the end.
    """

    if extra_data_dict["query_count"] > 0:
        extra_data_dict["average_duration"] = (
            extra_data_dict["total_duration"]
            / extra_data_dict["query_count"]
        )

    # Top-down
    processing_callback = extra_data_dict[
        "top_down_post_processing_callback"
    ]
    if processing_callback is not None:
        processing_callback(extra_data_dict)

    # Recursion
    for some_dict in extra_data_dict["subsets_extra_data"].values():
        synthetize_extra_data_dict_v1(some_dict)
    for sub_dict in extra_data_dict[
        "allocated_subsets_extra_data"
    ].values():
        for some_dict in sub_dict.values():
            synthetize_extra_data_dict_v1(some_dict)

    # Bottom-up
    processing_callback = extra_data_dict[
        "bottom_up_post_processing_callback"
    ]
    if processing_callback is not None:
        processing_callback(extra_data_dict)


def reorder_dict_by_total_duration_of_sub_dicts(some_dict):
    """
    A common tool to visualize the result of profiling DB queries
    is to see at the top
    similar queries where most of the time is spent.
    """

    couples_list = list(some_dict.items())
    couples_list.sort(
        key=lambda x: x[1]["total_duration"],
        reverse=True,
    )
    return dict(couples_list)


def apply_reorder_dict_by_total_duration_of_sub_dicts_to(
    main_dict,
    some_sub_dict_key,
):
    """
    This function simplifies use of the previous one.
    """

    main_dict[some_sub_dict_key] = (
        reorder_dict_by_total_duration_of_sub_dicts(
            main_dict[some_sub_dict_key]
        )
    )


def wrap_connections(
    exit_stack,
    custom_query_wrapper,
    connections_to_wrap=None,
):
    """
    Apply the context-manager connection.execute_wrapper()
    with the given custom_query_wrapper
    on an ExitStack() instance,
    for given connections or all connections if none is given.
    """

    if connections_to_wrap is None:
        connections_to_wrap = connections
    for connection_key in connections_to_wrap:
        connection = connections[connection_key]
        exit_stack.enter_context(
            connection.execute_wrapper(custom_query_wrapper)
        )


def stash_extra_data_dicts(reinit_after_stash=None):
    """
    Stash current django_monkey_patches_dicts
    in django_monkey_patches_stash_stacks.
    """

    connections.django_monkey_patches_stash_stack.append(
        connections.django_monkey_patches_dict
    )

    if reinit_after_stash is None:
        connections.django_monkey_patches_dict = None
    for connection_key in connections:
        connection = connections[connection_key]
        connection.django_monkey_patches_stash_stack.append(
            connection.django_monkey_patches_dict
        )
        if reinit_after_stash is None:
            connection.django_monkey_patches_dict = None

    if reinit_after_stash:
        reinit_after_stash()


# pylint: disable-next=too-many-arguments
def stash_extra_data_dicts_and_reinit_v1(
    manager=None,
    query_fields=None,
    min_seconds_threshold=0,
    max_seconds_threshold=float("inf"),
    filter_callback=None,
    insertion_callback=None,
    subsets_extra_data=None,
    allocated_subsets_extra_data=None,
    allocated_subsets_key_callback=None,
    allocated_subsets_init_callback=None,
    top_down_post_processing_callback=None,
    bottom_up_post_processing_callback=None,
):
    """
    Stash current django_monkey_patches_dicts
    in django_monkey_patches_stash_stacks,
    and apply a reinit using default init functions.
    """

    def lambda_init_connections_extra_data_v1():
        init_connections_extra_data_v1(
            manager=manager,
            empty_stash_stack=False,
            query_fields=query_fields,
            min_seconds_threshold=min_seconds_threshold,
            max_seconds_threshold=max_seconds_threshold,
            filter_callback=filter_callback,
            insertion_callback=insertion_callback,
            subsets_extra_data=subsets_extra_data,
            allocated_subsets_extra_data=allocated_subsets_extra_data,
            allocated_subsets_key_callback=(
                allocated_subsets_key_callback
            ),
            allocated_subsets_init_callback=(
                allocated_subsets_init_callback
            ),
            top_down_post_processing_callback=(
                top_down_post_processing_callback
            ),
            bottom_up_post_processing_callback=(
                bottom_up_post_processing_callback
            ),
        )

    stash_extra_data_dicts(
        reinit_after_stash=lambda_init_connections_extra_data_v1
    )


def pop_extra_data_dicts():
    """
    Pop last dicts in django_monkey_patches_stash_stacks
    to django_monkey_patches_dicts.
    """

    connections.django_monkey_patches_dict = (
        connections.django_monkey_patches_stash_stack.pop()
    )
    for connection_key in connections:
        connection = connections[connection_key]
        connection.django_monkey_patches_dict = (
            connection.django_monkey_patches_stash_stack.pop()
        )


# You should extract the data to logs or files,
# during execution or at the end,
# using custom insertion_callback or post_processing_callback.
# Here is an example of intermediate complexity
# using all of the above.
#
# from contextlib import ExitStack
#
# from django_monkey_patches import django__query_wrapper
# from django_monkey_patches.django__query_wrapper import (
#     apply_reorder_dict_by_total_duration_of_sub_dicts_to,
#     custom_query_wrapper_v1,
#     get_extra_data_template_for_set_of_queries_v1,
#     get_sql_signature_v1,
#     init_connections_extra_data_v1,
#     insert_in_connections_extra_data_v1,
#     synthetize_connections_extra_data_v1,
# )
#
# # /!\ Beware of double counting that may occur when you use
# # COUNT_QUERIES and insert_in_connections_extra_data_v1
# # simultaneously.
# # If you want to monitor COUNT_QUERIES all the time,
# # and activate something else more rarely,
# # you have 2 possibilities : unactivate COUNT_QUERIES when needed,
# # or activate insert_in_connections_extra_data_v1
# # with an insertion_callback that will cancel the double counting.
# # django__query_wrapper.COUNT_QUERIES = True
# django__query_wrapper.TIME_QUERIES = True
# django__query_wrapper.COMPUTE_CALL_STACK = True
# django__query_wrapper.POST_EXECUTION_CALLBACK = (
#     insert_in_connections_extra_data_v1
# )
#
#
# class CustomQueryWrapperMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         init_connections_extra_data_v1()
#         connection.django_monkey_patches_dict[
#             "allocated_subsets_extra_data"
#         ] = {"per_sql_signature_v1": {},}
#         connection.django_monkey_patches_dict[
#             "allocated_subsets_key_callback"
#         ] = {"per_sql_signature_v1": get_sql_signature_v1,}
#         connection.django_monkey_patches_dict[
#             "allocated_subsets_init_callback"
#         ] = {
#             "per_sql_signature_v1": (
#                 lambda x, y: (
#                     get_extra_data_template_for_set_of_queries_v1(
#                         query_fields=[
#                             "sql",
#                             "params",
#                             "many",
#                             # "call_stack",
#                             get_light_call_stack_v1,
#                             "start_time",
#                             "result",
#                             "end_time",
#                             "duration",
#                             get_full_query_v1,
#                         ],
#                     )
#                 )
#             ),
#         }
#
#         connection.django_monkey_patches_dict[
#             "bottom_up_post_processing_callback"
#         ] = (
#             lambda x: (
#               apply_reorder_dict_by_total_duration_of_sub_dicts_to(
#                 x["allocated_subsets_extra_data"],
#                 "per_sql_signature_v1",
#               )
#             )
#         )
#         with ExitStack() as exit_stack:
#             wrap_connections(exit_stack, custom_query_wrapper_v1)
#             response = self.get_response(request)
#             synthetize_connections_extra_data_v1()
#             # dump to file or log:
#             # connections.django_monkey_patches_dict
#             # for connection_key in connections:
#             #     some_connection = connections[connection_key]
#             #     # dump to file or log:
#             #     # some_connection.django_monkey_patches_dict
#             return response
