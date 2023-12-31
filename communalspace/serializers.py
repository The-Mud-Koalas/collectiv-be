from django.core.paginator import Page


class PaginatorSerializer:
    def __init__(self, page: Page, model_serializer, total_page_number):
        self.data = {
            'total_pages': total_page_number,
            'current': page.number,
            'next': page.next_page_number() if page.has_next() else None,
            'previous': page.previous_page_number() if page.has_previous() else None,
            'results': model_serializer(page.object_list, many=True).data
        }

