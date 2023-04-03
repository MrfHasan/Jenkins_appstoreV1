import boto3
import requests
import os

app_id = os.environ.get('APP_IDS', '1498060269')
current_version = os.environ.get('CURRENT_VERSION', '1.1.20')
recipient_emails = os.environ.get('RECIPIENT_EMAILS')
sender_email = os.environ.get('SENDER_EMAIL')
region = os.environ.get('AWS_REGION')


def send_email(subject, body):
    client = boto3.client('ses', region_name=region)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': recipient_emails.split(',')
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=sender_email
        )
        print("Email sent successfully.")
        return True
    except client.exceptions.ClientError as e:
        print(f"An error occurred while sending email: {e.response['Error']['Message']}")
        return False


def lambda_handler(event, context):
    try:
        app_ids = app_id.split(',')
        current_versions = current_version.split(',')
        for i in range(len(app_ids)):
            url = f"https://itunes.apple.com/lookup?id={app_ids[i]}"
            response = requests.get(url)
            data = response.json()

            if data['resultCount'] == 0:
                # Get app name from ID
                app_name_response = requests.get(f"https://itunes.apple.com/lookup?id={app_ids[i]}")
                app_name_data = app_name_response.json()
                app_name = app_name_data['results'][0]['trackName']

                message = f"Dear concern,\n\n{app_name} ({app_ids[i]}) is not available on the Apple App Store.\n\nRegards,\nTeam GIM"
                print(message)
                subject = f"{app_name} is not available on Apple App Store"
                send_email(subject, message)
            else:
                app_name = data['results'][0]['trackName']
                app_version = data['results'][0]['version']
                if app_version == current_versions[i]:
                    message = f"Dear concern,\n\n{app_name} is available on the Apple App Store and it is up to date. No need to worry.\n\nRegards,\nTeam GIM"
                    print(message)
                    # subject = f"{app_name} is available on Apple App Store"
                    # send_email(subject, message)
                else:
                    message = f"Dear concern,\n\n{app_name} is available on the Apple App Store, but it is not up to date. Please update to version {app_version}.\n\nRegards,\nTeam GIM"
                    print(message)
                    # subject = f"{app_name} is available on Apple App Store, but it is not up to date"
                    # send_email(subject, message)
    except Exception as e:
        print(f"Error checking app versions: {e}")
