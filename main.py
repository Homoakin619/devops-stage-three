from fastapi import FastAPI
from typing import Optional
from datetime import datetime
import smtplib
import logging
from celery import Celery
from email.message import EmailMessage
import os
from dotenv import load_dotenv
load_dotenv()




log_file = "/var/log/messaging_system.log"
broker = os.environ.get('BROKER_URL')
sender = os.environ.get('SMTP_USER')
port = os.environ.get('SMTP_PORT')
password= os.environ.get('SMTP_PASSWORD')
host = os.environ.get('SMTP_HOST')


celery_app = Celery('main', broker=broker, backend="rpc://")
app = FastAPI()



def fileLogger(message):
    try:
        with open(log_file,"a+") as file_handler:
            file_handler.write(f'{message}\n')
    except Exception as fileException:
        logging.error(fileException)



@celery_app.task
def sendmail_task(recipient: str):
    send_mail(recipient)
    return



@app.get("/")
def base(sendmail: Optional[str] = None, talktome: Optional[str] = None):
    if sendmail:
        sendmail_task.delay(sendmail)
   
    if talktome:
       current_time = datetime.now().time()
       fileLogger(current_time)
        
    return {"sendmail": sendmail,"talktome": talktome}

def send_mail(recipient: str):
    try:
        with smtplib.SMTP_SSL(host=host,port=port) as mailer:
            
            mailer.login(user=sender,password=password)
            body = f'Hello {recipient}! You have a message from {sender}'

            message = EmailMessage()
            message.set_content(body)
            message['Subject'] = "Random Mail"
            message['From'] = sender
            message['To'] = recipient

            mailer.sendmail(sender,recipient,body)
  
    except Exception as mailError:
        print("====================== Mailing error ================")
        print(mailError)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)