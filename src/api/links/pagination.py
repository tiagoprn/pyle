from rest_framework.pagination import LimitOffsetPagination


class LimitOffsetPaginationWithMaxLimit(LimitOffsetPagination):
    max_limit = 50   # de minimum offset is at settings.py, and the maximum is the one declared here
