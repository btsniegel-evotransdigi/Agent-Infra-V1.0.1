"""
Helper utilities for Agent-Infra-V1.0.1
"""

import re
import math
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Tuple, Union
import logging


logger = logging.getLogger(__name__)


def validate_metadata(metadata: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate metadata against required fields.
    
    Args:
        metadata: Dictionary containing metadata
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
        elif metadata[field] is None:
            errors.append(f"Field '{field}' is None")
        elif isinstance(metadata[field], str) and not metadata[field].strip():
            errors.append(f"Field '{field}' is empty")
    
    return len(errors) == 0, errors


def normalize_string(text: str) -> str:
    """
    Normalize a string by trimming, converting to lowercase, and removing extra whitespace.
    
    Args:
        text: Input string
        
    Returns:
        Normalized string
    """
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Normalize whitespace and trim
    text = ' '.join(text.split())
    
    return text.strip()


def parse_date(date_str: str, formats: Optional[List[str]] = None) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: Date string to parse
        formats: List of date formats to try (optional)
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Default formats to try
    if formats is None:
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d",
            "%Y/%m/%d %H:%M:%S",
            "%d.%m.%Y",
            "%d.%m.%Y %H:%M:%S",
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%B %d, %Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try ISO 8601 format
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    
    logger.warning(f"Could not parse date: {date_str}")
    return None


def format_date(dt: Union[datetime, date], fmt: str = "%Y-%m-%d") -> str:
    """
    Format a date/datetime object into a string.
    
    Args:
        dt: Date or datetime object
        fmt: Format string (default: YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    if dt is None:
        return ""
    
    if isinstance(dt, date) and not isinstance(dt, datetime):
        # Convert date to datetime for consistent formatting
        dt = datetime(dt.year, dt.month, dt.day)
    
    return dt.strftime(fmt)


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a value from one unit to another.
    
    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Converted value
        
    Raises:
        ValueError: If unit conversion is not supported
    """
    # Define conversion factors
    # Length conversions
    length_conversions = {
        "m": 1.0,  # meters
        "mm": 0.001,  # millimeters
        "cm": 0.01,  # centimeters
        "km": 1000.0,  # kilometers
        "in": 0.0254,  # inches
        "ft": 0.3048,  # feet
        "yd": 0.9144,  # yards
        "mi": 1609.344,  # miles
    }
    
    # Area conversions (square meters)
    area_conversions = {
        "m2": 1.0,
        "mm2": 1e-6,
        "cm2": 1e-4,
        "km2": 1e6,
        "in2": 0.00064516,
        "ft2": 0.092903,
        "yd2": 0.836127,
        "ac": 4046.86,  # acres
        "ha": 10000.0,  # hectares
    }
    
    # Volume conversions (cubic meters)
    volume_conversions = {
        "m3": 1.0,
        "mm3": 1e-9,
        "cm3": 1e-6,
        "km3": 1e9,
        "in3": 1.63871e-5,
        "ft3": 0.0283168,
        "yd3": 0.764555,
        "L": 0.001,  # liters
        "gal": 0.00378541,  # US gallons
    }
    
    # Determine conversion type based on units
    if from_unit in length_conversions and to_unit in length_conversions:
        # Length conversion
        from_factor = length_conversions[from_unit]
        to_factor = length_conversions[to_unit]
        return value * (from_factor / to_factor)
    
    elif from_unit in area_conversions and to_unit in area_conversions:
        # Area conversion
        from_factor = area_conversions[from_unit]
        to_factor = area_conversions[to_unit]
        return value * (from_factor / to_factor)
    
    elif from_unit in volume_conversions and to_unit in volume_conversions:
        # Volume conversion
        from_factor = volume_conversions[from_unit]
        to_factor = volume_conversions[to_unit]
        return value * (from_factor / to_factor)
    
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")


def calculate_distance(
    x1: float, y1: float, x2: float, y2: float, 
    z1: Optional[float] = None, z2: Optional[float] = None
) -> float:
    """
    Calculate distance between two points in 2D or 3D space.
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        z1, z2: Optional Z coordinates for 3D distance
        
    Returns:
        Distance between the points
    """
    dx = x2 - x1
    dy = y2 - y1
    
    if z1 is not None and z2 is not None:
        dz = z2 - z1
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    return math.sqrt(dx**2 + dy**2)


def validate_coordinates(
    coordinates: List[Tuple[float, float]],
    min_x: Optional[float] = None,
    max_x: Optional[float] = None,
    min_y: Optional[float] = None,
    max_y: Optional[float] = None
) -> Tuple[bool, List[str]]:
    """
    Validate a list of coordinates.
    
    Args:
        coordinates: List of (x, y) coordinate tuples
        min_x, max_x, min_y, max_y: Optional bounds
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not coordinates:
        errors.append("No coordinates provided")
        return False, errors
    
    for i, (x, y) in enumerate(coordinates):
        # Check for NaN or infinity
        if math.isnan(x) or math.isinf(x):
            errors.append(f"Invalid X coordinate at index {i}: {x}")
        if math.isnan(y) or math.isinf(y):
            errors.append(f"Invalid Y coordinate at index {i}: {y}")
        
        # Check bounds
        if min_x is not None and x < min_x:
            errors.append(f"X coordinate {x} at index {i} is below minimum {min_x}")
        if max_x is not None and x > max_x:
            errors.append(f"X coordinate {x} at index {i} is above maximum {max_x}")
        if min_y is not None and y < min_y:
            errors.append(f"Y coordinate {y} at index {i} is below minimum {min_y}")
        if max_y is not None and y > max_y:
            errors.append(f"Y coordinate {y} at index {i} is above maximum {max_y}")
    
    return len(errors) == 0, errors


def validate_projection(projection: str, valid_projections: List[str]) -> Tuple[bool, str]:
    """
    Validate a projection against a list of valid projections.
    
    Args:
        projection: Projection to validate
        valid_projections: List of valid projection names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not projection:
        return False, "Projection is empty"
    
    if projection.upper() not in [p.upper() for p in valid_projections]:
        return False, f"Invalid projection: {projection}. Valid projections: {', '.join(valid_projections)}"
    
    return True, ""


def validate_scale(scale: str) -> Tuple[bool, str]:
    """
    Validate a drawing scale.
    
    Args:
        scale: Scale string (e.g., "1:100", "1/100", "1:1000")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not scale:
        return False, "Scale is empty"
    
    # Common scale formats
    patterns = [
        r'^1:\d+$',  # 1:100
        r'^1/\d+$',  # 1/100
        r'^\d+:\d+$'  # 1:100 or 100:1
    ]
    
    for pattern in patterns:
        if re.match(pattern, scale):
            return True, ""
    
    return False, f"Invalid scale format: {scale}"


def extract_scale_factor(scale: str) -> Optional[float]:
    """
    Extract the scale factor from a scale string.
    
    Args:
        scale: Scale string (e.g., "1:100", "1/100")
        
    Returns:
        Scale factor (e.g., 0.01 for 1:100) or None if invalid
    """
    valid, error = validate_scale(scale)
    if not valid:
        return None
    
    # Handle 1:100 format
    if ':' in scale:
        parts = scale.split(':')
        if len(parts) == 2:
            try:
                numerator = float(parts[0])
                denominator = float(parts[1])
                return numerator / denominator
            except ValueError:
                return None
    
    # Handle 1/100 format
    if '/' in scale:
        parts = scale.split('/')
        if len(parts) == 2:
            try:
                numerator = float(parts[0])
                denominator = float(parts[1])
                return numerator / denominator
            except ValueError:
                return None
    
    return None


def check_required_attributes(
    data: Dict[str, Any],
    required_attrs: List[str]
) -> Tuple[bool, List[str]]:
    """
    Check if required attributes are present in data.
    
    Args:
        data: Dictionary to check
        required_attrs: List of required attribute names
        
    Returns:
        Tuple of (all_present, list_of_missing)
    """
    missing = []
    
    for attr in required_attrs:
        if attr not in data:
            missing.append(attr)
    
    return len(missing) == 0, missing


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Deep merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result
