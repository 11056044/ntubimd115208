from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from core.models import FamilyMember, BabyInformation, UserProfile
from views import join_request
from views.pregnancycase import resolve_active_pregnancy_case
from views.session_utils import get_current_user_profile
from views import baby_utils


def _parse_permissions_from_post(post_data, prefix='perm_'):
    result = {}
    for key in baby_utils.FEATURE_KEYS:
        default = 'off' if key == 'mom_records' else 'view'
        value = (post_data.get(f'{prefix}{key}') or default).strip()
        result[key] = value if value in baby_utils.PERMISSION_LEVELS else default
    return result


def edit_family_member(request):
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    case = resolve_active_pregnancy_case(request, current_user)

    # 協助者清單只有 case owner 能進入
    if case and case.user_id != current_user.user_id:
        return redirect('profile')

    babies = list(BabyInformation.objects.filter(pregnancycase=case).order_by('baby_id')) if case else []
    members = list(
        FamilyMember.objects
        .filter(pregnancycase_id=case)
        .select_related('user')
        .order_by('join_time')
    ) if case else []

    pending_members = []
    if case and case.user == current_user:
        pending_reqs = join_request.get_pending_requests(case.pregnancycase_id)
        for pr in pending_reqs:
            u = UserProfile.objects.filter(user_id=pr['user_id']).first()
            if u:
                class PendingMember:
                    def __init__(self, user_profile):
                        self.user_id = user_profile
                        self.familymember_id = user_profile.user_id
                pending_members.append(PendingMember(u))

    baby_id = request.GET.get('baby_id') or request.POST.get('baby_id')
    selected_baby = None
    if baby_id:
        selected_baby = next((b for b in babies if str(b.baby_id) == str(baby_id)), None)
    if selected_baby is None and babies:
        selected_baby = babies[0]

    member_id = request.GET.get('member_id') or request.POST.get('member_id')
    selected_member = None
    if member_id:
        selected_member = next(
            (m for m in members if str(m.familymember_id) == str(member_id)), None
        )
    if selected_member is None and members:
        selected_member = members[0]

    add_error = None
    add_success = None
    search_results = []

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'search':
            query = request.POST.get('search_query', '').strip()
            if query:
                search_results = list(
                    UserProfile.objects
                    .filter(name__icontains=query)
                    .exclude(user_id=current_user.user_id)
                    .order_by('name')[:10]
                )
                if not search_results:
                    add_error = f'找不到使用者「{query}」'
            else:
                add_error = '請輸入姓名或 Email 搜尋'

        elif action == 'add_member':
            if not case or case.user_id != current_user.user_id:
                add_error = '只有此胎數的擁有者才能新增協助者'
            else:
                target_user_id = request.POST.get('target_user_id', '').strip()
                if not target_user_id:
                    add_error = '請先搜尋並選擇使用者'
                else:
                    target_user = UserProfile.objects.filter(user_id=target_user_id).first()
                    if not target_user:
                        add_error = '找不到此使用者'
                    elif FamilyMember.objects.filter(pregnancycase_id=case, user_id=target_user).exists():
                        add_error = f'「{target_user.name}」已經是此胎數的協助者'
                    else:
                        FamilyMember.objects.create(
                            pregnancycase=case,
                            user=target_user,
                            permissions=_parse_permissions_from_post(request.POST),
                        )
                        add_success = f'已成功將「{target_user.name}」加入！'
                        members = list(
                            FamilyMember.objects.filter(pregnancycase_id=case)
                            .select_related('user').order_by('join_time')
                        )

        elif action == 'approve_request':
            if not case or case.user_id != current_user.user_id:
                add_error = '只有此胎數的擁有者才能核准申請'
            else:
                req_id = request.POST.get('request_id')
                if req_id and join_request.has_pending_request(case.pregnancycase_id, req_id):
                    target_user = UserProfile.objects.filter(user_id=req_id).first()
                    if target_user:
                        with transaction.atomic():
                            default_perms = {key: 'view' for key in baby_utils.FEATURE_KEYS}
                            default_perms['mom_records'] = 'off'
                            FamilyMember.objects.create(
                                pregnancycase=case,
                                user=target_user,
                                permissions=default_perms,
                            )
                            join_request.remove_request(case.pregnancycase_id, req_id)
                        add_success = f'已同意「{target_user.name}」加入，養育者記錄預設關閉，可至管理頁調整。'
                        members = list(
                            FamilyMember.objects.filter(pregnancycase_id=case)
                            .select_related('user').order_by('join_time')
                        )
                        pending_members = []
                        pending_reqs = join_request.get_pending_requests(case.pregnancycase_id)
                        for pr in pending_reqs:
                            u = UserProfile.objects.filter(user_id=pr['user_id']).first()
                            if u:
                                class PendingMember:
                                    def __init__(self, user_profile):
                                        self.user_id = user_profile
                                        self.familymember_id = user_profile.user_id
                                pending_members.append(PendingMember(u))
                    else:
                        add_error = '找不到此使用者'
                else:
                    add_error = '找不到該筆申請紀錄'

        elif action == 'reject_request':
            if not case or case.user_id != current_user.user_id:
                add_error = '只有此胎數的擁有者才能拒絕申請'
            else:
                req_id = request.POST.get('request_id')
                if req_id and join_request.has_pending_request(case.pregnancycase_id, req_id):
                    target_user = UserProfile.objects.filter(user_id=req_id).first()
                    applicant_name = target_user.name if target_user else "申請者"
                    with transaction.atomic():
                        join_request.remove_request(case.pregnancycase_id, req_id)
                    add_success = f'已拒絕「{applicant_name}」的加入申請。'
                    members = list(
                        FamilyMember.objects.filter(pregnancycase_id=case)
                        .select_related('user').order_by('join_time')
                    )
                    pending_members = []
                    pending_reqs = join_request.get_pending_requests(case.pregnancycase_id)
                    for pr in pending_reqs:
                        u = UserProfile.objects.filter(user_id=pr['user_id']).first()
                        if u:
                            class PendingMember:
                                def __init__(self, user_profile):
                                    self.user_id = user_profile
                                    self.familymember_id = user_profile.user_id
                            pending_members.append(PendingMember(u))
                else:
                    add_error = '找不到該筆申請紀錄'

        elif action == 'save_permissions':
            if not case or case.user_id != current_user.user_id:
                add_error = '只有此胎數的擁有者才能修改權限'
            elif selected_member:
                selected_member.permissions = _parse_permissions_from_post(request.POST)
                selected_member.save(update_fields=['permissions'])
                add_success = f'已更新「{selected_member.user.name}」的權限設定。'
                # 重新整理 members 讓頁面顯示最新狀態
                members = list(
                    FamilyMember.objects.filter(pregnancycase_id=case)
                    .select_related('user').order_by('join_time')
                )
                selected_member = next(
                    (m for m in members if str(m.familymember_id) == str(member_id)), None
                )

    return render(request, 'user/edit_family_member.html', {
        'pregnancy_case': case,
        'babies': babies,
        'selected_baby': selected_baby,
        'family_members': members,
        'pending_members': pending_members,
        'selected_member': selected_member,
        'add_error': add_error,
        'add_success': add_success,
        'search_results': search_results,
        'is_case_owner': bool(case and case.user_id == current_user.user_id),
        'feature_keys': baby_utils.FEATURE_KEYS,
    })


def edit_helper_permissions(request):
    """保留 URL 相容，直接 redirect 到合併後的 edit_family_member 頁面。"""
    member_id = request.GET.get('member_id') or request.POST.get('member_id')
    url = reverse('edit_family_member')
    if member_id:
        url += f'?member_id={member_id}'
    return redirect(url)