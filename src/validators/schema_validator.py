"""
Schema Validator for Agent-Infra-V1.0.1

Validates data against JSON schemas and custom validation rules.
"""

import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import logging
import re


logger = logging.getLogger(__name__)


@dataclass
class SchemaValidationError:
    """Represents a schema validation error"""
    code: str
    message: str
    path: str = ""
    expected: Any = None
    actual: Any = None
    schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "expected": self.expected,
            "actual": self.actual,
            "schema": self.schema
        }


@dataclass
class SchemaValidationResult:
    """Result of schema validation"""
    valid: bool = True
    errors: List[SchemaValidationError] = field(default_factory=list)
    warnings: List[SchemaValidationError] = field(default_factory=list)
    info: List[SchemaValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(
        self,
        code: str,
        message: str,
        path: str = "",
        expected: Any = None,
        actual: Any = None,
        schema: Dict[str, Any] = None
    ):
        """Add a validation error"""
        self.valid = False
        self.errors.append(SchemaValidationError(code, message, path, expected, actual, schema or {}))
    
    def add_warning(
        self,
        code: str,
        message: str,
        path: str = "",
        expected: Any = None,
        actual: Any = None,
        schema: Dict[str, Any] = None
    ):
        """Add a validation warning"""
        self.warnings.append(SchemaValidationError(code, message, path, expected, actual, schema or {}))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "info": [i.to_dict() for i in self.info],
            "metadata": self.metadata
        }


class SchemaValidator:
    """
    Validator for JSON schemas and custom validation rules.
    
    Supports:
    - JSON Schema validation
    - Custom validation rules
    - Type checking
    - Format validation
    - Pattern matching
    """
    
    def __init__(self):
        """Initialize the schema validator"""
        self.custom_validators = {}
        self.format_validators = {
            "date": self._validate_date_format,
            "date-time": self._validate_datetime_format,
            "email": self._validate_email_format,
            "uri": self._validate_uri_format,
            "uuid": self._validate_uuid_format,
            "ipv4": self._validate_ipv4_format,
            "ipv6": self._validate_ipv6_format,
            "regex": self._validate_regex_format
        }
    
    def validate(self, data: Any, schema: Dict[str, Any], path: str = "") -> SchemaValidationResult:
        """
        Validate data against a JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema to validate against
            path: Current path in the data structure (for error reporting)
            
        Returns:
            SchemaValidationResult
        """
        result = SchemaValidationResult()
        
        try:
            self._validate_recursive(data, schema, path, result)
        except Exception as e:
            result.add_error("VALIDATION_ERROR", f"Validation failed: {str(e)}", path)
        
        return result
    
    def _validate_recursive(
        self,
        data: Any,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Recursively validate data against schema"""
        # Check type
        self._validate_type(data, schema, path, result)
        
        # If data is invalid type, don't continue with other validations
        if not self._is_valid_type(data, schema):
            return
        
        # Check enum
        if "enum" in schema:
            self._validate_enum(data, schema, path, result)
        
        # Check minimum/maximum for numbers
        if isinstance(data, (int, float)):
            self._validate_numeric_constraints(data, schema, path, result)
        
        # Check minLength/maxLength for strings
        if isinstance(data, str):
            self._validate_string_constraints(data, schema, path, result)
        
        # Check minItems/maxItems for arrays
        if isinstance(data, list):
            self._validate_array_constraints(data, schema, path, result)
        
        # Check minProperties/maxProperties for objects
        if isinstance(data, dict):
            self._validate_object_constraints(data, schema, path, result)
        
        # Check pattern
        if "pattern" in schema and isinstance(data, str):
            self._validate_pattern(data, schema, path, result)
        
        # Check format
        if "format" in schema and isinstance(data, str):
            self._validate_format(data, schema, path, result)
        
        # Check required properties
        if isinstance(data, dict) and "required" in schema:
            self._validate_required_properties(data, schema, path, result)
        
        # Check additionalProperties
        if isinstance(data, dict) and "additionalProperties" in schema:
            self._validate_additional_properties(data, schema, path, result)
        
        # Check items schema for arrays
        if isinstance(data, list) and "items" in schema:
            self._validate_array_items(data, schema, path, result)
        
        # Check properties schema for objects
        if isinstance(data, dict) and "properties" in schema:
            self._validate_object_properties(data, schema, path, result)
        
        # Check allOf, anyOf, oneOf
        if "allOf" in schema:
            self._validate_all_of(data, schema, path, result)
        if "anyOf" in schema:
            self._validate_any_of(data, schema, path, result)
        if "oneOf" in schema:
            self._validate_one_of(data, schema, path, result)
        
        # Check custom validators
        if "x-validator" in schema:
            self._validate_custom(data, schema, path, result)
    
    def _validate_type(self, data: Any, schema: Dict[str, Any], path: str, result: SchemaValidationResult):
        """Validate data type"""
        if "type" not in schema:
            return
        
        expected_type = schema["type"]
        if isinstance(expected_type, list):
            # Multiple allowed types
            valid = any(self._check_type(data, t) for t in expected_type)
            if not valid:
                result.add_error(
                    "TYPE_ERROR",
                    f"Expected one of {expected_type}, got {type(data).__name__}",
                    path,
                    expected=expected_type,
                    actual=type(data).__name__
                )
        else:
            # Single expected type
            if not self._check_type(data, expected_type):
                result.add_error(
                    "TYPE_ERROR",
                    f"Expected {expected_type}, got {type(data).__name__}",
                    path,
                    expected=expected_type,
                    actual=type(data).__name__
                )
    
    def _check_type(self, data: Any, expected_type: str) -> bool:
        """Check if data matches expected type"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        if expected_type not in type_mapping:
            return True  # Unknown type, skip validation
        
        expected = type_mapping[expected_type]
        return isinstance(data, expected)
    
    def _is_valid_type(self, data: Any, schema: Dict[str, Any]) -> bool:
        """Check if data type is valid according to schema"""
        if "type" not in schema:
            return True
        
        expected_type = schema["type"]
        if isinstance(expected_type, list):
            return any(self._check_type(data, t) for t in expected_type)
        return self._check_type(data, expected_type)
    
    def _validate_enum(self, data: Any, schema: Dict[str, Any], path: str, result: SchemaValidationResult):
        """Validate enum constraint"""
        allowed_values = schema["enum"]
        if data not in allowed_values:
            result.add_error(
                "ENUM_ERROR",
                f"Value {data} is not one of {allowed_values}",
                path,
                expected=allowed_values,
                actual=data
            )
    
    def _validate_numeric_constraints(
        self,
        data: Union[int, float],
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate numeric constraints"""
        if "minimum" in schema and data < schema["minimum"]:
            result.add_error(
                "MINIMUM_ERROR",
                f"Value {data} is less than minimum {schema['minimum']}",
                path,
                expected=f">= {schema['minimum']}",
                actual=data
            )
        
        if "maximum" in schema and data > schema["maximum"]:
            result.add_error(
                "MAXIMUM_ERROR",
                f"Value {data} is greater than maximum {schema['maximum']}",
                path,
                expected=f"<= {schema['maximum']}",
                actual=data
            )
        
        if "exclusiveMinimum" in schema and data <= schema["exclusiveMinimum"]:
            result.add_error(
                "EXCLUSIVE_MINIMUM_ERROR",
                f"Value {data} is less than or equal to exclusive minimum {schema['exclusiveMinimum']}",
                path,
                expected=f"> {schema['exclusiveMinimum']}",
                actual=data
            )
        
        if "exclusiveMaximum" in schema and data >= schema["exclusiveMaximum"]:
            result.add_error(
                "EXCLUSIVE_MAXIMUM_ERROR",
                f"Value {data} is greater than or equal to exclusive maximum {schema['exclusiveMaximum']}",
                path,
                expected=f"< {schema['exclusiveMaximum']}",
                actual=data
            )
        
        if "multipleOf" in schema:
            divisor = schema["multipleOf"]
            if divisor != 0 and data % divisor != 0:
                result.add_error(
                    "MULTIPLE_OF_ERROR",
                    f"Value {data} is not a multiple of {divisor}",
                    path,
                    expected=f"multiple of {divisor}",
                    actual=data
                )
    
    def _validate_string_constraints(
        self,
        data: str,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate string constraints"""
        if "minLength" in schema and len(data) < schema["minLength"]:
            result.add_error(
                "MIN_LENGTH_ERROR",
                f"String length {len(data)} is less than minimum {schema['minLength']}",
                path,
                expected=f"length >= {schema['minLength']}",
                actual=len(data)
            )
        
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            result.add_error(
                "MAX_LENGTH_ERROR",
                f"String length {len(data)} is greater than maximum {schema['maxLength']}",
                path,
                expected=f"length <= {schema['maxLength']}",
                actual=len(data)
            )
    
    def _validate_array_constraints(
        self,
        data: list,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate array constraints"""
        if "minItems" in schema and len(data) < schema["minItems"]:
            result.add_error(
                "MIN_ITEMS_ERROR",
                f"Array has {len(data)} items, minimum is {schema['minItems']}",
                path,
                expected=f"length >= {schema['minItems']}",
                actual=len(data)
            )
        
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            result.add_error(
                "MAX_ITEMS_ERROR",
                f"Array has {len(data)} items, maximum is {schema['maxItems']}",
                path,
                expected=f"length <= {schema['maxItems']}",
                actual=len(data)
            )
        
        if "uniqueItems" in schema and schema["uniqueItems"]:
            if len(data) != len(set(data)):
                result.add_error(
                    "UNIQUE_ITEMS_ERROR",
                    f"Array contains duplicate items",
                    path
                )
    
    def _validate_object_constraints(
        self,
        data: dict,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate object constraints"""
        if "minProperties" in schema and len(data) < schema["minProperties"]:
            result.add_error(
                "MIN_PROPERTIES_ERROR",
                f"Object has {len(data)} properties, minimum is {schema['minProperties']}",
                path,
                expected=f"properties >= {schema['minProperties']}",
                actual=len(data)
            )
        
        if "maxProperties" in schema and len(data) > schema["maxProperties"]:
            result.add_error(
                "MAX_PROPERTIES_ERROR",
                f"Object has {len(data)} properties, maximum is {schema['maxProperties']}",
                path,
                expected=f"properties <= {schema['maxProperties']}",
                actual=len(data)
            )
    
    def _validate_pattern(
        self,
        data: str,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate pattern constraint"""
        pattern = schema["pattern"]
        if not re.match(pattern, data):
            result.add_error(
                "PATTERN_ERROR",
                f"String does not match pattern: {pattern}",
                path,
                expected=f"matches {pattern}",
                actual=data
            )
    
    def _validate_format(
        self,
        data: str,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate format constraint"""
        fmt = schema["format"]
        validator = self.format_validators.get(fmt)
        
        if validator:
            if not validator(data):
                result.add_error(
                    "FORMAT_ERROR",
                    f"String does not match format: {fmt}",
                    path,
                    expected=fmt,
                    actual=data
                )
        else:
            logger.warning(f"Unknown format: {fmt}")
    
    def _validate_required_properties(
        self,
        data: dict,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate required properties"""
        required = schema["required"]
        for prop in required:
            if prop not in data:
                result.add_error(
                    "MISSING_PROPERTY",
                    f"Missing required property: {prop}",
                    f"{path}.{prop}" if path else prop
                )
    
    def _validate_additional_properties(
        self,
        data: dict,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate additional properties"""
        additional_properties = schema["additionalProperties"]
        
        if additional_properties is False:
            # No additional properties allowed
            allowed_properties = set(schema.get("properties", {}).keys())
            for prop in data:
                if prop not in allowed_properties:
                    result.add_error(
                        "ADDITIONAL_PROPERTY",
                        f"Additional property not allowed: {prop}",
                        f"{path}.{prop}" if path else prop
                    )
        elif isinstance(additional_properties, dict):
            # Additional properties must match schema
            for prop, value in data.items():
                if prop not in schema.get("properties", {}):
                    self._validate_recursive(value, additional_properties, f"{path}.{prop}" if path else prop, result)
    
    def _validate_array_items(
        self,
        data: list,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate array items"""
        items_schema = schema["items"]
        
        if isinstance(items_schema, dict):
            # All items must match the schema
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]"
                self._validate_recursive(item, items_schema, item_path, result)
        elif isinstance(items_schema, list):
            # Tuple validation - each position has its own schema
            for i, item in enumerate(data):
                if i < len(items_schema):
                    item_path = f"{path}[{i}]"
                    self._validate_recursive(item, items_schema[i], item_path, result)
    
    def _validate_object_properties(
        self,
        data: dict,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate object properties"""
        properties_schema = schema["properties"]
        
        for prop, prop_schema in properties_schema.items():
            if prop in data:
                prop_path = f"{path}.{prop}" if path else prop
                self._validate_recursive(data[prop], prop_schema, prop_path, result)
    
    def _validate_all_of(
        self,
        data: Any,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate allOf constraint"""
        all_of = schema["allOf"]
        for subschema in all_of:
            self._validate_recursive(data, subschema, path, result)
    
    def _validate_any_of(
        self,
        data: Any,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate anyOf constraint"""
        any_of = schema["anyOf"]
        matches = 0
        
        for subschema in any_of:
            sub_result = SchemaValidationResult()
            self._validate_recursive(data, subschema, path, sub_result)
            if sub_result.valid:
                matches += 1
        
        if matches == 0:
            result.add_error(
                "ANY_OF_ERROR",
                f"Data does not match any of the {len(any_of)} schemas",
                path
            )
    
    def _validate_one_of(
        self,
        data: Any,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate oneOf constraint"""
        one_of = schema["oneOf"]
        matches = 0
        
        for subschema in one_of:
            sub_result = SchemaValidationResult()
            self._validate_recursive(data, subschema, path, sub_result)
            if sub_result.valid:
                matches += 1
        
        if matches != 1:
            result.add_error(
                "ONE_OF_ERROR",
                f"Data matches {matches} of the {len(one_of)} schemas, expected exactly 1",
                path
            )
    
    def _validate_custom(
        self,
        data: Any,
        schema: Dict[str, Any],
        path: str,
        result: SchemaValidationResult
    ):
        """Validate using custom validator"""
        validator_name = schema["x-validator"]
        validator_func = self.custom_validators.get(validator_name)
        
        if validator_func:
            try:
                is_valid, error_msg = validator_func(data, schema, path)
                if not is_valid:
                    result.add_error("CUSTOM_VALIDATION_ERROR", error_msg, path)
            except Exception as e:
                result.add_error("CUSTOM_VALIDATION_ERROR", f"Custom validator error: {str(e)}", path)
        else:
            logger.warning(f"Unknown custom validator: {validator_name}")
    
    def add_custom_validator(self, name: str, validator_func):
        """
        Add a custom validator function.
        
        Args:
            name: Name of the validator
            validator_func: Function that takes (data, schema, path) and returns (is_valid, error_msg)
        """
        self.custom_validators[name] = validator_func
    
    def add_format_validator(self, name: str, validator_func):
        """
        Add a custom format validator.
        
        Args:
            name: Name of the format
            validator_func: Function that takes (data) and returns bool
        """
        self.format_validators[name] = validator_func
    
    @staticmethod
    def _validate_date_format(data: str) -> bool:
        """Validate date format (YYYY-MM-DD)"""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, data))
    
    @staticmethod
    def _validate_datetime_format(data: str) -> bool:
        """Validate date-time format (ISO 8601)"""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$'
        return bool(re.match(pattern, data))
    
    @staticmethod
    def _validate_email_format(data: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, data))
    
    @staticmethod
    def _validate_uri_format(data: str) -> bool:
        """Validate URI format"""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, data))
    
    @staticmethod
    def _validate_uuid_format(data: str) -> bool:
        """Validate UUID format"""
        import re
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, data.lower()))
    
    @staticmethod
    def _validate_ipv4_format(data: str) -> bool:
        """Validate IPv4 format"""
        import re
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, data))
    
    @staticmethod
    def _validate_ipv6_format(data: str) -> bool:
        """Validate IPv6 format"""
        import re
        pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        return bool(re.match(pattern, data))
    
    @staticmethod
    def _validate_regex_format(data: str) -> bool:
        """Validate regex pattern format"""
        try:
            re.compile(data)
            return True
        except re.error:
            return False


# Global schema validator instance
schema_validator = SchemaValidator()
