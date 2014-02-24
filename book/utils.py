def makeSubPages(pages, arranged):
    found = False
    for page in pages:
        if not page.parent: continue
        for apage in arranged:
            if page.parent == apage: # ok find.
                parent_pos = arranged.index(apage)

                before_depth = page.depth
                page.depth = apage.depth + 1
                after_depth = page.depth

                if before_depth != after_depth:
                    page.depth_changed = True

                arranged.insert(parent_pos + 1, page)
                pages.remove(page)
                found = True
                break
        if found: break
    if found: makeSubPages(pages, arranged)


def getTree(pages, rootpages=None):
    result = []
    if not rootpages:
        rootpages = pages.filter(parent=None).order_by("subject")
    for rootpage in rootpages:
        if rootpage.depth != 0: rootpage.depth_changed = True
        rootpage.depth = 0
        arranged = [rootpage]
        makeSubPages(list(pages), arranged)

        result.extend(arranged)

    for i, page in enumerate(result):
        if page.seq != i:
            page.seq = i
            page.seq_changed = True
        else:
            page.seq_changed = False
    return result


