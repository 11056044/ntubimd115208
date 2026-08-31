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

    context = baby_utils.build_growth_timeline_context(baby)
    return render(request, "baby/baby_growthmap.html", context)