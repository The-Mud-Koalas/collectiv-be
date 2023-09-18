from django.core.paginator import Paginator
from .settings import DEFAULT_PAGE_LIMIT


def paginate_result(results, limit=DEFAULT_PAGE_LIMIT, page_number=1):
    if limit <= 1:
        limit = 1

    paginator = Paginator(results, limit)
    if not (1 <= page_number <= paginator.num_pages):
        page_number = 1

    return paginator.page(page_number)
