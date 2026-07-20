from django.db import models
from django.conf import settings
from django.utils import timezone
class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'À faire'
        IN_PROGRESS = 'in_progress', 'En cours'
        COMPLETED = 'completed', 'Terminée'
    class Priority(models.TextChoices):
        LOW = 'low', 'Basse'
        MEDIUM = 'medium', 'Moyenne'
        HIGH = 'high', 'Haute'
        URGENT = 'urgent', 'Urgente'
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Priorité"
    )
    due_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date limite"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Auteur"
    )
    is_completed = models.BooleanField(default=False, verbose_name="Terminée")
    
    class Meta:
        ordering = ['-priority', 'due_date']
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """Check if task is overdue / Vérifie si la tâche a dépassé la date limite"""
        if self.due_date and self.status != self.Status.COMPLETED:
            return timezone.now() > self.due_date
        return False
