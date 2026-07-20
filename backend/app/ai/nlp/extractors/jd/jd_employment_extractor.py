import re
from app.ai.nlp.extractors.base import EntityExtractor
from app.ai.nlp.schemas.processing_context import ProcessingContext
from app.ai.nlp.schemas.jd.jd_employment_schema import (
    JDEmploymentRecord,
    EmploymentType,
    RemoteType,
)
from app.ai.nlp.schemas.jd.salary_range import SalaryRange, SalaryPeriod


class JDEmploymentExtractor(EntityExtractor):
    """
    Extracts employment metadata from a Job Description.
    """

    @property
    def domain(self) -> str:
        return "employment"

    def extract(self, context: ProcessingContext) -> JDEmploymentRecord:
        text = context.document.cleaned_text

        job_title = self._extract_job_title(context)
        emp_type = self._extract_employment_type(text)
        rem_type = self._extract_remote_type(text)
        location = self._extract_location(text)
        salary = self._extract_salary(text)

        # Calculate overall confidence
        confidence = 1.0 if job_title else 0.8

        return JDEmploymentRecord(
            job_title=job_title,
            location=location,
            remote_type=rem_type,
            employment_type=emp_type,
            salary=salary,
            confidence=confidence,
        )

    def _extract_job_title(self, context: ProcessingContext) -> str | None:
        # 1. Explicit metadata
        if (
            context.document.extraction_metadata
            and "job_title" in context.document.extraction_metadata
        ):
            return context.document.extraction_metadata["job_title"]
        if context.metadata and "job_title" in context.metadata:
            return context.metadata["job_title"]

        # 2. Document title / top heading
        if context.document.sections:
            first_section_key = list(context.document.sections.keys())[0]
            first_section = context.document.sections[first_section_key]
            if first_section.section_type.value in ("summary", "objective", "other"):
                # Ensure it's near the top
                if first_section.start_char < 200:
                    heading = first_section.heading.strip()
                    # Filter out generic headings
                    if heading.lower() not in (
                        "summary",
                        "objective",
                        "about the role",
                        "job description",
                    ):
                        return heading

        # 3. Structured metadata fields
        match = re.search(
            r"(?i)^(?:Role|Job Title|Title|Position):\s*(.+)$",
            context.document.cleaned_text,
            re.MULTILINE,
        )
        if match:
            return match.group(1).strip()

        return None

    def _extract_employment_type(self, text: str) -> EmploymentType:
        if re.search(r"(?i)\b(full\s*time|full-time)\b", text):
            return EmploymentType.FULL_TIME
        if re.search(r"(?i)\b(part\s*time|part-time)\b", text):
            return EmploymentType.PART_TIME
        if re.search(r"(?i)\b(contract|contractor)\b", text):
            return EmploymentType.CONTRACT
        if re.search(r"(?i)\b(intern|internship)\b", text):
            return EmploymentType.INTERNSHIP
        if re.search(r"(?i)\b(freelance|freelancer)\b", text):
            return EmploymentType.FREELANCE
        return EmploymentType.UNKNOWN

    def _extract_remote_type(self, text: str) -> RemoteType:
        if re.search(r"(?i)\b(remote|work from home|wfh)\b", text):
            return RemoteType.REMOTE
        if re.search(r"(?i)\b(hybrid)\b", text):
            return RemoteType.HYBRID
        if re.search(r"(?i)\b(on-site|onsite|on site|in office|in-office)\b", text):
            return RemoteType.ON_SITE
        return RemoteType.UNKNOWN

    def _extract_location(self, text: str) -> str | None:
        match = re.search(
            r"(?i)^(?:Location|Location/Base):\s*(.+)$", text, re.MULTILINE
        )
        if match:
            return match.group(1).strip()
        return None

    def _extract_salary(self, text: str) -> SalaryRange | None:
        # Pattern to match salary
        pattern = re.compile(
            r"(?i)([\$₹£€]|Rs\.?)?\s*"
            r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|lpa|lakhs?|cr)?\s*"
            r"(?:(?:-|to|–|—)\s*"
            r"([\$₹£€]|Rs\.?)?\s*"
            r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|lpa|lakhs?|cr)?)?\s*"
            r"(/(?:year|mo|month|hr|hour)|annually|per\s*annum|monthly|hourly|p\.a\.)?"
        )

        best_salary = None
        best_conf = 0.0

        for match in pattern.finditer(text):
            c1, v1, m1, c2, v2, m2, p = match.groups()

            # Require at least a currency symbol or a period or a multiplier (like lpa) to avoid matching generic numbers
            if not c1 and not c2 and not p and not m1 and not m2:
                continue

            try:
                min_val = float(v1.replace(",", "")) if v1 else None
                max_val = float(v2.replace(",", "")) if v2 else None
            except ValueError:
                continue

            # Apply multipliers
            min_val = self._apply_multiplier(
                min_val, m1 or m2
            )  # sometimes '12-18 LPA' puts LPA on m2
            max_val = self._apply_multiplier(max_val, m2 or m1)

            # Currency
            curr_raw = c1 or c2
            currency = self._normalize_currency(curr_raw) if curr_raw else None

            # Period
            # LPA itself implies YEAR even if p is missing
            period = self._normalize_period(p)
            if not period and (
                (m1 and "lpa" in m1.lower()) or (m2 and "lpa" in m2.lower())
            ):
                period = SalaryPeriod.YEAR

            # Confidence
            conf = 1.0 if (currency and period) else 0.7
            if not period:
                # Missing period lowers confidence
                conf -= 0.2
            if not currency:
                conf -= 0.1

            # Discard obvious non-salaries (e.g. 0-0, small numbers without period/currency)
            if min_val is not None and min_val <= 0:
                continue

            if conf > best_conf:
                best_conf = conf
                best_salary = SalaryRange(
                    minimum=min_val,
                    maximum=max_val,
                    currency=currency,
                    period=period,
                    confidence=conf,
                )

        return best_salary

    def _apply_multiplier(self, val: float | None, mult: str | None) -> float | None:
        if val is None or mult is None:
            return val
        m = mult.lower()
        if "k" in m:
            return val * 1000
        if "lpa" in m or "lakh" in m:
            return val * 100000
        if "cr" in m:
            return val * 10000000
        return val

    def _normalize_currency(self, curr: str) -> str:
        c = curr.lower()
        if "$" in c:
            return "USD"
        if "₹" in c or "rs" in c:
            return "INR"
        if "£" in c:
            return "GBP"
        if "€" in c:
            return "EUR"
        return curr

    def _normalize_period(self, period: str | None) -> SalaryPeriod | None:
        if not period:
            return None
        p = period.lower()
        if "year" in p or "annual" in p or "annum" in p or "p.a" in p or "lpa" in p:
            return SalaryPeriod.YEAR
        if "month" in p or "mo" in p:
            return SalaryPeriod.MONTH
        if "hour" in p or "hr" in p:
            return SalaryPeriod.HOUR
        return None
