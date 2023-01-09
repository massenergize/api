from django.core.paginator import Paginator, EmptyPage

from _main_.utils.common import serialize_all
PAGINATION_LIMIT = 50

def paginate(queryset, page):
    try:
        p = Paginator(queryset, PAGINATION_LIMIT)
        items = []
        pag = p.page(page)
        meta = {
            "next":pag.next_page_number() if pag.has_next() else pag.paginator.num_pages,
            "count":len(queryset)
        }
        items = serialize_all(list(pag))
        to_return = {
            'meta':meta,
            "items": items
        }
        
        return to_return
    except EmptyPage:
        return p.get_page(1).object_list


