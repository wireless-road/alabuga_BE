from flask import url_for, request


def build_pages_dict(p, page, per_page):
    return {
        "page": page,
        "per_page": per_page,
        "total": p.total,
        "pages": p.pages,
        "prev_url": url_for(
            str(request.endpoint),
            page=p.prev_num,
            per_page=per_page,
            expanded=1,
            _external=True,
        )
        if p.has_prev
        else None,
        "next_url": url_for(
            str(request.endpoint),
            page=p.next_num,
            per_page=per_page,
            expanded=1,
            _external=True,
        )
        if p.has_next
        else None,
        "first_url": url_for(
            str(request.endpoint), page=1, per_page=per_page, expanded=1, _external=True
        ),
        "last_url": url_for(
            str(request.endpoint),
            page=p.pages,
            per_page=per_page,
            expanded=1,
            _external=True,
        ),
    }
