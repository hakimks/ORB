"""
Signal definitions to be used for resource content review.
"""

import django.dispatch


review_assigned = django.dispatch.Signal(providing_args=["review", "assigned_by"])
review_rejected = django.dispatch.Signal(providing_args=["review"])
review_approved = django.dispatch.Signal(providing_args=["review"])
