from django.db import models

# We'll use session-based storage for tokens instead of database models
# This is more secure and doesn't persist sensitive credentials

class AnalysisCache(models.Model):
    """Cache analysis results to avoid repeated API calls"""
    project_id = models.CharField(max_length=50)
    threshold_days = models.IntegerField()
    analysis_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_id', 'threshold_days']),
        ]

    def __str__(self):
        return f"{self.project_id} - {self.threshold_days} days ({self.created_at})"
