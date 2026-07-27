from django.shortcuts import render, redirect
from django.urls import reverse
from core.models import FamilyMember, BabyInformation, UserProfile
from core import join_requests_manager
from views.pregnancycase import resolve_active_pregnancy_case
from views.session_utils import get_current_user_profile
from views import baby_utils


def _parse_permissions_from_post(post_data, prefix='perm_'):
    result = {}
    for key in baby_utils.FEATURE_KEYS:
        value = (post_data.get(f'{prefix}{key}') or 'off').strip()
        result[key] = value if value in baby_utils.PERMISSION_LEVELS else 'off'
    return result


def edit_family_member(request):
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    case = resolve_active_pregnancy_case(request, current_user)

    if case and case.user_id != current_user.user_id:
        viewer_membership = FamilyMember.objects.filter(pregnancycase=case, user=current_user).first()
        if not baby_utils.has_permission(viewer_membership, 'helper_list', 'view'):
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
        pending_reqs = join_requests_manager.get_pending_requests(case.pregnancycase_id)
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
                if req_id and join_requests_manager.has_pending_request(case.pregnancycase_id, req_id):
                    target_user = UserProfile.objects.filter(user_id=req_id).first()
                    if target_user:
                        FamilyMember.objects.create(
                            pregnancycase=case,
                            user=target_user,
                            permissions={key: 'view' for key in baby_utils.FEATURE_KEYS},
                        )
                        join_requests_manager.remove_request(case.pregnancycase_id, req_id)
                        add_success = f'已同意「{target_user.name}」加入，預設權限為全部檢視，可再調整。'
                        members = list(
                            FamilyMember.objects.filter(pregnancycase_id=case)
                            .select_related('user').order_by('join_time')
                        )
                        pending_members = []
                        pending_reqs = join_requests_manager.get_pending_requests(case.pregnancycase_id)
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
                if req_id and join_requests_manager.has_pending_request(case.pregnancycase_id, req_id):
                    target_user = UserProfile.objects.filter(user_id=req_id).first()
                    applicant_name = target_user.name if target_user else "申請者"
                    join_requests_manager.remove_request(case.pregnancycase_id, req_id)
                    add_success = f'已拒絕「{applicant_name}」的加入申請。'
                    members = list(
                        FamilyMember.objects.filter(pregnancycase_id=case)
                        .select_related('user').order_by('join_time')
                    )
                    pending_members = []
                    pending_reqs = join_requests_manager.get_pending_requests(case.pregnancycase_id)
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
            return redirect('profile')

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
    })


def edit_helper_permissions(request):
    """單一協助者的權限編輯頁面，對應 edit_helper_permissions.html。"""
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    case = resolve_active_pregnancy_case(request, current_user)
    if not case or case.user_id != current_user.user_id:
        return redirect('profile')

    members = list(
        FamilyMember.objects
        .filter(pregnancycase_id=case)
        .select_related('user')
        .order_by('join_time')
    )

    member_id = request.GET.get('member_id') or request.POST.get('member_id')
    selected_member = next((m for m in members if str(m.familymember_id) == str(member_id)), None)
    if selected_member is None and members:
        selected_member = members[0]

    if request.method == 'POST' and selected_member:
        selected_member.permissions = _parse_permissions_from_post(request.POST)
        selected_member.save(update_fields=['permissions'])
        return redirect(f"{reverse('edit_helper_permissions')}?member_id={selected_member.familymember_id}")

    return render(request, 'user/edit_helper_permissions.html', {
        'pregnancy_case': case,
        'family_members': members,
        'selected_member': selected_member,
        'feature_keys': baby_utils.FEATURE_KEYS,
        'permission_levels': baby_utils.PERMISSION_LEVELS,
    })