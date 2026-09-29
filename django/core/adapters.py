from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        """
        當使用者在登入狀態下，成功綁定第二個社群帳號 (process=connect) 後，
        將會導向這裡回傳的 URL。預設是 socialaccount_connections，
        這裡我們把它改為導回個人資料頁面。
        """
        return reverse('profile')
