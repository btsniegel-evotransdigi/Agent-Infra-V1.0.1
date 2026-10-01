"""
EN Standard Implementation

European Norms (EN) for architecture and infrastructure planning.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class ENStandardConfig(BaseModel):
    """Configuration for EN standards"""
    enabled: bool = True
    versions: List[str] = Field(default_factory=lambda: [
        "EN ISO 19115:2005",
        "EN 1991-1-1:2002",
        "EN 1991-1-2:2002",
        "EN 1992-1-1:2004",
        "EN 1993-1-1:2005",
        "EN 1997-1:2004",
        "EN 1998-1:2004"
    ])
    required_fields: List[str] = Field(default_factory=lambda: [
        "standard_number",
        "publication_date",
        "scope",
        "title",
        "technical_committee"
    ])
    optional_fields: List[str] = Field(default_factory=lambda: [
        "edition",
        "language",
        "pages",
        "price",
        "cenelec_reference",
        "harmonized_standard"
    ])


@dataclass
class ENStandard:
    """
    EN Standard implementation for European norms.
    
    European Standards relevant for construction, infrastructure,
    and engineering in Europe.
    """
    
    standard_number: str
    title: str
    publication_date: str
    scope: str
    technical_committee: str = ""
    organization: str = "CEN"
    edition: str = "1"
    language: str = "en"
    pages: Optional[int] = None
    price: Optional[float] = None
    cenelec_reference: Optional[str] = None
    harmonized_standard: Optional[bool] = False
    
    # Metadata fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate standard number format"""
        if not self.standard_number.startswith("EN"):
            raise ValueError(f"EN standard number must start with 'EN': {self.standard_number}")
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate drawing metadata against EN standards.
        
        Args:
            metadata: Dictionary containing drawing metadata
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_fields": []
        }
        
        # Check required fields for EN standards
        required_fields = ["standard_number", "title", "publication_date", "scope"]
        for field in required_fields:
            if field not in metadata:
                results["valid"] = False
                results["missing_fields"].append(field)
                results["errors"].append(f"Missing required EN field: {field}")
        
        # Validate CE marking if present
        if "ce_marking" in metadata:
            ce_data = metadata["ce_marking"]
            if not isinstance(ce_data, dict):
                results["valid"] = False
                results["errors"].append("CE marking must be a dictionary")
            elif "notified_body" not in ce_data:
                results["warnings"].append("CE marking should include notified body information")
        
        # Validate harmonized standard reference
        if "harmonized_standard" in metadata:
            if not isinstance(metadata["harmonized_standard"], bool):
                results["valid"] = False
                results["errors"].append("harmonized_standard must be a boolean")
        
        return results
    
    def validate_structural_design(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate structural design against Eurocodes (EN 1990 series).
        
        Args:
            design_data: Dictionary with structural design information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Eurocode specific validations
        eurocode_standards = [
            "EN 1990", "EN 1991", "EN 1992", "EN 1993", 
            "EN 1994", "EN 1995", "EN 1996", "EN 1997", "EN 1998", "EN 1999"
        ]
        
        if "applied_standards" in design_data:
            for standard in design_data["applied_standards"]:
                if standard.startswith("EN ") and standard[:8] not in eurocode_standards:
                    results["warnings"].append(f"Unknown Eurocode standard: {standard}")
        
        # Validate safety factors
        if "safety_factors" in design_data:
            factors = design_data["safety_factors"]
            if not isinstance(factors, dict):
                results["valid"] = False
                results["errors"].append("safety_factors must be a dictionary")
            else:
                for material, factor in factors.items():
                    if not isinstance(factor, (int, float)) or factor <= 0:
                        results["valid"] = False
                        results["errors"].append(f"Invalid safety factor for {material}: {factor}")
        
        return results
    
    def validate_material_properties(self, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate material properties against EN material standards.
        
        Args:
            material_data: Dictionary with material properties
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Common EN material standards
        material_standards = {
            "concrete": ["EN 206", "EN 1992-1-1"],
            "steel": ["EN 10025", "EN 10080", "EN 1993-1-1"],
            "timber": ["EN 338", "EN 1995-1-1"],
            "masonry": ["EN 771", "EN 1996-1-1"],
            "aluminium": ["EN 573", "EN 1999-1-1"]
        }
        
        if "material_type" in material_data:
            mat_type = material_data["material_type"]
            if mat_type.lower() in material_standards:
                # Check if referenced standard is appropriate for material type
                if "standard_reference" in material_data:
                    ref = material_data["standard_reference"]
                    appropriate_standards = material_standards[mat_type.lower()]
                    if ref not in appropriate_standards:
                        results["warnings"].append(
                            f"Standard {ref} may not be appropriate for {mat_type}. "
                            f"Consider: {', '.join(appropriate_standards)}"
                        )
        
        # Validate characteristic values
        if "characteristic_values" in material_data:
            values = material_data["characteristic_values"]
            if not isinstance(values, dict):
                results["valid"] = False
                results["errors"].append("characteristic_values must be a dictionary")
            else:
                for prop, value in values.items():
                    if not isinstance(value, (int, float)):
                        results["valid"] = False
                        results["errors"].append(f"Invalid characteristic value for {prop}")
        
        return results
    
    def get_eurocode_template(self, eurocode: str = "EN 1992-1-1") -> Dict[str, Any]:
        """
        Get template for specific Eurocode.
        
        Args:
            eurocode: Eurocode identifier (e.g., "EN 1992-1-1")
            
        Returns:
            Dictionary with Eurocode template
        """
        templates = {
            "EN 1990": {
                "standard": "EN 1990",
                "title": "Eurocode: Basis of structural design",
                "sections": {
                    "1": "General",
                    "2": "Requirements",
                    "3": "Basic variables",
                    "4": "Verification by partial factor method",
                    "5": "Verification by the use of design charts and load tests",
                    "6": "Management of structural reliability for construction works"
                },
                "key_concepts": [
                    "limit states",
                    "design working life",
                    "durability",
                    "quality management"
                ]
            },
            "EN 1991-1-1": {
                "standard": "EN 1991-1-1",
                "title": "Eurocode 1: Actions on structures - Part 1-1: General actions - Densities, self-weight, imposed loads for buildings",
                "sections": {
                    "1": "General",
                    "2": "Classifications for actions",
                    "3": "Design situations",
                    "4": "Densities of construction materials and stored materials",
                    "5": "Self-weight and imposed loads",
                    "6": "Representation of actions"
                },
                "load_types": ["permanent", "variable", "accidental"]
            },
            "EN 1992-1-1": {
                "standard": "EN 1992-1-1",
                "title": "Eurocode 2: Design of concrete structures - Part 1-1: General rules and rules for buildings",
                "sections": {
                    "1": "General",
                    "2": "Basic assumptions",
                    "3": "Materials",
                    "4": "Durability and cover to reinforcement",
                    "5": "Structural analysis",
                    "6": "Ultimate limit states",
                    "7": "Serviceability limit states",
                    "8": "Detailing of reinforcement and prestressing tendons",
                    "9": "Special provisions for precast concrete elements and structures",
                    "10": "Additional rules for specific construction situations"
                },
                "material_properties": {
                    "concrete": {
                        "fck": "characteristic compressive strength",
                        "fctm": "mean axial tensile strength",
                        "Ecm": "secant modulus of elasticity"
                    },
                    "reinforcement": {
                        "fyk": "characteristic yield strength",
                        "fuk": "characteristic tensile strength",
                        "Es": "modulus of elasticity"
                    }
                }
            },
            "EN 1993-1-1": {
                "standard": "EN 1993-1-1",
                "title": "Eurocode 3: Design of steel structures - Part 1-1: General rules and rules for buildings",
                "sections": {
                    "1": "General",
                    "2": "Basis of design",
                    "3": "Materials",
                    "4": "Durability",
                    "5": "Structural analysis",
                    "6": "Ultimate limit states",
                    "7": "Serviceability limit states"
                },
                "material_properties": {
                    "steel": {
                        "fyk": "yield strength",
                        "fuk": "ultimate tensile strength",
                        "E": "modulus of elasticity"
                    }
                }
            }
        }
        
        return templates.get(eurocode, {
            "standard": eurocode,
            "title": f"Template for {eurocode}",
            "sections": {},
            "notes": "Custom template"
        })
    
    @staticmethod
    def _is_valid_en_date(date_str: str) -> bool:
        """
        Check if date string is in valid EN format (usually YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Boolean indicating if date is valid
        """
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, date_str))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ENStandard':
        """
        Create ENStandard instance from dictionary.
        
        Args:
            data: Dictionary with standard data
            
        Returns:
            ENStandard instance
        """
        return cls(
            standard_number=data.get("standard_number", "EN ISO 19115:2005"),
            title=data.get("title", ""),
            publication_date=data.get("publication_date", ""),
            scope=data.get("scope", ""),
            technical_committee=data.get("technical_committee", ""),
            organization=data.get("organization", "CEN"),
            edition=data.get("edition", "1"),
            language=data.get("language", "en"),
            pages=data.get("pages"),
            price=data.get("price"),
            cenelec_reference=data.get("cenelec_reference"),
            harmonized_standard=data.get("harmonized_standard", False),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "standard_number": self.standard_number,
            "title": self.title,
            "publication_date": self.publication_date,
            "scope": self.scope,
            "technical_committee": self.technical_committee,
            "organization": self.organization,
            "edition": self.edition,
            "language": self.language,
            "pages": self.pages,
            "price": self.price,
            "cenelec_reference": self.cenelec_reference,
            "harmonized_standard": self.harmonized_standard,
            "metadata": self.metadata
        }
