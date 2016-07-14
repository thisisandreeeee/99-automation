# sentlychimpsheets-bot
This is a bot that checks the [training sign up](https://docs.google.com/spreadsheets/d/1LKxCYVKpyAcDb4J0FhGviVoIHhO6fuPGHUn5RtnZk0M/edit#gid=1968485068) google sheets, which is autopopulated from a signup google form. It then sends a confirmation email (via mailchimp) to agents who have just signed up for the training, as well as a reminder SMS if their training is on the following day.

## Usage
Clone the repository
```
git clone git@github.com:team99/sentlychimpsheets-bot.git
```
Install the required packages
```
pip install -r requirements.txt
```
Create a `config.py` file of the following format:
```
# Sently
bearertoken = 'your-bearer-token-here'
sendermobile = '+6585699179' # default mobile number

 # Mailchimp
 mailchimpkey = 'your-mailchimp-key-here'
```
Obtain the credentials json file for your Google app and **name it creds.json**. It should look like this:
```
{
  "type": "service_account",
  "project_id": "project-id",
  "private_key_id": "private-key-id",
  "private_key": "private-key",
  "client_email": "client-email",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "cert-url"
}
```
You are now ready to run the script:
```
python Automation.py
```

## Improvements
- GSpreadHandler uses the `gspread` python library, which isn't very fast in searching for cell values. This results in a very naive way of updating our spreadsheet when emails / SMS have been sent.
- To implement a better way of updating the sheets ONLY when an email or SMS has been sent. Current implementation assumes that either all emails (or SMS) are sent, or not at all, instead of tracking individually.
- Further testing required for sending emails via Mailchimp campaigns.
