from django.db import models


class TimeStampedModel(models.Model):
    """Model definition for BaseModel."""

    # TODO: Define fields here
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for BaseModel."""
        abstract = True
