from .models import CartItem


def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        count = CartItem.objects.filter(session_key=session_key).count()

    return {"cart_item_count": count}
