from django.core import mail


def send_mass_html_mail(datatuple):
    """
    Send multiple emails using Django built-in mailing package.
    This code is adapted from One Day Intern Project (team member previous project)
    and was originally adapted from
    https://stackoverflow.com/questions/7583801/send-mass-emails-with-emailmultialternatives
    """
    connection = mail.get_connection(fail_silently=False)
    messages = []
    for subject, html, from_email, recipient in datatuple:
        message = mail.EmailMultiAlternatives(subject, '', from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)

    return connection.send_messages(messages)
