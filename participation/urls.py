from .views import (
    serve_get_user_ongoing_participation,
    serve_get_user_past_participation,
    serve_get_user_future_participation,
    serve_register_user_participation_to_event,
    serve_register_user_volunteer_to_event,
    serve_participation_self_check_in_confirmation,
    serve_participation_self_check_out_confirmation,
    serve_participation_automated_check_out,
    serve_participant_volunteer_leave_events,
    serve_volunteer_assisted_check_in,
    serve_volunteer_grant_managerial_role,
    serve_volunteer_mark_participant_contribution,
    serve_volunteer_self_check_out,
    serve_get_user_contribution,
)
from django.urls import path


urlpatterns = [
    path('participant/register/', serve_register_user_participation_to_event),
    path('volunteer/register/', serve_register_user_volunteer_to_event),

    path('participant/check-in/self/', serve_participation_self_check_in_confirmation),
    path('participant/check-out/self/', serve_participation_self_check_out_confirmation),
    path('participant/check-out/automated/', serve_participation_automated_check_out),

    path('project/contribution/register/', serve_volunteer_mark_participant_contribution),

    path('volunteer/check-in/assisted/', serve_volunteer_assisted_check_in),
    path('volunteer/check-out/self/', serve_volunteer_self_check_out),
    path('volunteer/grant-managerial-role/', serve_volunteer_grant_managerial_role),

    path('participant/delete/', serve_participant_volunteer_leave_events),

    path('participant/past/', serve_get_user_past_participation),
    path('participant/ongoing/', serve_get_user_ongoing_participation),
    path('participant/future/', serve_get_user_future_participation),

    path('contributor/history/', serve_get_user_contribution),
]
