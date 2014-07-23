from __future__ import division


def compare_objects(left, right):
    """
    Compare two objects and return a dict describing the differences.
    Only json-like objects are supported at the moment.
    """

    # The objects are equal: we don't care about the contents
    if left == right:
        return {'distance': 0.0, 'left': left, 'right': right}

    if _are_both(left, right, dict):
        return _compare_dicts(left, right)

    if _are_both(left, right, (list, tuple)):
        return _compare_sequences(left, right)

    # The objects are completely different
    return {'distance': 1.0, 'left': left, 'right': right}


def format_diff(diff):
    output = []

    def _format_diff(diff, indent=0):
        if diff['distance'] == 0:
            return
        _type = diff.get('type')
        ind = u"    " * indent

        if _type == 'dict':
            output.append(ind + u"Distance: {0}".format(diff['distance']))
            output.append(ind + u"Equal {0}".format(len(diff['equal'])))
            output.append(ind + u"Added")
            for key, val in diff['added'].iteritems():
                output.append(ind + u"    {0!r}: {1!r}".format(key, val))
            output.append(ind + u"Removed")
            for key, val in diff['removed'].iteritems():
                output.append(ind + u"    {0!r}: {1!r}".format(key, val))
            output.append(ind + u"Changes")
            for key, val in diff['changes'].iteritems():
                output.append(ind + u"    {0!r}:".format(key))
                _format_diff(val, indent + 2)
            return

        if _type == 'list':
            output.append(ind + u"Distance: {0}".format(diff['distance']))
            output.append(ind + u"Equal: {0}".format(len(diff['equal'])))

            if len(diff['added']):
                output.append(ind + u"Added")
                for key in diff['added']:
                    output.append(ind + u"    {0!r}: {1!r}".format(key, val))

            output.append(ind + u"Removed")
            for key in diff['removed']:
                output.append(ind + u"    {0!r}: {1!r}".format(key, val))

            output.append(ind + u"Reordered")
            for key, item in diff['changes'].iteritems():
                if item['distance'] != 0:
                    continue
                output.append(ind + u"    {0} -> {1}".format(key, item['pos']))

            output.append(ind + u"Changes")
            for key, item in diff['changes'].iteritems():
                if item['distance'] == 0:
                    continue
                output.append(ind + u"    {0} -> {1}".format(key, item['pos']))
                _format_diff(item['diff'], indent + 2)
            return

        if diff['distance'] > 0:
            output.append(ind + u"Left: {0!r}".format(diff['left']))
            output.append(ind + u"Right: {0!r}".format(diff['right']))
            return

    _format_diff(diff)
    return u"\n".join(output)


def _are_both(left, right, types):
    return isinstance(left, types) and isinstance(right, types)


def _compare_dicts(left, right):
    left_only = {}
    right_only = {}
    differences = {}
    equal = []

    all_keys = set(left.keys()).union(set(right.keys()))
    for key in all_keys:
        if key not in left:
            right_only[key] = right[key]
        elif key not in right:
            left_only[key] = left[key]
        else:
            diff = compare_objects(left[key], right[key])
            if diff['distance'] == 0:
                equal.append(key)
            else:
                differences[key] = diff

    total = len(all_keys)
    diff_count = len(differences) + len(left_only) + len(right_only)
    return {
        'type': 'dict',
        'distance': (diff_count / total) if total != 0 else 0,
        'added': right_only,
        'removed': left_only,
        'changed': differences.keys(),
        'equal': equal,
        'changes': differences,
        'total': len(all_keys),
    }


def _compare_sequences(left, right):
    """
    To compare two sequences:

    - Create comparison "pairs": (distance, left_id, right_id, diff)
    - Start taking pairs from the top if they both contain items
      for the first time
    """

    all_pairs = []
    for lid, litem in enumerate(left):
        for rid, ritem in enumerate(right):
            diff = compare_objects(litem, ritem)
            all_pairs.append((diff['distance'], lid, rid, diff))
    all_pairs.sort(key=lambda x: x[0])

    unproc_left = set(xrange(len(left)))
    unproc_right = set(xrange(len(right)))

    # Take only pairs containing unused items
    filtered_pairs = []
    for dist, lid, rid, diff in all_pairs:
        if (lid in unproc_left) and (rid in unproc_right):
            unproc_left.remove(lid)
            unproc_right.remove(rid)
            filtered_pairs.append((dist, lid, rid, diff))

    assert len(filtered_pairs) == min(len(left), len(right))

    # Take items left in "unproc" sets as items that have been
    # removed.
    left_only = list(unproc_left)
    right_only = list(unproc_right)

    # Extract differences (items changed or moved)
    differences = {}
    equal = []
    for (dist, lid, rid, diff) in filtered_pairs:
        if dist == 0 and (lid == rid):
            # Same thing in the same place
            equal.append(lid)

        elif dist < 1.0:
            # Something changed, but the item was the same
            differences[lid] = {
                'prev_pos': lid,
                'pos': rid,
                'distance': dist,
                'diff': diff}

        else:
            left_only.append(lid)
            right_only.append(rid)

    diff_count = len(left_only) + len(right_only) + len(differences)
    assert diff_count == len(left_only) + len(right_only) + len(differences)

    total = diff_count + len(equal)
    distance = (diff_count / total) if total != 0 else 0

    return {
        'type': 'list',
        'distance': distance,
        'added': right_only,
        'removed': left_only,
        'changed': differences.keys(),
        'equal': equal,
        'changes': differences,
        'total': total,
    }
