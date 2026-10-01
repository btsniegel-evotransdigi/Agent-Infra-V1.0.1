"""
Drawing Validator for Agent-Infra-V1.0.1

Validates drawing files against various standards and requirements.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error"""
    code: str
    message: str
    severity: str = "error"  # error, warning, info
    path: str = ""
    expected: Any = None
    actual: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "path": self.path,
            "expected": self.expected,
            "actual": self.actual
        }


@dataclass
class DrawingValidationResult:
    """Result of drawing validation"""
    valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, code: str, message: str, path: str = "", expected: Any = None, actual: Any = None):
        """Add a validation error"""
        self.valid = False
        self.errors.append(ValidationError(code, message, "error", path, expected, actual))
    
    def add_warning(self, code: str, message: str, path: str = "", expected: Any = None, actual: Any = None):
        """Add a validation warning"""
        self.warnings.append(ValidationError(code, message, "warning", path, expected, actual))
    
    def add_info(self, code: str, message: str, path: str = "", expected: Any = None, actual: Any = None):
        """Add a validation info"""
        self.info.append(ValidationError(code, message, "info", path, expected, actual))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "info": [i.to_dict() for i in self.info],
            "metadata": self.metadata
        }
    
    def merge(self, other: 'DrawingValidationResult'):
        """Merge another result into this one"""
        self.valid = self.valid and other.valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        self.metadata.update(other.metadata)


class DrawingValidator:
    """
    Validator for drawing files.
    
    Validates drawing files against:
    - File format and structure
    - Metadata requirements
    - Layer requirements
    - Attribute requirements
    - Geometric requirements
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the drawing validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.required_layers = self.config.get("required_layers", [])
        self.required_attributes = self.config.get("required_attributes", [])
        self.required_metadata = self.config.get("required_metadata", [])
    
    def validate(self, drawing_data: Dict[str, Any]) -> DrawingValidationResult:
        """
        Validate drawing data.
        
        Args:
            drawing_data: Dictionary containing drawing data
            
        Returns:
            DrawingValidationResult
        """
        result = DrawingValidationResult()
        
        # Validate metadata
        self._validate_metadata(drawing_data, result)
        
        # Validate layers
        self._validate_layers(drawing_data, result)
        
        # Validate attributes
        self._validate_attributes(drawing_data, result)
        
        # Validate geometry
        self._validate_geometry(drawing_data, result)
        
        return result
    
    def _validate_metadata(self, data: Dict[str, Any], result: DrawingValidationResult):
        """Validate drawing metadata"""
        metadata = data.get("metadata", {})
        
        for field in self.required_metadata:
            if field not in metadata:
                result.add_error(
                    "MISSING_METADATA",
                    f"Missing required metadata field: {field}",
                    "metadata"
                )
            elif not metadata[field]:
                result.add_warning(
                    "EMPTY_METADATA",
                    f"Metadata field '{field}' is empty",
                    "metadata"
                )
        
        # Check for common metadata fields
        common_fields = ["title", "author", "date", "scale", "units"]
        for field in common_fields:
            if field in metadata:
                result.add_info(
                    "METADATA_PRESENT",
                    f"Metadata field '{field}' present",
                    "metadata"
                )
    
    def _validate_layers(self, data: Dict[str, Any], result: DrawingValidationResult):
        """Validate drawing layers"""
        layers = data.get("layers", [])
        
        if not layers:
            result.add_warning("NO_LAYERS", "No layers found in drawing")
            return
        
        # Check for required layers
        present_layers = [layer.get("name", "").upper() for layer in layers]
        
        for required_layer in self.required_layers:
            if required_layer not in present_layers:
                result.add_error(
                    "MISSING_LAYER",
                    f"Missing required layer: {required_layer}",
                    "layers"
                )
            else:
                result.add_info(
                    "LAYER_PRESENT",
                    f"Required layer '{required_layer}' present",
                    "layers"
                )
        
        # Validate layer properties
        for layer in layers:
            self._validate_layer(layer, result)
    
    def _validate_layer(self, layer: Dict[str, Any], result: DrawingValidationResult):
        """Validate a single layer"""
        if "name" not in layer:
            result.add_error("MISSING_LAYER_NAME", "Layer missing name property", "layers")
            return
        
        # Check for common layer properties
        layer_name = layer.get("name", "")
        
        if not layer_name:
            result.add_error("EMPTY_LAYER_NAME", "Layer name is empty", "layers")
        
        # Check for valid layer properties
        valid_properties = ["name", "description", "color", "line_type", "line_weight", "visible", "freeze", "lock"]
        for prop in layer:
            if prop not in valid_properties:
                result.add_warning(
                    "UNKNOWN_LAYER_PROPERTY",
                    f"Unknown layer property: {prop}",
                    f"layers.{layer_name}"
                )
    
    def _validate_attributes(self, data: Dict[str, Any], result: DrawingValidationResult):
        """Validate drawing attributes"""
        attributes = data.get("attributes", {})
        
        for attr in self.required_attributes:
            if attr not in attributes:
                result.add_error(
                    "MISSING_ATTRIBUTE",
                    f"Missing required attribute: {attr}",
                    "attributes"
                )
            elif not attributes[attr]:
                result.add_warning(
                    "EMPTY_ATTRIBUTE",
                    f"Attribute '{attr}' is empty",
                    "attributes"
                )
        
        # Check for common attributes
        common_attrs = ["scale", "coordinate_system", "projection", "units", "precision"]
        for attr in common_attrs:
            if attr in attributes:
                result.add_info(
                    "ATTRIBUTE_PRESENT",
                    f"Attribute '{attr}' present",
                    "attributes"
                )
    
    def _validate_geometry(self, data: Dict[str, Any], result: DrawingValidationResult):
        """Validate geometric properties"""
        geometry = data.get("geometry", {})
        
        if not geometry:
            result.add_warning("NO_GEOMETRY", "No geometry data found")
            return
        
        # Check coordinate system
        if "coordinate_system" in geometry:
            coord_system = geometry["coordinate_system"]
            if not coord_system:
                result.add_error(
                    "MISSING_COORDINATE_SYSTEM",
                    "Coordinate system not specified",
                    "geometry.coordinate_system"
                )
            else:
                result.add_info(
                    "COORDINATE_SYSTEM_PRESENT",
                    f"Coordinate system: {coord_system}",
                    "geometry.coordinate_system"
                )
        
        # Check projection
        if "projection" in geometry:
            projection = geometry["projection"]
            if not projection:
                result.add_error(
                    "MISSING_PROJECTION",
                    "Projection not specified",
                    "geometry.projection"
                )
            else:
                result.add_info(
                    "PROJECTION_PRESENT",
                    f"Projection: {projection}",
                    "geometry.projection"
                )
        
        # Check units
        if "units" in geometry:
            units = geometry["units"]
            if not units:
                result.add_warning(
                    "MISSING_UNITS",
                    "Units not specified",
                    "geometry.units"
                )
            else:
                result.add_info(
                    "UNITS_PRESENT",
                    f"Units: {units}",
                    "geometry.units"
                )


class LayerValidator:
    """Validator for CAD layers"""
    
    def __init__(self, naming_conventions: Optional[Dict[str, Any]] = None):
        """
        Initialize the layer validator.
        
        Args:
            naming_conventions: Dictionary with layer naming conventions
        """
        self.naming_conventions = naming_conventions or {}
        self.prefix = self.naming_conventions.get("prefix", "")
        self.separator = self.naming_conventions.get("separator", "_")
        self.max_length = self.naming_conventions.get("max_length", 100)
        self.allowed_chars = self.naming_conventions.get("allowed_characters", r"[A-Za-z0-9_\-\.]")
    
    def validate_layer_name(self, name: str) -> Tuple[bool, List[str]]:
        """
        Validate a layer name.
        
        Args:
            name: Layer name to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not name:
            errors.append("Layer name is empty")
            return False, errors
        
        # Check prefix
        if self.prefix and not name.startswith(self.prefix):
            errors.append(f"Layer name must start with '{self.prefix}': {name}")
        
        # Check length
        if len(name) > self.max_length:
            errors.append(f"Layer name exceeds maximum length of {self.max_length}: {name}")
        
        # Check allowed characters
        import re
        if not re.match(f"^{self.allowed_chars}+$", name):
            errors.append(f"Layer name contains invalid characters: {name}")
        
        # Check for separator consistency
        if self.separator and self.separator in name:
            parts = name.split(self.separator)
            if any(not part for part in parts):
                errors.append(f"Layer name has empty parts when split by '{self.separator}': {name}")
        
        return len(errors) == 0, errors
    
    def validate_layer(self, layer: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a layer definition.
        
        Args:
            layer: Dictionary with layer definition
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if "name" not in layer:
            errors.append("Layer missing 'name' property")
            return False, errors
        
        name = layer["name"]
        name_valid, name_errors = self.validate_layer_name(name)
        if not name_valid:
            errors.extend(name_errors)
        
        # Check for required layer properties
        required_props = ["color", "line_type", "visible"]
        for prop in required_props:
            if prop not in layer:
                errors.append(f"Layer missing required property: {prop}")
        
        return len(errors) == 0, errors


class AttributeValidator:
    """Validator for drawing attributes"""
    
    def __init__(self, required_attrs: Optional[List[str]] = None):
        """
        Initialize the attribute validator.
        
        Args:
            required_attrs: List of required attribute names
        """
        self.required_attrs = required_attrs or []
    
    def validate(self, attributes: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate drawing attributes.
        
        Args:
            attributes: Dictionary with drawing attributes
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for attr in self.required_attrs:
            if attr not in attributes:
                errors.append(f"Missing required attribute: {attr}")
            elif not attributes[attr]:
                errors.append(f"Attribute '{attr}' is empty")
        
        return len(errors) == 0, errors
    
    def validate_scale(self, scale: str) -> Tuple[bool, str]:
        """
        Validate a scale value.
        
        Args:
            scale: Scale string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not scale:
            return False, "Scale is empty"
        
        # Common scale formats
        import re
        patterns = [
            r'^1:\d+$',  # 1:100
            r'^1/\d+$',  # 1/100
            r'^\d+:\d+$'  # 1:100 or 100:1
        ]
        
        for pattern in patterns:
            if re.match(pattern, scale):
                return True, ""
        
        return False, f"Invalid scale format: {scale}"
    
    def validate_coordinate_system(self, coord_system: str) -> Tuple[bool, str]:
        """
        Validate a coordinate system.
        
        Args:
            coord_system: Coordinate system string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not coord_system:
            return False, "Coordinate system is empty"
        
        # Common coordinate systems
        valid_systems = [
            "WGS84", "ETRS89", "DHDN", "NAD83", "NAD27",
            "UTM Zone 32N", "UTM Zone 33N", "UTM Zone 34N",
            "UTM Zone 32S", "UTM Zone 33S", "UTM Zone 34S"
        ]
        
        if coord_system not in valid_systems:
            return False, f"Unknown coordinate system: {coord_system}"
        
        return True, ""
