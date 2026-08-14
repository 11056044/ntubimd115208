import datetime
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from views import baby_utils

MONTH_ABBR = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

# ── 成長紀錄體徵合理範圍（0~3歲，體重 kg，其餘 cm）──
# 身高下限 25cm：對齊出生時的下限，確保極早產兒（22~24週）出生後第一筆紀錄不被擋住
RECORD_VITAL_RANGES = {
    'height':             (25.0,  130.0, '身高（cm）合理範圍為 25 ~ 130 cm'),
    'weight':             (0.3,   30.0,  '體重（kg）合理範圍為 0.3 ~ 30 kg'),
    'headcircumference':  (25.0,  60.0,  '頭圍（cm）合理範圍為 25 ~ 60 cm'),
    'chestcircumference': (20.0,  60.0,  '胸圍（cm）合理範圍為 20 ~ 60 cm'),
}

def _validate_record_vitals(height, weight, head, chest):
    """驗證成長紀錄體徵數值是否在合理範圍內。回傳 None 代表合法；否則回傳錯誤訊息。"""
    pairs = [
        (height, 'height'),
        (weight, 'weight'),
        (head,   'headcircumference'),
        (chest,  'chestcircumference'),
    ]
    for value, key in pairs:
        if value is None:
            continue
        lo, hi, msg = RECORD_VITAL_RANGES[key]
        if not (lo <= value <= hi):
            return msg
    return None

from core.models import (
    BabyInformation,
    BabyRecord,
    BabyGrowthMap,
    BabyStatus,
    PregnancyCase,
    FamilyMember,
)

from views.pregnancycase import url_with_active_selection
from views.session_utils import get_current_user_profile


# ── 權限與角色輔助函式 ──────────────────────────────────────────────
def _check_baby_permission(user, case, required='viewer'):
    if case.user_id == user.user_id:
        return True
    membership = FamilyMember.objects.filter(pregnancycase=case, user=user).first()
    required_level = 'edit' if required == 'caregiver' else 'view'
    return baby_utils.has_permission(membership, 'baby_records', required_level)


def _get_accessible_babies(user):
    """取得使用者可存取的全部嬰幼兒（自有 + 家庭成員共享且 perm_baby 不為 none）。"""
    cases_own = PregnancyCase.objects.filter(user=user)

    # 共享：只取 perm_baby 為 viewer 或 caregiver 的 FamilyMember
    shared_memberships = FamilyMember.objects.filter(user=user).select_related('pregnancycase')
    shared_case_ids = [m.pregnancycase_id for m in shared_memberships if baby_utils.get_permission(m, 'baby_records') != 'off']
    return BabyInformation.objects.filter(
        Q(pregnancycase__in=cases_own) | Q(pregnancycase_id__in=shared_case_ids)
    ).distinct()


# ── 新增生長紀錄 ─────────────────────────────────────────────────

def add_baby_record(request):
    """新增嬰幼兒生長紀錄。需要 perm_baby=caregiver 才可寫入。"""
    user = get_current_user_profile(request)
    if not user:
        return redirect('login')

    active_baby = baby_utils.get_active_baby(request)
   
    if active_baby is None:
        today = datetime.date.today()
        return render(request, 'baby/add_babyrecord.html', {
            'baby':                None,
            'baby_list':           _get_accessible_babies(user),
            'all_milestones':      BabyGrowthMap.objects.none(),
            'form_data':           {'date': today.isoformat()},
            'milestones':          '',
            'today_iso':           today.isoformat(),
            'selected_month_abbr': MONTH_ABBR[today.month],
            'selected_day':        today.day,
        })
    case = active_baby.pregnancycase

    # 權限：只有 caregiver 以上才能新增
    if not _check_baby_permission(user, case, required='caregiver'):
        return redirect('babyinformation')

    initial_date = request.GET.get('date', '')
    today_iso = datetime.date.today().isoformat()  # 供 template max 屬性使用

    if request.method == 'POST':
        date_str = request.POST.get('date')
        
        if not date_str:
            return render(request, 'baby/add_babyrecord.html', {
                'baby':      active_baby,
                'error':     '請填寫紀錄日期',
                'form_data': request.POST,
                'today_iso': today_iso,
            })

        # 後端二次驗證日期格式與未來日期
        try:
            record_date_post = datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return render(request, 'baby/add_babyrecord.html', {
                'baby':      active_baby,
                'error':     '日期格式不正確',
                'form_data': request.POST,
                'today_iso': today_iso,
            })
        #不能計超過今天日期
        if record_date_post > datetime.date.today():
            return render(request, 'baby/add_babyrecord.html', {
                'baby':      active_baby,
                'error':     '無法新增未來日期的紀錄',
                'form_data': request.POST,
                'today_iso': today_iso,
            })
        #未出生不能紀錄（birthdaytime=None 表示出生日尚未填寫）
        if not active_baby.birthdaytime:
            return render(request, 'baby/add_babyrecord.html', {
                'baby':      active_baby,
                'error':     '尚未填寫出生日期，無法新增成長紀錄',
                'form_data': request.POST,
                'today_iso': today_iso,
            })
        if active_baby.birthdaytime and record_date_post < active_baby.birthdaytime.date():
            return render(request, 'baby/add_babyrecord.html', {
                'baby':      active_baby,
                'error':     '尚未出生，無法新增成長紀錄',
                'form_data': request.POST,
                'today_iso': today_iso,
            })

        milestones_str = request.POST.get('milestones', '')
        # 內文直接去除前後空白儲存，里程碑摘要由個別的關聯表來呈現即可
        record_text    = (request.POST.get('record', '') or '').strip()
        photo_url      = baby_utils.save_uploaded_image(request.FILES.get('photo'))

        # ── 體徵範圍驗證 ──
        h  = baby_utils.parse_float(request.POST.get('height'))
        w  = baby_utils.parse_float(request.POST.get('weight'))
        hc = baby_utils.parse_float(request.POST.get('headcircumference'))
        cc = baby_utils.parse_float(request.POST.get('chestcircumference'))
        vital_error = _validate_record_vitals(h, w, hc, cc)
        if vital_error:
            return render(request, 'baby/add_babyrecord.html', {
                'baby':      active_baby,
                'error':     vital_error,
                'form_data': request.POST,
                'today_iso': today_iso,
            })

        baby_record = BabyRecord.objects.create(
            baby=active_baby,
            date=record_date_post,
            record=record_text,
            weight=w,
            height=h,
            headcircumference=hc,
            chestcircumference=cc,
            photo=photo_url,
        )

        # 解析 pipe-separated 里程碑字串，逐一建立 BabyStatus 關聯
        milestone_names = [m.strip() for m in milestones_str.split('|') if m.strip()]
        for m_name in milestone_names:
            growth_map = BabyGrowthMap.objects.filter(growthrecord=m_name).first()
            if growth_map:
                BabyStatus.objects.get_or_create(
                    babyrecord=baby_record,
                    babygrowthmap=growth_map,
                )

        # 儲存成功後跳回嬰幼兒資訊頁
        return redirect(url_with_active_selection(request, reverse('babyinformation')))

    # ── GET：準備表單資料 ────────────────────────────────────────
    try:
        record_date = datetime.date.fromisoformat(initial_date) if initial_date else datetime.date.today()
        
    except Exception:
        record_date = datetime.date.today()

    if active_baby.birthdaytime and record_date < active_baby.birthdaytime.date():
        record_date = active_baby.birthdaytime.date()


    age_in_months    = baby_utils.calculate_age_in_months(active_baby.birthdaytime, record_date)
    relevant_courses = baby_utils.get_relevant_timecourses(age_in_months)
    baby_list        = _get_accessible_babies(user)

    achieved_ids = BabyStatus.objects.filter(
        babyrecord__baby=active_baby
    ).values_list('babygrowthmap_id', flat=True)

    if relevant_courses:
        all_milestones = BabyGrowthMap.objects.filter(
            timecourse__in=relevant_courses
        ).exclude(babygrowthmap_id__in=achieved_ids).order_by('timecourse')
    else:
        all_milestones = BabyGrowthMap.objects.all().exclude(
            babygrowthmap_id__in=achieved_ids
        ).order_by('timecourse')

    return render(request, 'baby/add_babyrecord.html', {
        'is_edit':        False,
        'baby':           active_baby,
        'baby_list':      baby_list,
        'all_milestones': all_milestones,
        'form_data':      {'date': record_date.isoformat()},
        'milestones':     '',
        'today_iso':      today_iso,
        'selected_month_abbr': MONTH_ABBR[record_date.month],  
        'selected_day':        record_date.day, 
    })


# ── 編輯生長紀錄 ─────────────────────────────────────────────────

def edit_baby_record(request, babyrecord_id):
    
    """
    編輯特定生長紀錄。
    安全防護：水平越權（只有案例擁有者或 perm_baby=caregiver 的家庭成員可修改）。
    里程碑更新策略：先全量刪除再重新建立，確保與表單送出一致。
    """
    user = get_current_user_profile(request)
    if not user:
        return redirect('login')

    record = get_object_or_404(BabyRecord, babyrecord_id=babyrecord_id)
    
    baby   = record.baby
    case   = baby.pregnancycase

    # 需要 caregiver 權限才能編輯
    if not _check_baby_permission(user, case, required='caregiver'):
        return redirect('babyinformation')

    record.milestones, record.note_text = baby_utils.split_note_and_milestones(record)

    if request.method == 'POST':
        date_str = request.POST.get('date')
        if not date_str:
            return render(request, 'baby/add_babyrecord.html', {
                'is_edit':             True,
                'record':              record,
                'baby':                baby,
                'baby_list':           _get_accessible_babies(user),
                'all_milestones':      _get_milestones_for_edit(baby, record),
                'error':               '請填寫紀錄日期',
                'form_data':           request.POST,
                'selected_milestones': request.POST.get('milestones', ''),
                'today_iso':           datetime.date.today().isoformat(),
            })

        milestones_str = request.POST.get('milestones', '')

        # ── 日期後端驗證（與 add 一致） ──
        try:
            record_date_edit = datetime.date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return render(request, 'baby/add_babyrecord.html', {
                'is_edit': True, 'record': record, 'baby': baby,
                'baby_list': _get_accessible_babies(user),
                'all_milestones': _get_milestones_for_edit(baby, record),
                'error': '日期格式不正確',
                'form_data': request.POST,
                'selected_milestones': request.POST.get('milestones', ''),
                'today_iso': datetime.date.today().isoformat(),
            })
        if record_date_edit > datetime.date.today():
            return render(request, 'baby/add_babyrecord.html', {
                'is_edit': True, 'record': record, 'baby': baby,
                'baby_list': _get_accessible_babies(user),
                'all_milestones': _get_milestones_for_edit(baby, record),
                'error': '無法修改為未來日期的紀錄',
                'form_data': request.POST,
                'selected_milestones': request.POST.get('milestones', ''),
                'today_iso': datetime.date.today().isoformat(),
            })
        if baby.birthdaytime and record_date_edit < baby.birthdaytime.date():
            return render(request, 'baby/add_babyrecord.html', {
                'is_edit': True, 'record': record, 'baby': baby,
                'baby_list': _get_accessible_babies(user),
                'all_milestones': _get_milestones_for_edit(baby, record),
                'error': '紀錄日期不可早於寶寶出生日',
                'form_data': request.POST,
                'selected_milestones': request.POST.get('milestones', ''),
                'today_iso': datetime.date.today().isoformat(),
            })

        # ── 體徵範圍驗證 ──
        h  = baby_utils.parse_float(request.POST.get('height'))
        w  = baby_utils.parse_float(request.POST.get('weight'))
        hc = baby_utils.parse_float(request.POST.get('headcircumference'))
        cc = baby_utils.parse_float(request.POST.get('chestcircumference'))
        vital_error = _validate_record_vitals(h, w, hc, cc)
        if vital_error:
            return render(request, 'baby/add_babyrecord.html', {
                'is_edit': True, 'record': record, 'baby': baby,
                'baby_list': _get_accessible_babies(user),
                'all_milestones': _get_milestones_for_edit(baby, record),
                'error': vital_error,
                'form_data': request.POST,
                'selected_milestones': request.POST.get('milestones', ''),
                'today_iso': datetime.date.today().isoformat(),
            })

        record.date               = record_date_edit
        record.record             = (request.POST.get('record', '') or '').strip()
        record.weight             = w
        record.height             = h
        record.headcircumference  = hc
        record.chestcircumference = cc

        # 只有新上傳照片才覆蓋舊照片
        photo_url = baby_utils.save_uploaded_image(request.FILES.get('photo'))
        if photo_url:
            record.photo = photo_url

        record.update_time = timezone.now()
        record.save()

        # 全量重建里程碑關聯（先刪除再建立）
        BabyStatus.objects.filter(babyrecord=record).delete()
        for m_name in [m.strip() for m in milestones_str.split('|') if m.strip()]:
            growth_map = BabyGrowthMap.objects.filter(growthrecord=m_name).first()
            if growth_map:
                BabyStatus.objects.create(babyrecord=record, babygrowthmap=growth_map)

        return redirect(url_with_active_selection(request, reverse('babyinformation')))

    # ── GET：準備表單資料 ──────────────────────────────────
    return render(request, 'baby/add_babyrecord.html', {
        'is_edit':             True,
        'record':              record,
        'baby':                baby,
        'baby_list':           _get_accessible_babies(user),
        'all_milestones':      _get_milestones_for_edit(baby, record),
        'form_data': {
            'date':               record.date,
            'height':             record.height,
            'weight':             record.weight,
            'headcircumference':  record.headcircumference,
            'chestcircumference': record.chestcircumference,
            'record':             record.note_text,
        },
        'selected_milestones': '|'.join(record.milestones),
        'selected_month_abbr': MONTH_ABBR[record.date.month],
        'selected_day':        record.date.day,
        'today_iso':           datetime.date.today().isoformat(),
    })


def _get_milestones_for_edit(baby, record):
    """取得可供編輯頁顯示的里程碑列表（月齡區間 + 本筆已勾選，排除其他天已達成的）。"""
    record_date   = record.date
    age_in_months = baby_utils.calculate_age_in_months(baby.birthdaytime, record_date)
    relevant      = baby_utils.get_relevant_timecourses(age_in_months)

    achieved_other = BabyStatus.objects.filter(
        babyrecord__baby=baby
    ).exclude(babyrecord=record).values_list('babygrowthmap_id', flat=True)

    if relevant:
        return BabyGrowthMap.objects.filter(
            Q(timecourse__in=relevant) | Q(growthrecord__in=record.milestones)
        ).exclude(babygrowthmap_id__in=achieved_other).distinct().order_by('timecourse')
    return BabyGrowthMap.objects.all().exclude(
        babygrowthmap_id__in=achieved_other
    ).order_by('timecourse')


# ── 刪除生長紀錄 ─────────────────────────────────────────────────

def delete_baby_record(request, babyrecord_id):
    """
    刪除特定生長紀錄。
    安全防護：
      1. 水平越權：需 perm_baby=caregiver 或案例擁有者
      2. 僅接受 POST，防止 GET 意外觸發刪除
    """
    user = get_current_user_profile(request)
    if not user:
        return redirect('login')

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    record = get_object_or_404(BabyRecord, babyrecord_id=babyrecord_id)
    case   = record.baby.pregnancycase

    if not _check_baby_permission(user, case, required='caregiver'):
        return redirect('babyinformation')
    record.delete()
    return redirect(url_with_active_selection(request, reverse('babyinformation')))

