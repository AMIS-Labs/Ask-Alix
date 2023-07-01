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
import socket
import re
from googlesearch import search
from googletrans import Translator
from googlesearch import get_random_user_agent
from langdetect import detect_langs, lang_detect_exception
from iso639 import languages
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Informations d'identification Gmail
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
IMAP_SERVER = "imap.gmail.com"
PASSWORD = os.environ["GMAIL_PASSWORD"]
GMAIL_ADRESS = os.environ["GMAIL_ADDRESS"]

# Nom de la base de données SQLite
DATABASE_NAME = "AskAlixMemory"
DATABASE_FILE = "AskAlixMemory.db"

# Chemin d'accès à la base de données SQLite
DATABASE_PATH = "/Users/wagceo/AskAlixMemory.db"

# Établir la connexion à la base de données
db_connection = sqlite3.connect(DATABASE_PATH)

# Données liés au destinataire
RECEIVER_ADRESS = email_id
EMAIL_ID = extract_email_from_email(email)
LANGUAGE = detect_language(email_text)
DETECTED_LANGUAGE = detect_language(email_text)
RECEIVER = email_id
EMAIL_ADRESS = email_id

# Définition générale
SENDER_ADDRESS = os.environ["GMAIL_ADDRESS"]
BOT_EMAIL_ADRESS = sender_adress
SENDER = os.environ["GMAIL_ADDRESS"]
BOT_EMAIL_ADRESS = os.environ["GMAIL_ADDRESS"]
SENDER_ADRESS = os.environ["GMAIL_ADDRESS"]


def increment_sent_emails(conn, email_id):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Emails SET number_sent_emails = number_sent_emails + 1 WHERE email_id = ?;
    ''', (email_id,))
    conn.commit()
    

# Fonction pour extraire l'adresse e-mail de l'email entrant
def extract_email_from_email(email):
    email_address = email.sender
    return email_address

def save_email_to_db(email_address):
    conn = None
    try:
        # Connexion à la base de données
        conn = sqlite3.connect('AskAlixmemory.db')

        # Création d'un curseur
        cursor = conn.cursor()
        
        # Créez une table si elle n'existe pas déjà
        cursor.execute('''
              CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        firstname TEXT,
        lastname TEXT,
        email_id TEXT,
        jobtitle TEXT,
        company_city TEXT,
        company_country TEXT,
        language TEXT,
        company_name TEXT,
        insurance_broker_name TEXT,
        insurance_company_name TEXT,
        contract_duration TEXT,
        company_industry TEXT,
        user_desires TEXT,
        email_subjects TEXT,
        number_received_emails INTEGER DEFAULT 0,
        number_sent_emails INTEGER DEFAULT 0);
        ''')
        
        # Insérez l'adresse e-mail dans la table. 
        # NOTE: à ce stade, nous insérons des valeurs NULL pour les autres champs.
        cursor.execute('''
            INSERT OR IGNORE INTO Emails(email_id, lastname, firstname, jobtitle, company_name, company_city, company_country, company_industry, language, insurance_broker_name, insurance_company_name, contract_duration, email_subjects, number_received_emails,)
            VALUES (?, NULL, NULL, NULL);
        ''', (email_address,))
        
        # Commitez les changements
        conn.commit()

    except sqlite3.Error as e:
        print(f"Une erreur s'est produite lors de l'interaction avec la base de données: {e}")

    finally:
        # Fermeture de la connexion à la base de données
        if conn is not None:
            conn.close()


# Initialisation de la base de données
DATABASE_FILE = "AskAlixMemory.db"
conn = sqlite3.connect(DATABASE_FILE)
c = conn.cursor()

# Les informations d'identification de l'API Google
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Votre URL de formulaire Google
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe_3MZPKjeqN7IqvR3uaNmfUVC4ccIAikAL0k2i4e1a9mtS4A/viewform?embedded=true"

# Dictionnaire pour stocker le nombre de messages par adresse e-mail
email_counter = {}

def send_gmail(sender, receiver, subject, message):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.ehlo()
        server.starttls()
        server.login(sender, GMAIL_APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')
        
        
def handle_incoming_email(email):
    email_id = extract_email_from_email(email)
    from_address = email['from']
    # Incrémenter le compteur pour cette adresse e-mail
    email_counter[from_address] = email_counter.get(from_address, 0) + 1

    # Si c'est le 3ème, 10ème, 15ème message de cette adresse e-mail, etc., envoyer le lien vers le formulaire
    if email_counter[from_address] in [3, 10, 15] or (email_counter[from_address] > 15 and email_counter[from_address] % 5 == 0):
        send_form_link(form_url, from_address)        

# Envoyer une réponse automatique à l'expéditeur exclusivement qu'à partir du 3e message entrant
def send_form_link(form_url, to_address):
    receiver_email = email_id
    reply_subject = f"Personnalisation de votre expérience d'utilisation de l'assistance Alix"
    reply_message = f"Bonjour,\n\n\ Merci de votre utilisation du service d'assistance Alix,\n\ndans l'optique d'améliorer la qualité de mes réponses ainsi que vous offrir la meilleure expérience personnalisée possible,\n\nje vous invite à remplir ce formulaire ci-joint : \n{form_url}\n\n{POLITE_CLOSING}\n\nAu plaisir de collaborer avec vous,\n{BOT_NAME}\n\n"
    send_gmail(GMAIL_ADDRESS, receiver, reply_subject, reply_message)
    
def form_filled(email_address):
    # Ouverture du Google sheet
    sheet = client.open('ASK_ALIX_USERS_ID').sheet1

    # Obtenir toutes les valeurs du Google sheet
    all_values = sheet.get_all_values()

    # Chercher les données pour l'adresse e-mail donnée et retourner True si les données existent, False autrement
    for row in all_values:
        if row[0] == email_address:
            return True
    return False

def fetch_form_data(email_address):
    # Ouverture du Google sheet
    sheet = client.open('ASK_ALIX_USERS_ID').sheet1

    # Obtenir toutes les valeurs du Google sheet
    all_values = sheet.get_all_values()

    # Chercher les données pour l'adresse e-mail donnée et retourner les données
    for row in all_values:
        if row[0] == email_address:
            return row[1:]
    return None
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_to_db(data, email_id, email_address):
    # Connectez-vous à votre base de données SQLite
    conn = sqlite3.connect('AskAlixmemory.db')
    # Créez un curseur pour exécuter les commandes SQL
    cursor = conn.cursor()
    
    # Exécutez une commande SQL INSERT pour insérer les données dans la table
    cursor.execute('''
        UPDATE Emails SET data = ? WHERE email_id = ?;
    ''', (data, email_id))

    # Validez (commit) les changements
    conn.commit()

    # Fermez la connexion à la base de données
    conn.close()

    # Google Sheets
    # Définissez le scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # Ajoutez vos informations d'identification
    creds = ServiceAccountCredentials.from_json_keyfile_name('alix-assistant@ask-alix-users-id-ledger.iam.gserviceaccount.com', scope)

    # Autorisez les informations d'identification
    client = gspread.authorize(creds)

    # Ouvrez la feuille de calcul
    sheet = client.open('ASK_ALIX_USERS_ID').sheet1 # Assurez-vous de remplacer 'sheetname' par le nom de votre feuille de calcul

    # Écrivez les données
    sheet.append_row([email_id, data])

    # Si le formulaire a été rempli, enregistrer les données dans la base de données SQLite
    if form_filled(from_address):
        form_data = fetch_form_data(from_address)
        save_to_db(form_data, email_id, from_address)
 
def is_valid_email_domain(email):
    domain = email.split('@')[-1]
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:  # cela signifie que le nom d'hôte n'a pas été trouvé
        return False


# Clé secrète OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

# Options de l'appel API OpenAI
OPENAI_TEMPERATURE = 0.9
OPENAI_MAX_TOKENS = 1024
OPENAI_TOP_P = 1
OPENAI_FREQUENCY_PENALTY = 0
OPENAI_PRESENCE_PENALTY = 0.6
PROMPT_TO_FOLLOW = "Analyser l'objet de l'e-mail, puis analyser le corps de l'e-mail. Si la question concerne le sujet de l'assurance : Générer une réponse claire et pédagogique ; Décrire précisément les jargons, accronymes et termes techniques comme si tu l'expliquais à un enfant. Si la réponse nécéssite plus de spécification et/ou information pour être exacte et safisfaisante, tu dois formuler tes requêtes à l'expéditeur de l'email entrant. Une fois que tu as toutes les informations minimales nécéssaire à la formulation d'une réponse, tu génère cette réponse dans le respect des conditions indiquées. Tu ne dois jamais laisser l'interlocuteur rechercher par lui-même la réponse, tu dois lui fournir une réponse complète et pédagogique. Tu t'adresses à de parfaits novices sur le sujet. Si la question ne semble pas claire, tu dois lui poser des questions afin de pouvoir mieux comprendre sa requête, l'affiner et lui fournir une réponse avec la plus forte probabilité d'exactitute. Si la question ne concerne pas le sujet de l'assurance, tu dois répondre obligatoirement ceci : Bonjour {sender_firstname},\n\n{INTRODUCTION_SENTENCE}, cependant, je ne suis pas conçue pour répondre aux questions autres que celles concernant les assurances professionnelles."

# Délai de lecture de la boîte de réception (en secondes)
CHECK_INTERVAL = 60

# Variables pour personnaliser la réponse
BOT_NAME = "Alix"
INTRODUCTION_SENTENCE = "Je suis Alix, votre assistante virtuelle.\n\n\Je suis une intelligence artificielle produite par IASSUR dans le but de vous aider à mieux comprendre le sujet des assurances professionnelles."
GREETING_SENTENCE = "Je suis ravi de vous revoir,\n\n\j'espère que vous vous portez bien !\n\n\Je ferai de mon mieux pour vous aider aujourd'hui !\n\n\"
POLITE_CLOSING = "Il ne faut surtout pas à me poser d'autres questions.\n\n\Je suis là pour vous aider."
POST_SCRIPTUM = "Veuillez noter que cette réponse est simulée et basée sur mes connaissances générales.\n\n\Il est donc toujours conseillé de vérifier les sources officielles à jour et consulter votre expert IASSUR pour un accompagnement approfondi."

def detect_language(text):
    detected_lang = detect(text)
    return detected_lang

def translate_text(text, target_language):
    response = openai.Completion.create(
        engine='davinci',
        prompt=text,
        max_tokens=100,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=None,
        temperature=0.7
    )

    translated_text = response.choices[0].text.strip()
    return translated_text

# Détection de la langue de l'e-mail
detected_language = detect_language(email_text)

# Traduction des variables dans la langue détectée
translated_intro = translate_text(INTRODUCTION_SENTENCE, detected_language)
translated_greeting = translate_text(GREETING_SENTENCE, detected_language)
translated_closing = translate_text(POLITE_CLOSING, detected_language)
translated_post_scriptum = translate_text(POST_SCRIPTUM, detected_language)

# Utilisation des variables traduites dans la réponse
response = f"{translated_intro}\n\n{translated_greeting}\n\n{translated_closing}\n\n{translated_post_scriptum}"

print(response)

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
    
    
def increment_sent_emails(conn, email_id):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Emails SET number_sent_emails = number_sent_emails + 1 WHERE email_id = ?;
    ''', (email_id,))
    conn.commit()

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


def increment_received_emails(conn, email_id):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Emails SET number_received_emails = number_received_emails + 1 WHERE email_id = ?;
    ''', (email_id,))
    conn.commit()


# Fonction pour vérifier si les informations personnelles sont présentes dans la base de données
def is_personal_info_present_in_database(email_id, db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM users WHERE id = :id
    ''', {"id": email_id})
    count = cursor.fetchone()[0]
    return count > 0

def update_email_subjects(email_address, email_subject, db_connection):
    cursor = db_connection.cursor()
    # récupérez les sujets d'email actuels pour cet email_address
    cursor.execute('SELECT email_subjects FROM Emails WHERE email_id = ?', (email_address,))
    result = cursor.fetchone()
    if result is None:
        # si l'email_address n'existe pas encore, insérez-le avec le nouveau sujet
        cursor.execute('''
            INSERT INTO Emails(email_id, email_subjects)
            VALUES (?, ?);
        ''', (email_address, email_subject))
    else:
        # si l'email_address existe déjà, ajoutez le nouveau sujet à la liste
        current_subjects = result[0] if result[0] is not None else ""
        new_subjects = current_subjects + "," + email_subject if current_subjects else email_subject
        cursor.execute('''
            UPDATE Emails SET email_subjects = ? WHERE email_id = ?;
        ''', (new_subjects, email_address))

    # Commitez les changements
    db_connection.commit()

# Fonction pour récupérer les informations personnelles depuis la base de données
def get_personal_info_from_database(email_id, db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''
        SELECT firstname, lastname, email_id, jobtitle, company_city, company_country, language FROM users WHERE id = :id, company_name, insurance_broker_name, insurance_company_name, contract_duration, company_industry, user_desires, email_subjects, number_received_emails, number_sent_emails
    ''', {"id": email_id})
    row = cursor.fetchone()
    if row:
        return {
            "firstname": row[0],
            "lastname": row[1],
            "email_id": row[2],
            "jobtitle": row[3],
            "company_city": row[4],
            "company_country": row[5],
            "language": row[6],
            "company_name": row[7]
            "insurance_broker_name": row[8]
            "insurance_company_name": row[9]
            "contract_duration": row[10]
            "company_industry": row[11]
            "user_desires": row[12]
            "email_subjects": row[13]
            "number_received_emails": row[14]
            "number_sent_emails": row[15]
        }
    return None
        
# Fonction pour enregistrer les informations de l'e-mail dans la base de données
def save_email_info_to_database(email_id, email_type, location):
    db_connection = sqlite3.connect('AskAlixMemory.db')
    cursor = db_connection.cursor()

    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Enregistrer l'e-mail entrant
    if email_type == 'incoming':
        cursor.execute('''
            INSERT INTO emails (email_id, email_type, location, incoming_datetime)
            VALUES (?, ?, ?, ?)
        ''', (email_id, email_type, location, current_datetime))

    # Enregistrer l'e-mail sortant
    elif email_type == 'outgoing':
        cursor.execute('''
            UPDATE emails
            SET outgoing_datetime = ?
            WHERE email_id = ?
        ''', (current_datetime, email_id))

    db_connection.commit()
    db_connection.close()


def process_email(email):
    sender = email["From"]
    subject = email["Subject"]
    body = get_email_body(email)
    return sender, subject, body

def get_email_body(email):
    body = ""

    if email.is_multipart():
        for part in email.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8")
                break
    else:
        body = email.get_payload(decode=True).decode("utf-8")

    return body


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
def send_auto_reply(sender, subject, question, response, db_connection):
    receiver_email = email_id
    reply_subject = f"Re: {subject}"
    
    # Récupérer les informations personnelles de la base de données
    personal_info = get_personal_info_from_database(email_id, db_connection)

    # Vérifier si le prénom est présent dans les informations personnelles
    if personal_info and 'firstname' in personal_info:
        reply_message = f"Bonjour {personal_info['firstname']},\n\n{response}\n\n{POLITE_CLOSING}\n\nAu plaisir de collaborer avec vous,\n{BOT_NAME}\n\n{POST_SCRIPTUM}"
    else:
        reply_message = f"Bonjour,\n\n{response}\n\n{POLITE_CLOSING}\n\nAu plaisir de collaborer avec vous,\n{BOT_NAME}\n\n{POST_SCRIPTUM}"
    
    send_gmail(GMAIL_ADDRESS, receiver, reply_subject, reply_message)

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

        # Enregistrer l'interaction dans la base de données
        save_interaction_to_database(email_id, personal_info, response, db_connection)

        # Marquer l'e-mail comme lu
        mailbox.store(email.get("ID"), "+FLAGS", "\\Seen")

    mailbox.logout()

# Planifier l'exécution du traitement des e-mails toutes les CHECK_INTERVAL secondes
schedule.every(CHECK_INTERVAL).seconds.do(process_emails, db_connection)

# Fonction pour enregistrer l'interaction dans la base de données
def save_interaction_to_database(email_id, personal_info, response, db_connection):
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO interactions (email_id, personal_info, response) VALUES (?, ?, ?)",
        (email_id, json.dumps(personal_info), response),
    )
    db_connection.commit()

# Boucle d'exécution principale
if __name__ == "__main__":
    # Connexion à la base de données
    db_connection = sqlite3.connect(DATABASE_FILE)
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
