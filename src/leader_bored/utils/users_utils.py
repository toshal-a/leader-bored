from itsdangerous import URLSafeTimedSerializer
from leader_bored.email_server import emailSender
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
    link = "https://cp-leaderboard.me/confirm_email/"
    return link + hash


def create_reset_password_url(hash:str):
    link = "https://cp-leaderboard.me/reset_password/"
    return link + hash
    
def send_new_account_email(email_to: str, username: str):
    confirmation_id=generate_confirmation_token(email_to)
    confirmation_link=create_confirmation_url(confirmation_id)

    html = emailSender.render_template( settings.TEMPLATE_DIR + 'call_to_action.html', 
            header="Activate Account",
            text="You are almost there. To finish activating your account please click the link below. <br> This link will expire in 10 minutes.",
            c2a_link=confirmation_link,
            c2a_button="Activate Account")
    
    to_list = [email_to]
    sender = settings.MAIL_SENDER_EMAIL 
    subject = f"{settings.PROJECT_NAME} - New account for user {username}"
    password = settings.MAIL_SENDER_PASSWORD
    
    # send email to a list of email addresses.
    emailSender.send_email(to_list, sender, password, None, None, subject, html)

def send_reset_password_email(email_to: str, username: str):
    reset_id=generate_confirmation_token(email_to)
    reset_link=create_reset_password_url(reset_id)

    html = emailSender.render_template( settings.TEMPLATE_DIR + 'call_to_action.html', 
            	header= "Password Reset",
                text="You requested a password reset. Please use the button below to continue the process. <br> The link will expire in 10 minutes",
                c2a_link=reset_link,
                c2a_button="Reset Password")
    
    to_list = [email_to]
    sender = settings.MAIL_SENDER_EMAIL 
    subject = f"{settings.PROJECT_NAME} - Password reset request for user {username}"
    password = settings.MAIL_SENDER_PASSWORD
    
    # send email to a list of email addresses.
    emailSender.send_email(to_list, sender, password, None, None, subject, html)


def send_feedback_mail(
    username: str, 
    title: str, 
    feedback: str
):
    html = emailSender.render_template( settings.TEMPLATE_DIR + 'feedback_form.html', 
            	    header= f"Feedback from user - {username}",
                    text=feedback,
                )
    
    to_list = ['feedback@cp-leaderboard.me']
    sender = settings.MAIL_SENDER_EMAIL 
    subject = f"Feedback - {title}"
    password = settings.MAIL_SENDER_PASSWORD
    
    # send email to a list of email addresses.
    emailSender.send_email(to_list, sender, password, None, None, subject, html)

    