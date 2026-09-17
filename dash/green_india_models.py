from django.db import models


class GreenIndiaLead(models.Model):

    PARTNERSHIP_CHOICES = [
        ("csr_environment", "CSR Funding — Environmental Campaigns"),
        ("csr_women", "CSR Funding — Women Entrepreneurship (Women for Green)"),
        ("content_branding", "Content Co-Branding / Green Stories Series"),
        ("green_dialogues", "Green Dialogues — Policy Events & Podcasts"),
        ("green_action_labs", "Green Action Labs — On-Ground Programs"),
        ("green_network", "Green Network — Ecosystem Collaboration"),
        ("other", "Other / General Enquiry"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("engaged", "Engaged"),
    ]

    # Lead Details
    name = models.CharField(max_length=150)
    organisation = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    partnership_interest = models.CharField(
        max_length=50,
        choices=PARTNERSHIP_CHOICES
    )
    message = models.TextField(blank=True, null=True)

    # CRM Details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )
    engagement_notes = models.TextField(blank=True, null=True)

    # Form Tracking
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Green India Lead"
        verbose_name_plural = "Green India Leads"

    def __str__(self):
        return f"{self.name} - {self.organisation or 'Individual'}"