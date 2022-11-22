import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_mail(content):
    sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("20z434@psgtech.ac.in")  # Change to your verified sender
    to_email = To("20z435@psgtech.ac.in")  # Change to your recipient
    subject = "Low Stock Notification!!"
    # content = 'test'
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)