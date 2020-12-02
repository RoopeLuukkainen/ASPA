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

    NOTE that:
    Useful iterable bodies are body, orelse, handlers and finalbody,
    however, also type_ignores, decorator_list, argument lists (e.g. 
    args and kw_defaults) will get sibling attributes.
    """
    for node in ast.walk(tree):
        for field in ast.iter_fields(node): # Yield a tuple of (fieldname, value)

            # There could be check that name of the field is either 
            # body, orelse, handlers or finalbody
            if(isinstance(field[1], (list, tuple))):
                previous_sibling = None
                last = None
                for child_node in field[1]:
                    if(previous_sibling):
                        previous_sibling.next_sibling = child_node
                    child_node.previous_sibling = previous_sibling
                    previous_sibling = child_node
                    last = child_node
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
def get_parent_instance(node, allowed, denied=tuple()):
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
        if(isinstance(temp, allowed)):
            parent = temp
            break
    return parent


def has_same_parent(node, others, allowed, denied=tuple()):
    # NOT YET TESTED
    parent = get_parent_instance(node, allowed, denied)
    if(isinstance(others, (list, tuple, set))):
        for i in others:
            if(not parent or (parent != get_parent_instance(i, allowed, denied))):
                return False
    elif(not parent or (parent != get_parent_instance(others, allowed, denied))):
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


def get_attribute_name(node, splitted=False):
    try:
        name = node.id
    except AttributeError:
        try:
            name_parts = []
            temp = node
            while hasattr(temp, "attr"):
                name_parts.insert(0, temp.attr)
                temp = temp.value
            if(splitted):
                name = [temp.id] + name_parts
            else:
                name = ".".join([temp.id] + name_parts)
        except AttributeError:
            raise
        finally:
            name_parts.clear()
    return name