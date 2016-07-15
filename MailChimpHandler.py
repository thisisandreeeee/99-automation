import requests
import hashlib
from config import mailchimpkey
from Logger import log

class MailChimpHandler:
    def __init__(self):
        self.url = 'https://us8.api.mailchimp.com/3.0'
        self.auth = ('andre', mailchimpkey)
        self.agentListId = '435b3eca36'
        self.campaignId = '1a410c9956' # Training Confirmation - DO NOT DELETE

    def createUser(self, item):
        email = item['email']
        name = item['name']
        body = {
            'email_address': email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': name.split(' ')[0],
                'MMERGE11': item['session']['training_date'],
                'MMERGE14': item['session']['os']
            }
        }
        email_hash = hashlib.md5(email.lower()).hexdigest()
        urlpath = self.url + '/lists/' + self.agentListId + '/members/'
        r = requests.get(urlpath + str(email_hash), auth = self.auth)
        if r.status_code == 200: # member is already subscribed to list
            r = requests.patch(urlpath + str(email_hash), auth = self.auth, json = body)
            if r.status_code == 200:
                log("%s is already a subscriber. Profile updated" % item['name'])
            else:
                log("Error updating %s mailchimp profile" % item['name'])
        elif r.status_code == 404: # member is not subscribed to list
            r = requests.post(urlpath, auth = self.auth, json = body)
            log("%s has been successfully subscribed")
        else:
            log("Invalid http request for %s" % item['name'])
        return r.json()

    def sendEmails(self, allEmails, settings, tracking):
        # Replicate previous campaign
        replica = requests.post(self.url + '/campaigns/' + self.campaignId + '/actions/replicate', auth = self.auth).json()
        newId = replica['id']
        log("Campaign %s has been replicated. New id is %s" % (self.campaignId, newId))

        # Create new segment
        segmentBody = {
            'name': settings['title'],
            'static_segment': allEmails
        }
        newSegment = requests.post(self.url + '/lists/' + self.agentListId + '/segments', auth = self.auth, json = segmentBody).json()
        log("New segment has been created with id %s" % newSegment['id'])

        # Update campaign details
        campaignBody = {
            'type': 'regular',
            'recipients': {
                'list_id': self.agentListId,
                'segment_opts': {
                    'saved_segment_id': newSegment['id']
                }
            },
            'settings': settings,
            'tracking': tracking
        }
        updateCampaign = requests.patch(self.url + '/campaigns/' + newId, json = campaignBody, auth = self.auth).json()
        log("Campaign has been updated with latest details")

        # Send email
        sendEmail = requests.post(self.url + '/campaigns/' + newId + '/actions/send', auth = self.auth)
