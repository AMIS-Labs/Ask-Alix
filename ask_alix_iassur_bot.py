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
import requests
import openai
import schedule
import sqlite3
import json
import re
from googlesearch import search
from googlesearch import get_random_user_agent

# Informations d'identification Gmail
GMAIL_ADDRESS = "questions-alix@iassurpro.com"
EMAIL_ADDRESS = "questions-alix@iassurpro.com"
GMAIL_APP_PASSWORD = "cvyolriqdmaehgeu"
IMAP_SERVER = "imap.gmail.com"
PASSWORD = "cvyolriqdmaehgeu"
sender_address = "questions-alix@iassurpro.com"

# Clé secrète OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

# Options de l'appel API OpenAI
OPENAI_TEMPERATURE = 0.9
OPENAI_MAX_TOKENS = 1024
OPENAI_TOP_P = 1
OPENAI_FREQUENCY_PENALTY = 0
OPENAI_PRESENCE_PENALTY = 0.6
PROMPT_TO_FOLLOW = "Analyser l'objet de l'e-mail, puis analyser le corps de l'e-mail. Si la question concerne le sujet de l'assurance : Générer une réponse clair et pégagogique ; Décrire précisément les jargons, accronymes et termes techniques comme si tu l'expliquais à un enfant. Si la réponse nécéssite plus de spécification et/ou information pour être exacte et safisfaisante, tu dois formuler tes requêtes à l'expéditeur de l'email entrant. Une fois que tu as toutes les informations minimales nécéssaire à la formulation d'une réponse, tu génère cette réponse dans le respect des conditions indiquées. Tu ne dois jamais laisser l'interlocuteur rechercher par lui-même la réponse, tu dois lui fournir une réponse complète et pédagogique. Tu t'adresses à de parfaits novices sur le sujet. Si la question ne semble pas claire, tu dois lui poser des questions afin de pouvoir mieux comprendre sa requête, l'affiner et lui fournir une réponse avec la plus forte probabilité d'exactitute. Si la question ne concerne pas le sujet de l'assurance, tu dois répondre obligatoirement ceci : Bonjour {sender_firstname},\n\n{INTRODUCTION_SENTENCE}, cependant, je ne suis pas conçue pour répondre aux questions autres que celles concernant les assurances professionnelles."

# Délai de lecture de la boîte de réception (en secondes)
CHECK_INTERVAL = 60

# Variables pour personnaliser la réponse
BOT_NAME = "Alix"
INTRODUCTION_SENTENCE = "Je suis Alix, votre assistante virtuelle. Je suis une intelligence artificielle produite par IASSUR dans le but de vous aider à mieux comprendre le sujet des assurances professionnelles."
GREETING_SENTENCE = "Je suis ravi de vous revoir, j'espère que vous vous portez bien! Je ferai de mon mieux pour vous aider aujourd'hui !"
POLITE_CLOSING = "N'hésitez pas à me poser d'autres questions. Je suis là pour vous aider."
POST_SCRIPTUM = "Veuillez noter que cette réponse est simulée et basée sur mes connaissances générales. Il est donc toujours conseillé de vérifier les sources officielles à jour et consulter votre expert IASSUR pour un accompagnement approfondi."

# Fonction pour envoyer un e-mail Gmail
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

# Fonction pour se connecter à la boîte de réception
def connect_to_mailbox():
    mailbox = imaplib.IMAP4_SSL(IMAP_SERVER)
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
def extract_personal_info(body):
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(body)

    personal_info = {"Nom": "", "Prénom": ""}

    for entity in doc.ents:
        if entity.label_ == "PER":
            name_parts = entity.text.split()
            if len(name_parts) >= 2:
                if "Nom" not in personal_info:
                    personal_info["Nom"] = name_parts[-1]
                elif "Prénom" not in personal_info:
                    personal_info["Prénom"] = " ".join(name_parts[:-1])
                else:
                    break

    return personal_info

# Fonction pour extraire le lien LinkedIn de la signature
def extract_linkedin_url_from_signature(signature):
    pattern = r"(?i)\b(https?://(?:www\.)?linkedin\.com/\S+)\b"
    match = re.search(pattern, signature)
    if match:
        return match.group(1)
    return None

# Fonction pour extraire les informations du profil LinkedIn
def extract_linkedin_profile_info(linkedin_url):
    response = requests.get(linkedin_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("li", class_="inline t-24 t-black t-normal break-words").text.strip()
        job_title = soup.find("h2", class_="mt1 t-18 t-black t-normal break-words").text.strip()
        company = soup.find("h3", class_="t-16 t-black t-normal break-words").text.strip()
        return name, job_title, company
    return None, None, None

# Fonction pour extraire les informations de la signature et du profil LinkedIn
def extract_info_from_email(email, db_connection):
    signature = extract_signature_from_email(email)
    linkedin_url = extract_linkedin_url_from_signature(signature)
    if linkedin_url:
        name, job_title, company = extract_linkedin_profile_info(linkedin_url)
        if name and job_title and company:
            # Ajouter les informations extraites à personal_info
            personal_info["Nom"] = lastname(name)
            personal_info["Prénom"] = firstname(name)
            personal_info["Titre"] = job_title
            personal_info["Entreprise"] = company
            # Enregistrer les données dans la base de données
            save_interaction(email.get("ID"), personal_info, db_connection)
    return name

# Fonction pour enregistrer une interaction dans la base de données
def save_interaction(email_id, personal_info, db_connection):
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO interactions (email_id, personal_info) VALUES (?, ?)",
        (email_id, json.dumps(personal_info))
    )
    db_connection.commit()

# Fonction pour récupérer les données précédentes d'un interlocuteur depuis la base de données
def get_previous_interaction_data(email_id, db_connection):
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT personal_info FROM interactions WHERE email_id = ?",
        (email_id,)
    )
    data = cursor.fetchone()
    if data:
        return json.loads(data[0])
    return None

# Générer la réponse en utilisant OpenAI en fonction du prompt et des informations personnelles
def generate_response(prompt, personal_info):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=OPENAI_TEMPERATURE,
        max_tokens=OPENAI_MAX_TOKENS,
        top_p=OPENAI_TOP_P,
        frequency_penalty=OPENAI_FREQUENCY_PENALTY,
        presence_penalty=OPENAI_PRESENCE_PENALTY,
    )
    generated_text = response.choices[0].text.strip()
    # Ajouter un retour à la ligne après chaque point
    generated_text = ".\n".join(generated_text.split("."))
    return generated_text

# Générer le prompt pour OpenAI en fonction du nom de l'expéditeur et de la question
def generate_prompt(sender_name, question):
    prompt = ""

    # Vérifier si le destinataire a déjà reçu un premier email de l'adresse d'expédition
    if has_received_first_email(sender_name, db_connection):
        prompt += "{}\n\n".format(GREETING_SENTENCE)
        prompt += "J'ai bien reçu votre question : {}\n\n".format(question)
        prompt += "Je vais vous fournir une réponse dans les plus brefs délais.\n\n"
        prompt += "Au plaisir de collaborer avec vous,\n"
        prompt += "{}".format(BOT_NAME)
    else:
        prompt += "Bonjour {},\n\n{}\n\n".format(sender_name, INTRODUCTION_SENTENCE)
        prompt += "{}\n\n".format(INTRODUCTION_SENTENCE)
        prompt += "J'ai bien reçu votre question : {}\n\n".format(question)
        prompt += "Je vais vous fournir une réponse dans les plus brefs délais.\n\n"
        prompt += "Au plaisir de collaborer avec vous,\n"
        prompt += "{}".format(BOT_NAME)

    return prompt

# Envoyer une réponse automatique à l'expéditeur
def send_auto_reply(sender, subject, question, response):
    receiver = sender
    reply_subject = f"Re: {subject}"
    reply_message = f"Bonjour {personal_info['Prénom']},\n\n{response}\n\n{POLITE_CLOSING}\n\nAu plaisir de collaborer avec vous,\n{BOT_NAME}\n\n{POST_SCRIPTUM}"
    send_gmail(GMAIL_ADDRESS, receiver, reply_subject, reply_message)

# Fonction principale pour traiter les e-mails
def process_emails(db_connection):
    mailbox = connect_to_mailbox()
    unread_emails = fetch_unread_emails(mailbox)

    for email in unread_emails:
        sender, subject, body = process_email(email)
        personal_info = extract_personal_info(body)
        email_id = email.get("ID")
        previous_data = get_previous_interaction_data(email_id, db_connection)
        if previous_data:
            # Utiliser les données précédentes pour personnaliser la réponse
            personal_info.update(previous_data)
        prompt = generate_prompt(personal_info["Prénom"], body)
        response = generate_response(prompt, personal_info)
        send_auto_reply(sender, subject, body, response)

        # Marquer l'e-mail comme lu
        mailbox.store(email.get("ID"), "+FLAGS", "\\Seen")

    mailbox.logout()

# Planifier l'exécution du traitement des e-mails toutes les CHECK_INTERVAL secondes
schedule.every(CHECK_INTERVAL).seconds.do(process_emails, db_connection)

# Boucle d'exécution principale
if __name__ == "__main__":
    # Connexion à la base de données
    db_connection = sqlite3.connect("AskAlixMemory.db")
    cursor = db_connection.cursor()

    # Création de la table interactions si elle n'existe pas déjà
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS interactions (email_id TEXT PRIMARY KEY, personal_info TEXT)"
    )

    while True:
        schedule.run_pending()
        time.sleep(1)

    # Fermeture de la connexion à la base de données
    db_connection.close()
