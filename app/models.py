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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Project - {self.address}"

class ProposalUtility(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='proposal_utility'
    )
    openei_id = models.CharField(max_length=100)
    rate_name = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    start_date = models.DateField()
    pricing_matrix = models.JSONField()
    average_rate = models.FloatField()  # cents/kWh
    first_year_cost = models.FloatField()  # $

    def __str__(self):
        return f"Utility Proposal for {self.project.address}"