from itsdangerous import URLSafeTimedSerializer
import smtplib, ssl
import sys
import jinja2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import os

from leader_bored.core import settings

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt=settings.SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=settings.SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except:
        return False
    return email

def create_confirmation_url(hash:str):
    link = "https://cp-leaderboard.me/user/confirm_email/"
    return link + hash


def render_template(template, **kwargs):
    ''' renders a Jinja template into HTML '''
    # check if template exists.
    if not os.path.exists(template):
        print('No template file present: %s' % template)
        print(os.getcwd())
        sys.exit()

    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template(template)
    return templ.render(**kwargs)


def send_email(to, sender='CpLeaderbored<no-reply@cp-leaderboard.com>', password="",cc=None, bcc=None, subject=None, body=None):
    print(body)
    ''' sends email using a Jinja HTML template '''
    # convert TO into list if string
    if type(to) is not list:
        to = to.split()
    
    to_list = []
    if to != None:
        to_list += to 
    if cc != None:
        to_list += cc
    
    if bcc != None:
          to_list += bcc

    msg = MIMEMultipart('alternative')
    msg['From']    = sender
    msg['Subject'] = subject
    msg['To']      = ','.join(to)
    msg['Cc']      = ','.join(cc) if (cc!=None) else None 
    msg['Bcc']     = ','.join(bcc) if (bcc!=None) else None
    msg.attach(MIMEText(body, 'html'))
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(settings.MAIL_SERVER_HOST, settings.MAIL_SERVER_PORT, context=context) # or your smtp server
    server.login(sender, password)
    
    
    try:
        server.sendmail(sender, to_list, msg.as_string())
    except Exception as e:
        print(e)
    finally:
        server.quit()

    
def send_new_account_email(email_to: str, username: str):
    confirmation_id=generate_confirmation_token(email_to)
    confirmation_link=create_confirmation_url(confirmation_id)

    html = render_template( settings.TEMPLATE_DIR + 'call_to_action.html', 
            header="Activate Account",
            text="You are almost there. To finish activating your account please click the link below.\n This link will expire in 10 minutes.",
            c2a_link=confirmation_link,
            c2a_button="Activate Account")
    
    to_list = [email_to]
    sender = settings.MAIL_SENDER_EMAIL 
    subject = f"{settings.PROJECT_NAME} - New account for user {username}"
    password = settings.MAIL_SENDER_PASSWORD
    
    # send email to a list of email addresses.
    send_email(to_list, sender, password, None, None, subject, html)