import re
from datetime import datetime
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.education_schema import EducationRecord


class EducationExtractor(EntityExtractor):
    """
    Extracts education records using deterministic rules, regex, and structural heuristics.
    """

    @property
    def domain(self) -> str:
        return "education"

    def extract(self, context: ProcessingContext) -> list[EducationRecord]:
        records = []
        sections = context.document.sections
        edu_content = ""
        in_section = False
        
        if sections and "education" in sections:
            edu_content = sections["education"].content
            in_section = True
        else:
            edu_content = context.document.cleaned_text

        # Split into blocks by double newlines for isolated parsing
        blocks = [b.strip() for b in re.split(r'\n\s*\n', edu_content) if b.strip()]
        
        for block in blocks:
            record = self._parse_education_block(block, in_section)
            if record:
                records.append(record)
                
        return records

    def _parse_education_block(self, text: str, in_section: bool) -> EducationRecord | None:
        degree = self._extract_degree(text)
        institution = self._extract_institution(text)
        
        if not degree and not institution:
            return None
            
        field_of_study = self._extract_field_of_study(text)
        cgpa = self._extract_cgpa(text)
        percentage = self._extract_percentage(text)
        start_year, end_year = self._extract_years(text)
        is_current = self._is_current(text, end_year)
        
        if start_year is None and end_year is not None and is_current:
            start_year = end_year
            end_year = None
        
        confidence = self._calculate_confidence(degree, institution, start_year, cgpa, percentage, in_section)
        
        if confidence < 0.3:
            return None

        normalized_name = self._generate_normalized_name(degree, field_of_study, institution)

        return EducationRecord(
            degree=degree,
            field_of_study=field_of_study,
            institution=institution,
            start_year=start_year,
            graduation_year=end_year,
            cgpa=cgpa,
            percentage=percentage,
            is_current=is_current,
            confidence=confidence,
            raw_text=text,
            normalized_name=normalized_name
        )

    def _extract_degree(self, text: str) -> str | None:
        pattern = r"(^|\s)(B\.S\.|B\.S|B\.A\.|B\.A|B\.Tech|M\.Tech|M\.S\.|M\.S|M\.B\.A\.|M\.B\.A|Ph\.D\.|Ph\.D|Bachelors?|Masters?|Diploma|Associate|Degree|B\.E\.|B\.E)(?=\s|,|\.|$)"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return None

    def _extract_institution(self, text: str) -> str | None:
        lines = text.split('\n')
        for line in lines:
            if re.search(r"\b(University|College|Institute|School|Academy|Technology)\b", line, flags=re.IGNORECASE):
                # Clean up typical separators to get just the institution name
                return line.strip(" -:,|").split("|")[0].split("-")[0].strip()
        return None

    def _extract_field_of_study(self, text: str) -> str | None:
        branches = [
            "Computer Science", "Software Engineering", "Information Technology",
            "Electrical Engineering", "Mechanical Engineering", "Data Science",
            "Artificial Intelligence", "Mathematics", "Physics", 
            "Business Administration", "Economics", "Civil Engineering"
        ]
        for branch in branches:
            if re.search(rf"\b{re.escape(branch)}\b", text, flags=re.IGNORECASE):
                return branch
        return None

    def _extract_cgpa(self, text: str) -> float | None:
        match = re.search(r"\b(?:CGPA|GPA)\s*[:=]?\s*([0-9]\.[0-9]{1,2})\b", text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def _extract_percentage(self, text: str) -> float | None:
        match = re.search(r"\b([0-9]{2}(?:\.[0-9]{1,2})?)\s*%", text)
        if match:
            return float(match.group(1))
        return None

    def _extract_years(self, text: str) -> tuple[int | None, int | None]:
        years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
        if not years:
            return None, None
        years = sorted(list(set(years)))
        if len(years) == 1:
            return None, years[0]
        return years[0], years[-1]

    def _is_current(self, text: str, end_year: int | None) -> bool:
        if re.search(r"\b(Present|Ongoing|Current|Now)\b", text, flags=re.IGNORECASE):
            return True
        if end_year and end_year >= datetime.now().year:
            return True
        return False

    def _calculate_confidence(self, degree, institution, start_year, cgpa, percentage, in_section) -> float:
        score = 0.0
        if in_section: score += 0.2
        if degree: score += 0.3
        if institution: score += 0.3
        if start_year: score += 0.1
        if cgpa or percentage: score += 0.1
        return min(1.0, round(score, 2))

    def _generate_normalized_name(self, degree, field_of_study, institution) -> str:
        parts = []
        if degree: parts.append(degree)
        if field_of_study: parts.append(f"in {field_of_study}")
        if institution: parts.append(f"at {institution}")
        return " ".join(parts) if parts else "Education Record"
