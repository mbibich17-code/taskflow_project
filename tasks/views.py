from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

from .models import Task
from .forms import TaskForm, CustomUserCreationForm


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10  
    def get_queryset(self):
        queryset = Task.objects.filter(author=self.request.user)
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        priority_filter = self.request.GET.get('priority', '')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        sort_by = self.request.GET.get('sort', '')
        if sort_by == 'due_date':
            queryset = queryset.order_by('due_date')
        elif sort_by == 'priority':
            queryset = queryset.order_by('-priority')
        elif sort_by == 'created_at':
            queryset = queryset.order_by('-created_at')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tasks = Task.objects.filter(author=self.request.user)
        context['total_tasks'] = user_tasks.count()
        context['pending_tasks'] = user_tasks.filter(status=Task.Status.PENDING).count()
        context['in_progress_tasks'] = user_tasks.filter(status=Task.Status.IN_PROGRESS).count()
        context['completed_tasks'] = user_tasks.filter(status=Task.Status.COMPLETED).count()
        overdue_count = 0
        for task in user_tasks:
            if task.is_overdue():
                overdue_count += 1
        context['overdue_tasks'] = overdue_count
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['priority_filter'] = self.request.GET.get('priority', '')
        context['sort_by'] = self.request.GET.get('sort', '')
        return context


class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        return self.request.user == task.author


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_create.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.status == Task.Status.COMPLETED:
            form.instance.is_completed = True
            
        messages.success(self.request, "La tâche a été créée avec succès !")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_update.html'
    success_url = reverse_lazy('task_list')

    def test_func(self):
        task = self.get_object()
        return self.request.user == task.author

    def form_valid(self, form):
        if form.instance.status == Task.Status.COMPLETED:
            form.instance.is_completed = True
        else:
            form.instance.is_completed = False
            
        messages.success(self.request, "La tâche a été modifiée avec succès !")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        return self.request.user == task.author

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "La tâche a été supprimée avec succès !")
        return super().delete(request, *args, **kwargs)


def register(request):
    """User registration view / Vue d'inscription d'utilisateur"""
    if request.user.is_authenticated:
        return redirect('task_list')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Compte créé avec succès pour {user.username} ! Vous pouvez maintenant vous connecter.")
            return redirect('login')
        else:
            messages.error(request, "Erreur lors de la création du compte. Veuillez vérifier vos informations.")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})
