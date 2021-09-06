import hashlib


def parse_pos(pos):
    pos_c1 = pos.find(",")
    left = int(pos[1: pos_c1])
    pos_b1 = pos.find("]")
    top = int(pos[pos_c1 + 1: pos_b1])
    pos_c2 = pos.find(",", pos_b1)
    right = int(pos[pos_b1 + 2: pos_c2])
    bottom = int(pos[pos_c2 + 1: -1])
    return (top, left, bottom - top, right - left)


def hash_layout(layout):
    sanity_check_ok = True
    for field in ["bound", "act_id"]:
        if field not in layout:
            sanity_check_ok = False
            break
    if layout["act_id"] == "unknown" and not layout.get("focus", False):
        sanity_check_ok = False
    if not sanity_check_ok:
        print(layout)
        return None
    (s_t, s_l, s_h, s_w) = parse_pos(layout["bound"])
    check_elem_pos = s_h > 0 and s_w > 0
    if "vis" in layout:
        del layout["vis"]

    def traverse(layout, pool):
        if not layout:
            return None
        if "vis" in layout and layout["vis"] != 0:
            return None
        if "bound" not in layout:
            return None
        if check_elem_pos:
            (t, l, h, w) = parse_pos(layout["bound"])
            if t >= s_t + s_h or l >= s_l + s_w or s_t >= t + h or s_l >= l + w:
                return None
        pool.append(str(layout.get("id", "-1")))
        pool.append(str(layout["class"]))
        if "ch" in layout:
            for ch in layout["ch"]:
                traverse(ch, pool)

    ret = [layout.get("act_id", '?')]
    traverse(layout, ret)
    ret = sorted(ret)
    return hashlib.md5("".join(ret).encode()).hexdigest()


def hash_element(layout):
    ret = []

    def traverseX(layout):
        (s_t, s_l, s_h, s_w) = parse_pos(layout["bound"])
        check_elem_pos = s_h > 0 and s_w > 0
        if not layout:
            return None
        if "vis" in layout and layout["vis"] != 0:
            return None
        if "bound" not in layout:
            return None
        if check_elem_pos:
            (t, l, h, w) = parse_pos(layout["bound"])
            if t >= s_t + s_h or l >= s_l + s_w or s_t >= t + h or s_l >= l + w:
                return None
        if 'is_source' in layout:
            return layout
        if "ch" in layout:
            for ch in layout["ch"]:
                if traverseX(ch) != None:
                    return ch
        return None

    element = traverseX(layout)
    if element != None:
        ret.append(str(element.get("id", "-1")))
        ret.append(str(element["class"]))
    else:
        ret.append('back$')
    return hashlib.md5("".join(ret).encode()).hexdigest()
