from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator  # Pagination


class PaginationMixin:
    paginate_by = 1

    def paginate_queryset(self, queryset, page_number):
        paginator = Paginator(queryset, self.paginate_by)

        # Verificar si el número de página está fuera del rango válido
        if int(page_number) > paginator.num_pages or int(page_number) < 1:
            page_number = 1

        page_obj = paginator.get_page(page_number)

        return {
            'page_obj': page_obj,
            'paginator': {
                'page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'paginate_by': self.paginate_by,
                'total_results': paginator.count,
                'start_index': page_obj.start_index(),
                'end_index': page_obj.end_index()
            }
        }


class CustomPermissionRequiredMixin(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return redirect("booking:dashboard")
        return super().dispatch(request, *args, **kwargs) 


class CustomUserPassesTestMixin:
    list_methods = []

    # def dispatch(self, request, *args, **kwargs):
    #     response = {}
    #     status = None
    #     if request.method in self.list_methods and not self.has_group(request, 'Administrador'):
    #         status = 403
    #         response['error'] = 'No tiene permiso para  realizar esta accion'
    #         return JsonResponse(response, status=status)
    #     return super().dispatch(request, *args, **kwargs)

    # def has_group(self, request, name_group):
    #     if request.user.groups.filter(name=name_group).exists():
    #         return True
    #     return False

    # def is_allowed(self, request, name_group):
    #     if request.user.groups.filter(name=name_group).exists():
    #         return True
    #     return False


class ValidatePermissionRequiredMixin:
    permission_required = ""
    url_redirect = None

    def get_perms(self):
        perms = []
        if isinstance(self.permission_required, str):
            perms.append(self.permission_required)
        else:
            perms = list(self.permission_required)
        return perms

    def get_url_redirect(self):
        if self.url_redirect is None:
            return reverse_lazy("erp:home")
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        request = get_current_request()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs) 

        if "group" in request.session:
            group = request.session['group']

            perms = self.get_perms()  

            for p in perms:
                if not group.permissions.filter(codename=p).exists():
                    messages.error(request, "No tiene permiso para ingresar a este modulo")
                    return HttpResponseRedirect(self.get_url_redirect())
            return super().dispatch(request, *args, **kwargs)  
        messages.error(request, "No tiene permiso para ingresar a este modulo")
        return HttpResponseRedirect(self.get_url_redirect())
