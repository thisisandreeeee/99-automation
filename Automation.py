from pprint import pprint
from GSpreadHandler import GSpreadHandler
from MailChimpHandler import MailChimpHandler
from SentlyHandler import SentlyHandler
import sys, json
from datetime import datetime

class Automation:
    def __init__(self):
        isSafe = raw_input("Welcome! Type 'unsafe' to run without warnings. Enter any other key to proceed in safe mode.\n>> ")
        self.safeMode = False if isSafe.lower().strip() == 'unsafe' else True

    def run(self):
        gsh = GSpreadHandler()
        msg = "Press [Enter] to update the list of unsent emails and SMS.\nType 'Exit' to quit the program.\n>> "
        self.checkExit(msg)
        gsh.updateFromLatest()

        unsent_sms = json.loads(open("unsent_sms.json").read())
        unsent_emails = json.loads(open("unsent_emails.json").read())
        mch = MailChimpHandler()
        slh = SentlyHandler()

        msg = "Press [Enter] to continue adding new users to the MailChimp subscription list.\nType 'Exit' to quit the program.\n>> "
        self.checkExit(msg)
        allEmails = []
        allTimestamps = []
        for item in unsent_emails:
            resp = mch.createUser(item)
            allEmails.append(item['email'])
            allTimestamps.append(item['timestamp'])

        dtString = datetime.now().strftime("%d %B %Y") + ' Training Confirmation'
        settings = {
            'subject_line': dtString,
            'title': dtString,
            'from_name': '99.co',
            'reply_to': 'hello@99.co'
        }
        tracking = {
            'clicktale': dtString,
             'ecomm360': True,
             'goal_tracking': True,
             'google_analytics': dtString,
             'html_clicks': True,
             'opens': True,
             'text_clicks': True
        }

        msg = "Press [Enter] to send out emails to all newly subscribed users.\nType 'Exit' to quit the program.\n>> "
        self.checkExit(msg)
        if mch.sendEmails(allEmails, settings, tracking): # returns true if email sent successfully
            gsh.emailSent(allTimestamps)
        mch.printLogs()

        allTimestamps = []
        for item in unsent_sms:
            timestamp = slh.sendSms(item)
            allTimestamps.append(timestamp) if timestamp is not None else allTimestamps
        status = slh.checkStatus()
        curr = 0
        while not status:
            status = slh.checkStatus()
            time.sleep(5)
            curr += 1
            if curr == 10:
                print "Number of tries exceeded"
                sys.exit(0)
        gsh.smsSent(allTimestamps)


    def checkExit(self, msg):
        if self.safeMode:
            prompt = raw_input(msg)
            if prompt.lower().strip() == 'exit':
                print "Thank you. Goodbye."
                sys.exit(0)
            print "Please wait..."

if __name__=="__main__":
    app = Automation()
    app.run()
