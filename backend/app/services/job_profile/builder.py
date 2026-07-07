from datetime import datetime
from app.ai.nlp.schemas.jd.jd_extracted_entities import ExtractedJDEntities
from app.ai.nlp.schemas.jd.jd_skill_schema import RequirementTier
from app.ai.nlp.resources.taxonomy_resource import TaxonomyResourceManager

from .schemas import (
    JobProfile, JobIdentity, RemoteType, RequirementsProfile, 
    SkillRequirement, ResponsibilityRequirement, TechnologyProfile, 
    TechNode, EmploymentProfile, EmploymentType, SalaryProfile, 
    SalaryPeriod, QualificationProfile, ExperienceRequirements, 
    EducationRequirements, CompanyProfile, ProfileMetadata
)

class JobProfileBuilder:
    """
    Constructs the immutable JobProfile business aggregate from ExtractedJDEntities.
    This acts as the boundary between the AI layer and the Business layer.
    """

    def build(self, entities: ExtractedJDEntities) -> JobProfile:
        return JobProfile(
            identity=self._build_identity(entities),
            requirements=self._build_requirements(entities),
            technology=self._build_technology(entities),
            qualification=self._build_qualification(entities),
            employment=self._build_employment(entities),
            company=self._build_company(entities),
            metadata=self._build_metadata(entities)
        )

    def _build_identity(self, entities: ExtractedJDEntities) -> JobIdentity:
        remote_type = None
        if entities.employment and entities.employment.remote_type:
            try:
                remote_type = RemoteType(entities.employment.remote_type.value)
            except ValueError:
                pass
        
        return JobIdentity(
            job_title=entities.employment.job_title if entities.employment else None,
            raw_title=entities.employment.job_title if entities.employment else None,
            location=entities.employment.location if entities.employment else None,
            remote_type=remote_type
        )

    def _build_requirements(self, entities: ExtractedJDEntities) -> RequirementsProfile:
        required = []
        preferred = []
        optional = []
        unknown = []
        
        taxonomy = TaxonomyResourceManager.get_taxonomy()
        
        for skill in entities.skills:
            raw_name = skill.name
            normalized_name = raw_name
            if raw_name.lower() in taxonomy:
                normalized_name = taxonomy[raw_name.lower()][0]
                
            req = SkillRequirement(name=normalized_name)
            if skill.requirement_tier == RequirementTier.REQUIRED:
                required.append(req)
            elif skill.requirement_tier == RequirementTier.PREFERRED:
                preferred.append(req)
            elif skill.requirement_tier == RequirementTier.OPTIONAL:
                optional.append(req)
            else:
                unknown.append(req)
                
        responsibilities = [
            ResponsibilityRequirement(description=r.description)
            for r in entities.responsibilities
        ]
        
        return RequirementsProfile(
            required_skills=required,
            preferred_skills=preferred,
            optional_skills=optional,
            unknown_skills=unknown,
            responsibilities=responsibilities
        )

    def _build_technology(self, entities: ExtractedJDEntities) -> TechnologyProfile:
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
        
        cat_map = {
            "programming_languages": "languages",
            "frameworks": "frameworks",
            "libraries": "libraries",
            "databases": "databases",
            "cloud": "cloud",
            "devops": "devops",
            "ai_ml": "ai_ml",
            "testing": "testing",
            "operating_systems": "operating_systems",
            "tools": "tools",
            "language": "languages",
            "framework": "frameworks",
            "library": "libraries",
            "database": "databases",
            "machine learning": "ai_ml",
            "ai": "ai_ml",
            "os": "operating_systems",
            "operating system": "operating_systems",
            "tool": "tools"
        }
        
        unique_nodes = set()
        taxonomy = TaxonomyResourceManager.get_taxonomy()
        
        for skill in entities.skills:
            raw_name = skill.name
            norm = raw_name
            category = "tools"
            
            if raw_name.lower() in taxonomy:
                norm, category = taxonomy[raw_name.lower()]
                
            if norm in unique_nodes:
                continue
            unique_nodes.add(norm)
            
            node = TechNode(
                name=norm,
                years_applied=0.0,
                last_used_year=None,
                source_count=1
            )
            cat_key = cat_map.get(category.lower(), "tools")
            categories[cat_key].append(node)
            
        return TechnologyProfile(**categories)

    def _build_qualification(self, entities: ExtractedJDEntities) -> QualificationProfile:
        min_y = None
        max_y = None
        
        for exp in entities.experience:
            if exp.min_years is not None:
                if min_y is None or exp.min_years < min_y:
                    min_y = exp.min_years
            if exp.max_years is not None:
                if max_y is None or exp.max_years > max_y:
                    max_y = exp.max_years
                    
        exp_req = ExperienceRequirements(min_years=min_y, max_years=max_y)
        
        hierarchy = ["phd", "master", "bachelor", "diploma", "associate", "certificate"]
        best_rank = len(hierarchy)
        best_degree = None
        
        degrees = []
        for edu in entities.education:
            deg = edu.min_degree_level
            if deg:
                degrees.append(deg)
                deg_lower = deg.lower()
                for rank_idx, rank_keyword in enumerate(hierarchy):
                    if rank_keyword in deg_lower and rank_idx < best_rank:
                        best_rank = rank_idx
                        best_degree = deg
                        
        edu_req = EducationRequirements(
            minimum_degree=best_degree,
            degrees=degrees
        )
        
        return QualificationProfile(experience=exp_req, education=edu_req)

    def _build_employment(self, entities: ExtractedJDEntities) -> EmploymentProfile:
        emp_type = None
        salary_prof = None
        
        if entities.employment:
            if entities.employment.employment_type:
                try:
                    emp_type = EmploymentType(entities.employment.employment_type.value)
                except ValueError:
                    pass
                    
            if entities.employment.salary:
                sal = entities.employment.salary
                period = None
                if sal.period:
                    try:
                        period = SalaryPeriod(sal.period.value)
                    except ValueError:
                        pass
                salary_prof = SalaryProfile(
                    minimum=sal.minimum,
                    maximum=sal.maximum,
                    currency=sal.currency,
                    period=period
                )
                
        return EmploymentProfile(employment_type=emp_type, salary=salary_prof)

    def _build_company(self, entities: ExtractedJDEntities) -> CompanyProfile:
        if entities.company:
            return CompanyProfile(
                name=entities.company.company_name,
                industry=entities.company.industry,
                size=entities.company.company_size,
                culture_keywords=entities.company.culture_keywords or []
            )
        return CompanyProfile(name=None, industry=None, size=None, culture_keywords=[])

    def _build_metadata(self, entities: ExtractedJDEntities) -> ProfileMetadata:
        return ProfileMetadata(
            profile_created_at=datetime.utcnow(),
            source_filename=entities.source_filename,
            is_active=True
        )
