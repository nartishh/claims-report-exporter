# Claims Event Report Automation

## Overview
This project connects to Oracle database, executes SQL query, exports the result to an Excel file, and optionally sends via email.

The application supports two modes:
- **DIR** – saves the file locally
- **EML** – sends the file via email

## Features

- Oracle DB connection
- SQL execution from file
- Excel report generation
- Email sending via SMTP
- Automatic date handling from SQL query
- Empty result handling (no file/email if no data)
- Docker support

## Requirements

- Python 3.11+
- Docker (optional but recommended)
- Oracle database access
- Valid SMTP credentials (for EML mode)

## Project Structure

- main.py
- email_utils.py
- new_claims.sql
- requirements.txt
- Dockerfile
- .gitignore
- README.md

## How to Run (Without Docker)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```
### 2. Run the script
#### DIR Mode (save file locally):

```bash
python main.py \
/type:DIR \
/connection:"user/password@host:port/service" \
/sql:new_claims.sql \
/output:claims_event.xlsx
```

#### EML Mode (send email):

```bash
python main.py \
/type:EML \
/connection:"user/password@host:1521/XEPDB1" \
/sql:new_claims.sql \
/output:claims_event.xlsx \
/emailTo:recipient@example.com \
/emailFrom:sender@example.com \
/emailPassword:yourpassword \
/emailSubject:emailsubject \
/emailBody:emailbody
```

## How to Run With Docker

### 1. Build the image

```bash
docker build -t claims-app .
```

### 2. Run container
#### DIR Mode (save file locally):

```bash
docker run -v ${PWD}:/app claims-app \
/type:DIR \
/connection:"user/password@host:1521/XEPDB1" \
/sql:new_claims.sql \
/output:claims_event.xlsx
```
#### EML Mode (send email):
```bash
docker run claims-app \
/type:EML \
/connection:"user/password@host:1521/XEPDB1" \
/sql:new_claims.sql \
/output:claims_event.xlsx \
/emailTo:recipient@example.com \
/emailFrom:sender@example.com \
/emailPassword:yourpassword \
/emailSubject:emailsubject \
/emailBody:emailbody
```

## Parameters

| Parameter        | Required | Default | Description |
|------------------|----------|---------|------------|
| `/type`          | No       | DIR     | Execution mode: DIR or EML |
| `/connection`    | Yes      | -       | Oracle DB connection string |
| `/sql`           | No       | `SELECT * FROM claims_event` | Path to SQL file |
| `/output`        | No       | claims_event.xlsx | Output Excel file name |
| `/emailTo`       | Yes (for EML) | - | Recipient email |
| `/emailFrom`     | Yes (for EML) | - | Sender email |
| `/emailPassword` | Yes (for EML) | - | Email password |
| `/emailSubject`  | No       | Event Report | Email subject |
| `/emailBody`     | No       | Default message | Email body |

## SQL Example
Query with a specific date filter:

```sql
SELECT event_no,
       event_type,
       create_date
FROM claims_event
WHERE trunc(create_date) = DATE '2026-03-17'
ORDER BY event_no
```

## Date Handling
- If SQL contains:
  - `DATE 'YYYY-MM-DD'` → that date is used
  - `SYSDATE - N` → calculated date is used
- If no date is found:
  - no date is added to filename and subject

## Behavior
- If query returns no data:
  - No file created
  - No email sent
  - Execution stops

## Scheduling
This application is designed to be executed using external schedulers.  
It does not include built-in scheduling logic, but it can be triggered automatically via command-line execution.

### Windows Task Scheduler
On Windows, the script can be automated using Task Scheduler:

#### Program/script:
path to location where `python.exe` exists
#### Arguments:
main.py /type:DIR /connection:"user/password@host:1521/XEPDB1" /sql:new_claims.sql /output:claims_event.xlsx
#### Start in:
path to location where `main.py` exists

### Cron Scheduler (Linux/macOS)
On Linux or macOS, the script can be automated using `cron`:
#### Open crontab:
`crontab -e`

#### Add a scheduled job (example: run every day at 08:00):
```
0 8 * * * /usr/bin/python3 /path/to/main.py /type:DIR /connection:"user/password@host:1521/XEPDB1" /sql:/path/to/new_claims.sql /output:/path/to/claims_event.xlsx
```
#### Explanation:
- `0 8 * * *` → runs daily at 08:00
- `/usr/bin/python3` → path to Python executable
- `/path/to/main.py` → path to script

#### Important:
- Always use **full paths**
- Ensure required Python packages are installed in the environment

## Notes
- In production, environment variables should be used for sensitive data
- Output file is created locally (or via Docker volume)
- For Docker, use `host.docker.internal` instead of `localhost` for DB connection
- Application can be extended to support batch processing for large datasets if required.

## Key Design Notes
- The solution is database-agnostic at query level, meaning any table or structure can be used as long as the SQL query is valid
- The application exits when no data is returned to avoid sending empty reports
- Docker is used to ensure environment consistency
- Parameters are passed via command line for flexibility
- Email functionality is optional and controlled via `/type` parameter
- The application is CLI-driven and stateless, which makes it suitable for automation without requiring any code changes.  
All execution behavior is controlled via input parameters.

## Author
Eriks Nartiss
