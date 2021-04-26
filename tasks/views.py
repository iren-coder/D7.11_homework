import functools
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from tasks.models import TodoItem, Category, Priority
from django.views.decorators.cache import cache_page


@functools.lru_cache(maxsize=128, typed=False)
def index(request):
    from django.db.models import Count

    counts = Category.objects.annotate(total_tasks=Count('todoitem')).order_by("-total_tasks")
    counts = {c.name: c.total_tasks for c in counts}

    priorities = Priority.objects.all()

    return render(request, "tasks/index.html", {"counts": counts, "priorities": priorities})


# @property
@functools.lru_cache(maxsize=128, typed=False)
def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    categories = []
    for cat in Category.objects.all():
        if cat not in categories:
            categories.append(cat)

    return render(
        request,
        "tasks/list_by_cat.html",
        {"category": cat, "tasks": tasks, "categories": categories},
    )


class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    @functools.lru_cache(maxsize=128, typed=False)
    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    @functools.lru_cache(maxsize=128, typed=False)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = []
        for cat in Category.objects.all():
            if cat not in categories:
                categories.append(cat)
        context["categories"] = categories

        return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"


@cache_page(300)
def datetime(request):
    from datetime import datetime
    template_name = "tasks/datetime.html"
    datetimenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render(request, template_name, {"datetimenow": datetimenow})

