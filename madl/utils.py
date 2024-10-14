import re
import unicodedata


def sanitize_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    name_normalized = unicodedata.normalize('NFKD', name)
    name_no_accents = ''.join(
        c for c in name_normalized if not unicodedata.combining(c)
    )
    name_no_specials = re.sub(r'[^a-zA-Z\s]', ' ', name_no_accents)
    name_corrected = ''.join(
        name[i] if name_no_accents[i] in name_no_specials else ' '
        for i in range(len(name))
    )

    name_corrected = name_corrected.lower()
    name_corrected = re.sub(r'\s+', ' ', name_corrected)

    return name_corrected.strip()


def sanitize_email(email: str) -> str:
    email = email.lower()
    email_normalized = unicodedata.normalize('NFKD', email)
    email_no_accents = ''.join(
        c for c in email_normalized if not unicodedata.combining(c)
    )

    parts = email_no_accents.split('@')
    if len(parts) > 2:  # noqa
        email_no_accents = f"{parts[0]}@{''.join(parts[1:])}"

    if '@' not in email_no_accents:
        email_no_accents = f'{email_no_accents}@example.com'

    local_part, domain_part = email_no_accents.split('@', 1)

    local_part = re.sub(r'[^a-zA-Z0-9._-]', '', local_part)

    domain_part = re.sub(r'[^a-zA-Z0-9.-]', '', domain_part)

    if not re.match(r'^.*\.com\.[a-zA-Z]{2,}$', domain_part):
        domain_part = re.sub(r'(\.com.*)', '.com', domain_part)

    sanitized_email = f'{local_part}@{domain_part}'

    return sanitized_email
