import re
from typing import Any
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.contact_schema import ContactInfo


class ContactExtractor(EntityExtractor):
    """
    Extracts candidate contact details and social links using classical NLP,
    regex, and rule-based heuristics.
    """

    @property
    def domain(self) -> str:
        return "contact"

    def extract(self, context: ProcessingContext) -> ContactInfo:
        text = context.document.cleaned_text
        original_text = context.document.raw_text

        # 1. Email extraction
        email = None
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        if email_match:
            email = email_match.group(0)

        # 2. Phone extraction
        phone = None
        # Match +1-123-456-7890, 123.456.7890, (123) 456-7890, etc.
        phone_match = re.search(
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", 
            text
        )
        if phone_match:
            phone = phone_match.group(0).strip()

        # 3. URL extraction
        linkedin_url = None
        github_url = None
        portfolio_url = None
        leetcode_url = None
        hackerrank_url = None
        kaggle_url = None

        # Search for URLs using regex
        urls = re.findall(r"https?://[^\s()<>]+", text)
        
        # Clean trailing punctuation from URLs and search for direct platform handles/links without http/https
        all_urls = []
        for url in urls:
            cleaned_url = url.rstrip(".,;:)[]!?'\"")
            all_urls.append(cleaned_url)

        platform_patterns = [
            r"\blinkedin\.com/in/[^\s()<>]+",
            r"\bgithub\.com/[^\s()<>]+",
            r"\bkaggle\.com/[^\s()<>]+",
            r"\bleetcode\.com/[^\s()<>]+",
            r"\bhackerrank\.com/[^\s()<>]+"
        ]
        for pattern in platform_patterns:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            for m in matches:
                full_url = m.rstrip(".,;:)[]!?'\"")
                if not any(full_url.lower() in u.lower() for u in all_urls):
                    if not full_url.startswith("http"):
                        full_url = "https://" + full_url
                    all_urls.append(full_url)

        # Check for domains like www.xyz.com or xyz.dev or xyz.io to catch raw portfolio links
        domain_pattern = r"\b(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:/[^\s()<>]+)?\b"
        for m in re.finditer(domain_pattern, text):
            match_str = m.group(0).rstrip(".,;:)[]!?'\"")
            start, end = m.span()
            # If it's preceded or followed by '@' (part of email), skip
            if start > 0 and text[start-1] == "@":
                continue
            if end < len(text) and text[end] == "@":
                continue
            # If it contains '@', skip
            if "@" in match_str:
                continue
            
            # Avoid matching common resume noise (like "Seattle, WA" or file extensions like ".pdf")
            exclude_extensions = {".pdf", ".docx", ".doc", ".png", ".jpg"}
            if any(match_str.lower().endswith(ext) for ext in exclude_extensions):
                continue

            # If it is part of the extracted email domain, skip
            if email:
                email_parts = email.split("@")
                if len(email_parts) == 2 and match_str.lower() in email_parts[1].lower():
                    continue

            full_url = match_str
            if not full_url.startswith("http"):
                full_url = "https://" + full_url

            if not any(full_url.lower() in u.lower() for u in all_urls):
                all_urls.append(full_url)

        for url in all_urls:
            url_lower = url.lower()
            if "linkedin.com" in url_lower:
                linkedin_url = url
            elif "github.com" in url_lower:
                github_url = url
            elif "kaggle.com" in url_lower:
                kaggle_url = url
            elif "leetcode.com" in url_lower:
                leetcode_url = url
            elif "hackerrank.com" in url_lower:
                hackerrank_url = url
            else:
                exclude_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}
                if not any(domain in url_lower for domain in exclude_domains):
                    if not portfolio_url:
                        portfolio_url = url

        # 4. Name extraction
        full_name = None
        # Heuristic 1: Look for the first PERSON named entity early in the document
        person_entities = [
            ent for ent in context.processed_document.named_entities 
            if ent.label == "PERSON"
        ]
        if person_entities:
            valid_persons = []
            for ent in person_entities:
                cleaned_ent = ent.text.strip()
                if "\n" in cleaned_ent:
                    cleaned_ent = cleaned_ent.split("\n")[0].strip()
                words = cleaned_ent.split()
                if 2 <= len(words) <= 4 and not any(c.isdigit() or c == '@' for c in cleaned_ent):
                    valid_persons.append(cleaned_ent)
            if valid_persons:
                full_name = valid_persons[0]

        # Heuristic 2: If no PERSON entity found, check the first line of the document
        if not full_name and original_text:
            lines = [line.strip() for line in original_text.split("\n") if line.strip()]
            for line in lines[:3]:
                if "@" in line or any(c.isdigit() for c in line):
                    continue
                words = line.split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                    full_name = line
                    break

        # 5. Location extraction
        location = None
        # Heuristic: Find GPE named entities
        gpe_entities = [
            ent for ent in context.processed_document.named_entities 
            if ent.label == "GPE"
        ]
        if gpe_entities:
            first_gpe = gpe_entities[0]
            location = first_gpe.text
            for next_gpe in gpe_entities[1:]:
                if next_gpe.start_char - first_gpe.end_char <= 5:
                    combined_text = original_text[first_gpe.start_char:next_gpe.end_char]
                    if "," in combined_text or " " in combined_text:
                        location = combined_text
                        break

        if location:
            location = re.sub(r"\s+", " ", location).strip()

        return ContactInfo(
            full_name=full_name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin_url,
            github_url=github_url,
            portfolio_url=portfolio_url,
            leetcode_url=leetcode_url,
            hackerrank_url=hackerrank_url,
            kaggle_url=kaggle_url
        )
