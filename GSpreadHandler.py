import gspread, requests, pandas as pd, re, json, time
from oauth2client.service_account import ServiceAccountCredentials

class GSpreadHandler:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        self.gc = gspread.authorize(credentials)
        self.workbook_id = '1LKxCYVKpyAcDb4J0FhGviVoIHhO6fuPGHUn5RtnZk0M'
        self.errors = []
        self.start = time.time()
        self.wks = self.gc.open_by_key(self.workbook_id).sheet1

    def updateFromLatest(self, starting_row = 3300):
        wks = self.wks

        list_of_lists = wks.get_all_values()
        df = pd.DataFrame(list_of_lists[starting_row:], columns=list_of_lists[0])
        df.drop(['', 'Name'], axis = 1, inplace = True)

        unsent_emails, unsent_sms = [], []
        for i in df.index:
            timestamp = df['Timestamp'][i]
            if timestamp == '':
                break
            is_email_sent, is_sms_sent = df['Confirmation Email'][i], df['SMS'][i]
            if not is_email_sent or not is_sms_sent:
                user = {}
                user['cea'] = df['CEA Number'][i]
                user['agency'] = df['Agency'][i]
                user['name'] = df['First Name'][i]
                user['timestamp'] = timestamp
                user['mobile'] = self.validateMobile(df['Phone Number'][i])
                user['email'] = self.validateEmail(df['Email Address'][i])
                user['session'] = self.parseSession(df['Which training session are you attending? (All trainings will be at Real Centre Network, #09-16 HDB Hub Biz 3, 310490)'][i])
            unsent_emails.append(user) if not is_email_sent else None
            unsent_sms.append(user) if not is_sms_sent else None
        open("unsent_emails.json",'w').write(json.dumps(unsent_emails, indent=4))
        open("unsent_sms.json",'w').write(json.dumps(unsent_sms, indent=4))

        if self.errors:
            print "###### Errors Encountered ######"
            for error in self.errors:
                print error
        print "Pulled latest information from google sheets in %.2f seconds" % (time.time() - self.start)

    def validateMobile(self, mobile):
        mobile = mobile.translate(None, '+ ') # remove + and whitespace
        try:
            if len(mobile) == 8:
                firstNum = int(mobile[0])
                if firstNum == 8 or firstNum == 9:
                    return mobile
            elif int(mobile[:2]) == 65 and len(mobile) == 10:
                return mobile[:2]
        except ValueError:
            return None
        else:
            self.errors.append('Invalid mobile number: ' + str(mobile))
            return None

    def validateEmail(self, email):
        email = email.translate(None, ' ').lower()
        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            return email
        else:
            self.errors.append('Invalid email: ' + str(email))
            return None

    def parseSession(self, session):
        try:
            details = {}
            details['os'] = session[session.index('(')+1:session.index(')')]
            timings = session[:session.index('(')].strip()
            details['training_date'] = timings
            return details
        except:
            self.errors.append('Invalid session: ' + str(session))
            return None

    def emailSent(self, allTimestamps):
        for timestamp in allTimestamps:
            cell = self.wks.find(timestamp)
            coord = "Q" + str(cell.row) # update column Q
            self.wks.update_acell(coord, 'Sent')
        print 'Google sheets updated with sent emails.'

    def smsSent(self, allTimestamps):
        for timestamp in allTimestamps:
            cell = self.wks.find(timestamp)
            coord = "P" + str(cell.row)
            self.wks.update_acell(coord, 'Sent')
        print 'Google sheets updated with sent SMS.'
