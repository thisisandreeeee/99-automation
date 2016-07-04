from pprint import pprint
from GSpreadHandler import GSpreadHandler
from MailChimpHandler import MailChimpHandler
from SentlyHandler import SentlyHandler
import sys, json

class Automation:
    def __init__(self):
        pass

    def run(self):
        gsh = GSpreadHandler()
        msg = "Welcome! Press [Enter] to update the list of unsent emails and SMS.\nType 'Exit' to quit the program.\n>> "
        self.checkExit(msg)
        gsh.updateFromLatest()

        unsent_sms = json.loads(open("unsent_sms.json").read())
        unsent_emails = json.loads(open("unsent_emails.json").read())
        mch = MailChimpHandler()
        slh = SentlyHandler()

        msg = "Press [Enter] to continue adding new users to the MailChimp subscription list.\nType 'Exit' to quit the program.\n>> "
        self.checkExit(msg)
        for item in unsent_emails:
            resp = mch.createUser(item)
            # gsh.emailSent(item)
        mch.printLogs()

        for item in unsent_sms:
            slh.sendSms(item)
        status = sh.checkStatus()
        curr = 0
        while not status:
            status = sh.checkStatus()
            time.sleep(5)
            curr += 1
            if curr == 10:
                print "Number of tries exceeded"
                break

    def checkExit(self, msg):
        prompt = raw_input(msg)
        if prompt.lower().strip() == 'exit':
            print "Thank you. Goodbye."
            sys.exit(0)
        print "Please wait..."

if __name__=="__main__":
    app = Automation()
    app.run()
