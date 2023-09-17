
from event.models import Event
from event.services import utils
from utils import app_utils

def _update_event(request_data, event):
    event.name = request_data.get('name')
    event.description = request_data.get('description')
    event.min_num_of_volunteers = request_data.get('min_num_of_volunteers')
    event.start_date_time = app_utils.get_date_from_date_time_string(request_data.get('start_date_time'))
    event.end_date_time = app_utils.get_date_from_date_time_string(request_data.get('end_date_time'))
    event.location = utils.get_event_space_by_id_or_raise_exception(request_data.get('location_id'))

    if event.is_project:
        event.goal = request_data.get('project_goal')
        event.measurement_unit = request_data.get('goal_measurement_unit')

    event.save()