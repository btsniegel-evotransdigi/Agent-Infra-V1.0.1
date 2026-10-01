"""
ANSI Standard Implementation

American National Standards Institute (ANSI) standards for architecture and infrastructure.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class ANSIStandardConfig(BaseModel):
    """Configuration for ANSI standards"""
    enabled: bool = True
    versions: List[str] = Field(default_factory=lambda: [
        "ANSI A14.1-2017",
        "ANSI A14.2-2017", 
        "ANSI A14.3-2008",
        "ANSI A14.4-2009",
        "ANSI A14.5-2017",
        "ANSI A14.7-2018",
        "ANSI A117.1-2017",
        "ANSI Z1.1-1996",
        "ANSI Z535.1-2017"
    ])
    required_fields: List[str] = Field(default_factory=lambda: [
        "standard_id",
        "title",
        "publication_date",
        "description",
        "developer",
        "approver"
    ])
    optional_fields: List[str] = Field(default_factory=lambda: [
        "edition",
        "language",
        "pages",
        "price",
        "ics_code",
        "replaces",
        "reaffirmed_date",
        "withdrawn_date"
    ])


@dataclass
class ANSIStandard:
    """
    ANSI Standard implementation for American standards.
    
    ANSI standards relevant for construction, architecture, and
    infrastructure in the United States.
    """
    
    standard_id: str
    title: str
    publication_date: str
    description: str
    developer: str = ""
    approver: str = "ANSI"
    edition: str = "1"
    language: str = "en"
    pages: Optional[int] = None
    price: Optional[float] = None
    ics_code: Optional[str] = None
    replaces: Optional[str] = None
    reaffirmed_date: Optional[str] = None
    withdrawn_date: Optional[str] = None
    
    # Metadata fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate standard ID format"""
        if not self.standard_id.startswith("ANSI"):
            raise ValueError(f"ANSI standard ID must start with 'ANSI': {self.standard_id}")
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate drawing metadata against ANSI standards.
        
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
        
        # Check required fields for ANSI standards
        required_fields = ["standard_id", "title", "publication_date", "description"]
        for field in required_fields:
            if field not in metadata:
                results["valid"] = False
                results["missing_fields"].append(field)
                results["errors"].append(f"Missing required ANSI field: {field}")
        
        # Validate ANSI-specific fields
        if "approver" in metadata:
            approver = metadata["approver"]
            if approver != "ANSI" and not approver.startswith("ANSI/"):
                results["warnings"].append(f"Approver should be ANSI or ANSI/accredited organization: {approver}")
        
        # Check for US customary units if specified
        if "units" in metadata:
            units = metadata["units"]
            us_units = ["inches", "feet", "yards", "miles", "US survey feet"]
            if units.lower() not in us_units and units.lower() != "metric":
                results["warnings"].append(f"ANSI typically uses US customary or metric units: {units}")
        
        return results
    
    def validate_safety_standards(self, safety_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate safety standards against ANSI A14 series (Ladder safety).
        
        Args:
            safety_data: Dictionary with safety information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # ANSI A14.1 - Portable Metal Ladders
        # ANSI A14.2 - Portable Wood Ladders  
        # ANSI A14.3 - Fixed Ladders
        # ANSI A14.4 - Job-Made Wooden Ladders
        # ANSI A14.5 - Portable Reinforced Plastic Ladders
        # ANSI A14.7 - Mobile Ladder Stands and Mobile Ladder Stand Platforms
        
        a14_standards = ["A14.1", "A14.2", "A14.3", "A14.4", "A14.5", "A14.7"]
        
        if "applied_safety_standards" in safety_data:
            for standard in safety_data["applied_safety_standards"]:
                if standard.startswith("ANSI A14") and standard[7:11] not in a14_standards:
                    results["warnings"].append(f"Unknown ANSI A14 standard: {standard}")
        
        # Validate load ratings
        if "load_ratings" in safety_data:
            ratings = safety_data["load_ratings"]
            if not isinstance(ratings, dict):
                results["valid"] = False
                results["errors"].append("load_ratings must be a dictionary")
            else:
                # ANSI load ratings: Type I, Type IA, Type II, Type III
                valid_ratings = ["Type I", "Type IA", "Type II", "Type III"]
                for rating, value in ratings.items():
                    if rating not in valid_ratings:
                        results["warnings"].append(f"Unknown ANSI load rating: {rating}")
                    if not isinstance(value, (int, float)) or value <= 0:
                        results["valid"] = False
                        results["errors"].append(f"Invalid load rating value for {rating}: {value}")
        
        return results
    
    def validate_accessibility(self, accessibility_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate accessibility against ANSI A117.1 (Accessible and Usable Buildings).
        
        Args:
            accessibility_data: Dictionary with accessibility information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # ANSI A117.1 requirements
        accessibility_requirements = {
            "door_width": {"min": 32, "unit": "inches"},  # 32 inches minimum
            "hallway_width": {"min": 36, "unit": "inches"},  # 36 inches minimum
            "ramp_slope": {"max": 8.33, "unit": "percent"},  # 1:12 slope max
            "elevation_change": {"max": 0.5, "unit": "inches"},  # 0.5 inches max
            "clear_floor_space": {"min": 30, "min_diameter": 60, "unit": "inches"}
        }
        
        for requirement, spec in accessibility_requirements.items():
            if requirement in accessibility_data:
                value = accessibility_data[requirement]
                if "min" in spec and value < spec["min"]:
                    results["valid"] = False
                    results["errors"].append(
                        f"{requirement} must be at least {spec['min']} {spec['unit']}: {value}"
                    )
                elif "max" in spec and value > spec["max"]:
                    results["valid"] = False
                    results["errors"].append(
                        f"{requirement} must be at most {spec['max']} {spec['unit']}: {value}"
                    )
        
        return results
    
    def validate_drawing_standards(self, drawing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate drawing standards against ANSI Z1.1 (Graphic Symbols for Architectural and Building Construction).
        
        Args:
            drawing_data: Dictionary with drawing information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # ANSI Z1.1 - Graphic Symbols
        if "symbols" in drawing_data:
            symbols = drawing_data["symbols"]
            if not isinstance(symbols, list):
                results["valid"] = False
                results["errors"].append("symbols must be a list")
            else:
                # Check for standard symbol sets
                standard_symbols = [
                    "electrical", "plumbing", "HVAC", "structural",
                    "architectural", "fire_protection", "security"
                ]
                for symbol in symbols:
                    if "type" in symbol and symbol["type"].lower() not in standard_symbols:
                        results["warnings"].append(f"Unknown symbol type: {symbol['type']}")
        
        # Validate drawing sheet sizes (ANSI standard sizes)
        if "sheet_size" in drawing_data:
            size = drawing_data["sheet_size"]
            ansi_sizes = [
                "A", "B", "C", "D", "E", "F", 
                "A0", "A1", "A2", "A3", "A4",
                "ARCH A", "ARCH B", "ARCH C", "ARCH D", "ARCH E"
            ]
            if size not in ansi_sizes:
                results["warnings"].append(f"Non-standard ANSI sheet size: {size}")
        
        return results
    
    def get_ansi_drawing_template(self) -> Dict[str, Any]:
        """
        Get template for ANSI-compliant construction drawings.
        
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
                    "units": "feet and inches"
                },
                "drawing_type": "",  # architectural, structural, electrical, mechanical, plumbing
                "disciplines": []
            },
            "technical_information": {
                "dimensions": {
                    "units": "",
                    "precision": ""
                },
                "tolerances": {
                    "dimensional": "",
                    "angular": ""
                },
                "materials": [],
                "finishes": [],
                "notes": []
            },
            "safety_information": {
                "safety_standards": [],
                "warnings": [],
                "hazards": []
            },
            "accessibility": {
                "ada_compliance": False,
                "accessibility_features": [],
                "clearances": {}
            },
            "compliance": {
                "ansi_standards": [],
                "osha_standards": [],
                "local_codes": []
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
    def _is_valid_ansi_date(date_str: str) -> bool:
        """
        Check if date string is in valid ANSI format (usually MM/DD/YYYY or YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Boolean indicating if date is valid
        """
        import re
        patterns = [
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{4}-\d{2}-\d{2}$'    # YYYY-MM-DD
        ]
        return any(re.match(pattern, date_str) for pattern in patterns)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ANSIStandard':
        """
        Create ANSIStandard instance from dictionary.
        
        Args:
            data: Dictionary with standard data
            
        Returns:
            ANSIStandard instance
        """
        return cls(
            standard_id=data.get("standard_id", "ANSI Z1.1-1996"),
            title=data.get("title", ""),
            publication_date=data.get("publication_date", ""),
            description=data.get("description", ""),
            developer=data.get("developer", ""),
            approver=data.get("approver", "ANSI"),
            edition=data.get("edition", "1"),
            language=data.get("language", "en"),
            pages=data.get("pages"),
            price=data.get("price"),
            ics_code=data.get("ics_code"),
            replaces=data.get("replaces"),
            reaffirmed_date=data.get("reaffirmed_date"),
            withdrawn_date=data.get("withdrawn_date"),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "standard_id": self.standard_id,
            "title": self.title,
            "publication_date": self.publication_date,
            "description": self.description,
            "developer": self.developer,
            "approver": self.approver,
            "edition": self.edition,
            "language": self.language,
            "pages": self.pages,
            "price": self.price,
            "ics_code": self.ics_code,
            "replaces": self.replaces,
            "reaffirmed_date": self.reaffirmed_date,
            "withdrawn_date": self.withdrawn_date,
            "metadata": self.metadata
        }
