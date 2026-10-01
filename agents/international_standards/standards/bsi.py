"""
BSI Standard Implementation

British Standards Institution (BSI) standards for architecture and infrastructure.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class BSIStandardConfig(BaseModel):
    """Configuration for BSI standards"""
    enabled: bool = True
    versions: List[str] = Field(default_factory=lambda: [
        "BS EN ISO 19115:2005",
        "BS 1192-4:2014",
        "BS 8541-1:2012",
        "BS 8541-2:2011",
        "BS 8541-3:2012",
        "BS 8541-4:2015",
        "BS EN 1990:2002+A1:2005",
        "BS EN 1991-1-1:2002",
        "BS EN 1992-1-1:2004",
        "BS EN 1993-1-1:2005"
    ])
    required_fields: List[str] = Field(default_factory=lambda: [
        "standard_ref",
        "title",
        "issue_date",
        "scope",
        "status",
        "publisher"
    ])
    optional_fields: List[str] = Field(default_factory=lambda: [
        "edition",
        "language",
        "pages",
        "price",
        "isbn",
        "replaces",
        "replaced_by",
        "committees"
    ])


@dataclass
class BSIStandard:
    """
    BSI Standard implementation for British standards.
    
    BSI standards relevant for construction, architecture, and
    infrastructure in the United Kingdom.
    """
    
    standard_ref: str
    title: str
    issue_date: str
    scope: str
    status: str = "Current"
    publisher: str = "BSI"
    edition: str = "1"
    language: str = "en"
    pages: Optional[int] = None
    price: Optional[float] = None
    isbn: Optional[str] = None
    replaces: Optional[str] = None
    replaced_by: Optional[str] = None
    committees: Optional[List[str]] = None
    
    # Metadata fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate standard reference format"""
        if not self.standard_ref.startswith("BS"):
            raise ValueError(f"BSI standard reference must start with 'BS': {self.standard_ref}")
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate drawing metadata against BSI standards.
        
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
        
        # Check required fields for BSI standards
        required_fields = ["standard_ref", "title", "issue_date", "scope"]
        for field in required_fields:
            if field not in metadata:
                results["valid"] = False
                results["missing_fields"].append(field)
                results["errors"].append(f"Missing required BSI field: {field}")
        
        # Validate BSI-specific fields
        valid_statuses = ["Current", "Superseded", "Withdrawn", "Draft", "Under Review"]
        if "status" in metadata:
            status = metadata["status"]
            if status not in valid_statuses:
                results["warnings"].append(f"Unknown BSI status: {status}")
        
        # Check for UK-specific requirements
        if "location" in metadata:
            location = metadata["location"]
            if "UK" not in location and "United Kingdom" not in location:
                results["warnings"].append(
                    f"BSI standards are primarily for UK use. Location: {location}"
                )
        
        return results
    
    def validate_bim_standards(self, bim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Building Information Modeling (BIM) against BS 1192 and BS 8541 series.
        
        Args:
            bim_data: Dictionary with BIM information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # BS 1192-4:2014 - Collaborative production of information
        # BS 8541 series - Library objects for architecture, engineering and construction
        
        if "bim_execution_plan" in bim_data:
            plan = bim_data["bim_execution_plan"]
            if not isinstance(plan, dict):
                results["valid"] = False
                results["errors"].append("bim_execution_plan must be a dictionary")
            else:
                # Check for required BEP components
                required_components = [
                    "project_information",
                    "project_roles",
                    "responsibilities",
                    "standards_methods_procedures",
                    "information_requirements",
                    "delivery_strategy"
                ]
                for component in required_components:
                    if component not in plan:
                        results["warnings"].append(f"Missing BEP component: {component}")
        
        # Validate Common Data Environment (CDE)
        if "cde" in bim_data:
            cde = bim_data["cde"]
            if not isinstance(cde, dict):
                results["valid"] = False
                results["errors"].append("cde must be a dictionary")
            else:
                # BS 1192:2007 CDE workflow states
                workflow_states = ["Work in Progress", "Shared", "Published", "Archive"]
                if "workflow_states" in cde:
                    for state in cde["workflow_states"]:
                        if state not in workflow_states:
                            results["warnings"].append(f"Unknown CDE workflow state: {state}")
        
        return results
    
    def validate_structural_design(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate structural design against BS EN 1990 series (Eurocodes as adopted in UK).
        
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
        
        # UK National Annexes to Eurocodes
        uk_annexes = [
            "BS EN 1990:2002+A1:2005 NA",
            "BS EN 1991-1-1:2002 NA",
            "BS EN 1992-1-1:2004 NA",
            "BS EN 1993-1-1:2005 NA"
        ]
        
        if "national_annexes" in design_data:
            for annex in design_data["national_annexes"]:
                if annex not in uk_annexes:
                    results["warnings"].append(f"Non-UK national annex: {annex}")
        
        # Validate UK-specific design parameters
        if "design_parameters" in design_data:
            params = design_data["design_parameters"]
            if not isinstance(params, dict):
                results["valid"] = False
                results["errors"].append("design_parameters must be a dictionary")
            else:
                # UK-specific parameters
                uk_params = [
                    "partial_factor_gamma_g",
                    "partial_factor_gamma_q",
                    "wind_load_factor",
                    "snow_load_factor"
                ]
                for param in uk_params:
                    if param in params and not isinstance(params[param], (int, float)):
                        results["valid"] = False
                        results["errors"].append(f"Invalid {param} value")
        
        return results
    
    def validate_fire_safety(self, fire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fire safety against BS 476, BS EN 13501, and related standards.
        
        Args:
            fire_data: Dictionary with fire safety information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Fire resistance classifications
        fire_classifications = [
            "A1", "A2", "B", "C", "D", "E", "F",
            "A1fl", "A2fl", "Bfl", "Cfl", "Dfl", "Efl", "Ffl"
        ]
        
        if "material_classifications" in fire_data:
            for material, classification in fire_data["material_classifications"].items():
                if classification not in fire_classifications:
                    results["warnings"].append(
                        f"Unknown fire classification for {material}: {classification}"
                    )
        
        # Fire resistance durations
        if "fire_resistance" in fire_data:
            resistance = fire_data["fire_resistance"]
            if not isinstance(resistance, dict):
                results["valid"] = False
                results["errors"].append("fire_resistance must be a dictionary")
            else:
                for element, duration in resistance.items():
                    if not isinstance(duration, (int, float)) or duration <= 0:
                        results["valid"] = False
                        results["errors"].append(f"Invalid fire resistance duration for {element}: {duration}")
        
        return results
    
    def get_bsi_drawing_template(self) -> Dict[str, Any]:
        """
        Get template for BSI-compliant construction drawings.
        
        Returns:
            Dictionary with drawing template
        """
        return {
            "drawing_information": {
                "title_block": {
                    "project_name": "",
                    "project_number": "",
                    "drawing_title": "",
                    "drawing_number": "",
                    "revision": "",
                    "date": "",
                    "drawn_by": "",
                    "checked_by": "",
                    "approved_by": "",
                    "scale": "",
                    "sheet_size": "",
                    "north_arrow": True,
                    "units": "millimetres"
                },
                "drawing_type": "",  # architectural, structural, services, etc.
                "bs_standards": []
            },
            "technical_information": {
                "dimensions": {
                    "units": "mm",
                    "precision": ""
                },
                "tolerances": {
                    "dimensional": "BS 4500",
                    "geometric": "BS EN ISO 2768"
                },
                "materials": [],
                "finishes": [],
                "notes": []
            },
            "bim_information": {
                "bim_level": "",  # Level 0, 1, 2, 3
                "cde_workflow": "",
                "classification": "",
                "objects": []
            },
            "compliance": {
                "bsi_standards": [],
                "bs_en_standards": [],
                "uk_building_regulations": []
            },
            "metadata": {
                "created_by": "",
                "created_date": "",
                "last_modified": "",
                "software": "",
                "version": "",
                "bsi_reference": ""
            }
        }
    
    @staticmethod
    def _is_valid_bsi_date(date_str: str) -> bool:
        """
        Check if date string is in valid BSI format (usually DD/MM/YYYY or YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Boolean indicating if date is valid
        """
        import re
        patterns = [
            r'^\d{2}/\d{2}/\d{4}$',  # DD/MM/YYYY
            r'^\d{4}-\d{2}-\d{2}$'    # YYYY-MM-DD
        ]
        return any(re.match(pattern, date_str) for pattern in patterns)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BSIStandard':
        """
        Create BSIStandard instance from dictionary.
        
        Args:
            data: Dictionary with standard data
            
        Returns:
            BSIStandard instance
        """
        return cls(
            standard_ref=data.get("standard_ref", "BS EN ISO 19115:2005"),
            title=data.get("title", ""),
            issue_date=data.get("issue_date", ""),
            scope=data.get("scope", ""),
            status=data.get("status", "Current"),
            publisher=data.get("publisher", "BSI"),
            edition=data.get("edition", "1"),
            language=data.get("language", "en"),
            pages=data.get("pages"),
            price=data.get("price"),
            isbn=data.get("isbn"),
            replaces=data.get("replaces"),
            replaced_by=data.get("replaced_by"),
            committees=data.get("committees", []),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "standard_ref": self.standard_ref,
            "title": self.title,
            "issue_date": self.issue_date,
            "scope": self.scope,
            "status": self.status,
            "publisher": self.publisher,
            "edition": self.edition,
            "language": self.language,
            "pages": self.pages,
            "price": self.price,
            "isbn": self.isbn,
            "replaces": self.replaces,
            "replaced_by": self.replaced_by,
            "committees": self.committees,
            "metadata": self.metadata
        }
