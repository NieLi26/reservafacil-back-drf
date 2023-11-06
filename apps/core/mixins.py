from rest_framework.pagination import PageNumberPagination


class PaginationMixins(PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        return {
            'number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'has_previous': self.page.has_previous(),
            'has_next': self.page.has_next(),
            'paginate_by': self.page_size,
            'total_results': self.page.paginator.count,
            'start_index': self.page.start_index(),
            'end_index': self.page.end_index(),
            'results': data
        }
