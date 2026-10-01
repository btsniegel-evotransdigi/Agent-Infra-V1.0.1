"""
Tests for Validators
"""

import unittest
from agents.international_standards.agent import ValidationResult
from src.validators.drawing_validator import (
    DrawingValidator,
    DrawingValidationResult,
    LayerValidator,
    AttributeValidator
)
from src.validators.norm_validator import NormValidator, NormValidationResult
from src.validators.schema_validator import SchemaValidator, SchemaValidationResult


class TestDrawingValidator(unittest.TestCase):
    """Test cases for DrawingValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "required_layers": ["ARCHITECTURE", "STRUCTURE"],
            "required_attributes": ["scale", "units"],
            "required_metadata": ["title", "author", "date"]
        }
        self.validator = DrawingValidator(self.config)
    
    def test_validate_with_valid_data(self):
        """Test validation with valid data"""
        data = {
            "metadata": {
                "title": "Test Drawing",
                "author": "John Doe",
                "date": "2024-01-01"
            },
            "layers": [
                {"name": "ARCHITECTURE"},
                {"name": "STRUCTURE"}
            ],
            "attributes": {
                "scale": "1:100",
                "units": "meters"
            }
        }
        
        result = self.validator.validate(data)
        self.assertTrue(result.valid)
    
    def test_validate_with_missing_metadata(self):
        """Test validation with missing metadata"""
        data = {
            "metadata": {
                "title": "Test Drawing"
                # Missing author and date
            },
            "layers": [
                {"name": "ARCHITECTURE"},
                {"name": "STRUCTURE"}
            ],
            "attributes": {
                "scale": "1:100",
                "units": "meters"
            }
        }
        
        result = self.validator.validate(data)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_with_missing_layers(self):
        """Test validation with missing layers"""
        data = {
            "metadata": {
                "title": "Test Drawing",
                "author": "John Doe",
                "date": "2024-01-01"
            },
            "layers": [
                {"name": "ARCHITECTURE"}
                # Missing STRUCTURE layer
            ],
            "attributes": {
                "scale": "1:100",
                "units": "meters"
            }
        }
        
        result = self.validator.validate(data)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_with_missing_attributes(self):
        """Test validation with missing attributes"""
        data = {
            "metadata": {
                "title": "Test Drawing",
                "author": "John Doe",
                "date": "2024-01-01"
            },
            "layers": [
                {"name": "ARCHITECTURE"},
                {"name": "STRUCTURE"}
            ],
            "attributes": {
                "scale": "1:100"
                # Missing units
            }
        }
        
        result = self.validator.validate(data)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_with_empty_data(self):
        """Test validation with empty data"""
        data = {}
        result = self.validator.validate(data)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)


class TestLayerValidator(unittest.TestCase):
    """Test cases for LayerValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.naming_conventions = {
            "prefix": "EVTD_",
            "separator": "_",
            "max_length": 50,
            "allowed_characters": r"[A-Za-z0-9_\-\.]"
        }
        self.validator = LayerValidator(self.naming_conventions)
    
    def test_validate_layer_name_valid(self):
        """Test validation of valid layer name"""
        valid, errors = self.validator.validate_layer_name("EVTD_INFRASTRUCTURE_ROADS")
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_layer_name_missing_prefix(self):
        """Test validation of layer name without prefix"""
        valid, errors = self.validator.validate_layer_name("INFRASTRUCTURE_ROADS")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_layer_name_too_long(self):
        """Test validation of layer name that is too long"""
        long_name = "EVTD_" + "A" * 60
        valid, errors = self.validator.validate_layer_name(long_name)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_layer_name_invalid_characters(self):
        """Test validation of layer name with invalid characters"""
        valid, errors = self.validator.validate_layer_name("EVTD_LAYER@NAME")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_layer_empty_name(self):
        """Test validation of empty layer name"""
        valid, errors = self.validator.validate_layer_name("")
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_layer_with_all_properties(self):
        """Test validation of layer with all properties"""
        layer = {
            "name": "EVTD_INFRASTRUCTURE",
            "color": "red",
            "line_type": "continuous",
            "line_weight": 0.35,
            "visible": True,
            "freeze": False,
            "lock": False
        }
        
        valid, errors = self.validator.validate_layer(layer)
        self.assertTrue(valid)
    
    def test_validate_layer_missing_name(self):
        """Test validation of layer without name"""
        layer = {
            "color": "red",
            "line_type": "continuous"
            # Missing name
        }
        
        valid, errors = self.validator.validate_layer(layer)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)


class TestAttributeValidator(unittest.TestCase):
    """Test cases for AttributeValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.required_attrs = ["scale", "units", "coordinate_system"]
        self.validator = AttributeValidator(self.required_attrs)
    
    def test_validate_with_all_attributes(self):
        """Test validation with all required attributes"""
        attributes = {
            "scale": "1:100",
            "units": "meters",
            "coordinate_system": "ETRS89"
        }
        
        valid, errors = self.validator.validate(attributes)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_with_missing_attribute(self):
        """Test validation with missing attribute"""
        attributes = {
            "scale": "1:100",
            "units": "meters"
            # Missing coordinate_system
        }
        
        valid, errors = self.validator.validate(attributes)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_with_empty_attribute(self):
        """Test validation with empty attribute value"""
        attributes = {
            "scale": "1:100",
            "units": "",
            "coordinate_system": "ETRS89"
        }
        
        valid, errors = self.validator.validate(attributes)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_scale(self):
        """Test scale validation"""
        valid, error = self.validator.validate_scale("1:100")
        self.assertTrue(valid)
        
        valid, error = self.validator.validate_scale("1/100")
        self.assertTrue(valid)
        
        valid, error = self.validator.validate_scale("invalid")
        self.assertFalse(valid)
    
    def test_validate_coordinate_system(self):
        """Test coordinate system validation"""
        valid, error = self.validator.validate_coordinate_system("ETRS89")
        self.assertTrue(valid)
        
        valid, error = self.validator.validate_coordinate_system("WGS84")
        self.assertTrue(valid)
        
        valid, error = self.validator.validate_coordinate_system("Invalid")
        self.assertFalse(valid)


class TestNormValidator(unittest.TestCase):
    """Test cases for NormValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "standards": {
                "ISO 19115:2003": {
                    "required_fields": ["title", "abstract", "date", "organization"]
                },
                "EN ISO 19115:2005": {
                    "required_fields": ["standard_number", "publication_date", "scope"]
                }
            }
        }
        self.validator = NormValidator(self.config)
    
    def test_validate_iso_standard(self):
        """Test validation against ISO standard"""
        data = {
            "metadata": {
                "title": "Test",
                "abstract": "Test abstract",
                "date": "2024-01-01",
                "organization": "Test Org"
            }
        }
        
        result = self.validator.validate(data, "ISO 19115:2003")
        self.assertTrue(result.valid)
    
    def test_validate_en_standard(self):
        """Test validation against EN standard"""
        data = {
            "metadata": {
                "standard_number": "EN ISO 19115:2005",
                "publication_date": "2005-01-01",
                "scope": "Metadata standard"
            }
        }
        
        result = self.validator.validate(data, "EN ISO 19115:2005")
        self.assertTrue(result.valid)
    
    def test_validate_with_missing_fields(self):
        """Test validation with missing required fields"""
        data = {
            "metadata": {
                "title": "Test",
                "abstract": "Test abstract"
                # Missing date and organization
            }
        }
        
        result = self.validator.validate(data, "ISO 19115:2003")
        self.assertFalse(result.valid)
    
    def test_validate_unknown_standard(self):
        """Test validation against unknown standard"""
        data = {"metadata": {"title": "Test"}}
        result = self.validator.validate(data, "UNKNOWN_STANDARD")
        
        # Should use generic validation
        self.assertIsInstance(result, NormValidationResult)


class TestSchemaValidator(unittest.TestCase):
    """Test cases for SchemaValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = SchemaValidator()
        
        # Simple schema for testing
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"]
        }
    
    def test_validate_valid_data(self):
        """Test validation of valid data"""
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        result = self.validator.validate(data, self.schema)
        self.assertTrue(result.valid)
    
    def test_validate_missing_required_field(self):
        """Test validation with missing required field"""
        data = {
            "name": "John Doe"
            # Missing age
        }
        
        result = self.validator.validate(data, self.schema)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_invalid_type(self):
        """Test validation with invalid type"""
        data = {
            "name": "John Doe",
            "age": "thirty"  # Should be integer
        }
        
        result = self.validator.validate(data, self.schema)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_minimum_constraint(self):
        """Test validation with minimum constraint violation"""
        data = {
            "name": "John Doe",
            "age": -5  # Below minimum of 0
        }
        
        result = self.validator.validate(data, self.schema)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_maximum_constraint(self):
        """Test validation with maximum constraint violation"""
        data = {
            "name": "John Doe",
            "age": 150  # Above maximum of 120
        }
        
        result = self.validator.validate(data, self.schema)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_email_format(self):
        """Test validation with email format"""
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "invalid-email"  # Invalid email format
        }
        
        result = self.validator.validate(data, self.schema)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_array_schema(self):
        """Test validation with array schema"""
        array_schema = {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 3
        }
        
        # Valid array
        result = self.validator.validate(["a", "b"], array_schema)
        self.assertTrue(result.valid)
        
        # Invalid array (wrong type)
        result = self.validator.validate([1, 2], array_schema)
        self.assertFalse(result.valid)
        
        # Array with too many items
        result = self.validator.validate(["a", "b", "c", "d"], array_schema)
        self.assertFalse(result.valid)
    
    def test_validate_string_constraints(self):
        """Test validation with string constraints"""
        string_schema = {
            "type": "string",
            "minLength": 3,
            "maxLength": 10,
            "pattern": "^[A-Za-z]+$"
        }
        
        # Valid string
        result = self.validator.validate("Hello", string_schema)
        self.assertTrue(result.valid)
        
        # Too short
        result = self.validator.validate("Hi", string_schema)
        self.assertFalse(result.valid)
        
        # Too long
        result = self.validator.validate("Hello World", string_schema)
        self.assertFalse(result.valid)
        
        # Invalid pattern (contains numbers)
        result = self.validator.validate("Hello123", string_schema)
        self.assertFalse(result.valid)
    
    def test_custom_validator(self):
        """Test custom validator"""
        # Define a custom validator
        def custom_validator(data, schema, path):
            if data != "valid_value":
                return False, f"Value must be 'valid_value', got {data}"
            return True, ""
        
        self.validator.add_custom_validator("custom", custom_validator)
        
        # Schema with custom validator
        custom_schema = {
            "type": "string",
            "x-validator": "custom"
        }
        
        # Valid data
        result = self.validator.validate("valid_value", custom_schema)
        self.assertTrue(result.valid)
        
        # Invalid data
        result = self.validator.validate("invalid_value", custom_schema)
        self.assertFalse(result.valid)


if __name__ == "__main__":
    unittest.main()
