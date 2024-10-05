from django.db import models

class UserForm(models.Model):
    team_name = models.CharField(max_length=255)
    team_leader = models.CharField(max_length=255)
    leader_contact = models.CharField(max_length=15)
    email = models.EmailField()
    college_name = models.CharField(max_length=255)
    member1 = models.CharField(max_length=255, blank=True, null=True)  # Optional
    member1_contact = models.CharField(max_length=15, blank=True, null=True)  # Optional
    member2 = models.CharField(max_length=255, blank=True, null=True)  # Optional
    member2_contact = models.CharField(max_length=15, blank=True, null=True)  # Optional
    member3 = models.CharField(max_length=255, blank=True, null=True)  # Optional
    member3_contact = models.CharField(max_length=15, blank=True, null=True)  # Optional
    member4 = models.CharField(max_length=255, blank=True, null=True)  # Optional
    member4_contact = models.CharField(max_length=15, blank=True, null=True)  # Optional

    def __str__(self):
        return self.team_name
