from communalspace.email import send_mass_html_mail
from communalspace.firebase_admin import firebase as firebase_utils
from communalspace.settings import EMAIL_HOST_USER
from event.models import Event


def generate_message(participant_email, participant_name, event_creator_contact, event: Event):
    """
    The following email content is generated using ChatGPT.
    """
    email_message = (
        'Collectiv Event Cancellation Notice',
        f"""         
            <body style="font-family: Arial, sans-serif;">
            <h1>Cancellation of Event</h1>
            <p>Dear {participant_name or "Participant"},</p>
            <p>We hope this message finds you in good health and high spirits.</p>
            <p>It is with great regret that we must inform you of the cancellation of an event. This decision was reached after careful consideration of various factors that have unfortunately made it impossible to proceed as planned.</p>
            <p><strong>Event Name:</strong> {event.get_name()}<br>
                <strong>Initial Location:</strong> {event.get_location_name()}<br>
                <strong>Initial Start Date:</strong> {event.get_start_date_time_iso_format()}</p>
            <p>We understand the disappointment this news may bring, and we share in your sentiment. We remain committed to providing you with valuable content and experiences in the future. Please be assured that we are exploring alternative avenues to continue our engagement with you.</p>
            <p>If you have any questions or need further information, please do not hesitate to contact us at <strong>{event_creator_contact}</strong>.</p>
            <p>Wishing you all the best in your endeavors, and we look forward to connecting with you in the future.</p>
            <p>Warm regards,</p>
            <p>
                {event.get_creator_name() or "Event Creator"}<br>
                {"Event Creator<br>" if event.get_creator_name() is not None else ""}
                {event_creator_contact}
           </p>
           """,
        EMAIL_HOST_USER,
        [participant_email]
    )

    return email_message


def send_cancellation_email(event, participant_mailing_list):
    event_creator_contact = firebase_utils.get_email_or_phone_number_from_id(event.get_creator_id())
    messages = []
    for participant_data in participant_mailing_list:
        message = generate_message(
            participant_data.get('email'),
            participant_data.get('full_name'),
            event_creator_contact,
            event
        )
        messages.append(message)

    send_mass_html_mail(messages)


