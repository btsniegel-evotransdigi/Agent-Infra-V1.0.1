"""
DIN Standard Implementation

Deutsches Institut für Normung (DIN) standards for architecture and infrastructure.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class DINStandardConfig(BaseModel):
    """Configuration for DIN standards"""
    enabled: bool = True
    versions: List[str] = Field(default_factory=lambda: [
        "DIN EN ISO 19115:2005",
        "DIN 1356-1:1995",
        "DIN 18201:2012",
        "DIN 18202:2013",
        "DIN 18203-1:2016",
        "DIN 276-1:2008",
        "DIN 277-1:2016",
        "DIN 4102-1:1998",
        "DIN EN 1992-1-1:2005",
        "DIN EN 1993-1-1:2005"
    ])
    required_fields: List[str] = Field(default_factory=lambda: [
        "norm_number",
        "title",
        "validity",
        "publication_date",
        "issuing_body"
    ])
    optional_fields: List[str] = Field(default_factory=lambda: [
        "edition",
        "language",
        "pages",
        "price",
        "replaces",
        "replaced_by",
        "application_area"
    ])


@dataclass
class DINStandard:
    """
    DIN Standard implementation for German norms.
    
    DIN standards relevant for construction, architecture, and
    infrastructure in Germany.
    """
    
    norm_number: str
    title: str
    validity: str
    publication_date: str
    issuing_body: str = "DIN"
    edition: str = "1"
    language: str = "de"
    pages: Optional[int] = None
    price: Optional[float] = None
    replaces: Optional[str] = None
    replaced_by: Optional[str] = None
    application_area: Optional[str] = None
    
    # Metadata fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate norm number format"""
        if not self.norm_number.startswith("DIN"):
            raise ValueError(f"DIN norm number must start with 'DIN': {self.norm_number}")
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate drawing metadata against DIN standards.
        
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
        
        # Check required fields for DIN standards
        required_fields = ["norm_number", "title", "publication_date"]
        for field in required_fields:
            if field not in metadata:
                results["valid"] = False
                results["missing_fields"].append(field)
                results["errors"].append(f"Missing required DIN field: {field}")
        
        # Validate DIN-specific fields
        if "validity" in metadata:
            validity = metadata["validity"]
            valid_statuses = ["valid", "withdrawn", "replaced", "draft"]
            if validity.lower() not in valid_statuses:
                results["warnings"].append(f"Unknown validity status: {validity}")
        
        # Check for German language if specified
        if "language" in metadata:
            lang = metadata["language"]
            if lang != "de" and lang != "en":
                results["warnings"].append(f"DIN standards are typically in German or English: {lang}")
        
        return results
    
    def validate_construction_drawing(self, drawing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate construction drawing against DIN 1356 and related standards.
        
        Args:
            drawing_data: Dictionary with construction drawing information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # DIN 1356-1: Building drawing - Part 1: Types and contents of drawings
        if "drawing_type" in drawing_data:
            valid_types = [
                "site_plan", "floor_plan", "elevation", "section", 
                "detail", "assembly", "workshop", "as_built"
            ]
            if drawing_data["drawing_type"].lower() not in valid_types:
                results["warnings"].append(f"Unknown drawing type: {drawing_data['drawing_type']}")
        
        # DIN 18201: Tolerances in building construction
        if "tolerances" in drawing_data:
            tolerances = drawing_data["tolerances"]
            if not isinstance(tolerances, dict):
                results["valid"] = False
                results["errors"].append("tolerances must be a dictionary")
            else:
                # Check for standard tolerance classes
                if "class" in tolerances:
                    valid_classes = ["1", "2", "3", "4"]
                    if tolerances["class"] not in valid_classes:
                        results["warnings"].append(f"Unknown tolerance class: {tolerances['class']}")
        
        # DIN 18202: Tolerances in building construction - Supplementary tolerances
        if "supplementary_tolerances" in drawing_data:
            supp_tols = drawing_data["supplementary_tolerances"]
            if not isinstance(supp_tols, list):
                results["valid"] = False
                results["errors"].append("supplementary_tolerances must be a list")
        
        return results
    
    def validate_cost_calculation(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate cost calculation against DIN 276 (Costs in building construction).
        
        Args:
            cost_data: Dictionary with cost calculation data
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # DIN 276-1: High-level breakdown of construction costs
        cost_groups = [
            "100", "200", "300", "400", "500", "600", "700", "800"
        ]
        cost_group_names = {
            "100": "Preparation of the site",
            "200": "Structure",
            "300": "Building shell",
            "400": "Interior construction",
            "500": "Building services",
            "600": "External works",
            "700": "Equipment and furnishings",
            "800": "Other costs"
        }
        
        if "cost_groups" in cost_data:
            for group in cost_data["cost_groups"]:
                group_id = str(group.get("id", ""))[:3]  # Get first 3 digits
                if group_id not in cost_groups:
                    results["warnings"].append(f"Unknown cost group: {group_id}")
                else:
                    # Validate cost values
                    if "cost" in group:
                        cost = group["cost"]
                        if not isinstance(cost, (int, float)) or cost < 0:
                            results["valid"] = False
                            results["errors"].append(f"Invalid cost value in group {group_id}: {cost}")
        
        return results
    
    def validate_area_calculation(self, area_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate area calculation against DIN 277 (Areas and volumes of buildings).
        
        Args:
            area_data: Dictionary with area calculation data
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # DIN 277-1: Areas and volumes
        area_types = [
            "gross_floor_area",
            "net_floor_area", 
            "usable_area",
            "traffic_area",
            "functional_area",
            "technical_functional_area",
            "construction_area",
            "other_area"
        ]
        
        if "areas" in area_data:
            areas = area_data["areas"]
            if not isinstance(areas, dict):
                results["valid"] = False
                results["errors"].append("areas must be a dictionary")
            else:
                for area_type, value in areas.items():
                    if area_type.lower() not in area_types:
                        results["warnings"].append(f"Unknown area type: {area_type}")
                    if not isinstance(value, (int, float)) or value < 0:
                        results["valid"] = False
                        results["errors"].append(f"Invalid area value for {area_type}: {value}")
        
        return results
    
    def get_din_drawing_template(self) -> Dict[str, Any]:
        """
        Get template for DIN-compliant construction drawings.
        
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
                    "unit": "mm"
                },
                "drawing_type": "",  # site_plan, floor_plan, elevation, section, detail
                "drawing_size": "",  # A0, A1, A2, A3, A4
                "orientation": ""  # portrait, landscape
            },
            "technical_information": {
                "materials": [],
                "dimensions": {
                    "length": None,
                    "width": None,
                    "height": None
                },
                "tolerances": {
                    "class": "",
                    "values": {}
                },
                "finishes": [],
                "notes": []
            },
            "compliance": {
                "din_standards": [],
                "en_standards": [],
                "iso_standards": [],
                "other_standards": []
            },
            "metadata": {
                "created_by": "",
                "created_date": "",
                "last_modified": "",
                "software": "",
                "version": ""
            }
        }
    
    @staticmethod
    def _is_valid_din_date(date_str: str) -> bool:
        """
        Check if date string is in valid DIN format (usually DD.MM.YYYY or YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Boolean indicating if date is valid
        """
        import re
        patterns = [
            r'^\d{2}\.\d{2}\.\d{4}$',  # DD.MM.YYYY
            r'^\d{4}-\d{2}-\d{2}$'    # YYYY-MM-DD
        ]
        return any(re.match(pattern, date_str) for pattern in patterns)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DINStandard':
        """
        Create DINStandard instance from dictionary.
        
        Args:
            data: Dictionary with standard data
            
        Returns:
            DINStandard instance
        """
        return cls(
            norm_number=data.get("norm_number", "DIN 1356-1:1995"),
            title=data.get("title", ""),
            validity=data.get("validity", "valid"),
            publication_date=data.get("publication_date", ""),
            issuing_body=data.get("issuing_body", "DIN"),
            edition=data.get("edition", "1"),
            language=data.get("language", "de"),
            pages=data.get("pages"),
            price=data.get("price"),
            replaces=data.get("replaces"),
            replaced_by=data.get("replaced_by"),
            application_area=data.get("application_area"),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "norm_number": self.norm_number,
            "title": self.title,
            "validity": self.validity,
            "publication_date": self.publication_date,
            "issuing_body": self.issuing_body,
            "edition": self.edition,
            "language": self.language,
            "pages": self.pages,
            "price": self.price,
            "replaces": self.replaces,
            "replaced_by": self.replaced_by,
            "application_area": self.application_area,
            "metadata": self.metadata
        }
