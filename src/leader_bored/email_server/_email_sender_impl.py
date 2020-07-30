import jinja2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import sys
import smtplib, ssl
import os

from leader_bored.core import settings

def render_template(self, template, **kwargs):
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


def send_email(self, to, sender='CpLeaderbored<no-reply@cp-leaderboard.com>', password="",cc=None, bcc=None, subject=None, body=None):
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