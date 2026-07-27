from django.db import models
from django.utils import timezone
from .PregnancyCase import PregnancyCase
from .UserProfile import UserProfile

class FamilyMember(models.Model):
    familymember_id = models.AutoField(primary_key=True)
    pregnancycase = models.ForeignKey(PregnancyCase, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    permissions = models.JSONField(default=dict)
    join_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'familymember'
        managed = True 

    def __str__(self):
        return f"Family Member {self.familymember_id}"