from itertools import islice, chain
import time
from numbers import Number


def split_list(list_, indexes=None):
    parts = []

    if list_[-1] != len(list_) - 1:
        indexes.append(None)
    last_end = 0

    for end in indexes:
        parts.append(list_[last_end:end])
        last_end = end

    if not len(parts[0]):
       parts.pop(0)
    return parts

def remove_duplicates(iterable):
    return list(dict.fromkeys(iterable))


def isnumber(string):
    try:
        return int(string)
    except:
        try:
            return float(string)
        except:
            return None


def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None
