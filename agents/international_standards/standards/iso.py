"""
ISO Standard Implementation

International Organization for Standardization (ISO) standards for
architecture and infrastructure planning.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class ISOStandardConfig(BaseModel):
    """Configuration for ISO standards"""
    enabled: bool = True
    versions: List[str] = Field(default_factory=lambda: [
        "ISO 19115:2003",
        "ISO 19115-1:2014", 
        "ISO 19115-2:2019",
        "ISO 19131:2007",
        "ISO 19139:2007"
    ])
    required_fields: List[str] = Field(default_factory=lambda: [
        "title",
        "abstract", 
        "date",
        "organization",
        "standard_number",
        "publication_date"
    ])
    optional_fields: List[str] = Field(default_factory=lambda: [
        "edition",
        "language",
        "pages",
        "price",
        "ics_code"
    ])


@dataclass
class ISOStandard:
    """
    ISO Standard implementation for architecture and infrastructure.
    
    ISO standards relevant for geographic information, metadata, and
    quality principles for building and infrastructure.
    """
    
    standard_number: str
    title: str
    publication_date: str
    abstract: str = ""
    organization: str = "ISO"
    edition: str = "1"
    language: str = "en"
    pages: Optional[int] = None
    price: Optional[float] = None
    ics_code: Optional[str] = None
    
    # Metadata fields
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate standard number format"""
        if not self.standard_number.startswith("ISO"):
            raise ValueError(f"ISO standard number must start with 'ISO': {self.standard_number}")
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate drawing metadata against ISO 19115 standard.
        
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
        
        # Check required fields
        required_fields = ["title", "abstract", "date", "organization"]
        for field in required_fields:
            if field not in metadata:
                results["valid"] = False
                results["missing_fields"].append(field)
                results["errors"].append(f"Missing required field: {field}")
        
        # ISO 19115 specific validations
        if "date" in metadata:
            date_str = metadata["date"]
            # ISO 8601 date format validation
            if not self._is_valid_iso_date(date_str):
                results["valid"] = False
                results["errors"].append(f"Invalid date format: {date_str}. Must be ISO 8601 format (YYYY-MM-DD)")
        
        if "organization" in metadata:
            org = metadata["organization"]
            if not isinstance(org, str) or len(org.strip()) == 0:
                results["valid"] = False
                results["errors"].append("Organization must be a non-empty string")
        
        return results
    
    def validate_coordinate_system(self, coordinate_system: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate coordinate system against ISO 19111 standard.
        
        Args:
            coordinate_system: Dictionary with coordinate system info
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for required coordinate system fields
        required = ["type", "datum", "projection"]
        for field in required:
            if field not in coordinate_system:
                results["valid"] = False
                results["errors"].append(f"Missing coordinate system field: {field}")
        
        # Validate projection type
        valid_projections = ["UTM", "Geographic", "Lambert", "Mercator", "Transverse Mercator"]
        if "projection" in coordinate_system:
            proj = coordinate_system["projection"]
            if proj not in valid_projections:
                results["warnings"].append(f"Unknown projection type: {proj}")
        
        return results
    
    def validate_quality(self, quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate quality information against ISO 19157 standard.
        
        Args:
            quality_data: Dictionary with quality information
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Quality elements
        quality_elements = ["completeness", "logical_consistency", "positional_accuracy", 
                          "temporal_accuracy", "thematic_accuracy"]
        
        for element in quality_elements:
            if element in quality_data:
                value = quality_data[element]
                if not isinstance(value, (int, float)) or not (0 <= value <= 100):
                    results["valid"] = False
                    results["errors"].append(f"Quality element '{element}' must be a percentage (0-100)")
        
        return results
    
    def get_metadata_template(self) -> Dict[str, Any]:
        """
        Get metadata template according to ISO 19115.
        
        Returns:
            Dictionary with metadata template
        """
        return {
            "metadata_standard": {
                "name": "ISO 19115",
                "version": "2003/2014"
            },
            "identification_info": {
                "title": "",
                "abstract": "",
                "purpose": "",
                "status": "",
                "point_of_contact": {
                    "name": "",
                    "organization": "",
                    "email": ""
                },
                "resource_maintenance": {
                    "maintenance_frequency": "",
                    "date_of_next_update": ""
                },
                "descriptive_keywords": [],
                "resource_specific_usage": "",
                "access_constraints": "",
                "use_constraints": "",
                "aggregation_info": None
            },
            "data_quality_info": {
                "scope": "",
                "lineage": "",
                "positional_accuracy": None,
                "attribute_accuracy": None,
                "logical_consistency": None,
                "completeness": None,
                "temporal_quality": None,
                "usability": None
            },
            "spatial_representation_info": {
                "type": "",
                "scale_factor": None,
                "axis_dimension_properties": None
            },
            "reference_system_info": {
                "reference_system_identifier": {
                    "code": "",
                    "code_space": "",
                    "version": ""
                }
            },
            "content_info": {
                "feature_catalogue_citation": {
                    "title": "",
                    "date": {
                        "date": "",
                        "date_type": ""
                    },
                    "identifier": ""
                },
                "coverage_description": None,
                "image_description": None
            },
            "portrayal_catalogue_info": None,
            "metadata_extension_info": None,
            "distribution_info": {
                "distributor": {
                    "distributor_contact": {
                        "organization": "",
                        "email": ""
                    },
                    "distribution_order_process": {
                        "fees": "",
                        "ordered": False,
                        "planned_available_date_time": ""
                    },
                    "distributor_format": None,
                    "distributor_transfer_options": None
                },
                "resource_locator": None
            },
            "metadata_constraints": {
                "access_constraints": "",
                "use_constraints": "",
                "other_constraints": ""
            },
            "metadata_maintenance": {
                "maintenance_frequency": "",
                "date_of_next_update": "",
                "user_defined_maintenance_frequency": "",
                "maintenance_contact": {
                    "organization": "",
                    "email": ""
                }
            }
        }
    
    @staticmethod
    def _is_valid_iso_date(date_str: str) -> bool:
        """
        Check if date string is in ISO 8601 format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Boolean indicating if date is valid ISO 8601
        """
        import re
        # ISO 8601 date pattern: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
        pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$'
        return bool(re.match(pattern, date_str))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ISOStandard':
        """
        Create ISOStandard instance from dictionary.
        
        Args:
            data: Dictionary with standard data
            
        Returns:
            ISOStandard instance
        """
        return cls(
            standard_number=data.get("standard_number", "ISO 19115:2003"),
            title=data.get("title", ""),
            publication_date=data.get("publication_date", ""),
            abstract=data.get("abstract", ""),
            organization=data.get("organization", "ISO"),
            edition=data.get("edition", "1"),
            language=data.get("language", "en"),
            pages=data.get("pages"),
            price=data.get("price"),
            ics_code=data.get("ics_code"),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "standard_number": self.standard_number,
            "title": self.title,
            "publication_date": self.publication_date,
            "abstract": self.abstract,
            "organization": self.organization,
            "edition": self.edition,
            "language": self.language,
            "pages": self.pages,
            "price": self.price,
            "ics_code": self.ics_code,
            "metadata": self.metadata
        }
