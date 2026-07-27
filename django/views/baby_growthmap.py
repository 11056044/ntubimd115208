# baby_growthmap.py
from django.shortcuts import render, redirect
from core.models import FamilyMember
from views import baby_utils
from views.session_utils import get_current_user_profile

def baby_growthmap(request):
    """成長里程碑地圖（獨立分頁）"""
    user = get_current_user_profile(request)
    if not user:
        return redirect('login')

    baby = baby_utils.get_active_baby(request)

    if baby and baby.pregnancycase and baby.pregnancycase.user_id != user.user_id:
        membership = FamilyMember.objects.filter(pregnancycase=baby.pregnancycase, user=user).first()
        if not baby_utils.has_permission(membership, 'growth', 'view'):
            return redirect('profile')

    context = baby_utils.build_growth_timeline_context(baby)
    return render(request, "baby/baby_growthmap.html", context)