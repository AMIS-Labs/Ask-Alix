# -*- coding: utf-8 -*-

import spacy
import os
import time
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
import schedule
import time

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
PROMPT_TO_FOLLOW = "Analyser l'objet de l'e-mail, puis analyser le corps de l'e-mail. Si la question concerne le sujet de l'assurance, générer une réponse clair et pégagogique ; Décrire précisément les jargons, accronymes et termes techniques comme si tu l'expliquais à un enfant. Si la réponse nécéssite plus de spécification et/ou information pour être exacte et safisfaisante, tu dois formuler tes requêtes à l'expéditeur de l'email entrant. Une fois que tu as toutes les informations minimales nécéssaire à la formulation d'une réponse, tu génère cette réponse dans le respect des conditions indiquées. Tu ne dois jamais laisser l'interlocuteur rechercher par lui-même la réponse, tu dois lui fournir et si ce n'est pas possible, tu dois lui poser des questions afin de pouvoir mieux comprendre sa requête, l'affiner et lui fournir une réponse avec la plus forte probabilité d'exactitute. Si la question ne concerne pas le sujet de l'assurance, tu dois répondre obligatoirement ceci : Bonjour {sender_firstname},\n\n{INTRODUCTION_SENTENCE}, je ne suis pas conçue pour répondre aux questions autres que celles concernant les assurances."

# Délai de lecture de la boîte de réception (en secondes)
CHECK_INTERVAL = 60

# Variables pour personnaliser la réponse
BOT_NAME = "Alix"
INTRODUCTION_SENTENCE = "Je suis Alix, votre assistante virtuelle. Je suis une intelligence artificielle produite par IASSUR dans le but de vous aider au sujet de vos assurances professionnelles."
POLITE_CLOSING = "N'hésitez pas à me poser d'autres questions. Je suis là pour vous aider."
POST_SCRIPTUM = "Veuillez noter que cette réponse est simulée et basée sur mes connaissances générales. Il est donc toujours conseillé de vérifier les sources officielles à jour"

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

def run_program():
    process_emails()

# Planifier l'exécution toutes les 5 minutes
schedule.every(5).minutes.do(run_program)

# Boucle d'exécution principale
while True:
    schedule.run_pending()
    time.sleep(1)

# Fonction pour extraire les informations personnelles du corps de l'e-mail
# (Nom, Prénom, Job Title, Nom de l'entreprise, Site internet, Profil LinkedIn, etc.)
    # Extraction du nom et du prénom

def extract_personal_info(body):
    nlp = spacy.load("fr_core_news_sm")

    personal_info = {"Last Name": "", "First Name": ""}

    # Extraction du nom et du prénom
    for entity in doc.ents:
        if entity.label_ == "PER":
            name_parts = entity.text.split()
            if len(name_parts) >= 2:
                if "Nom" not in personal_info:
                    personal_info["Nom"] = name_parts[-1]  # Dernier élément du nom
                elif "Prénom" not in personal_info:
                    personal_info["Prénom"] = " ".join(name_parts[:-1])  # Tous les éléments précédents
                else:
                    break

    return personal_info


    
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


    for entity in doc.ents:
        if entity.label_ == "PER":
            name_parts = entity.text.split()
            if len(name_parts) >= 2:
                personal_info["Nom"] = name_parts[-1]  # Dernier élément du nom
                personal_info["Prénom"] = " ".join(name_parts[:-1])  # Tous les éléments précédents


# Se connecter à la boîte de réception
mailbox = connect_to_mailbox()

# Liste pour stocker les identifiants des e-mails déjà traités
emails_traites = []
nouveaux_emails = []

def process_emails():
    # Votre code pour la récupération des nouveaux e-mails
    
    for email in nouveaux_emails:
        # Récupérer l'identifiant de l'e-mail
        email_id = get_email_id(email)

        # Vérifier si l'e-mail a déjà été traité
        if email_id in emails_traites:
            continue  # Ignorer l'e-mail car il a déjà été traité

        # Vérifier si l'e-mail est indésirable
        if is_email_indesirable(email):
            continue  # Ignorer l'e-mail indésirable

        # Traitement de l'e-mail
        traiter_email(email)

        # Ajouter l'identifiant de l'e-mail à la liste des e-mails traités
        emails_traites.append(email_id)

        # Autres actions à effectuer après le traitement de l'e-mail

# Fonction pour récupérer l'identifiant de l'e-mail
def get_email_id(email):
        sender = get_sender(email)
        body = get_body(email)
    # Logique pour extraire l'identifiant de l'e-mail
    # Retournez l'identifiant de l'e-mail
        pass

# Fonction pour vérifier si l'e-mail est indésirable
def is_email_indesirable(email):
    
    if "noreply" in email:
        return True
    else:
        return False

    # Logique pour vérifier si l'e-mail est indésirable
    # Retournez True si l'e-mail est indésirable, False sinon


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
    openai.api_key = os.environ["OPENAI_API_KEY"]
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
    prompt = "Bonjour"

    sender_firstname = ""  # Valeur par défaut

    # Vérifier si l'information a été extraite de l'e-mail
    if "sender_firstname" in personal_info:
        sender_firstname = personal_info["sender_firstname"]

    # Utiliser la variable sender_firstname dans la génération de la réponse
    prompt = "Bonjour {},\n\n{}\n\n".format(sender_firstname, INTRODUCTION_SENTENCE)

    prompt += "{}\n\n".format(INTRODUCTION_SENTENCE)
    prompt += "J'ai bien reçu votre question : {}\n\n".format(question)
    prompt += "Je vais vous fournir une réponse dans les plus brefs délais.\n\n"
    prompt += "Au plaisir de collaborer avec vous,\n"
    prompt += "{}".format(BOT_NAME)

    return prompt


def send_auto_reply(sender, subject, question, response):
    receiver = sender
    reply_subject = f"Re: {subject}"
    reply_message = f"Bonjour {sender_firstname},\n\n{response}\n\n{POLITE_CLOSING}\n\nAu plaisir de collaborer avec vous,\n{BOT_NAME}n\n{POST_SCRIPTUM}"

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
