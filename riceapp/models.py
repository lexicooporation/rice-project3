from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ClassificationResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classifications')
    image = models.ImageField(upload_to='classification_images/')
    predicted_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    class_probabilities = models.JSONField()  # Store all class probabilities
    uploaded_at = models.DateTimeField(default=timezone.now)
    # Disease information (if available)
    disease_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.predicted_class} ({self.confidence}%)"