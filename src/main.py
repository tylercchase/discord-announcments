from bs4 import BeautifulSoup
import requests
from datetime import date
from pprint import pprint
import boto3
import os
url = [os.environ["CLASS"]]
webhookURL = [os.environ["WEBHOOK"]]

db = boto3.resource("dynamodb")
tables = [db.Table(os.environ["DYNAMO_DB"])]

def lambda_handler(event, context):
    for x in range(0,len(url)):
        r = requests.get(url[x])
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
                if not tables[x].get_item(Key={'announcement-id' : temp['announcement-id']}).get("Item"):
                    tables[x].put_item(
                            Item=temp
                    )
                    payload = {
                        "username": "Class Announcement",
                        "embeds": [
                            {
                                "title": temp['title'],
                                "description": temp['desc']
                            }
                        ]
                    }
                    requests.post(webhookURL[x], json=payload)
            except Exception as e:
                print(e)

