import json_fix

object_lookup = {}

class Options:
    def __init__(self, data=None, default=None, _auto_generated=False, _parent_callbacks=None):
        self.default  = default or (lambda key, self_, *args: Object(
            Options(_auto_generated=True,_parent_callbacks=[self_, key])
        ))
        self.data            = data
        self._auto_generated = _auto_generated
        self._parent_callbacks = _parent_callbacks or []

    
class Object:
    def __init__(self, options_or_dict=None, **kwargs):
        this = id(self)
        options = options_or_dict if isinstance(options_or_dict, Options         ) else Options()
        a_dict  = options_or_dict if isinstance(options_or_dict, (dict, Object)) else {}
        a_dict  = to_dict(a_dict)
        a_dict.update(kwargs)
        
        self.__class__ = ObjectClass
        object_lookup[this] = (tuple(), a_dict, options.default, {}, options._parent_callbacks, options._auto_generated, len(a_dict) == 0)

class ObjectClass(Object):
    # this is "more powerful" than __getattr__
    def __getattribute__(self, key):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        if key in data:
            return data[key]
        for each_parent in lineage:
            if key in each_parent:
                return each_parent[key]
            if hasattr(each_parent, key):
                return getattr(each_parent, key)
        try:
            return object.__getattribute__(self, key)
        except Exception as error:
            return self[key]
    
    def __setattr__(self, key, value):
        this = id(self)
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[this]
        if untouched:
            if len(parent_callbacks):
                for each_parent, each_key in parent_callbacks:
                    each_parent[each_key] = self
                    parent_id = id(each_parent)
                    parent_lineage, parent_data, parent_default, parent_uninitilized_children, parent_parent_callbacks, parent_was_autogenerated, parent_untouched = object_lookup[parent_id]
                    if each_key in parent_uninitilized_children:
                        del parent_uninitilized_children[each_key]
                    object_lookup[parent_id] = (parent_lineage, parent_data, parent_default, parent_uninitilized_children, parent_parent_callbacks, parent_was_autogenerated, False)
            # touched
            object_lookup[this] = (lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, False)
        
        data[key] = value
    
    def __setitem__(self, key, value):
        this = id(self)
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[this]
        if untouched:
            if len(parent_callbacks):
                for each_parent, each_key in parent_callbacks:
                    each_parent[each_key] = self
                    parent_id = id(each_parent)
                    parent_lineage, parent_data, parent_default, parent_uninitilized_children, parent_parent_callbacks, parent_was_autogenerated, parent_untouched = object_lookup[parent_id]
                    if each_key in parent_uninitilized_children:
                        del parent_uninitilized_children[each_key]
                    object_lookup[parent_id] = (parent_lineage, parent_data, parent_default, parent_uninitilized_children, parent_parent_callbacks, parent_was_autogenerated, False)
            # touched
            object_lookup[this] = (lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, False)
        
        data[key] = value
    
    def __getattr__(self, key):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        if key in data:
            return data[key]
        for each_parent in lineage:
            if key in each_parent:
                return each_parent[key]
            if hasattr(each_parent, key):
                return getattr(each_parent, key)
        
        if key not in uninitilized_children:
            uninitilized_children[key] = default_function(key, self)
        return uninitilized_children[key]
    
    def __getitem__(self, key):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        if key in data:
            return data[key]
        for each_parent in lineage:
            if key in each_parent:
                return each_parent[key]
            if hasattr(each_parent, key):
                return getattr(each_parent, key)
        
        if key not in uninitilized_children:
            uninitilized_children[key] = default_function(key, self)
        return uninitilized_children[key]
            
    def __len__(self):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        return len(data)
    
    def __contains__(self, key):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        return key in data
    
    def __delattr__(self, key):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        
        if key in data:
            del data[key]
        if key in uninitilized_children:
            child_id = id(uninitilized_children[key])
            # detach self from the UninitilizedChild
            parent_callbacks_for[child_id] = [
                (each_parent, each_key)
                    for each_parent, each_key in parent_callbacks_for[child_id]
                    if each_key != key
            ]
            del uninitilized_children[key]
    
    def __delitem__(self, key):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        
        if key in data:
            del data[key]
        if key in uninitilized_children:
            child_id = id(uninitilized_children[key])
            # detach self from the UninitilizedChild
            parent_callbacks_for[child_id] = [
                (each_parent, each_key)
                    for each_parent, each_key in parent_callbacks_for[child_id]
                    if each_key != key
            ]
            del uninitilized_children[key]
        
    # the truthy value of obj
    def __nonzero__(self):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        if was_autogenerated and uninitilized_children:
            return False
        else:
            return True
    
    def __iter__(self):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        return data.items()
    
    def __reversed__(self):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        return reversed(data.items())
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        if len(data) == 0:
            return "{}"
        return _stringify(data)
    
    def __eq__(self, other):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        return data == other
    
    def __add__(self, other):
        # this is what makes += work
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        
        if untouched and was_autogenerated:
            for each_parent, each_key in parent_callbacks:
                each_parent[each_key] = other
                return other
        else:
            if isinstance(other, dict):
                data.update(other)
                return self
            elif isinstance(other, Object):
                data.update(to_dict(other))
                return self
            else:
                # TODO: should probably be an error
                pass
    
    def __json__(self):
        lineage, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[id(self)]
        return data


def lineage(obj):
    this = id(obj)
    if this in object_lookup:
        lineage_, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[this]
        return lineage_
    else:
        return tuple()

def add_ancestor(obj, *, ancestor):
    this = id(obj)
    if this in object_lookup:
        lineage_, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[this]
        object_lookup[this] = ((*lineage_, ancestor), data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched)
    return obj

def to_dict(obj):
    this = id(obj)
    if this in object_lookup:
        lineage_, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[this]
        return data
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, (tuple, list)):
        return {
            index: each
                for index, each in enumerate(obj)
        }
    if isinstance(obj, (set, frozenset)):
        return {
            each: True
                for each in obj
        }

def length(obj):
    return len(to_dict(obj))

def size(obj):
    return len(to_dict(obj))

def keys(obj):
    return list(to_dict(obj).keys())

def values(obj):
    return list(to_dict(obj).values())

def items(obj):
    return list(to_dict(obj).items())

def overwrite(obj, *args):
    data = to_dict(obj)
    for each in args:
        data.update(to_dict(each))
    return obj

def merge(*args):
    return overwrite(Object(), *args)

def copy(obj):
    original_id = id(obj)
    new_obj     = Object()
    new_id      = id(new_obj)
    
    lineage_, data, default_function, uninitilized_children, parent_callbacks, was_autogenerated, untouched = object_lookup[original_id]
    object_lookup[new_id] = (lineage_, dict(data), default_function, dict(uninitilized_children), list(parent_callbacks), False, False)
    
    return new_obj

def clear(obj):
    a_dict = to_dict(obj)
    a_dict.clear()
    return obj

def sort_keys(obj):
    a_dict = to_dict(obj)
    keys = sorted(list(a_dict.keys()))
    dict_copy = {}
    # save copy and remove
    for each_key in keys:
        dict_copy[each_key] = a_dict[each_key]
    a_dict.clear()
    # re-add in correct order
    for each_key in keys:
        a_dict[each_key] = dict_copy[each_key]
    return obj
    
# TODO
# def sort_values(obj):
#     pass

# TODO
# def grab(key_list, default):
#     pass

# TODO
# def shove(key_list, value):
#     pass

# TODO
# def recursive_merge(obj):
#     pass

Object.lineage      = lineage
Object.add_ancestor = add_ancestor
Object.to_dict      = to_dict
Object.length       = length
Object.size         = size
Object.keys         = keys
Object.values       = values
Object.items        = items
Object.overwrite    = overwrite
Object.merge        = merge
Object.copy         = copy
Object.clear        = clear
Object.sort_keys    = sort_keys

def _indent(string, by):
    indent_string = (" "*by)
    return indent_string + string.replace("\n", "\n"+indent_string)

def _stringify(value):
    onelineify_threshold = 50 # characters (of inner content)
    length = 0
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, Object):
        if len(value) == 0:
            return "{}"
        items = value if isinstance(value, Object) else value.items()
        output = "{\n"
        for each_key, each_value in items:
            element_string = _stringify(each_key) + ": " + _stringify(each_value)
            length += len(element_string)+2
            output += _indent(element_string, by=4) + ", \n"
        output += "}"
        if length < onelineify_threshold:
            output = output.replace("\n    ","").replace("\n","")
        return output
    elif isinstance(value, dict):
        if len(value) == 0:
            return "{}"
        items = value if isinstance(value, Object) else value.items()
        output = "{\n"
        for each_key, each_value in items:
            element_string = _stringify(each_key) + ": " + _stringify(each_value)
            length += len(element_string)+2
            output += _indent(element_string, by=4) + ", \n"
        output += "}"
        if length < onelineify_threshold:
            output = output.replace("\n    ","").replace("\n","")
        return output
    elif isinstance(value, list):
        if len(value) == 0:
            return "[]"
        output = "[\n"
        for each_value in value:
            element_string = _stringify(each_value)
            length += len(element_string)+2
            output += _indent(element_string, by=4) + ", \n"
        output += "]"
        if length < onelineify_threshold:
            output = output.replace("\n    ","").replace("\n","")
        return output
    elif isinstance(value, set):
        if len(value) == 0:
            return "set([])"
        output = "set([\n"
        for each_value in value:
            element_string = _stringify(each_value)
            length += len(element_string)+2
            output += _indent(element_string, by=4) + ", \n"
        output += "])"
        if length < onelineify_threshold:
            output = output.replace("\n    ","").replace("\n","")
        return output
    elif isinstance(value, tuple):
        if len(value) == 0:
            return "tuple()"
        output = "(\n"
        for each_value in value:
            element_string = _stringify(each_value)
            length += len(element_string)+2
            output += _indent(element_string, by=4) + ", \n"
        output += ")"
        if length < onelineify_threshold:
            output = output.replace("\n    ","").replace("\n","")
        return output
    else:
        try:
            debug_string = value.__repr__()
        except Exception as error:
            from io import StringIO
            import builtins
            string_stream = StringIO()
            builtins.print(value, file=string_stream)
            debug_string = string_stream.getvalue()
        
        # TODO: handle "<slot wrapper '__repr__' of 'object' objects>"
        if debug_string.startswith("<class") and hasattr(value, "__name__"):
            return value.__name__
        if debug_string.startswith("<function <lambda>"):
            return "(lambda)"
        if debug_string.startswith("<function") and hasattr(value, "__name__"):
            return value.__name__
        if debug_string.startswith("<module") and hasattr(value, "__name__"):
            _, *file_path, _, _ = debug_string.split(" ")[-1]
            file_path = "".join(file_path)
            return f"module(name='{value.__name__}', path='{file_path}')"
        
        space_split = debug_string.split(" ")
        if len(space_split) >= 4 and debug_string[0] == "<" and debug_string[-1] == ">":
            
            if space_split[-1].startswith("0x") and space_split[-1] == "at":
                _, *name_pieces = space_split[0]
                *parts, name = "".join(name_pieces).split(".")
                parts_str = ".".join(parts)
                return f'{name}(from="{parts_str}")'
        
        return debug_string

