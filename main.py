from bs4 import BeautifulSoup
import requests
from datetime import date
from pprint import pprint
import boto3
url = "secret"
webhookURL = "secret"

db = boto3.resource("dynamodb")
table = db.Table("311-announcements")

def lambda_handler(event, context):
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")
    list = soup.find_all('ul')[0].find_all('li')
    for item in list:
        temp = {}
        temp['announcement-id'] = item['id']
        temp['title'] = item.find('span', 'announce-title').get_text()
        item.find('span', 'announce-title').extract()
        temp['desc'] = item.get_text()[7:]
        try:
            if not table.get_item(Key={'announcement-id' : temp['announcement-id']}).get("Item"):
                table.put_item(
                        Item=temp
                )
                payload = {
                    "username": "311 Announcement",
                    "embeds": [
                        {
                            "title": temp['title'],
                            "description": temp['desc']
                        }
                    ]
                }
                requests.post(webhookURL, json=payload)
        except Exception as e:
            print(e)

