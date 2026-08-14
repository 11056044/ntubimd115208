from core.models import JoinRequest

def add_request(case_id, user_id):
    #新增申請。如果已存在（同一人對同一 case 申請過），不會重複建立。回傳 True 表示新建、False 表示已存在
    _obj, created = JoinRequest.objects.get_or_create(
        pregnancycase_id=int(case_id),
        user_id=int(user_id),
    )
    return created

def remove_request(case_id, user_id):
    #核准或拒絕後，移除這筆申請紀錄
    JoinRequest.objects.filter(
        pregnancycase_id=int(case_id),
        user_id=int(user_id),
    ).delete()

def get_pending_requests(case_id):

    return [
        {
            'case_id':   r.pregnancycase_id,
            'user_id':   r.user_id,
            'join_time': r.join_time.isoformat(),
        }
        for r in JoinRequest.objects.filter(pregnancycase_id=int(case_id))
    ]

def has_pending_request(case_id, user_id):
    #檢查特定使用者是否已對該 case 提出申請
    return JoinRequest.objects.filter(
        pregnancycase_id=int(case_id),
        user_id=int(user_id),
    ).exists()
