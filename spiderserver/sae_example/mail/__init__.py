class EmailMessage:
    def __init__(self):
        self.to = 'to'
        self.subject = 'subject'
        self.html = 'html'
        self.smtp = 'smtp'

    def send(self):
        return True