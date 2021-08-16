"""Library containing utility functions for static analysers."""

import ast

# AST improvement utilities
def add_parents(tree):
    """Function to add parent_node attribute to each node in AST."""

    for node in ast.walk(tree):
        for child_node in ast.iter_child_nodes(node):
            child_node.parent_node = node


def add_siblings(tree):
    """
    Function to add previous_sibling and next_sibling attributes to each
    node in AST, which are inside iterable body of parent node. For
    nodes which are inside these iterable bodies, if no there is no
    previous or next sibling the respective value will be None.

    NOTE 1:
    Useful iterable bodies are body, orelse, handlers and finalbody,
    however, also type_ignores, decorator_list, argument lists (e.g.
    args and kw_defaults) will get sibling attributes.

    NOTE 2:
    In addition global-keyword creates Global node which has str typed
    elements and this creates attribute error when trying to assign
    values to next_sibling and previous_sibling attrbutes.
    """

    for node in ast.walk(tree):
        for field in ast.iter_fields(node): # Yield a tuple of (fieldname, value)

            # There could be check that name of the field is either
            # body, orelse, handlers or finalbody
            # but not in 'names' used in Global node.
            if(isinstance(field[1], (list, tuple))):
                previous_sibling = last = None
                for child_node in field[1]:
                    try:
                        if(previous_sibling):
                            previous_sibling.next_sibling = child_node

                        child_node.previous_sibling = previous_sibling
                        previous_sibling = last = child_node

                    # This error may occur e.g. when
                    #   'str' object has no attribute 'previous_sibling'
                    # which is case e.g. with global-keyword creating node
                    #   Global(names=['with_global_keyword']),
                    except AttributeError:
                        pass
                if(last):
                    last.next_sibling = None

    # # Print siblings
    # for node in ast.walk(tree):
    #     try:
    #         pl = nl = ""
    #         if(node.previous_sibling):
    #             pl = node.previous_sibling.lineno

    #         if(node.next_sibling):
    #             nl = node.next_sibling.lineno

    #         print(f"{node.lineno:4}: {node}, PREV {pl}: {node.previous_sibling}, NEXT {nl}: {node.next_sibling}")
    #     except AttributeError:
    #         print("---", node)

# AST search utilities
def get_parent(node, allowed, denied=tuple()):
    """
    Function to get parent instance of a node.
    'allowed' argument defines type of the desired parent, it should be
    any of the ast node types and can be tuple. Optional argument '
    denied' defines not allowed parents as ast node types.

    If allowed type is found, returns found node, if denied type is
    found first or neither of them is found returns None.
    """

    temp = node
    parent = None
    while(hasattr(temp, "parent_node") and not isinstance(temp, denied)):
        temp = temp.parent_node
        if isinstance(temp, allowed):
            parent = temp
            break
    return parent


def get_outer_parent(node, allowed, **kwargs):
    """
    Function to get outermost parent instance with allowed type. Uses
    get_parent function until denied is found or no more allowed type is
    found.

    Return:
    IF parent is found: outer_parent - ast Node - Outermost parent node
                        of a reguested type.
    ELSE: node - the parameter node itself.
    """

    outer_parent = node
    while (temp := get_parent(outer_parent, allowed, **kwargs)):
        outer_parent = temp
    return outer_parent


def has_same_parent(node, others, allowed, **kwargs): #denied=tuple()):
    # NOT YET TESTED
    parent = get_parent(node, allowed, **kwargs)
    if isinstance(others, (list, tuple, set)):
        for i in others:
            if not parent or (parent != get_parent(i, allowed, **kwargs)):
                return False
    elif not parent or (parent != get_parent(others, allowed, **kwargs)):
        return False
    return True


def get_child_instance(node, allowed, denied=tuple()):
    """
    Function to get child instance of a node.
    'allowed' argument defines type of the desired child, it should be
    any of the ast node types and can be tuple. Optional argument '
    denied' defines not allowed children as ast node types.

    If allowed type is found, returns found node, if denied type is
    found first or neither of them is found returns None.
    """

    child = None
    for child_node in ast.walk(node):
        if(isinstance(child_node, allowed)):
            child = child_node
            break
        elif(isinstance(child_node, denied)):
            break
    return child

# AST tests and value gets
def is_always_true(test):
    """
    Function to define cases where conditional test is always true.
    'test' should be ast.Compare type or ast.Constant. Returns truth
    value.
    TODO: Add more always true cases.
    """

    is_true = False
    try:
        if(isinstance(test, ast.Constant) and test.value == True):
            is_true = True
    except AttributeError:
        pass
    return is_true


def is_added_to_data_structure(node, data_stuct_node, data_stuct_name, add_attrs):
    """
    Helper function to detect if node is added to a datastucture.
    So far tested and commented only with ast.List.
    """

    is_added = False
    parent = get_parent(node, (data_stuct_node, ast.Call))

    # This detect list_name += [...] and list_name = list_name + [...]
    # and cases with extend where list_name.extend([...])
    if(isinstance(parent, data_stuct_node)):
        is_added = True

    # This detect list_name.append() and list_name.insert()
    # and in some cases list_name.extend()
    elif(isinstance(parent, ast.Call)
            and isinstance(parent.func, (ast.Attribute))
            and parent.func.attr in add_attrs):
        is_added = True

    #  This detect all cases inside list(...)-call
    elif(isinstance(parent, ast.Call) and parent.func.id == data_stuct_name):
        is_added = True

    return is_added


def get_attribute_name(node, splitted=False, omit_n_last=0):
    """
    Function to parse name from attributes. If the is only single Name
    node then node.id is enough. Otherwise add all attrs in front of
    the id.

    Optional parameters:
    1. "splitted" is used get result as list instead of joined string,
        i.e. "[like, this]" instead of "like.this".
    2. "omit_n_last" is used to leave n last attrs out.
    """

    try:
        name = node.id
    except AttributeError:
        # If omit_n_last != 0 then it is changed to negative
        # otherwise it will be None
        # This is used in substring [:-n] where [:None] is same as [:]
        omit_n_last = -omit_n_last or None

        try:
            name_parts = []
            temp = node
            while hasattr(temp, "attr"):
                name_parts.insert(0, temp.attr)
                temp = temp.value

            name = [temp.id] + name_parts[:omit_n_last]
            if not splitted:
                name = ".".join(name)

        except AttributeError:
            raise
        finally:
            name_parts.clear()
    return name


def get_class_name(node, **kwargs):
    """
    Function to get name of a class. The class can be 'called' with or
    without parenthesis. When parenthesis are not used creates
    ast.Attribute node and when they are used creates ast.Call node.
    Uses get_attribute_name function but with different node parameter
    depending on the case.

    Arguments:
    kwargs can be "splitted" or "omit_n_last".

    Return values:
    On success: name of the class (and trailing attributes depending on
                **kwargs.)
    On failure: empty str ''.
    """

    try:
        name = get_attribute_name(
            node,
            **kwargs
        )
    except AttributeError:
        try:
            name = get_attribute_name(
                node.func,
                **kwargs
            )
        except AttributeError:
            name = ""
    return name

####################################################################
# Statistic functions
def calculate_statistics(results):
    statistics = {}
    found_violation = False

    for result in results:
        for violation in result[1]:
            try:
                if violation.status == False: # = violation
                    try:
                        statistics[violation.vid] += 1
                    except KeyError:
                        statistics[violation.vid] = 1
                    found_violation = True
            except AttributeError as e:
                print("error....", e) # TODO remove this
                pass

    statistics["all_ok"] = not found_violation
    statistics["file_count"] = 1
    return statistics

def sum_statistics(all_statistics, student, new):
    """
    """

    # def add_to_dict(d, k, v):
    #     try:
    #         d[k] += v
    #     except KeyError:
    #         d[k] = v
    #     return None

    submission = all_statistics.setdefault(student, {})

    # add_to_dict(all_statistics["ALL"], "file_count", 1)

    for key, value in new.items():
        # TODO setting absolute value / number of submissions where this occur
        # v = value
        v = 1 # With this and all_ok does not work because if it was False
              # it is counted as 0 now it will be forced to be 1.
        try:
            all_statistics["ALL"][key] += v
        except KeyError:
            all_statistics["ALL"][key] = v

        try:
            submission[key] += value
        except KeyError:
            submission[key] = value

def print_statistics(statistics):
    try:
        import pprint
        pprint.pprint(statistics)
    except (ImportError, Exception):
        print(statistics)
    return None

####################################################################
#  Debug functions
def dump_node(node):
    try:
        print(f"{node.lineno}: {ast.dump(node)}")
    except AttributeError:
        print(f"No line: {ast.dump(node)}")
