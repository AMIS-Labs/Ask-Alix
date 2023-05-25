# -*- coding: utf-8 -*-

import os
import time
import imaplib
import email
import spacy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai

# Informations d'identification Gmail
GMAIL_ADDRESS = "questions-alix@iassurpro.com"
EMAIL_ADDRESS = "questions-alix@iassurpro.com"
GMAIL_APP_PASSWORD = "cvyolriqdmaehgeu"
IMAP_SERVER = "imap.gmail.com"
PASSWORD = "cvyolriqdmaehgeu"

# Clé secrète OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

# Options de l'appel API OpenAI
OPENAI_TEMPERATURE = 0.9
OPENAI_MAX_TOKENS = 1024
OPENAI_TOP_P = 1
OPENAI_FREQUENCY_PENALTY = 0
OPENAI_PRESENCE_PENALTY = 0.6
PROMPT_TO_FOLLOW = "Analyser l'objet de l'e-mail, puis analyser le corps de l'e-mail. Si la question concerne le sujet de l'assurance, générer une réponse clair et pégagogique ; Décrire précisément les jargons, accronymes et termes techniques comme si tu l'expliquais à un enfant. Si la question ne concerne pas le sujet de l'assurance, tu dois répondre obligatoirement ceci : Bonjour {sender_firstname},\n\n{INTRODUCTION_SENTENCE}, je ne suis pas conçue pour répondre aux questions autres que celles concernant les assurances."

# Délai de lecture de la boîte de réception (en secondes)
CHECK_INTERVAL = 60

# Variables pour personnaliser la réponse
BOT_NAME = "Alix"
INTRODUCTION_SENTENCE = "Je suis Alix, votre assistante virtuelle. Je suis une intelligence artificielle produite par la société IASSUR dans le but de vous aider au sujet de vos assurances professionnelles."
POLITE_CLOSING = "N'hésitez pas à me poser d'autres questions. Je suis là pour vous aider."

def send_gmail(sender_address, receiver_address, mail_subject, mail_content):
    message = MIMEMultipart()
    message["From"] = sender_address
    message["To"] = receiver_address
    message["Subject"] = mail_subject
    message.attach(MIMEText(mail_content, "plain"))

    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender_address, GMAIL_APP_PASSWORD)

    text = message.as_string()

    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print("Sent email to " + receiver_address + " with subject: " + mail_subject)

def process_email(email_data):
    message = email.message_from_bytes(email_data[0][1])
    sender = message["From"]
    subject = message["Subject"]
    body = ""

    if message.is_multipart():
        for part in message.get_payload():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8")
                break
    else:
        body = message.get_payload(decode=True).decode("utf-8")

    return sender, subject, body

def extract_personal_info(body):
    soup = BeautifulSoup(body, "html.parser")
    personal_info = {}
    
    # Fonction pour se connecter à la boîte de réception
def connect_to_mailbox():
    mailbox = imaplib.IMAP4_SSL("imap.gmail.com")
    mailbox.login(EMAIL_ADDRESS, PASSWORD)
    mailbox.select("INBOX")
    return mailbox

# Fonction pour récupérer les e-mails non lus
def fetch_unread_emails(mailbox):
    _, data = mailbox.search(None, "UNSEEN")
    email_ids = data[0].split()
    emails = []
    for email_id in email_ids:
        _, data = mailbox.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        emails.append(email_message)
    return emails

# Fonction pour extraire les informations personnelles du corps de l'e-mail
# (Nom, Prénom, Job Title, Nom de l'entreprise, Site internet, Profil LinkedIn, etc.)
def extract_personal_info(body):
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(body)

    personal_info = {}

    # Extraction du nom et du prénom
    for entity in doc.ents:
        if entity.label_ == "PER":
            name_parts = entity.text.split()
            if len(name_parts) >= 2:
                personal_info["Nom"] = name_parts[-1]  # Dernier élément du nom
                personal_info["Prénom"] = " ".join(name_parts[:-1])  # Tous les éléments précédents

    return personal_info

# Se connecter à la boîte de réception
mailbox = connect_to_mailbox()

# Récupérer les e-mails non lus
emails = fetch_unread_emails(mailbox)

# Parcourir les e-mails et extraire les informations personnelles

def process_emails():
    for email in emails:
        email_subject = email["Subject"]
        email_body = ""

        if email.is_multipart():
            for part in email.get_payload():
                if part.get_content_type() == "text/plain":
                    email_body = part.get_payload(decode=True).decode("utf-8")
                    break
        else:
            email_body = email.get_payload(decode=True).decode("utf-8")

        personal_info = extract_personal_info(email_body)

        print("Sujet:", email_subject)
        print("Informations personnelles:", personal_info)
        print("---")

        return personal_info

def generate_response(prompt, personal_info):
    # Générer la réponse en utilisant OpenAI en fonction du prompt et des informations personnelles
    openai.api_key = OPENAI_SECRET_KEY
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=PROMPT_TO_FOLLOW,
        temperature=0.9,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        n=1,
    )
    
    generated_text = response.choices[0].text.strip()
    
    # Ajouter un retour à la ligne après chaque point
    generated_text = ".\n".join(generated_text.split("."))
    
    return generated_text

def generate_prompt(sender_name, question):
    # Générer le prompt pour OpenAI en fonction du nom de l'expéditeur et de la question
    
    prompt = "Bonjour {},\n\n{}\n\n".format(sender_firstname, INTRODUCTION_SENTENCE)
    prompt += "J'ai bien reçu votre question : {}\n\n".format(question)
    prompt += "Je vais vous fournir une réponse dans les plus brefs délais.\n\n"
    prompt += "Cordialement,\n"
    prompt += "{}".format(BOT_NAME)


    return prompt

def send_auto_reply(sender, subject, question, response):
    receiver = sender
    reply_subject = f"Re: {subject}"
    reply_message = f"Bonjour {sender_firstname},\n\n{response}\n\n{POLITE_CLOSING}\n\nCordialement,\n{BOT_NAME}"

    send_gmail(GMAIL_ADDRESS, receiver, reply_subject, reply_message)

def process_emails():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        mail.select("inbox")

        while True:
            typ, email_data = mail.search(None, "UNSEEN")
            if typ != "OK":
                continue

            for num in email_data[0].split():
                typ, email_data = mail.fetch(num, "(RFC822)")
                if typ != "OK":
                    continue

                sender, subject, body = process_email(email_data)
                personal_info = extract_personal_info(body)
                prompt = generate_prompt(personal_info["Nom"], body)
                response = generate_response(prompt, personal_info)
                send_auto_reply(sender, subject, body, response)

                # Marquer l'email comme lu
                mail.store(num, "+FLAGS", "\\Seen")

            time.sleep(CHECK_INTERVAL)

    finally:
        mail.logout()

process_emails()

