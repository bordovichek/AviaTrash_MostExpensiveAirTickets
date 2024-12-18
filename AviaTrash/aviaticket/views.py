from django.core.paginator import Paginator
from django.views.generic import ListView
from .models import Flight

class FlightListView(ListView):
    model = Flight
    template_name = 'aviaticket/ticket_list.html'
    context_object_name = 'page_obj'
    paginate_by = 15
    ordering = ['day_of_departure']

    def get_queryset(self):
        return Flight.objects.all().order_by('day_of_departure')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flights = self.get_queryset()
        paginator = Paginator(flights, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context
