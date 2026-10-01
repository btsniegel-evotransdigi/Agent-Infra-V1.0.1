"""
Tests for International Standards Agent
"""

import unittest
import os
import tempfile
from pathlib import Path

from agents.international_standards.agent import (
    InternationalStandardsAgent,
    ValidationResult,
    AgentConfig
)
from agents.international_standards.standards.iso import ISOStandard
from agents.international_standards.standards.en import ENStandard
from agents.international_standards.standards.din import DINStandard
from agents.international_standards.standards.ansi import ANSIStandard
from agents.international_standards.standards.bsi import BSIStandard


class TestInternationalStandardsAgent(unittest.TestCase):
    """Test cases for InternationalStandardsAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = InternationalStandardsAgent()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = InternationalStandardsAgent()
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.config)
        self.assertIsNotNone(agent.standards)
        self.assertIsNotNone(agent.drawing_validator)
    
    def test_agent_with_config(self):
        """Test agent initialization with configuration"""
        agent = InternationalStandardsAgent(
            config_path="src/config/standards_config.yaml",
            evotransdigi_config="src/config/evotransdigi_config.yaml"
        )
        self.assertIsNotNone(agent)
        self.assertTrue(agent.config.evotransdigi_config.get("enabled", False))
    
    def test_get_supported_standards(self):
        """Test getting supported standards"""
        standards = self.agent.get_supported_standards()
        self.assertIsInstance(standards, list)
        self.assertGreater(len(standards), 0)
        
        # Check for specific standards
        self.assertIn("ISO 19115:2003", standards)
        self.assertIn("EN ISO 19115:2005", standards)
        self.assertIn("DIN 1356-1:1995", standards)
    
    def test_get_standard_config(self):
        """Test getting standard configuration"""
        # Test ISO standard
        config = self.agent.get_standard_config("ISO 19115:2003")
        self.assertIsNotNone(config)
        self.assertIn("required_fields", config)
        
        # Test EN standard
        config = self.agent.get_standard_config("EN ISO 19115:2005")
        self.assertIsNotNone(config)
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        result = self.agent.validate_drawing("/nonexistent/file.dwg")
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_with_generate_report(self):
        """Test validation with report generation"""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, "test.dwg")
        with open(temp_file, 'w') as f:
            f.write("test")
        
        result = self.agent.validate_drawing(temp_file, generate_report=True)
        self.assertIsInstance(result, dict)
        self.assertIn("validation_summary", result)
        self.assertIn("file_information", result)
    
    def test_validate_with_specific_standard(self):
        """Test validation with specific standard"""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, "test.dwg")
        with open(temp_file, 'w') as f:
            f.write("test")
        
        result = self.agent.validate_drawing(
            temp_file,
            standard="ISO 19115:2003"
        )
        self.assertEqual(result.standard, "ISO 19115:2003")
    
    def test_validate_with_evotransdigi(self):
        """Test EvoTransDigi validation"""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, "test.dwg")
        with open(temp_file, 'w') as f:
            f.write("test")
        
        result = self.agent.validate_with_evotransdigi(
            temp_file,
            compliance_level="level_2"
        )
        self.assertEqual(result.compliance_level, "level_2")
        self.assertEqual(result.standard, "EvoTransDigi")
    
    def test_validate_against_multiple_standards(self):
        """Test validation against multiple standards"""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, "test.dwg")
        with open(temp_file, 'w') as f:
            f.write("test")
        
        standards = ["ISO 19115:2003", "EN ISO 19115:2005"]
        results = self.agent.validate_against_multiple_standards(
            temp_file,
            standards
        )
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), len(standards))
        for standard in standards:
            self.assertIn(standard, results)
    
    def test_generate_compliance_report(self):
        """Test compliance report generation"""
        # Create a temporary file
        temp_file = os.path.join(self.temp_dir, "test.dwg")
        with open(temp_file, 'w') as f:
            f.write("test")
        
        report = self.agent.generate_compliance_report(
            temp_file,
            compliance_level="level_2"
        )
        
        self.assertIsInstance(report, dict)
        self.assertIn("metadata", report)
        self.assertIn("standards_validated", report)
        self.assertIn("overall_compliance", report)
    
    def test_save_report(self):
        """Test saving report to file"""
        report = {
            "test": "report",
            "valid": True
        }
        
        report_path = os.path.join(self.temp_dir, "test_report.json")
        result = self.agent.save_report(report, report_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(report_path))
    
    def test_get_validation_rules(self):
        """Test getting validation rules"""
        rules = self.agent.get_validation_rules("ISO 19115:2003")
        self.assertIsInstance(rules, dict)
        self.assertIn("required_fields", rules)


class TestStandardClasses(unittest.TestCase):
    """Test cases for standard classes"""
    
    def test_iso_standard_creation(self):
        """Test ISO standard creation"""
        iso = ISOStandard(
            standard_number="ISO 19115:2003",
            title="Geographic Information - Metadata",
            publication_date="2003-01-01"
        )
        self.assertEqual(iso.standard_number, "ISO 19115:2003")
        self.assertEqual(iso.title, "Geographic Information - Metadata")
    
    def test_iso_standard_validation(self):
        """Test ISO standard metadata validation"""
        iso = ISOStandard(
            standard_number="ISO 19115:2003",
            title="Geographic Information - Metadata"
        )
        
        # Valid metadata
        metadata = {
            "title": "Test",
            "abstract": "Test abstract",
            "date": "2024-01-01",
            "organization": "Test Org"
        }
        result = iso.validate_metadata(metadata)
        self.assertTrue(result["valid"])
        
        # Invalid metadata (missing required field)
        invalid_metadata = {
            "title": "Test",
            "abstract": "Test abstract"
            # Missing date and organization
        }
        result = iso.validate_metadata(invalid_metadata)
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["missing_fields"]), 0)
    
    def test_en_standard_creation(self):
        """Test EN standard creation"""
        en = ENStandard(
            standard_number="EN ISO 19115:2005",
            title="Geographic Information - Metadata",
            scope="European adoption of ISO 19115",
            publication_date="2005-01-01"
        )
        self.assertEqual(en.standard_number, "EN ISO 19115:2005")
        self.assertEqual(en.scope, "European adoption of ISO 19115")
    
    def test_din_standard_creation(self):
        """Test DIN standard creation"""
        din = DINStandard(
            norm_number="DIN 1356-1:1995",
            title="Building drawing - Types and contents",
            validity="valid",
            publication_date="1995-01-01"
        )
        self.assertEqual(din.norm_number, "DIN 1356-1:1995")
        self.assertEqual(din.validity, "valid")
    
    def test_ansi_standard_creation(self):
        """Test ANSI standard creation"""
        ansi = ANSIStandard(
            standard_id="ANSI Z1.1-1996",
            title="Graphic Symbols for Architectural and Building Construction",
            publication_date="1996-01-01",
            description="Standard for graphic symbols"
        )
        self.assertEqual(ansi.standard_id, "ANSI Z1.1-1996")
    
    def test_bsi_standard_creation(self):
        """Test BSI standard creation"""
        bsi = BSIStandard(
            standard_ref="BS EN ISO 19115:2005",
            title="Geographic Information - Metadata",
            issue_date="2005-01-01",
            scope="British adoption of ISO 19115"
        )
        self.assertEqual(bsi.standard_ref, "BS EN ISO 19115:2005")
    
    def test_standard_from_dict(self):
        """Test creating standard from dictionary"""
        data = {
            "standard_number": "ISO 19115:2003",
            "title": "Test Standard",
            "publication_date": "2003-01-01"
        }
        iso = ISOStandard.from_dict(data)
        self.assertEqual(iso.standard_number, "ISO 19115:2003")
    
    def test_standard_to_dict(self):
        """Test converting standard to dictionary"""
        iso = ISOStandard(
            standard_number="ISO 19115:2003",
            title="Test Standard",
            publication_date="2003-01-01"
        )
        data = iso.to_dict()
        self.assertIn("standard_number", data)
        self.assertIn("title", data)
        self.assertIn("publication_date", data)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation"""
        result = ValidationResult()
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
    
    def test_add_error(self):
        """Test adding error to ValidationResult"""
        result = ValidationResult()
        result.add_error("Test error")
        
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Test error")
    
    def test_add_warning(self):
        """Test adding warning to ValidationResult"""
        result = ValidationResult()
        result.add_warning("Test warning")
        
        self.assertTrue(result.valid)  # Warnings don't invalidate
        self.assertEqual(len(result.warnings), 1)
    
    def test_merge_results(self):
        """Test merging ValidationResults"""
        result1 = ValidationResult()
        result1.add_error("Error 1")
        
        result2 = ValidationResult()
        result2.add_warning("Warning 1")
        result2.add_info("Info 1")
        
        result1.merge(result2)
        
        self.assertFalse(result1.valid)
        self.assertEqual(len(result1.errors), 1)
        self.assertEqual(len(result1.warnings), 1)
        self.assertEqual(len(result1.info), 1)
    
    def test_to_dict(self):
        """Test converting ValidationResult to dictionary"""
        result = ValidationResult()
        result.add_error("Test error")
        result.add_warning("Test warning")
        result.standard = "ISO 19115:2003"
        
        data = result.to_dict()
        self.assertIn("valid", data)
        self.assertIn("errors", data)
        self.assertIn("warnings", data)
        self.assertIn("standard", data)


class TestAgentConfig(unittest.TestCase):
    """Test cases for AgentConfig"""
    
    def test_config_creation(self):
        """Test AgentConfig creation"""
        config = AgentConfig()
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.iso_config)
        self.assertIsNotNone(config.en_config)
    
    def test_config_from_yaml(self):
        """Test loading config from YAML"""
        config = AgentConfig.from_yaml("src/config/standards_config.yaml")
        self.assertIsNotNone(config)
        self.assertTrue(config.iso_config.enabled)
    
    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = AgentConfig()
        data = config.to_dict()
        self.assertIn("standards", data)
        self.assertIn("agent", data)


if __name__ == "__main__":
    unittest.main()
