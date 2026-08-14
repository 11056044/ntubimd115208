from django.db import models
from django.utils import timezone
from .PregnancyCase import PregnancyCase
from .UserProfile import UserProfile

# 加入案例的申請紀錄
class JoinRequest(models.Model):
    joinrequest_id = models.AutoField(primary_key=True)
    pregnancycase  = models.ForeignKey(PregnancyCase, on_delete=models.CASCADE)
    user           = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    join_time      = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table        = 'joinrequest'
        managed         = True
        unique_together = ('pregnancycase', 'user')  # 同一人對同一 case 只能有一筆申請

    def __str__(self):
        return f"JoinRequest {self.joinrequest_id}"
