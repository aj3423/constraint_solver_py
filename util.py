# returns items from iter1 that are not in iter2
def exclude(iter1, iter2):
    # Consume iter2 into a set
    set2 = set(iter2)
    # Collect items from iter1 not in set2
    result = []
    for item in iter1:
        if item not in set2:
            result.append(item)
    return result
