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
import re
from googlesearch import search
from googlesearch import get_random_user_agent

# Informations d'identification Gmail
GMAIL_ADDRESS = "questions-alix@iassurpro.com"
BOT_EMAIL_ADRESS = "questions_alix@iassurpro.com"
GMAIL_APP_PASSWORD = "cvyolriqdmaehgeu"
IMAP_SERVER = "imap.gmail.com"
PASSWORD = "cvyolriqdmaehgeu"
SENDER_ADRESS = "questions-alix@iassurpro.com"

# Nom de la base de données SQLite
DATABASE_NAME = "AskAlixMemory"
DATABASE_FILE = "AskAlixMemory.db"

# Chemin d'accès à la base de données SQLite
DATABASE_PATH = "/Users/wagceo/AskAlixMemory.db"

# Établir la connexion à la base de données
db_connection = sqlite3.connect(DATABASE_PATH)

# Données liés au destinataire
RECEIVER_ADRESS = email_id
EMAIL_ID = extract_email_id(EMAIL_ADDRESS)

# Définition générale
SENDER_ADDRESS = "questions-alix@iassurpro.com"
RECEIVER_ADRESS = email_id

# Fonction pour extraire l'adresse e-mail de l'email entrant
def extract_email_from_email(email):
    email_address = email.sender
    return email_address

# Fonction pour extraire le nom et le prénom à partir de l'adresse e-mail
def extract_name_from_email(email_address):
    parts = email_address.split("@")
    if len(parts) >= 2:
        name_parts = parts[0].split(".")
        if len(name_parts) >= 2:
            firstname = name_parts[0]
            lastname = name_parts[1]
            return firstname, lastname
    return None, None

# Fonction pour extraire la signature et vérifier la présence d'un lien LinkedIn
def extract_signature_from_email(email):
    signature = email.signature
    linkedin_url = None
    if signature:
        # Recherche d'un lien LinkedIn dans la signature
        if "linkedin.com" in signature:
            linkedin_url = extract_linkedin_url_from_signature(signature)
    return signature, linkedin_url

# Fonction pour extraire les informations personnelles à partir de l'email
def extract_personal_info_from_email(email):
    email_address = extract_email_from_email(email)
    firstname, lastname = extract_name_from_email(email_address)
    signature, linkedin_url = extract_signature_from_email(email)
    
    personal_info = {
        "Nom": lastname,
        "Prénom": firstname,
        "Lien LinkedIn": linkedin_url
    }
    return personal_info

# Fonction pour extraire les informations du profil LinkedIn
def extract_linkedin_profile_info(linkedin_url):
    # Code pour extraire les informations du profil LinkedIn
    # ...
    return profile_info

# Fonction pour valider les données en recherchant sur Google
def validate_data_with_google(firstname, lastname, domain):
    query = f"{firstname} {lastname} {domain} LinkedIn"
    # Code pour effectuer la recherche sur Google et valider les données
    # ...
    return is_valid

# Fonction pour extraire les informations de profil
def extract_profile_info(email):
    personal_info = extract_personal_info_from_email(email)
    firstname = personal_info["Prénom"]
    lastname = personal_info["Nom"]
    domain = email.domain
    is_valid = validate_data_with_google(firstname, lastname, domain)
    if is_valid:
        linkedin_profile_info = extract_linkedin_profile_info(personal_info["Lien LinkedIn"])
        # Extraire les autres informations du profil
        # ...
        return profile_info
    else:
        return None

# Utilisation de la fonction pour extraire l'adresse e-mail
email_id = extract_email_address(email)
print("Email address:", email_id)


# Créer la table avec les colonnes appropriées
db_connection.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        firstname TEXT,
        lastname TEXT,
        location TEXT,
        jobtitle TEXT,
        city TEXT,
        country TEXT
    )
''')

# Insérer les données dans la table
data = {
    'firstname': 'John',
    'lastname': 'Doe',
    'location': 'Paris',
    'jobtitle': 'Engineer',
    'city': 'Paris',
    'country': 'France'
}

db_connection.execute('''
    INSERT INTO users (firstname, lastname, location, jobtitle, city, country)
    VALUES (:firstname, :lastname, :location, :jobtitle, :city, :country)
''', data)

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
def extract_personal_info_from_email_body(body):
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(body)

    personal_info = {"Nom": "", "Prénom": ""}

    for entity in doc.ents:
        if entity.label_ == "PER":
            name_parts = entity.text.split()
            if len(name_parts) >= 2:
                personal_info["Nom"] = name_parts[-1]
                personal_info["Prénom"] = " ".join(name_parts[:-1])
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

# Fonction pour extraire les informations personnelles depuis l'e-mail, l'adresse e-mail et l'URL LinkedIn
def extract_personal_info(email, body, db_connection):
    personal_info = {}
    
    # Vérification dans la base de données
    email_id = email.get("ID")
    personal_info = get_personal_info_from_database(email_id, db_connection)
    if personal_info:
        return personal_info
    
    # Extraction depuis l'e-mail
    personal_info_email = extract_personal_info_from_email_body(body)
    personal_info.update(personal_info_email)
    
    # Extraction depuis l'adresse e-mail
    email_address = email.get("From")
    personal_info_email_address = extract_personal_info_from_email_address(email_address)
    personal_info.update(personal_info_email_address)
    
    # Extraction depuis l'URL LinkedIn
    signature = extract_signature_from_email(email)
    linkedin_url = extract_linkedin_url_from_signature(signature)
    if linkedin_url:
        name, job_title, company = extract_linkedin_profile_info(linkedin_url)
        if name and job_title and company:
            personal_info["Nom"] = name
            personal_info["Prénom"] = firstname(name)
            personal_info["Titre"] = job_title
            personal_info["Entreprise"] = company
            personal_info["Ville"], personal_info["Pays"] = extract_location_info(linkedin_url)
    
    # Vérification des informations dans la base de données
    if personal_info:
        email_id = email.get("ID")
        if not is_personal_info_present_in_database(email_id, db_connection):
            # Enregistrement des informations dans la base de données
            save_personal_info_to_database(email_id, personal_info, db_connection)
    
    return personal_info


# Fonction pour enregistrer les informations personnelles dans la base de données
def save_personal_info_to_database(email_id, personal_info, db_connection):
    db_connection.execute('''
        INSERT INTO users (id, firstname, lastname, location, jobtitle, city, country)
        VALUES (:id, :firstname, :lastname, :location, :jobtitle, :city, :country)
    ''', {"id": email_id, "firstname": personal_info.get("Prénom"), "lastname": personal_info.get("Nom"),
          "location": personal_info.get("Lieu"), "jobtitle": personal_info.get("Titre"),
          "city": personal_info.get("Ville"), "country": personal_info.get("Pays")})
    db_connection.commit()

# Fonction pour vérifier si les informations personnelles sont présentes dans la base de données
def is_personal_info_present_in_database(email_id, db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM users WHERE id = :id
    ''', {"id": email_id})
    count = cursor.fetchone()[0]
    return count > 0

# Fonction pour récupérer les informations personnelles depuis la base de données
def get_personal_info_from_database(email_id, db_connection):
    cursor = db_connection.cursor()
    cursor.execute('''
        SELECT firstname, lastname, location, jobtitle, city, country FROM users WHERE id = :id
    ''', {"id": email_id})
    row = cursor.fetchone()
    if row:
        return {
            "Prénom": row[0],
            "Nom": row[1],
            "Lieu": row[2],
            "Titre": row[3],
            "Ville": row[4],
            "Pays": row[5]
        }
    return None

# Fonction pour extraire les informations personnelles depuis l'adresse e-mail
def extract_personal_info_from_email_address(email_address):
    personal_info = {"Nom": "", "Prénom": ""}
    parts = email_address.split("@")
    if len(parts) >= 2:
        name_parts = parts[0].split(".")
        if len(name_parts) >= 2:
            personal_info["Nom"] = name_parts[-1]
            personal_info["Prénom"] = " ".join(name_parts[:-1])
    return personal_info

# Fonction pour rechercher l'URL LinkedIn à partir du nom, prénom et domaine de l'e-mail
def search_linkedin_url(firstname, lastname, domain):
    query = f"site:linkedin.com/in {name} {domain}"
    user_agent = get_random_user_agent()
    for url in search(query, num_results=5, user_agent=user_agent):
        if "linkedin.com/in" in url:
            return url
    return None

# Fonction pour extraire les informations depuis l'URL LinkedIn
def extract_personal_info_from_linkedin(url):
    personal_info = {}
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        name_element = soup.find("li", class_="inline t-24 t-black t-normal break-words")
        job_title_element = soup.find("h2", class_="mt1 t-18 t-black t-normal break-words")
        company_element = soup.find("h3", class_="t-16 t-black t-normal break-words")
        if name_element:
            name = name_element.text.strip()
            personal_info["Nom"] = name
            personal_info["Prénom"] = firstname(name)
        if job_title_element:
            personal_info["Titre"] = job_title_element.text.strip()
        if company_element:
            personal_info["Entreprise"] = company_element.text.strip()
    return personal_info

# Fonction pour extraire les informations personnelles en recherchant sur Bing ou Google
def extract_personal_info_from_search(firstname, lastname, domain):
    personal_info = {}
    search_query = f'"{name}" "{domain}" site:linkedin.com/in'
    user_agent = get_random_user_agent()
    for url in search(search_query, num_results=5, user_agent=user_agent):
        if "linkedin.com/in" in url:
            personal_info = extract_personal_info_from_linkedin(url)
            break
    return personal_info

# Fonction principale pour extraire les informations personnelles
def extract_personal_info(email, body, db_connection):
    personal_info = {}
    
    # Vérification dans la base de données
    email_id = email.get("ID")
    personal_info = get_personal_info_from_database(email_id, db_connection)
    if personal_info:
        return personal_info
    
    # Extraction depuis l'e-mail
    personal_info_email = extract_personal_info_from_email_body(body)
    personal_info.update(personal_info_email)
    
    # Extraction depuis l'adresse e-mail
    email_address = email.get("From")
    personal_info_email_address = extract_personal_info_from_email_address(email_address)
    personal_info.update(personal_info_email_address)
    
    # Extraction depuis l'URL LinkedIn
    signature = extract_signature_from_email(email)
    linkedin_url = extract_linkedin_url_from_signature(signature)
    if linkedin_url:
        name, job_title, company = extract_linkedin_profile_info(linkedin_url)
        if name and job_title and company:
            personal_info["Nom"] = name
            personal_info["Prénom"] = firstname(name)
            personal_info["Titre"] = job_title
            personal_info["Entreprise"] = company
            personal_info["Ville"], personal_info["Pays"] = extract_location_info(linkedin_url)
    
    # Vérification des informations dans la base de données
    if personal_info:
        email_id = email.get("ID")
        if not is_personal_info_present_in_database(email_id, db_connection):
            # Enregistrement des informations dans la base de données
            save_personal_info_to_database(email_id, personal_info, db_connection)
    
    # Vérification des informations sur LinkedIn en effectuant une recherche
    if not personal_info.get("Nom") and not personal_info.get("Prénom"):
        name = personal_info.get("Nom") or personal_info.get("Prénom")
        domain = email_address.split("@")[-1]
        if name and domain:
            personal_info_search = extract_personal_info_from_search(name, domain)
            personal_info.update(personal_info_search)
    
    return personal_info

# Fonction pour vérifier si les informations personnelles sont présentes dans la base de données
def is_personal_info_present_in_database(email_id, db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT personal_info FROM interactions WHERE email_id = ?", (email_id,))
    data = cursor.fetchone()
    if data:
        return True
    return False


# Fonction pour analyser l'adresse email et définir le firstname et le lastname
def extract_name_from_email(email_id):
    structures = [
        "firstname.lastname",
        "firstname_lastname",
        "lastname.firstname",
        "lastname_firstname",
        "firstinitial.lastname",
        "firstinitial_lastname",
        "lastname.firstinitial",
        "lastname_firstinitial",
        "firstname",
        "lastname",
        "firstinitial",
        "firstnamelastname",
        "lastinitial",
        "firstname_lastname_initial",
        "firstname.lastinitial",
        "firstname_lastinitial",
        "firstinitial_lastname_initial",
        "firstinitial_lastname.lastinitial",
        "firstinitial_lastname_lastinitial",
        "lastname.firstinitial",
        "lastname.firstinitial_lastinitial",
        "lastname_firstinitial_lastinitial",
        "lastname.firstinitial_lastinitial",
    ]

   for structure in structures:
        parts = re.split(r"\W", structure)
        parts = [part.lower() for part in parts if part != ""]
        pattern = parts[0] + r"\." + parts[1] + r"@\w+"
        match = re.match(pattern, email_id)
        if match:
            firstname = match.group(1).capitalize()
            lastname = match.group(2).capitalize()
            return firstname, lastname

    return None, None

    # Méthode 1: Extraction depuis l'adresse e-mail (si possible)
    parts = re.split(r"\W", email_id)
    parts = [part.lower() for part in parts if part != ""]
    if len(parts) >= 2:
        firstname = parts[0].capitalize()
        lastname = parts[1].capitalize()

    # Méthode 2: Extraction depuis la signature (si disponible)
    if signature:
        name_parts = signature.split()
        if len(name_parts) >= 2:
            extracted_firstname = name_parts[0].capitalize()
            extracted_lastname = name_parts[-1].capitalize()

            if firstname is None:
                firstname = extracted_firstname
            elif firstname != extracted_firstname:
                firstname = None
                lastname = None

            if lastname is None:
                lastname = extracted_lastname
            elif lastname != extracted_lastname:
                firstname = None
                lastname = None

    # Méthode 3: Extraction depuis le compte LinkedIn (si disponible)
    if linkedin_url:
        name, _ = extract_name_from_linkedin(linkedin_url)
        if name:
            name_parts = name.split()
            if len(name_parts) >= 2:
                extracted_firstname = name_parts[0].capitalize()
                extracted_lastname = name_parts[-1].capitalize()

                if firstname is None:
                    firstname = extracted_firstname
                elif firstname != extracted_firstname:
                    firstname = None
                    lastname = None

                if lastname is None:
                    lastname = extracted_lastname
                elif lastname != extracted_lastname:
                    firstname = None
                    lastname = None

    return firstname, lastname

def extract_personal_info_from_email(email):
    body = get_email_body(email)
    signature = extract_signature_from_email(email)
    linkedin_url = extract_linkedin_url_from_email(email)
    firstname, lastname = extract_name_from_email(email["From"], signature, linkedin_url)

    if firstname and lastname:
        personal_info = {
            "Firstname": firstname,
            "Lastname": lastname,
        }
    else:
        personal_info = {
            "Firstname": None,
            "Lastname": None,
        }

    return personal_info


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

def extract_signature_from_email(email):
    body = get_email_body(email)
    # Extraction de la signature depuis le corps de l'e-mail
    signature = re.search(r"--\n(.*)", body, re.DOTALL)
    if signature:
        return signature.group(1).strip()
    return None

def extract_linkedin_url_from_email(email):
    signature = extract_signature_from_email(email)
    if signature:
        # Extraction de l'URL LinkedIn depuis la signature
        linkedin_url = re.search(r"linkedin\.com/.*", signature, re.IGNORECASE)
        if linkedin_url:
            return linkedin_url.group().strip()
    return None

def extract_name_from_linkedin(linkedin_url):
    # Extraction du nom depuis l'URL LinkedIn
    # ...
    return firstname, lastname

def is_personal_info_valid(personal_info):
    firstname = personal_info["Firstname"]
    lastname = personal_info["Lastname"]
    if firstname and lastname:
        # Vérification de la validité des informations
        return True
    return False

def process_question(email):
    personal_info = extract_personal_info_from_email(email)

    if is_personal_info_valid(personal_info):
        question = get_question_from_email(email)
        response = generate_response(question, personal_info)
        send_response_email(email, response)
    else:
        response = question_personal_infos()
        send_personal_info_question(email, response)

# Fonction pour enregistrer les informations personnelles dans la base de données
def save_personal_info_to_database(email_id, personal_info, db_connection):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO interactions (email_id, personal_info) VALUES (?, ?)", (email_id, json.dumps(personal_info)))
    db_connection.commit()

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
    receiver_email = email_id
    reply_subject = f"Re: {subject}"
    reply_message = f"Bonjour {personal_info['Prénom']},\n\n{response}\n\n{POLITE_CLOSING}\n\nAu plaisir de collaborer avec vous,\n{BOT_NAME}\n\n{POST_SCRIPTUM}"
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
