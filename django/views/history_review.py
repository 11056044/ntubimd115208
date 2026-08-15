import datetime
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.utils import timezone

from core.models import (
    BabyGrowthMap,
    BabyInformation,
    BabyRecord,
    BabyStatus,
    CareRecord,
    FamilyMember,
    Feeling,
    PhysicalCondition,
    PregnancyCase,
    PregnancyRecord,
    Prenatalrecord,
    QAMessage,
    Userfeeling,
    Userphysicalcondition,
    UserProfile,
)
from views.pregnancycase import (
    get_gestation_parts,
    get_lmp_date,
    is_pregnancy_ongoing,
    resolve_active_baby,
    resolve_active_pregnancy_case,
    sync_active_selection_from_request,
)
from views.session_utils import get_current_user_profile

FEELING_EMOJI_MAP = {
    '快樂': '😊',
    '幸福': '🥰',
    '開心': '😆',
    '心跳加速': '😳',
    '還好': '😐',
    '煩': '😮‍💨',
    '怒': '😡',
    '累': '😫',
    '不安': '😰',
    '難受': '😭',
    '不舒服': '🤢',
}


def _calc_stats(current_user, pregnancy_case, active_baby, today):
    """計算陪伴天數、照片總數、里程碑數、AI問答次數等通用統計。"""
    days_accompanied = 0
    if pregnancy_case:
        lmp = get_lmp_date(pregnancy_case)
        if lmp:
            delta = today - lmp
            days_accompanied = max(0, delta.days)
    elif active_baby and active_baby.birthdaytime:
        birth_date = (
            active_baby.birthdaytime.date()
            if hasattr(active_baby.birthdaytime, 'date')
            else active_baby.birthdaytime
        )
        if birth_date:
            delta = today - birth_date
            days_accompanied = max(0, delta.days)
    else:
        first_preg = (
            PregnancyRecord.objects.filter(user=current_user)
            .order_by('check_date')
            .first()
        )
        if first_preg and first_preg.check_date:
            days_accompanied = max(0, (today - first_preg.check_date).days)

    total_ultrasounds = Prenatalrecord.objects.filter(
        pregnancyrecord__user=current_user, photo__isnull=False
    ).exclude(photo='').count()

    total_baby_photos = BabyRecord.objects.filter(
        baby__pregnancycase__user=current_user, photo__isnull=False
    ).exclude(photo='').count()

    total_photos = total_ultrasounds + total_baby_photos

    total_milestones = BabyStatus.objects.filter(
        babyrecord__baby__pregnancycase__user=current_user
    ).count()

    total_qas = QAMessage.objects.filter(
        qa_conversation__user_id=current_user, role='assistant'
    ).count()

    return {
        'days_accompanied': days_accompanied,
        'total_ultrasounds': total_ultrasounds,
        'total_baby_photos': total_baby_photos,
        'total_photos': total_photos if total_photos > 0 else total_ultrasounds,
        'total_milestones': total_milestones,
        'total_qas': total_qas,
    }


def history_review(request):
    """歷史回顧首頁：我的孕期與寶寶成長旅程。"""
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    sync_active_selection_from_request(request, current_user)
    has_baby_selection = bool(
        request.session.get('active_baby_id') or request.GET.get('baby_id')
    )
    active_baby = resolve_active_baby(
        request, current_user, fallback=has_baby_selection
    )
    pregnancy_case = resolve_active_pregnancy_case(request, current_user)
    today = timezone.now().date()

    stats = _calc_stats(current_user, pregnancy_case, active_baby, today)

    # 1. 孕期進度計算
    current_week = 28
    current_day = 0
    progress_percent = 70
    if pregnancy_case:
        lmp = get_lmp_date(pregnancy_case)
        if lmp:
            delta = today - lmp
            if delta.days >= 0:
                current_week = min(42, delta.days // 7 + 1)
                current_day = delta.days % 7
                progress_percent = min(100, max(0, round(delta.days / 280 * 100)))

    # 2. 三個統計數字
    preg_records_count = PregnancyRecord.objects.filter(user=current_user).count()
    prenatal_records_count = Prenatalrecord.objects.filter(pregnancyrecord__user=current_user).count()
    growth_records_count = BabyRecord.objects.filter(baby__pregnancycase__user=current_user).count()

    total_pregnancy_records = preg_records_count if preg_records_count > 0 else 12
    total_prenatal_records = prenatal_records_count if prenatal_records_count > 0 else 8
    total_growth_records = growth_records_count if growth_records_count > 0 else 24

    # 3. 我的孕期故事時間軸 (Vertical Timeline)
    timeline_nodes = []
    preg_qs = (
        PregnancyRecord.objects.filter(user=current_user)
        .order_by('check_date')
        .select_related()
    )

    lmp = get_lmp_date(pregnancy_case) if pregnancy_case else None

    for rec in preg_qs:
        prenatal = Prenatalrecord.objects.filter(pregnancyrecord=rec).first()
        week_num = None
        if lmp and rec.check_date:
            d = (rec.check_date - lmp).days
            if d >= 0:
                week_num = d // 7 + 1

        week_str = f"第 {week_num} 週" if week_num else "孕期紀錄"
        type_str = "產檢紀錄" if prenatal else "孕期日記"
        title_str = "產檢超音波" if prenatal else "溫馨日常"
        if rec.record:
            desc_str = rec.record
        elif prenatal and prenatal.sbp:
            desc_str = f"血壓 {prenatal.sbp}/{prenatal.dbp} mmHg，胎心率穩定。"
        else:
            desc_str = "記錄了這一天的美好感受。"

        timeline_nodes.append({
            'week_label': week_str,
            'title': title_str,
            'date': rec.check_date.strftime('%Y/%m/%d') if hasattr(rec.check_date, 'strftime') else str(rec.check_date),
            'type_label': type_str,
            'description': desc_str,
            'is_current': False,
        })

    if len(timeline_nodes) < 3:
        timeline_nodes = [
            {
                'week_label': '第 12 週',
                'title': '第一次產檢',
                'date': '2026/04/10',
                'type_label': '產檢紀錄',
                'description': '第一次在超音波螢幕上看到小小的你，心跳有力而穩定。',
                'is_current': False,
            },
            {
                'week_label': '第 20 週',
                'title': '寶寶成長紀錄',
                'date': '2026/06/05',
                'type_label': '孕期紀錄',
                'description': '感受到第一次明顯的胎動，像小魚在肚子裡輕輕游動。',
                'is_current': False,
            },
            {
                'week_label': '第 24 週',
                'title': '重要產檢紀錄',
                'date': '2026/07/03',
                'type_label': '產檢紀錄',
                'description': '高層次超音波檢查，五官與四肢健全，成長各項指標皆在健康範圍。',
                'is_current': False,
            },
            {
                'week_label': f'第 {current_week} 週',
                'title': '現在',
                'date': today.strftime('%Y/%m/%d'),
                'type_label': '目前進度',
                'description': '肚子漸漸圓滾滾，每天都在期待與你正式相見的那一天。',
                'is_current': True,
            },
        ]
    else:
        timeline_nodes[-1]['is_current'] = True

    # 4. 重要時刻 (2~4 個小卡片)
    important_moments = [
        {
            'icon': 'favorite',
            'title': '第一次看到寶寶',
            'subtitle': '第 8 週超音波紀錄',
            'note': '看見那一閃一閃的小小心跳，全世界都變溫柔了。',
        },
        {
            'icon': 'health_and_safety',
            'title': '第一次常規產檢',
            'subtitle': '第 12 週建檔完成',
            'note': '正式領取孕婦健康手冊，展開專屬陪伴旅程。',
        },
        {
            'icon': 'child_care',
            'title': '初次感受胎動',
            'subtitle': '第 20 週生命躍動',
            'note': '肚皮裡輕巧的一踢，是最踏實的甜蜜互動。',
        },
        {
            'icon': 'stars',
            'title': f'邁入第 {current_week} 週',
            'subtitle': '孕晚期溫馨倒數',
            'note': '準備好迎接這段成長旅程中最美麗的結晶。',
        },
    ]

    # 5. 成長分析趨勢預覽數據
    trend_chart_data = [
        {'week': '20週', 'val': '320g', 'pct': 28},
        {'week': '22週', 'val': '460g', 'pct': 42},
        {'week': '24週', 'val': '650g', 'pct': 58},
        {'week': '26週', 'val': '890g', 'pct': 75},
        {'week': '28週', 'val': '1200g', 'pct': 95},
    ]

    # 6. 最近紀錄
    recent_records = []
    for r in PregnancyRecord.objects.filter(user=current_user).order_by('-check_date')[:3]:
        has_prenatal = Prenatalrecord.objects.filter(pregnancyrecord=r).exists()
        recent_records.append({
            'date': r.check_date.strftime('%m/%d') if hasattr(r.check_date, 'strftime') else str(r.check_date),
            'title': r.record[:20] if r.record else '產檢定期紀錄',
            'type_label': '產檢紀錄' if has_prenatal else '孕期紀錄',
            'url': '/pregnancyrecord/',
        })

    if active_baby:
        for br in BabyRecord.objects.filter(baby=active_baby).order_by('-date')[:2]:
            recent_records.append({
                'date': br.date.strftime('%m/%d') if hasattr(br.date, 'strftime') else str(br.date),
                'title': f'{active_baby.name} 生長紀錄 ({br.weight or ""}kg)',
                'type_label': '成長紀錄',
                'url': '/babyinformation/',
            })

    if not recent_records:
        recent_records = [
            {'date': '08/10', 'title': '第 28 週常規產檢紀錄', 'type_label': '產檢紀錄', 'url': '/pregnancyrecord/'},
            {'date': '08/03', 'title': '寶寶成長胎動與日常筆記', 'type_label': '成長紀錄', 'url': '/babyinformation/'},
            {'date': '07/27', 'title': '第 27 週體重與生理數值', 'type_label': '產檢紀錄', 'url': '/pregnancyrecord/'},
        ]

    context = {
        'current_user': current_user,
        'pregnancy_case': pregnancy_case,
        'active_baby': active_baby,
        'current_week': current_week,
        'current_day': current_day,
        'progress_percent': progress_percent,
        'journey_title': f"一起走過 {current_week} 週",
        'total_pregnancy_records': total_pregnancy_records,
        'total_prenatal_records': total_prenatal_records,
        'total_growth_records': total_growth_records,
        'timeline_nodes': timeline_nodes,
        'important_moments': important_moments,
        'trend_chart_data': trend_chart_data,
        'recent_records': recent_records[:5],
        **stats,
    }
    return render(request, 'history/history_hub.html', context)


def pregnancy_journey_view(request):
    """
    PAGE 1 — 成長時間軸 (Growth Timeline)
    依時間由新到舊排列，支援水平篩選（全部、孕期、產檢、成長、重要），右下角提供 FAB 新增紀錄按鈕。
    """
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    sync_active_selection_from_request(request, current_user)
    pregnancy_case = resolve_active_pregnancy_case(request, current_user)
    has_baby_selection = bool(request.session.get('active_baby_id') or request.GET.get('baby_id'))
    active_baby = resolve_active_baby(request, current_user, fallback=has_baby_selection)
    today = timezone.now().date()
    stats = _calc_stats(current_user, pregnancy_case, active_baby, today)

    lmp = get_lmp_date(pregnancy_case) if pregnancy_case else None

    # 聚合所有紀錄 (由新到舊)
    timeline_items = []

    # 1. 孕期與產檢紀錄
    preg_records_qs = (
        PregnancyRecord.objects.filter(user=current_user)
        .order_by('-check_date', '-pregnancyrecord_id')
    )

    for rec in preg_records_qs:
        prenatal = Prenatalrecord.objects.filter(pregnancyrecord=rec).first()
        feelings_qs = Userfeeling.objects.filter(pregnancyrecord=rec).select_related('feeling')
        feelings = [
            {
                'name': uf.feeling.feeling_name if uf.feeling else '',
                'emoji': FEELING_EMOJI_MAP.get(uf.feeling.feeling_name if uf.feeling else '', '🌸')
            }
            for uf in feelings_qs if uf.feeling
        ]

        weeks = None
        if lmp and rec.check_date:
            delta = rec.check_date - lmp
            if delta.days >= 0:
                weeks = delta.days // 7 + 1

        category = 'prenatal' if prenatal else 'pregnancy'
        category_label = '🩺 產檢紀錄' if prenatal else '📅 孕期紀錄'
        title = f'第 {weeks} 週產檢' if (weeks and prenatal) else (f'第 {weeks} 週孕期筆記' if weeks else '溫馨紀錄')
        summary = rec.record or (f'血壓: {prenatal.sbp}/{prenatal.dbp} mmHg，胎心率穩定' if prenatal and prenatal.sbp else '紀錄了這一天的美好感受')

        timeline_items.append({
            'date': rec.check_date.strftime('%m/%d') if hasattr(rec.check_date, 'strftime') else str(rec.check_date),
            'full_date': rec.check_date.strftime('%Y/%m/%d') if hasattr(rec.check_date, 'strftime') else str(rec.check_date),
            'year': rec.check_date.year if hasattr(rec.check_date, 'year') else 2026,
            'category': category,
            'category_label': category_label,
            'title': title,
            'summary': summary,
            'week': weeks,
            'weight': rec.weight,
            'prenatal': prenatal,
            'feelings': feelings,
            'is_current': False,
            'detail_url': '/pregnancyrecord/',
        })

    # 2. 寶寶成長紀錄
    if active_baby:
        baby_records = BabyRecord.objects.filter(baby=active_baby).order_by('-date')
        for br in baby_records:
            statuses = BabyStatus.objects.filter(babyrecord=br).select_related('babygrowthmap')
            milestones = [st.babygrowthmap.growthrecord for st in statuses if st.babygrowthmap]
            dt = br.date or today
            is_milestone = bool(milestones)

            timeline_items.append({
                'date': dt.strftime('%m/%d') if hasattr(dt, 'strftime') else str(dt),
                'full_date': dt.strftime('%Y/%m/%d') if hasattr(dt, 'strftime') else str(dt),
                'year': dt.year if hasattr(dt, 'year') else 2026,
                'category': 'important' if is_milestone else 'baby',
                'category_label': '⭐ 里程碑' if is_milestone else '👶 寶寶成長',
                'title': f'{active_baby.name} 成長紀錄',
                'summary': f'體重: {br.weight or "-"} kg，身高: {br.height or "-"} cm。' + (f' 達成：{", ".join(milestones)}' if milestones else ''),
                'week': None,
                'weight': br.weight,
                'prenatal': None,
                'feelings': [],
                'is_current': False,
                'detail_url': '/babyinformation/',
            })

    # 依日期由新到舊排序
    timeline_items.sort(key=lambda x: str(x['full_date']), reverse=True)

    # 若真實紀錄少於 3 筆，提供展示示範資料
    if len(timeline_items) < 3:
        timeline_items = [
            {
                'date': '08/10',
                'full_date': '2026/08/10',
                'year': 2026,
                'category': 'prenatal',
                'category_label': '🩺 產檢紀錄',
                'title': '第 28 週產檢',
                'summary': '寶寶目前狀況良好，胎心率 145 bpm，體重平穩增長。',
                'week': 28,
                'weight': '58.5',
                'is_current': True,
                'detail_url': '/pregnancyrecord/',
            },
            {
                'date': '08/03',
                'full_date': '2026/08/03',
                'year': 2026,
                'category': 'baby',
                'category_label': '👶 寶寶成長',
                'title': '寶寶成長紀錄',
                'summary': '預估體重：1,120 g，胎動活躍且規律。',
                'week': 27,
                'weight': '58.0',
                'is_current': False,
                'detail_url': '/babyinformation/',
            },
            {
                'date': '07/27',
                'full_date': '2026/07/27',
                'year': 2026,
                'category': 'pregnancy',
                'category_label': '📅 孕期紀錄',
                'title': '第 27 週',
                'summary': '進入第 27 週，睡眠品質良好，心情放鬆愉快。',
                'week': 27,
                'weight': '57.6',
                'is_current': False,
                'detail_url': '/pregnancyrecord/',
            },
            {
                'date': '07/03',
                'full_date': '2026/07/03',
                'year': 2026,
                'category': 'important',
                'category_label': '⭐ 重要時刻',
                'title': '高層次超音波檢查',
                'summary': '詳細檢查寶寶各器官發育狀況，一切健康平安！',
                'week': 24,
                'weight': '56.2',
                'is_current': False,
                'detail_url': '/pregnancyrecord/',
            },
        ]
    else:
        timeline_items[0]['is_current'] = True

    context = {
        'current_user': current_user,
        'pregnancy_case': pregnancy_case,
        'active_baby': active_baby,
        'timeline_items': timeline_items,
        'has_records': bool(timeline_items),
        **stats,
    }
    return render(request, 'history/pregnancy_journey.html', context)


def memory_wall_view(request):
    """
    PAGE 2 — 成長相簿 (Growth Photo Album)
    2-column grid，1:1 拍立得卡片，分類標籤，重要照片 ⭐ 標記，點擊開啟 Photo Detail Lightbox Modal。
    """
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    sync_active_selection_from_request(request, current_user)
    pregnancy_case = resolve_active_pregnancy_case(request, current_user)
    active_baby = resolve_active_baby(request, current_user)
    today = timezone.now().date()
    stats = _calc_stats(current_user, pregnancy_case, active_baby, today)

    # 孕週
    current_week = 28
    if pregnancy_case:
        lmp = get_lmp_date(pregnancy_case)
        if lmp:
            delta = today - lmp
            if delta.days >= 0:
                current_week = min(42, delta.days // 7 + 1)

    photos = []

    # 1. 產檢超音波照片
    ultrasound_records = (
        Prenatalrecord.objects.filter(pregnancyrecord__user=current_user, photo__isnull=False)
        .exclude(photo='')
        .select_related('pregnancyrecord')
    )
    for p in ultrasound_records:
        dt = p.pregnancyrecord.check_date if p.pregnancyrecord else today
        photos.append({
            'category': 'prenatal',
            'type_label': '產檢超音波',
            'date': dt.strftime('%Y/%m/%d') if hasattr(dt, 'strftime') else str(dt),
            'week_label': '產檢紀錄',
            'photo': p.photo,
            'title': f'產檢超音波相片',
            'notes': p.pregnancyrecord.record if p.pregnancyrecord else '紀錄了產檢當下的感動時刻。',
            'is_important': True,
        })

    # 2. 寶寶成長照片
    baby_records = (
        BabyRecord.objects.filter(baby__pregnancycase__user=current_user, photo__isnull=False)
        .exclude(photo='')
        .select_related('baby')
    )
    for br in baby_records:
        dt = br.date or today
        baby_name = br.baby.name if br.baby else '寶寶'
        photos.append({
            'category': 'baby',
            'type_label': f'{baby_name} 成長相片',
            'date': dt.strftime('%Y/%m/%d') if hasattr(dt, 'strftime') else str(dt),
            'week_label': f'{baby_name}',
            'photo': br.photo,
            'title': f'{baby_name} 成長紀錄',
            'notes': br.record or '捕捉孩子長大的每一瞬間。',
            'is_important': False,
        })

    photos.sort(key=lambda x: str(x['date']), reverse=True)

    context = {
        'current_user': current_user,
        'pregnancy_case': pregnancy_case,
        'active_baby': active_baby,
        'current_week': current_week,
        'photos': photos,
        'total_photos_count': len(photos),
        'has_photos': bool(photos),
        **stats,
    }
    return render(request, 'history/memory_wall.html', context)


def baby_growth_view(request):
    """
    PAGE 3 — 成長分析 (Growth Analysis)
    目前孕週、預產期倒數週數、3 個統計指標、成長趨勢圖、本月產檢/成長次數小卡與趨勢摘要。
    """
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    sync_active_selection_from_request(request, current_user)
    pregnancy_case = resolve_active_pregnancy_case(request, current_user)
    has_baby_selection = bool(request.session.get('active_baby_id') or request.GET.get('baby_id'))
    active_baby = resolve_active_baby(request, current_user, fallback=has_baby_selection)
    today = timezone.now().date()
    stats = _calc_stats(current_user, pregnancy_case, active_baby, today)

    # 孕週與倒數週數
    current_week = 28
    remaining_weeks = 12
    if pregnancy_case:
        lmp = get_lmp_date(pregnancy_case)
        if lmp:
            delta = today - lmp
            if delta.days >= 0:
                current_week = min(42, delta.days // 7 + 1)
                remaining_weeks = max(0, 40 - current_week)

    # 統計數據
    prenatal_count = Prenatalrecord.objects.filter(pregnancyrecord__user=current_user).count() or 8
    growth_count = BabyRecord.objects.filter(baby__pregnancycase__user=current_user).count() or 24
    moments_count = 6

    # 本月統計
    this_month_start = today.replace(day=1)
    monthly_prenatal = PregnancyRecord.objects.filter(user=current_user, check_date__gte=this_month_start).count() or 2
    monthly_growth = BabyRecord.objects.filter(baby__pregnancycase__user=current_user, date__gte=this_month_start).count() or 6

    # 最近 4 週新增筆數
    four_weeks_ago = today - datetime.timedelta(days=28)
    recent_4w_count = (
        PregnancyRecord.objects.filter(user=current_user, check_date__gte=four_weeks_ago).count()
        + BabyRecord.objects.filter(baby__pregnancycase__user=current_user, date__gte=four_weeks_ago).count()
    ) or 8

    # 最近一次產檢日期
    latest_prenatal_record = PregnancyRecord.objects.filter(user=current_user).order_by('-check_date').first()
    latest_prenatal_date = latest_prenatal_record.check_date.strftime('%m/%d') if (latest_prenatal_record and latest_prenatal_record.check_date) else '08/10'

    # 成長趨勢圖數據 (20週 ~ 28週)
    trend_chart_data = [
        {'week': '20週', 'val': '320g', 'pct': 28},
        {'week': '22週', 'val': '460g', 'pct': 42},
        {'week': '24週', 'val': '650g', 'pct': 58},
        {'week': '26週', 'val': '890g', 'pct': 75},
        {'week': '28週', 'val': '1200g', 'pct': 95},
    ]

    context = {
        'current_user': current_user,
        'pregnancy_case': pregnancy_case,
        'active_baby': active_baby,
        'current_week': current_week,
        'remaining_weeks': remaining_weeks,
        'prenatal_count': prenatal_count,
        'growth_count': growth_count,
        'moments_count': moments_count,
        'monthly_prenatal': monthly_prenatal,
        'monthly_growth': monthly_growth,
        'recent_4w_count': recent_4w_count,
        'latest_prenatal_date': latest_prenatal_date,
        'trend_chart_data': trend_chart_data,
        **stats,
    }
    return render(request, 'history/baby_growth.html', context)


def ai_growth_journey_view(request):
    """
    PAGE 4 — 重要時刻 (Important Moments)
    Hero 收藏卡片、垂直重要時刻節點、＋ 新增重要時刻 Modal、Empty State。
    """
    current_user = get_current_user_profile(request)
    if not current_user:
        return redirect('login')

    sync_active_selection_from_request(request, current_user)
    has_baby_selection = bool(request.session.get('active_baby_id') or request.GET.get('baby_id'))
    active_baby = resolve_active_baby(request, current_user, fallback=has_baby_selection)
    pregnancy_case = resolve_active_pregnancy_case(request, current_user)
    today = timezone.now().date()
    stats = _calc_stats(current_user, pregnancy_case, active_baby, today)

    # 重要時刻清單 (支援時間軸節點展示)
    important_moments = [
        {
            'icon': 'favorite',
            'title': '第一次看到寶寶',
            'week': '第 8 週',
            'date': '2026 / 03 / 15',
            'notes': '看見那一閃一閃的小小心跳，全世界都變溫柔了。',
            'detail_url': '/pregnancyrecord/',
        },
        {
            'icon': 'health_and_safety',
            'title': '第一次常規產檢',
            'week': '第 12 週',
            'date': '2026 / 04 / 12',
            'notes': '正式領取孕婦健康手冊，展開專屬陪伴旅程。',
            'detail_url': '/pregnancyrecord/',
        },
        {
            'icon': 'child_care',
            'title': '初次感受胎動',
            'week': '第 20 週',
            'date': '2026 / 06 / 08',
            'notes': '肚皮裡輕巧的一踢，是最踏實的甜蜜互動。',
            'detail_url': '/pregnancyrecord/',
        },
        {
            'icon': 'visibility',
            'title': '高層次超音波檢查',
            'week': '第 24 週',
            'date': '2026 / 07 / 05',
            'notes': '五官、心臟與小手小腳都健全，成長指標健康。',
            'detail_url': '/pregnancyrecord/',
        },
        {
            'icon': 'stars',
            'title': '邁入孕晚期第 28 週',
            'week': '第 28 週',
            'date': '2026 / 08 / 02',
            'notes': '肚子漸漸圓滾滾，每天都在期待與你相見的那一天。',
            'detail_url': '/pregnancyrecord/',
        },
        {
            'icon': 'celebration',
            'title': '準備迎接新生命',
            'week': '第 32 週預備',
            'date': '2026 / 08 / 13',
            'notes': '整理待產包與嬰兒房，滿滿的愛與期待。',
            'detail_url': '/pregnancyrecord/',
        },
    ]

    context = {
        'current_user': current_user,
        'pregnancy_case': pregnancy_case,
        'active_baby': active_baby,
        'important_moments': important_moments,
        'total_moments_count': len(important_moments),
        'has_moments': bool(important_moments),
        **stats,
    }
    return render(request, 'history/stage_summary.html', context)
