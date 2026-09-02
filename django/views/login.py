import json
import logging

from django.conf import settings
from django.db import transaction
from django.db.models import Max
from django.dispatch import receiver
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from google.auth.transport import requests
from google.oauth2 import id_token
from allauth.account.signals import user_logged_in
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.signals import social_account_added

from core.models import UserProfile

logger = logging.getLogger(__name__)

def login_page(request):
    return render(request, 'login.html')

def _next_user_id():
    max_user_id = UserProfile.objects.aggregate(max_user_id=Max('user_id')).get('max_user_id')
    return (max_user_id or 0) + 1

@receiver(user_logged_in)
def handle_allauth_login_success(request, user, **kwargs):
    social_account = SocialAccount.objects.filter(user=user).first()
    if not social_account:
        return

    provider = str(social_account.provider)
    extra_data = social_account.extra_data

    email = ''
    raw_name = ''
    picture = ''
    line_user_id = ''

    # 🌟 智慧判斷來源，不再死守 'line' 字串
    is_google = (provider == 'google')
    is_line = (provider == 'line' or provider == '2010267631' or extra_data.get('iss') == 'https://access.line.me')

    if is_google:
        email = extra_data.get('email', '')
        raw_name = extra_data.get('name', '')
        picture = extra_data.get('picture', '')
    elif is_line:
        email = extra_data.get('email', '')
        # 🎯 根據 Log 顯示，這裡直接抓 'name' 跟 'picture' 才是對的！
        raw_name = extra_data.get('name', '')
        picture = extra_data.get('picture', '')
        line_user_id = extra_data.get('sub') or social_account.uid

    if not email:
        email = f"{line_user_id or social_account.uid}@line.platform"
    display_name = (raw_name or email.split('@')[0])[:50]

    try:
        with transaction.atomic():
            user_profile = UserProfile.objects.filter(email=email).first()
            if not user_profile and is_line:
                user_profile = UserProfile.objects.filter(line_id=line_user_id).first()

            if not user_profile:
                user_profile = UserProfile(
                    user_id=_next_user_id(),
                    line_id=line_user_id if is_line else '',
                    name=display_name,
                    avatar=picture or '',
                    email=email,
                )
                user_profile.save(force_insert=True)
            else:
                # 已存在的 UserProfile：不覆寫 name/avatar/email 等既有資料，
                # 只有 LINE 登入且 line_id 欄位目前是空的情況下才補寫入，
                # 讓「是否已綁定 LINE」的狀態能正確判斷。
                # （Google 這邊因為是直接用 email 完全比對找到帳號，比對到時
                # email 本來就已經等於這次登入的 email，不需要再補寫。）
                if is_line and line_user_id and not user_profile.line_id:
                    user_profile.line_id = line_user_id
                    user_profile.save(update_fields=['line_id'])

        request.session['user_id'] = str(user_profile.user_id)
        request.session['user_email'] = user_profile.email
        request.session['user_name'] = user_profile.name
        request.session['user_avatar'] = user_profile.avatar or ''
        request.session.pop('active_case_id', None)
        request.session.pop('active_baby_id', None)
        request.session.modified = True

    except Exception as e:
        logger.error(f"社交登入同步至 UserProfile 失敗，原因: {str(e)}", exc_info=True)
        print(f"======= 🔴 LINE/Google 登入同步失敗: {str(e)} =======")
        raise e

# ==========================================
# 舊有的原生 Google 登入 API
# ==========================================
@csrf_exempt
def google_auth_login(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    is_json_request = (request.content_type or '').startswith('application/json')
    if is_json_request:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        payload = request.POST

    token = payload.get('token') or payload.get('credential')
    if not token:
        return JsonResponse({'status': 'error', 'message': 'Missing token'}, status=400)

    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    if not client_id:
        return JsonResponse({'status': 'error', 'message': 'Google client id is not configured'}, status=500)

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=401)

    email = idinfo.get('email', '')
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email not found in token'}, status=400)

    name = idinfo.get('name') or email
    picture = idinfo.get('picture', '')
    name = (name or email.split('@')[0])[:50]

    with transaction.atomic():
        # find existing user by email or by line id
        user_profile = UserProfile.objects.filter(email=email).first()
        if not user_profile:
            user_profile = UserProfile.objects.filter(line_id=email).first()

        if not user_profile:
            # unmanaged table: assign the next numeric user_id manually
            user_profile = UserProfile(
                user_id=_next_user_id(),
                line_id='',
                name=name,
                avatar=picture or '',
                email=email,
            )
            user_profile.save(force_insert=True)
        # 已存在的 UserProfile：不再覆寫 name/line_id/avatar 等欄位，
        # 僅在首次建立帳號時才會寫入這些從 Google 帳號取得的資訊。

    request.session['user_id'] = str(user_profile.user_id)
    request.session['user_email'] = user_profile.email
    request.session['user_name'] = user_profile.name
    request.session['user_avatar'] = user_profile.avatar or ''
    request.session.pop('active_case_id', None)
    request.session.pop('active_baby_id', None)
    request.session.modified = True

    if is_json_request:
        return JsonResponse({
            'status': 'success',
            'email': user_profile.email,
            'name': user_profile.name,
            'user_id': str(user_profile.user_id),
            'redirect_url': reverse('index'),
        })

    return HttpResponseRedirect(reverse('index'))

# ==========================================
# 帳號綁定（在已登入狀態下，額外連結第二個社群帳號）
# ==========================================
@receiver(social_account_added)
def handle_social_account_connected(request, sociallogin, **kwargs):
    """
    當使用者已經登入，並透過 allauth 的 `?process=connect` 流程
    額外連結第二個社群帳號時（例如原本用 Google 登入，再去綁定 LINE），
    allauth 會發出 social_account_added 訊號（而不是 user_logged_in）。

    這裡把新綁定的社群帳號 ID 寫回「目前這一筆」UserProfile（用 session 裡的
    user_id 判斷是哪一筆），避免又跑去 handle_allauth_login_success 那條
    「找不到就新建」的邏輯，產生出兩個帳號。
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return

    user_profile = UserProfile.objects.filter(user_id=user_id).first()
    if not user_profile:
        return

    social_account = sociallogin.account
    provider = str(social_account.provider)
    extra_data = social_account.extra_data or {}

    is_google = (provider == 'google')
    is_line = (provider == 'line' or provider == '2010267631' or extra_data.get('iss') == 'https://access.line.me')

    try:
        with transaction.atomic():
            if is_google and not user_profile.google_linked:
                google_email = extra_data.get('email', '')
                if google_email:
                    user_profile.email = google_email
                    user_profile.save(update_fields=['email'])
            elif is_line and not user_profile.line_id:
                user_profile.line_id = extra_data.get('sub') or social_account.uid
                user_profile.save(update_fields=['line_id'])
    except Exception as e:
        logger.error(f"綁定社群帳號寫回 UserProfile 失敗，原因: {str(e)}", exc_info=True)


def _current_user_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return UserProfile.objects.filter(user_id=user_id).first()


def bind_google_account(request):
    """個人資料頁「綁定 Google」按鈕的入口，導向 allauth 的 connect 流程"""
    user_profile = _current_user_profile(request)
    if not user_profile:
        return redirect('login')

    if user_profile.google_linked:
        return redirect(f"{reverse('profile')}?perm_error=already_google")

    if not request.user.is_authenticated:
        # 理論上完成過任一種社群登入後 request.user 就會是 allauth 對應的帳號，
        # 若不是，代表目前的 session 狀態異常，請使用者重新登入再綁定。
        return redirect(f"{reverse('profile')}?perm_error=need_relogin")

    return redirect(f"{reverse('google_login')}?process=connect")


def bind_line_account(request):
    """個人資料頁「綁定 LINE」按鈕的入口，導向 allauth 的 connect 流程"""
    user_profile = _current_user_profile(request)
    if not user_profile:
        return redirect('login')

    if user_profile.line_linked:
        return redirect(f"{reverse('profile')}?perm_error=already_line")

    if not request.user.is_authenticated:
        return redirect(f"{reverse('profile')}?perm_error=need_relogin")

    return redirect(f"{reverse('line_login')}?process=connect")


@require_POST
def logout_user(request):
    request.session.flush()
    return redirect('login')