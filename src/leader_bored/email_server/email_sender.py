class EmailSender(object):
    __instance = None
    @staticmethod
    def getInstance():
        if EmailSender.__instance == None:
            EmailSender()
        return EmailSender.__instance

    def __init__(self):
        if EmailSender.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            EmailSender.__instance = self

    # Imported Methods.
    from ._email_sender_impl import render_template, send_email

emailSender = EmailSender.getInstance()
