import os


def setup_google_storage_credentials():
    google_application_credentials = os.getenv('GOOGLE_STORAGE_CREDENTIAL_VALUES')
    if google_application_credentials:
        google_application_credentials = google_application_credentials.replace('\\\\', '\\')

        with open('storage-credentials.json', mode='w') as google_storage_credential_file:
            google_storage_credential_file.write(google_application_credentials)

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'storage-credentials.json'
