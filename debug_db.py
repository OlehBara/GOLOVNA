import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finsmart_project.settings")
django.setup()

from main.models import CartItem, UserSubscription, SubscriptionPlan
from django.contrib.auth.models import User

print("--- Cart Items ---")
for ci in CartItem.objects.all():
    print(f"ID: {ci.id}, User: {ci.user}, Course ID: {ci.course_id}, Plan ID: {ci.plan_id}")

print("\n--- Subscriptions ---")
for sub in UserSubscription.objects.all():
    print(f"ID: {sub.id}, Owner: {sub.owner}, Plan: {sub.plan.name if sub.plan else None}")

print("\n--- Subscription Plans ---")
for p in SubscriptionPlan.objects.all():
    print(f"ID: {p.id}, {p.name}")
