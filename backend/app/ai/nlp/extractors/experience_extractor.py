import re
from datetime import datetime
from pathlib import Path
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.experience_schema import ExperienceRecord
from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager


class ExperienceExtractor(EntityExtractor):
    """
    Extracts work experience records and role-specific technologies used.
    Reuses taxonomy dictionaries from shared TaxonomyResourceManager.
    """

    def __init__(self, taxonomy_dir: Path | None = None) -> None:
        self._taxonomy = TaxonomyResourceManager.get_taxonomy(taxonomy_dir)
        self._synonyms = TaxonomyResourceManager.get_synonyms(taxonomy_dir)
        self._technology_categories = (
            TaxonomyResourceManager.get_technology_categories()
        )

    @property
    def domain(self) -> str:
        return "experience"

    def extract(self, context: ProcessingContext) -> list[ExperienceRecord]:
        records = []
        sections = context.document.sections
        exp_content = ""
        in_section = False

        for sec_name in ["experience", "work_experience", "employment"]:
            if sections and sec_name in sections:
                exp_content += sections[sec_name].content + "\n\n"
                in_section = True

        if not exp_content.strip():
            exp_content = context.document.cleaned_text

        blocks = [b.strip() for b in re.split(r"\n\s*\n", exp_content) if b.strip()]

        for block in blocks:
            record = self._parse_experience_block(block, in_section, context)
            if record:
                records.append(record)

        return records

    def _parse_experience_block(
        self, text: str, in_section: bool, context: ProcessingContext
    ) -> ExperienceRecord | None:
        company = self._extract_company(text, context)
        job_title = self._extract_job_title(text)

        if not company and not job_title:
            return None

        employment_type = self._extract_employment_type(text)
        location = self._extract_location(text, context)
        start_date, end_date = self._extract_dates(text)
        is_current = self._is_current(text, end_date)
        duration_months = self._calculate_duration(start_date, end_date, is_current)
        description = self._extract_description(text)
        technologies_used = self._extract_technologies(text)

        confidence = self._calculate_confidence(
            company, job_title, start_date, in_section
        )

        if confidence < 0.3:
            return None

        normalized_name = self._generate_normalized_name(job_title, company)

        return ExperienceRecord(
            job_title=job_title,
            company=company,
            employment_type=employment_type,
            location=location,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            duration_months=duration_months,
            description=description,
            technologies_used=technologies_used,
            confidence=confidence,
            raw_text=text,
            normalized_name=normalized_name,
        )

    def _extract_company(self, text: str, context: ProcessingContext) -> str | None:
        for ent in context.processed_document.named_entities:
            if ent.label == "ORG" and ent.text in text:
                return ent.text
        match = re.search(
            r"^\s*([A-Z][a-zA-Z0-9&, ]+(?:Inc\.|LLC|Ltd\.|Corp\.|Group|Technologies|Solutions|Company))(?=\s|$|,)",
            text,
            flags=re.MULTILINE,
        )
        if match:
            return match.group(1).strip()
        return None

    def _extract_job_title(self, text: str) -> str | None:
        titles = [
            "Software Engineer",
            "Frontend Developer",
            "Backend Developer",
            "Data Scientist",
            "Project Manager",
            "Developer",
            "Intern",
            "Manager",
            "Analyst",
            "Architect",
            "Lead",
            "Consultant",
            "Director",
            "Engineer",
            "Programmer",
        ]
        for title in titles:
            match = re.search(
                rf"\b((?:(?:Senior|Junior|Staff|Principal|Lead|Chief)\s+)?{re.escape(title)}(?:\s+Intern)?)\b",
                text,
                flags=re.IGNORECASE,
            )
            if match:
                return match.group(1).title()
        return None

    def _extract_employment_type(self, text: str) -> str | None:
        types = [
            "Full-time",
            "Part-time",
            "Contract",
            "Freelance",
            "Internship",
            "Intern",
        ]
        for emp_type in types:
            if re.search(rf"\b{re.escape(emp_type)}\b", text, flags=re.IGNORECASE):
                return "Internship" if "intern" in emp_type.lower() else emp_type

        # If job title has intern, it's an internship
        if re.search(r"\bintern(?:ship)?\b", text, flags=re.IGNORECASE):
            return "Internship"

        return None

    def _extract_location(self, text: str, context: ProcessingContext) -> str | None:
        for ent in context.processed_document.named_entities:
            if ent.label in ("GPE", "LOC") and ent.text in text:
                return ent.text
        if re.search(r"\b(Remote|Hybrid)\b", text, flags=re.IGNORECASE):
            match = re.search(r"\b(Remote|Hybrid)\b", text, flags=re.IGNORECASE)
            return match.group(1).capitalize()
        return None

    def _extract_dates(self, text: str) -> tuple[str | None, str | None]:
        pattern = r"\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d{4}|\d{4})\b"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if not matches:
            return None, None
        if len(matches) == 1:
            return matches[0], None
        return matches[0], matches[-1]

    def _is_current(self, text: str, end_date: str | None) -> bool:
        if re.search(r"\b(Present|Current|Now)\b", text, flags=re.IGNORECASE):
            return True
        return False

    def _calculate_duration(
        self, start_date: str | None, end_date: str | None, is_current: bool
    ) -> int | None:
        if not start_date:
            return None

        def parse_date(d_str):
            try:
                # Try to parse Month Year
                dt = datetime.strptime(d_str.strip(), "%b %Y")
                return dt
            except ValueError:
                pass
            try:
                dt = datetime.strptime(d_str.strip(), "%B %Y")
                return dt
            except ValueError:
                pass
            try:
                # Just year
                year = int(re.search(r"\d{4}", d_str).group())
                return datetime(year, 1, 1)
            except Exception:
                return None

        start_dt = parse_date(start_date)
        if not start_dt:
            return None

        end_dt = (
            datetime.now() if is_current else parse_date(end_date) if end_date else None
        )

        if end_dt and end_dt >= start_dt:
            months = (end_dt.year - start_dt.year) * 12 + (
                end_dt.month - start_dt.month
            )
            return max(1, months)  # Minimum 1 month

        return None

    def _extract_description(self, text: str) -> str | None:
        lines = text.split("\n")
        desc_lines = [
            line for line in lines if line.strip().startswith(("-", "•", "*"))
        ]
        if desc_lines:
            return "\n".join(desc_lines).strip()
        return text.strip()

    def _extract_technologies(self, text: str) -> list[str]:
        techs = set()
        for name, (normalized, category) in self._taxonomy.items():
            if category in self._technology_categories:
                pattern = rf"(?<!\w){re.escape(name)}(?!\w)"
                if re.search(pattern, text, flags=re.IGNORECASE):
                    techs.add(normalized)

        for pattern_str, normalized in self._synonyms.items():
            _, category = self._taxonomy.get(normalized.lower(), (normalized, "tools"))
            if category in self._technology_categories:
                if re.search(pattern_str, text, flags=re.IGNORECASE):
                    techs.add(normalized)
        return sorted(list(techs))

    def _calculate_confidence(
        self, company, job_title, start_date, in_section
    ) -> float:
        score = 0.0
        if in_section:
            score += 0.3
        if company:
            score += 0.3
        if job_title:
            score += 0.3
        if start_date:
            score += 0.1
        return min(1.0, round(score, 2))

    def _generate_normalized_name(self, job_title, company) -> str:
        if job_title and company:
            return f"{job_title} at {company}"
        if job_title:
            return job_title
        if company:
            return company
        return "Experience Record"
