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


class Article(models.Model):
    """Store article metadata for historical tracking"""
    article_id = models.CharField(max_length=100, unique=True)
    project_id = models.CharField(max_length=50)
    summary = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField(null=True, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['project_id']),
            models.Index(fields=['article_id']),
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f"{self.article_id}: {self.summary[:50]}"


class ViewHistory(models.Model):
    """Store individual view timestamps for trend analysis"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField()
    synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['article', 'viewed_at']),
            models.Index(fields=['viewed_at']),
        ]
        # Prevent duplicate views from being stored
        unique_together = [['article', 'viewed_at']]

    def __str__(self):
        return f"{self.article.article_id} - {self.viewed_at}"
