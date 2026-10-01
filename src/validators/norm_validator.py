"""
Norm Validator for Agent-Infra-V1.0.1

Validates against international norms and standards (ISO, EN, DIN, ANSI, BSI).
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


@dataclass
class NormValidationResult:
    """Result of norm validation"""
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    standard: str = ""
    compliance_level: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error: str):
        """Add a validation error"""
        self.valid = False
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a validation warning"""
        self.warnings.append(warning)
    
    def add_info(self, info: str):
        """Add a validation info"""
        self.info.append(info)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "standard": self.standard,
            "compliance_level": self.compliance_level,
            "metadata": self.metadata
        }


class NormValidator:
    """
    Validator for international norms and standards.
    
    Validates data against:
    - ISO standards
    - EN standards (Eurocodes)
    - DIN standards (German norms)
    - ANSI standards (American norms)
    - BSI standards (British norms)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the norm validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.standard_configs = self.config.get("standards", {})
    
    def validate(self, data: Dict[str, Any], standard: str) -> NormValidationResult:
        """
        Validate data against a specific standard.
        
        Args:
            data: Data to validate
            standard: Standard to validate against
            
        Returns:
            NormValidationResult
        """
        result = NormValidationResult()
        result.standard = standard
        
        # Get configuration for the standard
        standard_config = self._get_standard_config(standard)
        
        if not standard_config:
            result.add_warning(f"Unknown standard: {standard}. Using generic validation.")
            return self._generic_validation(data, result)
        
        # Perform standard-specific validation
        standard_upper = standard.upper()
        
        if standard_upper.startswith("ISO"):
            return self._validate_iso(data, standard, result)
        elif standard_upper.startswith("EN"):
            return self._validate_en(data, standard, result)
        elif standard_upper.startswith("DIN"):
            return self._validate_din(data, standard, result)
        elif standard_upper.startswith("ANSI"):
            return self._validate_ansi(data, standard, result)
        elif standard_upper.startswith("BS"):
            return self._validate_bsi(data, standard, result)
        else:
            return self._generic_validation(data, result)
    
    def _get_standard_config(self, standard: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific standard"""
        standard_upper = standard.upper()
        
        # Check for exact match
        if standard in self.standard_configs:
            return self.standard_configs[standard]
        
        # Check for prefix match
        for config_standard, config in self.standard_configs.items():
            if standard_upper.startswith(config_standard.upper()):
                return config
        
        return None
    
    def _validate_iso(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ISO standards"""
        # ISO 19115: Geographic Information - Metadata
        if "19115" in standard:
            return self._validate_iso_19115(data, standard, result)
        
        # ISO 19111: Spatial referencing by coordinates
        if "19111" in standard:
            return self._validate_iso_19111(data, standard, result)
        
        # ISO 19157: Data quality
        if "19157" in standard:
            return self._validate_iso_19157(data, standard, result)
        
        # Generic ISO validation
        return self._validate_iso_generic(data, standard, result)
    
    def _validate_iso_19115(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ISO 19115 (Metadata)"""
        metadata = data.get("metadata", {})
        
        # Required metadata fields for ISO 19115
        required_fields = [
            "title", "abstract", "date", "organization", 
            "standard_number", "publication_date"
        ]
        
        for field in required_fields:
            if field not in metadata:
                result.add_error(f"Missing required ISO 19115 field: {field}")
            elif not metadata[field]:
                result.add_warning(f"ISO 19115 field '{field}' is empty")
            else:
                result.add_info(f"ISO 19115 field '{field}' present")
        
        # Validate date format
        if "date" in metadata:
            date_str = metadata["date"]
            if not self._is_valid_iso_date(date_str):
                result.add_error(f"Invalid date format: {date_str}. Must be ISO 8601 format.")
        
        return result
    
    def _validate_iso_19111(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ISO 19111 (Spatial referencing)"""
        geometry = data.get("geometry", {})
        
        # Required fields for coordinate system
        required_fields = ["type", "datum", "projection"]
        
        for field in required_fields:
            if field not in geometry:
                result.add_error(f"Missing required ISO 19111 field: {field}")
            elif not geometry[field]:
                result.add_warning(f"ISO 19111 field '{field}' is empty")
            else:
                result.add_info(f"ISO 19111 field '{field}' present: {geometry[field]}")
        
        # Validate projection
        if "projection" in geometry:
            projection = geometry["projection"]
            valid_projections = ["UTM", "Geographic", "Lambert", "Mercator", "Transverse Mercator"]
            if projection not in valid_projections:
                result.add_warning(f"Unknown projection type: {projection}")
        
        return result
    
    def _validate_iso_19157(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ISO 19157 (Data quality)"""
        quality = data.get("quality", {})
        
        # Quality elements
        quality_elements = [
            "completeness", "logical_consistency", "positional_accuracy",
            "temporal_accuracy", "thematic_accuracy"
        ]
        
        for element in quality_elements:
            if element in quality:
                value = quality[element]
                if not isinstance(value, (int, float)) or not (0 <= value <= 100):
                    result.add_error(f"Quality element '{element}' must be a percentage (0-100): {value}")
                else:
                    result.add_info(f"Quality element '{element}': {value}%")
        
        return result
    
    def _validate_iso_generic(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Generic ISO validation"""
        # Check for common ISO metadata fields
        common_fields = ["title", "abstract", "date", "organization", "standard_number"]
        metadata = data.get("metadata", {})
        
        for field in common_fields:
            if field not in metadata:
                result.add_warning(f"Missing common ISO field: {field}")
            else:
                result.add_info(f"ISO field '{field}' present")
        
        return result
    
    def _validate_en(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against EN standards"""
        # Eurocodes
        if standard.startswith("EN 199"):
            return self._validate_eurocode(data, standard, result)
        
        # Generic EN validation
        return self._validate_en_generic(data, standard, result)
    
    def _validate_eurocode(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against Eurocodes"""
        # Common Eurocode requirements
        design_data = data.get("design", {})
        
        # Check for safety factors
        if "safety_factors" in design_data:
            factors = design_data["safety_factors"]
            if not isinstance(factors, dict):
                result.add_error("Safety factors must be a dictionary")
            else:
                for material, factor in factors.items():
                    if not isinstance(factor, (int, float)) or factor <= 0:
                        result.add_error(f"Invalid safety factor for {material}: {factor}")
                    else:
                        result.add_info(f"Safety factor for {material}: {factor}")
        
        # Check for material properties
        if "material_properties" in design_data:
            properties = design_data["material_properties"]
            if not isinstance(properties, dict):
                result.add_error("Material properties must be a dictionary")
            else:
                for prop, value in properties.items():
                    if not isinstance(value, (int, float)):
                        result.add_warning(f"Invalid material property value for {prop}")
                    else:
                        result.add_info(f"Material property {prop}: {value}")
        
        return result
    
    def _validate_en_generic(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Generic EN validation"""
        # Check for common EN fields
        common_fields = ["standard_number", "publication_date", "scope", "title", "technical_committee"]
        metadata = data.get("metadata", {})
        
        for field in common_fields:
            if field not in metadata:
                result.add_warning(f"Missing common EN field: {field}")
            else:
                result.add_info(f"EN field '{field}' present")
        
        return result
    
    def _validate_din(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against DIN standards"""
        # DIN 1356: Building drawing standards
        if "1356" in standard:
            return self._validate_din_1356(data, standard, result)
        
        # DIN 276: Cost calculation
        if "276" in standard:
            return self._validate_din_276(data, standard, result)
        
        # DIN 277: Area calculation
        if "277" in standard:
            return self._validate_din_277(data, standard, result)
        
        # Generic DIN validation
        return self._validate_din_generic(data, standard, result)
    
    def _validate_din_1356(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against DIN 1356 (Building drawing)"""
        drawing_data = data.get("drawing", {})
        
        # Check drawing type
        valid_types = [
            "site_plan", "floor_plan", "elevation", "section",
            "detail", "assembly", "workshop", "as_built"
        ]
        
        if "drawing_type" in drawing_data:
            drawing_type = drawing_data["drawing_type"].lower()
            if drawing_type not in valid_types:
                result.add_warning(f"Unknown DIN 1356 drawing type: {drawing_data['drawing_type']}")
            else:
                result.add_info(f"DIN 1356 drawing type: {drawing_type}")
        
        # Check tolerances
        if "tolerances" in drawing_data:
            tolerances = drawing_data["tolerances"]
            if not isinstance(tolerances, dict):
                result.add_error("Tolerances must be a dictionary")
            else:
                if "class" in tolerances:
                    valid_classes = ["1", "2", "3", "4"]
                    if tolerances["class"] not in valid_classes:
                        result.add_warning(f"Unknown DIN 1356 tolerance class: {tolerances['class']}")
                    else:
                        result.add_info(f"DIN 1356 tolerance class: {tolerances['class']}")
        
        return result
    
    def _validate_din_276(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against DIN 276 (Costs in building construction)"""
        cost_data = data.get("costs", {})
        
        # DIN 276 cost groups
        cost_groups = ["100", "200", "300", "400", "500", "600", "700", "800"]
        
        if "cost_groups" in cost_data:
            for group in cost_data["cost_groups"]:
                group_id = str(group.get("id", ""))[:3]
                if group_id not in cost_groups:
                    result.add_warning(f"Unknown DIN 276 cost group: {group_id}")
                else:
                    result.add_info(f"DIN 276 cost group: {group_id}")
        
        return result
    
    def _validate_din_277(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against DIN 277 (Areas and volumes)"""
        area_data = data.get("areas", {})
        
        # DIN 277 area types
        area_types = [
            "gross_floor_area", "net_floor_area", "usable_area",
            "traffic_area", "functional_area", "technical_functional_area",
            "construction_area", "other_area"
        ]
        
        if "areas" in area_data:
            for area_type, value in area_data["areas"].items():
                if area_type.lower() not in area_types:
                    result.add_warning(f"Unknown DIN 277 area type: {area_type}")
                elif not isinstance(value, (int, float)) or value < 0:
                    result.add_error(f"Invalid DIN 277 area value for {area_type}: {value}")
                else:
                    result.add_info(f"DIN 277 area {area_type}: {value}")
        
        return result
    
    def _validate_din_generic(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Generic DIN validation"""
        # Check for common DIN fields
        common_fields = ["norm_number", "title", "validity", "publication_date", "issuing_body"]
        metadata = data.get("metadata", {})
        
        for field in common_fields:
            if field not in metadata:
                result.add_warning(f"Missing common DIN field: {field}")
            else:
                result.add_info(f"DIN field '{field}' present")
        
        return result
    
    def _validate_ansi(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ANSI standards"""
        # ANSI A14: Ladder safety
        if "A14" in standard or "a14" in standard.lower():
            return self._validate_ansi_a14(data, standard, result)
        
        # ANSI A117.1: Accessibility
        if "A117.1" in standard or "a117.1" in standard.lower():
            return self._validate_ansi_a117_1(data, standard, result)
        
        # ANSI Z1.1: Graphic symbols
        if "Z1.1" in standard or "z1.1" in standard.lower():
            return self._validate_ansi_z1_1(data, standard, result)
        
        # Generic ANSI validation
        return self._validate_ansi_generic(data, standard, result)
    
    def _validate_ansi_a14(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ANSI A14 (Ladder safety)"""
        safety_data = data.get("safety", {})
        
        # ANSI A14 load ratings
        valid_ratings = ["Type I", "Type IA", "Type II", "Type III"]
        
        if "load_ratings" in safety_data:
            ratings = safety_data["load_ratings"]
            if not isinstance(ratings, dict):
                result.add_error("Load ratings must be a dictionary")
            else:
                for rating, value in ratings.items():
                    if rating not in valid_ratings:
                        result.add_warning(f"Unknown ANSI A14 load rating: {rating}")
                    elif not isinstance(value, (int, float)) or value <= 0:
                        result.add_error(f"Invalid ANSI A14 load rating value for {rating}: {value}")
                    else:
                        result.add_info(f"ANSI A14 load rating {rating}: {value}")
        
        return result
    
    def _validate_ansi_a117_1(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ANSI A117.1 (Accessibility)"""
        accessibility_data = data.get("accessibility", {})
        
        # ANSI A117.1 requirements
        requirements = {
            "door_width": {"min": 32, "unit": "inches"},
            "hallway_width": {"min": 36, "unit": "inches"},
            "ramp_slope": {"max": 8.33, "unit": "percent"},
            "elevation_change": {"max": 0.5, "unit": "inches"}
        }
        
        for requirement, spec in requirements.items():
            if requirement in accessibility_data:
                value = accessibility_data[requirement]
                if "min" in spec and value < spec["min"]:
                    result.add_error(
                        f"{requirement} must be at least {spec['min']} {spec['unit']}: {value}"
                    )
                elif "max" in spec and value > spec["max"]:
                    result.add_error(
                        f"{requirement} must be at most {spec['max']} {spec['unit']}: {value}"
                    )
                else:
                    result.add_info(f"ANSI A117.1 {requirement}: {value} {spec['unit']}")
        
        return result
    
    def _validate_ansi_z1_1(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against ANSI Z1.1 (Graphic symbols)"""
        drawing_data = data.get("drawing", {})
        
        if "symbols" in drawing_data:
            symbols = drawing_data["symbols"]
            if not isinstance(symbols, list):
                result.add_error("Symbols must be a list")
            else:
                standard_symbols = [
                    "electrical", "plumbing", "HVAC", "structural",
                    "architectural", "fire_protection", "security"
                ]
                for symbol in symbols:
                    if "type" in symbol and symbol["type"].lower() not in standard_symbols:
                        result.add_warning(f"Unknown ANSI Z1.1 symbol type: {symbol['type']}")
                    else:
                        result.add_info(f"ANSI Z1.1 symbol type: {symbol.get('type', 'unknown')}")
        
        return result
    
    def _validate_ansi_generic(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Generic ANSI validation"""
        # Check for common ANSI fields
        common_fields = ["standard_id", "title", "publication_date", "description", "developer", "approver"]
        metadata = data.get("metadata", {})
        
        for field in common_fields:
            if field not in metadata:
                result.add_warning(f"Missing common ANSI field: {field}")
            else:
                result.add_info(f"ANSI field '{field}' present")
        
        return result
    
    def _validate_bsi(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against BSI standards"""
        # BS 1192: BIM standards
        if "1192" in standard:
            return self._validate_bsi_1192(data, standard, result)
        
        # BS 8541: Library objects
        if "8541" in standard:
            return self._validate_bsi_8541(data, standard, result)
        
        # Generic BSI validation
        return self._validate_bsi_generic(data, standard, result)
    
    def _validate_bsi_1192(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against BS 1192 (BIM)"""
        bim_data = data.get("bim", {})
        
        # Check for BIM Execution Plan
        if "bim_execution_plan" in bim_data:
            plan = bim_data["bim_execution_plan"]
            if not isinstance(plan, dict):
                result.add_error("BIM Execution Plan must be a dictionary")
            else:
                required_components = [
                    "project_information", "project_roles", "responsibilities",
                    "standards_methods_procedures", "information_requirements", "delivery_strategy"
                ]
                for component in required_components:
                    if component not in plan:
                        result.add_warning(f"Missing BIM Execution Plan component: {component}")
                    else:
                        result.add_info(f"BIM Execution Plan component '{component}' present")
        
        # Check for CDE
        if "cde" in bim_data:
            cde = bim_data["cde"]
            if not isinstance(cde, dict):
                result.add_error("CDE must be a dictionary")
            else:
                workflow_states = ["Work in Progress", "Shared", "Published", "Archive"]
                if "workflow_states" in cde:
                    for state in cde["workflow_states"]:
                        if state not in workflow_states:
                            result.add_warning(f"Unknown BS 1192 CDE workflow state: {state}")
                        else:
                            result.add_info(f"BS 1192 CDE workflow state: {state}")
        
        return result
    
    def _validate_bsi_8541(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Validate against BS 8541 (Library objects)"""
        library_data = data.get("library", {})
        
        if "objects" in library_data:
            objects = library_data["objects"]
            if not isinstance(objects, list):
                result.add_error("Library objects must be a list")
            else:
                result.add_info(f"BS 8541 library contains {len(objects)} objects")
        
        return result
    
    def _validate_bsi_generic(self, data: Dict[str, Any], standard: str, result: NormValidationResult) -> NormValidationResult:
        """Generic BSI validation"""
        # Check for common BSI fields
        common_fields = ["standard_ref", "title", "issue_date", "scope", "status", "publisher"]
        metadata = data.get("metadata", {})
        
        for field in common_fields:
            if field not in metadata:
                result.add_warning(f"Missing common BSI field: {field}")
            else:
                result.add_info(f"BSI field '{field}' present")
        
        return result
    
    def _generic_validation(self, data: Dict[str, Any], result: NormValidationResult) -> NormValidationResult:
        """Generic validation for unknown standards"""
        # Check for common metadata fields
        common_fields = ["title", "date", "author", "organization", "description"]
        metadata = data.get("metadata", {})
        
        for field in common_fields:
            if field not in metadata:
                result.add_warning(f"Missing common field: {field}")
            else:
                result.add_info(f"Field '{field}' present")
        
        return result
    
    @staticmethod
    def _is_valid_iso_date(date_str: str) -> bool:
        """Check if date string is in ISO 8601 format"""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$'
        return bool(re.match(pattern, date_str))
