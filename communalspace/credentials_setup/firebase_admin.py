import os


def setup_firebase_admin_credentials():
    firebase_admin_credentials = os.getenv('FIREBASE_ADMIN_CREDENTIAL_VALUES')
    if firebase_admin_credentials:
        firebase_admin_credentials = firebase_admin_credentials.replace('\\\\', '\\')

        with open('firebase-credentials.json', mode='w') as google_storage_credential_file:
            google_storage_credential_file.write(firebase_admin_credentials)

