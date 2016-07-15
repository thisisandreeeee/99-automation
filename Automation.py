from pprint import pprint
from GSpreadHandler import GSpreadHandler
from MailChimpHandler import MailChimpHandler
from SentlyHandler import SentlyHandler
import sys, json
from datetime import datetime
from Logger import log
import schedule, time

class Automation:
    def __init__(self, safe = False):
        self.safeMode = safe
        msg = "START - safe mode ON" if self.safeMode else "START - safe mode OFF"
        log(msg)

    def run(self):
        print "Running schedule: " + datetime.now().strftime("%H:%M:%S %d %B")
        gsh = GSpreadHandler()
        msg = "Press [Enter] to update the list of unsent emails and SMS.\nType 'Exit' to quit the program.\n>> "
        self.checkExit(msg)
        gsh.updateFromLatest()
        log('List of unsent emails and SMS has been updated.')

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
        mch.sendEmails(allEmails, settings, tracking) # TODO: check status code when this succeeds
        log("Emails sent to " + ", ".join(allEmails))
        gsh.emailSent(allTimestamps)
        log("Google Sheets updated with sent emails")

        msg = "Press [Enter] to proceed with sending reminder SMS.\nType 'Exit' to quit the program.\n>> "
        self.checkExit(msg)
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
                log("Exceeded maximum number of tries to check if SMS is sent.")
                sys.exit(0)
        gsh.smsSent(allTimestamps)
        log("Google Sheets updated with sent SMS\n\n#####\n")

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

    # uncomment below to run automagically
    # schedule.every().day.at("20:00").do(app.run)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(900)
