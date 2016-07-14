import requests
import base64
from datetime import datetime
from config import bearertoken, sendermobile

class SentlyHandler:
    def __init__(self):
        self.url = 'https://apiserver.sent.ly'
        self.headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': 'Bearer ' + bearertoken,
          'Accept-Encoding': 'gzip'
        }
        self.sender = sendermobile
        self.message_ids = []

    def sendSms(self, item):
        mobile = "+65" + item['mobile']
        timing = item['session']['training_date']
        if self.trainingIsTomorrow(timing):
            msg = "Hi " + item['name'].split(' ')[0]
            msg += ", thank you for signing up for 99.co's agents training tomorrow! :)\n"
            msg += "Training details: " + str(timing) + "\n"
            msg += "Venue: Real Centre Network, #09-16 HDB Hub Biz 3, 310490.\n"
            msg += "This training only covers the " + str(item['session']['os'].split(' ')[0]) + " app, so do bring them along with you. Call +65 64640552 if you need any assistance. See you tomorrow! :)"
            body = {
                'from' : self.sender,
                'to' : mobile,
                'text' : msg
            }
            urlpath = self.url + '/api/outboundmessage/'
            r = requests.post(urlpath, headers = self.headers, json = body)
            if r.status_code != 200:
                message_id = r.json()['response_data']['message_id']
                self.message_ids.append((item['name'], message_id))
                print 'SMS sent to %s' % item['name']

    def trainingIsTomorrow(self, timing):
        day, date, time = timing.split(',')
        year = str(datetime.now().year)
        starttime = str(time.split("-")[0].strip())
        dt = datetime.strptime(year + " " + date.strip() + " " + starttime, "%Y %d %B %I:%M%p")
        return True if (dt - datetime.now()).days <= 2 else False

    def checkStatus(self):
        allSent = True
        for name, idx in self.message_ids:
            r = requests.get(urlpath + idx, headers = self.headers)
            if r.status_code == 200:
                status = r.json()['response_data']['status']
                if status != 'Delivered':
                    allSent = False
                    print "%s status: %s" % (name, status)
        print ''
        return allSent

if __name__ == "__main__":
    sh = SentlyHandler()
    sh.sendSms({
        "name": "Sihao",
        "cea": "r014196A",
        "mobile": "97461960",
        "timestamp": "6/26/2016 22:27:15",
        "agency": "ERA",
        "session": {
            "training_date": "Wednesday, 5 July, 10:00am - 12:00pm",
            "os": "Samsung/Android phone only"
        },
        "email": "rs8188@yahoo.com.sg"
    })
    status = sh.checkStatus()
    while not status:
        status = sh.checkStatus()
