import oracledb
import pandas as pd
import sys
import os
import re
import logging
import warnings
from datetime import datetime, timedelta
from email_utils import EmailSender

# Ignorē UserWarning lai logs ir tīri
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy"
)

# Iestata logging iestatijumus
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Application started")

# Apstrādā komandrindas argumentus un ievieto tos vārdnīcā
args = sys.argv[1:]
params = {}
for arg in args:
    if ":" in arg:
        key, value = arg.split(":", 1)
        params[key.lower()] = value


# Nolasa SQL vaicājumu no faila
sql_file = params.get("/sql")
if sql_file:
    with open(sql_file, "r", encoding="utf-8") as f:
        query = f.read().strip()
else:
    query = "SELECT * FROM claims_event"


# Pārbauda un sadala DB pieslēguma virkni
conn_str = params.get("/connection")
if not conn_str:
    logging.exception("Connection string is missing")
    sys.exit(1)
try:
    user_pass, host_service = conn_str.split("@")
    username, password = user_pass.split("/")
    host_port, service_name = host_service.split("/")
    host, port = host_port.split(":")
    dsn = f'{host}:{port}/{service_name}'
except Exception:
    logging.exception("Invalid connection string format. Expected user/password@host:port/service")
    sys.exit(1)


# E-pasta konfigurācijas parametri
email_from = params.get("/emailfrom")
email_to = params.get("/emailto")
subject = params.get("/emailsubject", "Event Report")
body = params.get(
    "/emailbody", 
    "This is an automatically generated email. The attached file contains the report based on the executed SQL query.")
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = email_from
smtp_password = params.get("/emailpassword")


# Nosaka izpildes tipu (EML vai DIR) un validē e-pasta parametrus, ja nepieciešams
output_type = params.get("/type", "DIR").upper()
output_file = params.get("/output", "claims_event.xlsx")
if output_type == "EML" and (not email_from or not email_to or not smtp_password):
    logging.exception("Email parameters missing from EML Mode")
    sys.exit(1)


# Atrod datumu no SQL vaicajuma, ja tāds ir norādīts
date_detected = None
match_date = re.search(r"DATE\s+'(\d{4}-\d{2}-\d{2})'", query)
if match_date:
    date_detected = datetime.strptime(match_date.group(1), "%Y-%m-%d")
else:
    match_sysdate = re.search(r"SYSDATE\s*-\s*(\d+)", query)
    if match_sysdate:
        days_ago = int(match_sysdate.group(1))
        date_detected = datetime.now() - timedelta(days=days_ago)

if date_detected:
    date_str = date_detected.strftime("%d-%m-%Y")
    name, ext = os.path.splitext(output_file)
    output_file = f'{name}_{date_str}{ext}'
    subject = f'{subject} {date_str}'


# Pieslēdzas Oracle DB un izpilda vaicājumu
try:
    with oracledb.connect(user=username, password=password, dsn=dsn) as conn:
        logging.info("Connection to Oracle DB successful!")
        df = pd.read_sql(query, conn)
        logging.info(f"Records fetched: {len(df)}")
        # Pārbauda vai vaicājuma rezultāts nav tukšs, ja ir tad nesūta epastu un nesaglabā failu
        if df.empty:
            logging.info("No records found. Terminating execution without creating file or sending email.")
            sys.exit(0)

        # Eksportē vaicājuma rezultātu uz Excel
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Claims Event", index=False)
            df.to_excel(writer, sheet_name="Claims Event Backup", index=False)
        logging.info(f'Excel file created: {output_file}')
        
        # Atkarībā no /type parametra nosūta e-pastu vai saglabā failu lokāli
        if output_type == "EML":
            email_sender = EmailSender(smtp_server, smtp_port, smtp_user, smtp_password)
            email_sender.send(output_file, email_from, email_to, subject, body)
            if os.path.exists(output_file):
                os.remove(output_file)
                logging.info(f'File deleted after successfully sending via Email: {output_file}')
        else:
            logging.info(f'File saved locally: {output_file}')
    
except Exception:
    logging.exception("Unexpected error occurred")

logging.info("Application finished successfully")