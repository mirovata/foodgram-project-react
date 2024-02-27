from rest_framework.pagination import PageNumberPagination

from core.constants import PAGE_PARAM, PAGE_SIZE


class PageNumberAndLimitPagination(PageNumberPagination):

    page_size = PAGE_SIZE
    page_size_query_param = PAGE_PARAM
