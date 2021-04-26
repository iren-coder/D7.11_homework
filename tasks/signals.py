from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import TodoItem, Category, Priority


@receiver(post_save, sender=TodoItem)
def count_tasks_priority(sender, **kwargs):
    for category in Category.objects.all():
        Category.objects.filter(name=category.name).update(todos_count=TodoItem.objects.filter(category=category).count())

    for priority in Priority.objects.all():
        Priority.objects.filter(prior=priority.prior).update(todos_count=TodoItem.objects.filter(priority=priority).count())
