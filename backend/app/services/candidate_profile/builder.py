from datetime import datetime

from app.ai.nlp.schemas.extracted_entities import ExtractedEntities
from app.ai.nlp.schemas.experience_schema import ExperienceRecord
from app.ai.nlp.schemas.project_schema import ProjectRecord

from .schemas.profile import CandidateProfile
from .schemas.identity import IdentityProfile, ContactInformation, SocialProfile
from .schemas.career import CareerProfile, CareerStage
from .schemas.career_position import CareerPosition
from .schemas.academic_degree import AcademicDegree
from .schemas.candidate_certification import CandidateCertification
from .schemas.candidate_project import CandidateProject
from .schemas.education import EducationProfile
from .schemas.technology import TechnologyProfile, TechNode
from .schemas.metadata import ProfileMetadata


class CandidateProfileBuilder:
    """
    Constructs the immutable CandidateProfile from ValidatedExtractedEntities.
    Applies deterministic business rules for calculation and aggregation.
    """

    def build(self, entities: ExtractedEntities) -> CandidateProfile:
        identity = self._build_identity(entities)
        career = self._build_career(entities)
        education = self._build_education(entities)
        technology = self._build_technology(entities)
        metadata = self._build_metadata(entities)

        projects = []
        for p in entities.projects:
            desc = p.summary or ""
            if p.achievements:
                desc += "\nAchievements:\n" + "\n".join(f"- {a}" for a in p.achievements)
            projects.append(
                CandidateProject(
                    name=p.name,
                    description=desc.strip() or p.description,
                    technologies=p.technologies,
                    skills=p.skills,
                    start_date=p.start_date,
                    end_date=p.end_date
                )
            )

        certifications = [
            CandidateCertification(
                name=c.name,
                issuing_organization=c.issuing_organization,
                issue_date=c.issue_date,
                expiry_date=c.expiry_date,
                credential_id=c.credential_id,
                credential_url=c.credential_url
            )
            for c in entities.certifications
        ]

        return CandidateProfile(
            identity=identity,
            career=career,
            education=education,
            technology=technology,
            projects=projects,
            certifications=certifications,
            metadata=metadata
        )

    def _build_identity(self, entities: ExtractedEntities) -> IdentityProfile:
        contact_info = ContactInformation(
            email=entities.contact.email,
            phone=entities.contact.phone,
            location=entities.contact.location
        )
        social_profile = SocialProfile(
            linkedin=entities.contact.linkedin_url,
            github=entities.contact.github_url,
            portfolio=entities.contact.portfolio_url,
            kaggle=entities.contact.kaggle_url,
            leetcode=entities.contact.leetcode_url,
            hackerrank=entities.contact.hackerrank_url
        )
        return IdentityProfile(
            full_name=entities.contact.full_name,
            contact=contact_info,
            social=social_profile
        )

    def _build_career(self, entities: ExtractedEntities) -> CareerProfile:
        total_months = sum(ex.duration_months or 0 for ex in entities.experience)
        
        internship_months = sum(
            ex.duration_months or 0
            for ex in entities.experience
            if ex.employment_type and "intern" in ex.employment_type.lower()
        )

        current_role = next(
            (ex.job_title for ex in entities.experience if ex.is_current),
            entities.experience[0].job_title if entities.experience else None
        )

        most_recent_employer = next(
            (ex.company for ex in entities.experience if ex.is_current),
            entities.experience[0].company if entities.experience else None
        )

        positions = [
            CareerPosition(
                job_title=ex.job_title,
                company=ex.company,
                employment_type=ex.employment_type,
                location=ex.location,
                start_date=ex.start_date,
                end_date=ex.end_date,
                is_current=ex.is_current,
                duration_months=ex.duration_months,
                description=ex.description,
                technologies_used=ex.technologies_used
            )
            for ex in entities.experience
        ]

        return CareerProfile(
            career_stage=self._compute_career_stage(total_months),
            current_role=current_role,
            most_recent_employer=most_recent_employer,
            total_months_experience=total_months,
            internship_months=internship_months,
            positions=positions
        )

    def _compute_career_stage(self, months: int) -> CareerStage:
        if months == 0:
            return CareerStage.STUDENT
        elif 1 <= months <= 24:
            return CareerStage.ENTRY
        elif 25 <= months <= 48:
            return CareerStage.ASSOCIATE
        elif 49 <= months <= 84:
            return CareerStage.MID
        elif 85 <= months <= 144:
            return CareerStage.SENIOR
        elif 145 <= months <= 216:
            return CareerStage.LEAD
        else:
            return CareerStage.PRINCIPAL

    def _build_education(self, entities: ExtractedEntities) -> EducationProfile:
        is_studying = any(ed.is_current for ed in entities.education)
        
        latest_institution = next(
            (ed.institution for ed in entities.education if ed.is_current),
            entities.education[0].institution if entities.education else None
        )

        degrees = [
            AcademicDegree(
                degree=ed.degree,
                field_of_study=ed.field_of_study,
                institution=ed.institution,
                start_year=ed.start_year,
                graduation_year=ed.graduation_year,
                cgpa=ed.cgpa,
                percentage=ed.percentage,
                is_current=ed.is_current
            )
            for ed in entities.education
        ]

        certifications = [
            CandidateCertification(
                name=c.name,
                issuing_organization=c.issuing_organization,
                issue_date=c.issue_date,
                expiry_date=c.expiry_date,
                credential_id=c.credential_id,
                credential_url=c.credential_url
            )
            for c in entities.certifications
        ]

        return EducationProfile(
            highest_qualification=self._compute_highest_qualification(entities),
            latest_institution=latest_institution,
            is_currently_studying=is_studying,
            degrees=degrees,
            certifications=certifications
        )

    def _compute_highest_qualification(self, entities: ExtractedEntities) -> str | None:
        hierarchy = [
            (["phd", "ph.d", "doctorate"], "PhD"),
            (["master", "m.tech", "m.s", "m.a", "mba", "m.b.a", "m.e", "m.sc"], "Master"),
            (["bachelor", "b.tech", "b.s", "b.a", "b.e", "b.sc", "b.com"], "Bachelor"),
            (["diploma"], "Diploma"),
            (["associate"], "Associate"),
            (["certificate"], "Certificate")
        ]
        
        best_rank = len(hierarchy)
        best_degree = None

        for ed in entities.education:
            degree_str = (ed.degree or "").lower()
            for rank_idx, (keywords, title) in enumerate(hierarchy):
                if any(kw in degree_str for kw in keywords) and rank_idx < best_rank:
                    best_rank = rank_idx
                    best_degree = title

        return best_degree

    def _extract_year(self, date_str: str | None) -> int | None:
        # Architecture constraint: Builder must not parse strings or use regex.
        # If the NLP schema did not provide a structured year field, we do not infer it.
        return None

    def _build_technology(self, entities: ExtractedEntities) -> TechnologyProfile:
        all_skills = entities.skills.skills + entities.skills.technologies
        
        categories = {
            "languages": [],
            "frameworks": [],
            "libraries": [],
            "databases": [],
            "cloud": [],
            "devops": [],
            "ai_ml": [],
            "testing": [],
            "operating_systems": [],
            "tools": []
        }
        
        # Mapping from NLP categories to business profile categories
        cat_map = {
            "language": "languages",
            "languages": "languages",
            "programming_languages": "languages",
            "framework": "frameworks",
            "frameworks": "frameworks",
            "library": "libraries",
            "libraries": "libraries",
            "database": "databases",
            "databases": "databases",
            "cloud": "cloud",
            "devops": "devops",
            "machine learning": "ai_ml",
            "ai": "ai_ml",
            "ai_ml": "ai_ml",
            "testing": "testing",
            "os": "operating_systems",
            "operating system": "operating_systems",
            "operating_systems": "operating_systems",
            "tool": "tools",
            "tools": "tools"
        }

        unique_nodes = {}

        for skill in all_skills:
            norm = skill.normalized_name
            if norm in unique_nodes:
                continue
                
            years, last_used, count = self._compute_skill_metrics(norm, entities.experience, entities.projects)
            
            node = TechNode(
                name=norm,
                years_applied=years,
                last_used_year=last_used,
                source_count=count
            )
            unique_nodes[norm] = node
            
            # Map category
            cat_key = cat_map.get(skill.category.lower(), "tools")
            categories[cat_key].append(node)

        return TechnologyProfile(
            languages=categories["languages"],
            frameworks=categories["frameworks"],
            libraries=categories["libraries"],
            databases=categories["databases"],
            cloud=categories["cloud"],
            devops=categories["devops"],
            ai_ml=categories["ai_ml"],
            testing=categories["testing"],
            operating_systems=categories["operating_systems"],
            tools=categories["tools"]
        )

    def _compute_skill_metrics(self, skill_name: str, experiences: list[ExperienceRecord], projects: list[ProjectRecord]) -> tuple[float, int | None, int]:
        total_months = 0
        last_year = None
        count = 0
        
        skill_lower = skill_name.lower()
        
        for ex in experiences:
            techs = [t.lower() for t in ex.technologies_used]
            if skill_lower in techs:
                count += 1
                total_months += (ex.duration_months or 0)
                
                # Check year
                end_y = self._extract_year(ex.end_date)
                start_y = self._extract_year(ex.start_date)
                y = end_y or start_y or (datetime.utcnow().year if ex.is_current else None)
                if y and (last_year is None or y > last_year):
                    last_year = y

        for pr in projects:
            techs = [t.lower() for t in pr.technologies] + [s.lower() for s in pr.skills]
            if skill_lower in techs:
                count += 1
                # Projects usually represent a few months if duration is missing
                total_months += 3
                
                end_y = self._extract_year(pr.end_date)
                start_y = self._extract_year(pr.start_date)
                y = end_y or start_y
                if y and (last_year is None or y > last_year):
                    last_year = y

        years = round(total_months / 12.0, 1)
        return years, last_year, count

    def _build_metadata(self, entities: ExtractedEntities) -> ProfileMetadata:
        # Compute avg confidence
        confidences = []
        confidences.extend(s.confidence for s in entities.skills.skills)
        confidences.extend(s.confidence for s in entities.skills.technologies)
        confidences.extend(e.confidence for e in entities.education)
        confidences.extend(e.confidence for e in entities.experience)
        confidences.extend(p.confidence for p in entities.projects)
        confidences.extend(c.confidence for c in entities.certifications)
        
        avg = sum(confidences) / len(confidences) if confidences else 1.0

        return ProfileMetadata(
            pipeline_version=entities.pipeline_version,
            profile_version="1.0",
            generated_timestamp=datetime.utcnow(),
            average_confidence=round(avg, 2),
            processing_duration_ms=entities.processing_time_ms
        )
