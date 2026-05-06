from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AutoSignupSocialAdapter(DefaultSocialAccountAdapter):
    """
    Автоматично генерує username з email при вході через Google,
    щоб пропустити проміжну сторінку /accounts/3rdparty/signup/.
    """

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username and user.email:
            # Беремо частину email до @ як username
            base_username = user.email.split("@")[0]
            user.username = base_username
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        # Завжди дозволяємо автоматичну реєстрацію через Google
        return True
