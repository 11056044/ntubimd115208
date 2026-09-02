from types import SimpleNamespace

from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase

from core.models import UserProfile
from views.login import handle_social_account_connected


class SocialAccountBindingTests(TestCase):
    def test_connect_line_to_google_user_when_session_user_id_is_missing(self):
        user_profile = UserProfile.objects.create(
            user_id=1,
            line_id='',
            email='alice@gmail.com',
            avatar='https://example.com/avatar.png',
            name='Alice',
        )

        request = RequestFactory().get('/profile/')
        request.session = SessionStore()
        request.session.pop('user_id', None)

        sociallogin = SimpleNamespace(
            account=SimpleNamespace(
                provider='line',
                uid='line-user-123',
                extra_data={'sub': 'line-user-123', 'email': 'alice@gmail.com'},
            )
        )

        handle_social_account_connected(request, sociallogin=sociallogin)
        user_profile.refresh_from_db()

        self.assertEqual(user_profile.line_id, 'line-user-123')
        self.assertEqual(request.session.get('user_id'), str(user_profile.user_id))
