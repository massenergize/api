from django.core.paginator import Paginator, EmptyPage
from _main_.utils.common import serialize_all


def paginate(queryset, pagination_data):
    try:
        limit = pagination_data.get('limit')
        page = pagination_data.get('next_page')
        paginator = Paginator(queryset, limit)
        items = []
        next_page = paginator.page(page)
        cursor = {
            "next": next_page.next_page_number() if next_page.has_next() else next_page.paginator.num_pages,
            "count":len(queryset)
        }
        items = serialize_all(list(next_page))
        to_return = {
            'cursor':cursor,
            "items": items
        }
        
        return to_return
    except EmptyPage:
        return {}


