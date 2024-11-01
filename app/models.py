from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=255)
    consumption = models.IntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(10000)
        ]
    )
    percentage = models.FloatField(
        validators=[
            MinValueValidator(4.0),
            MaxValueValidator(10.0)
        ]
    )
    selected_rate = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Project - {self.address}"

class ProposalUtility(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='proposal'
    )
    openei_id = models.CharField(max_length=100)
    rate_name = models.CharField(max_length=255)
    average_rate = models.FloatField()  # cents/kWh
    first_year_cost = models.FloatField()  # $
    pricing_matrix = models.JSONField(
        null=True,
        blank=True,
        help_text="Stores the complete rate structure including time periods and tiers"
    )

    def __str__(self):
        return f"Utility Proposal for {self.project.address}"
