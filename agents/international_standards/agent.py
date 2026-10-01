"""
International Standards Agent

Main agent for validating drawings against international standards.
Integrates with EvoTransDigi for project-specific requirements.
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import logging

# Import standard implementations
from .standards.iso import ISOStandard, ISOStandardConfig
from .standards.en import ENStandard, ENStandardConfig
from .standards.din import DINStandard, DINStandardConfig
from .standards.ansi import ANSIStandard, ANSIStandardConfig
from .standards.bsi import BSIStandard, BSIStandardConfig


class ValidationResult:
    """Result of a validation operation"""
    
    def __init__(self):
        self.valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.compliance_level: str = "none"
        self.standard: str = ""
        self.timestamp: str = datetime.now().isoformat()
        self.metadata: Dict[str, Any] = {}
    
    def add_error(self, error: str):
        """Add an error"""
        self.valid = False
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a warning"""
        self.warnings.append(warning)
    
    def add_info(self, info: str):
        """Add information"""
        self.info.append(info)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another result into this one"""
        self.valid = self.valid and other.valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        if other.compliance_level:
            self.compliance_level = other.compliance_level
        if other.standard:
            self.standard = other.standard
        self.metadata.update(other.metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "compliance_level": self.compliance_level,
            "standard": self.standard,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    def __str__(self):
        status = "VALID" if self.valid else "INVALID"
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        return f"{status} ({error_count} errors, {warning_count} warnings)"


class DrawingValidator:
    """Validator for drawing files"""
    
    def __init__(self, agent):
        self.agent = agent
        self.supported_formats = [".dwg", ".dxf", ".pdf", ".svg", ".step", ".iges"]
    
    def validate_file_format(self, filepath: str) -> ValidationResult:
        """Validate file format"""
        result = ValidationResult()
        
        path = Path(filepath)
        if not path.exists():
            result.add_error(f"File not found: {filepath}")
            return result
        
        extension = path.suffix.lower()
        if extension not in self.supported_formats:
            result.add_warning(f"Unsupported file format: {extension}. Supported: {', '.join(self.supported_formats)}")
        
        result.metadata["file_format"] = extension
        result.metadata["file_size"] = path.stat().st_size
        result.metadata["file_path"] = str(path)
        
        return result
    
    def extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract metadata from drawing file"""
        # This is a placeholder - actual implementation would use specific libraries
        # for each file format
        metadata = {
            "title": Path(filepath).stem,
            "file_format": Path(filepath).suffix,
            "file_size": os.path.getsize(filepath),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
        }
        return metadata


class EvoTransDigiValidator:
    """Validator for EvoTransDigi-specific requirements"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.evotransdigi_standards = config.get("evotransdigi", {}).get("specific_standards", [])
        self.validation_rules = config.get("evotransdigi", {}).get("validation_rules", {})
        self.compliance_levels = config.get("evotransdigi", {}).get("compliance_levels", {})
    
    def validate_metadata(self, metadata: Dict[str, Any], compliance_level: str = "level_2") -> ValidationResult:
        """Validate metadata against EvoTransDigi requirements"""
        result = ValidationResult()
        result.standard = "EvoTransDigi"
        result.compliance_level = compliance_level
        
        # Get required fields for the compliance level
        level_config = self.compliance_levels.get(compliance_level, {})
        checks = level_config.get("checks", [])
        
        # Check metadata requirements
        metadata_rules = self.validation_rules.get("metadata", {}).get("required", [])
        for field in metadata_rules:
            if field not in metadata:
                result.add_error(f"Missing required EvoTransDigi metadata field: {field}")
            else:
                result.add_info(f"Metadata field '{field}' present")
        
        # Check optional fields
        optional_fields = self.validation_rules.get("metadata", {}).get("optional", [])
        for field in optional_fields:
            if field in metadata:
                result.add_info(f"Optional metadata field '{field}' present")
        
        return result
    
    def validate_drawing(self, drawing_data: Dict[str, Any], compliance_level: str = "level_2") -> ValidationResult:
        """Validate drawing against EvoTransDigi requirements"""
        result = ValidationResult()
        result.standard = "EvoTransDigi"
        result.compliance_level = compliance_level
        
        # Check drawing requirements
        drawing_rules = self.validation_rules.get("drawing", {})
        
        # Check required layers
        required_layers = drawing_rules.get("required_layers", [])
        if "layers" in drawing_data:
            present_layers = [layer.get("name", "").upper() for layer in drawing_data["layers"]]
            for layer in required_layers:
                if layer not in present_layers:
                    result.add_error(f"Missing required layer: {layer}")
                else:
                    result.add_info(f"Required layer '{layer}' present")
        else:
            result.add_warning("No layer information available")
        
        # Check required attributes
        required_attributes = drawing_rules.get("required_attributes", [])
        if "attributes" in drawing_data:
            present_attrs = list(drawing_data["attributes"].keys())
            for attr in required_attributes:
                if attr not in present_attrs:
                    result.add_error(f"Missing required attribute: {attr}")
                else:
                    result.add_info(f"Required attribute '{attr}' present")
        else:
            result.add_warning("No attribute information available")
        
        return result
    
    def validate_compliance_level(self, data: Dict[str, Any], level: str = "level_3") -> ValidationResult:
        """Validate against specific compliance level"""
        result = ValidationResult()
        result.standard = "EvoTransDigi"
        result.compliance_level = level
        
        level_config = self.compliance_levels.get(level, {})
        checks = level_config.get("checks", [])
        
        # Perform all checks for this level
        for check in checks:
            if check == "metadata_complete":
                # This would be handled by validate_metadata
                pass
            elif check == "required_layers_present":
                # This would be handled by validate_drawing
                pass
            elif check == "attribute_validation":
                if "attributes" in data:
                    result.add_info("Attribute validation passed")
                else:
                    result.add_warning("Attribute validation not performed - no attributes")
            elif check == "geometric_accuracy":
                result.add_info("Geometric accuracy check placeholder")
            elif check == "semantic_validation":
                result.add_info("Semantic validation check placeholder")
            elif check == "cross_reference_check":
                result.add_info("Cross-reference check placeholder")
            else:
                result.add_warning(f"Unknown check: {check}")
        
        return result


@dataclass
class AgentConfig:
    """Configuration for the International Standards Agent"""
    
    # Standard configurations
    iso_config: ISOStandardConfig = field(default_factory=ISOStandardConfig)
    en_config: ENStandardConfig = field(default_factory=ENStandardConfig)
    din_config: DINStandardConfig = field(default_factory=DINStandardConfig)
    ansi_config: ANSIStandardConfig = field(default_factory=ANSIStandardConfig)
    bsi_config: BSIStandardConfig = field(default_factory=BSIStandardConfig)
    
    # EvoTransDigi configuration
    evotransdigi_config: Dict[str, Any] = field(default_factory=dict)
    
    # Agent settings
    debug: bool = False
    strict_mode: bool = False
    default_standard: str = "ISO 19115:2003"
    default_compliance_level: str = "level_2"
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'AgentConfig':
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
        
        # Create default instance
        config = cls()
        
        # Load standard configurations
        standards_config = config_data.get("standards", {})
        
        if "iso" in standards_config:
            config.iso_config = ISOStandardConfig(**standards_config["iso"])
        if "en" in standards_config:
            config.en_config = ENStandardConfig(**standards_config["en"])
        if "din" in standards_config:
            config.din_config = DINStandardConfig(**standards_config["din"])
        if "ansi" in standards_config:
            config.ansi_config = ANSIStandardConfig(**standards_config["ansi"])
        if "bsi" in standards_config:
            config.bsi_config = BSIStandardConfig(**standards_config["bsi"])
        
        # Load EvoTransDigi configuration
        if "evotransdigi" in config_data:
            config.evotransdigi_config = config_data["evotransdigi"]
        
        # Load agent settings
        agent_settings = config_data.get("agent", {})
        if "debug" in agent_settings:
            config.debug = agent_settings["debug"]
        if "strict_mode" in agent_settings:
            config.strict_mode = agent_settings["strict_mode"]
        if "default_standard" in agent_settings:
            config.default_standard = agent_settings["default_standard"]
        if "default_compliance_level" in agent_settings:
            config.default_compliance_level = agent_settings["default_compliance_level"]
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "standards": {
                "iso": asdict(self.iso_config),
                "en": asdict(self.en_config),
                "din": asdict(self.din_config),
                "ansi": asdict(self.ansi_config),
                "bsi": asdict(self.bsi_config)
            },
            "evotransdigi": self.evotransdigi_config,
            "agent": {
                "debug": self.debug,
                "strict_mode": self.strict_mode,
                "default_standard": self.default_standard,
                "default_compliance_level": self.default_compliance_level
            }
        }


class InternationalStandardsAgent:
    """
    International Standards Agent for validating drawings against international norms.
    
    This agent supports:
    - ISO standards (International Organization for Standardization)
    - EN standards (European Norms)
    - DIN standards (Deutsches Institut für Normung)
    - ANSI standards (American National Standards Institute)
    - BSI standards (British Standards Institution)
    - EvoTransDigi-specific requirements
    
    Example usage:
        >>> agent = InternationalStandardsAgent()
        >>> result = agent.validate_drawing("path/to/drawing.dwg")
        >>> print(result)
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        evotransdigi_config: Optional[str] = None,
        debug: bool = False
    ):
        """
        Initialize the International Standards Agent.
        
        Args:
            config_path: Path to YAML configuration file
            evotransdigi_config: Path to EvoTransDigi configuration file
            debug: Enable debug mode
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Load configuration
        self.config = AgentConfig(debug=debug)
        if config_path:
            self.config = AgentConfig.from_yaml(config_path)
        
        # Initialize standard validators
        self.standards = {
            "iso": ISOStandard(
                standard_number=self.config.default_standard,
                title="Default ISO Standard"
            ),
            "en": ENStandard(
                standard_number="EN ISO 19115:2005",
                title="Default EN Standard",
                scope="Metadata for geographic information"
            ),
            "din": DINStandard(
                norm_number="DIN 1356-1:1995",
                title="Building drawing - Types and contents",
                validity="valid",
                publication_date="1995-01-01"
            ),
            "ansi": ANSIStandard(
                standard_id="ANSI Z1.1-1996",
                title="Graphic Symbols for Architectural and Building Construction",
                publication_date="1996-01-01",
                description="Standard for graphic symbols in construction drawings"
            ),
            "bsi": BSIStandard(
                standard_ref="BS EN ISO 19115:2005",
                title="Geographic Information - Metadata",
                issue_date="2005-01-01",
                scope="Metadata standards for geographic information"
            )
        }
        
        # Initialize validators
        self.drawing_validator = DrawingValidator(self)
        self.evotransdigi_validator = None
        
        # Load EvoTransDigi configuration
        if evotransdigi_config:
            with open(evotransdigi_config, 'r') as f:
                evotransdigi_data = yaml.safe_load(f) or {}
            self.config.evotransdigi_config = evotransdigi_data
            self.evotransdigi_validator = EvoTransDigiValidator(self.config)
        elif self.config.evotransdigi_config:
            self.evotransdigi_validator = EvoTransDigiValidator(self.config)
        
        self.debug = debug
        self.logger.info("International Standards Agent initialized")
    
    def get_supported_standards(self) -> List[str]:
        """Get list of supported standards"""
        supported = []
        
        if self.config.iso_config.enabled:
            supported.extend(self.config.iso_config.versions)
        if self.config.en_config.enabled:
            supported.extend(self.config.en_config.versions)
        if self.config.din_config.enabled:
            supported.extend(self.config.din_config.versions)
        if self.config.ansi_config.enabled:
            supported.extend(self.config.ansi_config.versions)
        if self.config.bsi_config.enabled:
            supported.extend(self.config.bsi_config.versions)
        
        # Add EvoTransDigi standards
        if self.config.evotransdigi_config:
            evotransdigi_standards = self.config.evotransdigi_config.get("specific_standards", [])
            supported.extend(evotransdigi_standards)
        
        return sorted(set(supported))
    
    def get_standard_config(self, standard: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific standard"""
        standard_upper = standard.upper()
        
        if standard_upper.startswith("ISO"):
            return asdict(self.config.iso_config)
        elif standard_upper.startswith("EN"):
            return asdict(self.config.en_config)
        elif standard_upper.startswith("DIN"):
            return asdict(self.config.din_config)
        elif standard_upper.startswith("ANSI"):
            return asdict(self.config.ansi_config)
        elif standard_upper.startswith("BS"):
            return asdict(self.config.bsi_config)
        elif "EvoTransDigi" in standard or "EVOTRANSDIGI" in standard_upper:
            return self.config.evotransdigi_config
        
        return None
    
    def validate_drawing(
        self,
        filepath: str,
        standard: Optional[str] = None,
        generate_report: bool = False
    ) -> Union[ValidationResult, Dict[str, Any]]:
        """
        Validate a drawing file against the specified standard.
        
        Args:
            filepath: Path to the drawing file
            standard: Specific standard to validate against (defaults to config default)
            generate_report: If True, return a detailed report dictionary
            
        Returns:
            ValidationResult or detailed report dictionary
        """
        result = ValidationResult()
        
        # Use default standard if not specified
        if not standard:
            standard = self.config.default_standard
        
        result.standard = standard
        
        # Step 1: Validate file format
        file_result = self.drawing_validator.validate_file_format(filepath)
        result.merge(file_result)
        
        if not file_result.valid:
            return result if not generate_report else result.to_dict()
        
        # Step 2: Extract metadata
        metadata = self.drawing_validator.extract_metadata(filepath)
        
        # Step 3: Validate against the specified standard
        standard_result = self._validate_against_standard(metadata, standard)
        result.merge(standard_result)
        
        # Step 4: If EvoTransDigi is enabled, validate against EvoTransDigi requirements
        if self.evotransdigi_validator and self.config.evotransdigi_config.get("enabled", True):
            evotransdigi_result = self.evotransdigi_validator.validate_metadata(
                metadata, 
                self.config.default_compliance_level
            )
            result.merge(evotransdigi_result)
        
        if generate_report:
            return self._generate_detailed_report(result, metadata, filepath)
        
        return result
    
    def validate_with_evotransdigi(
        self,
        filepath: str,
        compliance_level: str = "level_2"
    ) -> ValidationResult:
        """
        Validate a drawing file against EvoTransDigi requirements.
        
        Args:
            filepath: Path to the drawing file
            compliance_level: EvoTransDigi compliance level (level_1, level_2, level_3)
            
        Returns:
            ValidationResult
        """
        result = ValidationResult()
        result.standard = "EvoTransDigi"
        result.compliance_level = compliance_level
        
        if not self.evotransdigi_validator:
            result.add_error("EvoTransDigi validator not initialized")
            return result
        
        # Step 1: Validate file format
        file_result = self.drawing_validator.validate_file_format(filepath)
        result.merge(file_result)
        
        if not file_result.valid:
            return result
        
        # Step 2: Extract metadata
        metadata = self.drawing_validator.extract_metadata(filepath)
        
        # Step 3: Validate against EvoTransDigi requirements
        evotransdigi_result = self.evotransdigi_validator.validate_metadata(
            metadata, 
            compliance_level
        )
        result.merge(evotransdigi_result)
        
        # Step 4: Validate drawing-specific requirements
        if "layers" in metadata or "attributes" in metadata:
            drawing_data = {
                "layers": metadata.get("layers", []),
                "attributes": metadata.get("attributes", {})
            }
            drawing_result = self.evotransdigi_validator.validate_drawing(
                drawing_data,
                compliance_level
            )
            result.merge(drawing_result)
        
        # Step 5: Validate compliance level
        level_result = self.evotransdigi_validator.validate_compliance_level(
            metadata,
            compliance_level
        )
        result.merge(level_result)
        
        return result
    
    def validate_against_multiple_standards(
        self,
        filepath: str,
        standards: List[str]
    ) -> Dict[str, ValidationResult]:
        """
        Validate a drawing against multiple standards.
        
        Args:
            filepath: Path to the drawing file
            standards: List of standards to validate against
            
        Returns:
            Dictionary with validation results for each standard
        """
        results = {}
        
        # First validate file format
        file_result = self.drawing_validator.validate_file_format(filepath)
        if not file_result.valid:
            for standard in standards:
                result = ValidationResult()
                result.merge(file_result)
                result.standard = standard
                results[standard] = result
            return results
        
        # Extract metadata once
        metadata = self.drawing_validator.extract_metadata(filepath)
        
        # Validate against each standard
        for standard in standards:
            result = ValidationResult()
            result.merge(file_result)
            
            standard_result = self._validate_against_standard(metadata, standard)
            result.merge(standard_result)
            result.standard = standard
            
            results[standard] = result
        
        return results
    
    def _validate_against_standard(
        self,
        metadata: Dict[str, Any],
        standard: str
    ) -> ValidationResult:
        """Internal method to validate against a specific standard"""
        result = ValidationResult()
        result.standard = standard
        
        standard_upper = standard.upper()
        
        try:
            if standard_upper.startswith("ISO"):
                iso_standard = ISOStandard.from_dict({
                    "standard_number": standard,
                    "title": f"ISO Standard {standard}"
                })
                validation = iso_standard.validate_metadata(metadata)
                for error in validation.get("errors", []):
                    result.add_error(error)
                for warning in validation.get("warnings", []):
                    result.add_warning(warning)
                for missing in validation.get("missing_fields", []):
                    result.add_error(f"Missing field: {missing}")
                
            elif standard_upper.startswith("EN"):
                en_standard = ENStandard.from_dict({
                    "standard_number": standard,
                    "title": f"EN Standard {standard}",
                    "scope": "European standard for construction",
                    "publication_date": "2005-01-01"
                })
                validation = en_standard.validate_metadata(metadata)
                for error in validation.get("errors", []):
                    result.add_error(error)
                for warning in validation.get("warnings", []):
                    result.add_warning(warning)
                for missing in validation.get("missing_fields", []):
                    result.add_error(f"Missing field: {missing}")
                
            elif standard_upper.startswith("DIN"):
                din_standard = DINStandard.from_dict({
                    "norm_number": standard,
                    "title": f"DIN Standard {standard}",
                    "validity": "valid",
                    "publication_date": "2000-01-01"
                })
                validation = din_standard.validate_metadata(metadata)
                for error in validation.get("errors", []):
                    result.add_error(error)
                for warning in validation.get("warnings", []):
                    result.add_warning(warning)
                for missing in validation.get("missing_fields", []):
                    result.add_error(f"Missing field: {missing}")
                
            elif standard_upper.startswith("ANSI"):
                ansi_standard = ANSIStandard.from_dict({
                    "standard_id": standard,
                    "title": f"ANSI Standard {standard}",
                    "publication_date": "2000-01-01",
                    "description": "American National Standard"
                })
                validation = ansi_standard.validate_metadata(metadata)
                for error in validation.get("errors", []):
                    result.add_error(error)
                for warning in validation.get("warnings", []):
                    result.add_warning(warning)
                for missing in validation.get("missing_fields", []):
                    result.add_error(f"Missing field: {missing}")
                
            elif standard_upper.startswith("BS"):
                bsi_standard = BSIStandard.from_dict({
                    "standard_ref": standard,
                    "title": f"BSI Standard {standard}",
                    "issue_date": "2000-01-01",
                    "scope": "British Standard for construction"
                })
                validation = bsi_standard.validate_metadata(metadata)
                for error in validation.get("errors", []):
                    result.add_error(error)
                for warning in validation.get("warnings", []):
                    result.add_warning(warning)
                for missing in validation.get("missing_fields", []):
                    result.add_error(f"Missing field: {missing}")
            
            else:
                result.add_warning(f"Unknown standard: {standard}. Using generic validation.")
                # Generic validation - check for common fields
                common_fields = ["title", "date", "author", "organization"]
                for field in common_fields:
                    if field not in metadata:
                        result.add_warning(f"Missing common field: {field}")
        
        except Exception as e:
            result.add_error(f"Error validating against {standard}: {str(e)}")
            self.logger.error(f"Validation error for {standard}: {str(e)}")
        
        return result
    
    def _generate_detailed_report(
        self,
        result: ValidationResult,
        metadata: Dict[str, Any],
        filepath: str
    ) -> Dict[str, Any]:
        """Generate a detailed validation report"""
        report = {
            "validation_summary": result.to_dict(),
            "file_information": {
                "path": filepath,
                "metadata": metadata
            },
            "recommendations": self._generate_recommendations(result),
            "compliance_matrix": self._generate_compliance_matrix(result)
        }
        
        return report
    
    def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if not result.valid:
            recommendations.append("Address all errors to achieve compliance")
        
        if result.warnings:
            recommendations.append("Review warnings for potential improvements")
        
        # Add specific recommendations based on missing fields
        if "Missing field" in str(result.errors):
            recommendations.append("Add missing metadata fields to the drawing")
        
        return recommendations
    
    def _generate_compliance_matrix(self, result: ValidationResult) -> Dict[str, Any]:
        """Generate compliance matrix"""
        matrix = {
            "standard": result.standard,
            "compliance_level": result.compliance_level,
            "overall_status": "COMPLIANT" if result.valid else "NON-COMPLIANT",
            "requirements": []
        }
        
        # Add requirements based on standard
        if result.standard:
            config = self.get_standard_config(result.standard)
            if config:
                required_fields = config.get("required_fields", [])
                for field in required_fields:
                    matrix["requirements"].append({
                        "field": field,
                        "status": "PRESENT" if field not in str(result.errors) else "MISSING"
                    })
        
        return matrix
    
    def get_validation_rules(self, standard: str) -> Dict[str, Any]:
        """Get validation rules for a specific standard"""
        config = self.get_standard_config(standard)
        if config:
            return {
                "required_fields": config.get("required_fields", []),
                "optional_fields": config.get("optional_fields", []),
                "versions": config.get("versions", [])
            }
        return {}
    
    def generate_compliance_report(
        self,
        filepath: str,
        compliance_level: str = "level_3",
        standards: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report.
        
        Args:
            filepath: Path to the drawing file
            compliance_level: EvoTransDigi compliance level
            standards: List of standards to validate against (None for all supported)
            
        Returns:
            Comprehensive compliance report
        """
        if standards is None:
            standards = self.get_supported_standards()
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "file": filepath,
                "compliance_level": compliance_level
            },
            "standards_validated": [],
            "overall_compliance": True,
            "total_errors": 0,
            "total_warnings": 0
        }
        
        # Validate against each standard
        for standard in standards:
            result = self.validate_drawing(filepath, standard, generate_report=False)
            
            standard_report = {
                "standard": standard,
                "valid": result.valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "info": result.info
            }
            
            report["standards_validated"].append(standard_report)
            report["overall_compliance"] = report["overall_compliance"] and result.valid
            report["total_errors"] += len(result.errors)
            report["total_warnings"] += len(result.warnings)
        
        # Add EvoTransDigi validation if enabled
        if self.evotransdigi_validator:
            evotransdigi_result = self.validate_with_evotransdigi(
                filepath, 
                compliance_level
            )
            report["evotransdigi_validation"] = evotransdigi_result.to_dict()
            report["overall_compliance"] = report["overall_compliance"] and evotransdigi_result.valid
            report["total_errors"] += len(evotransdigi_result.errors)
            report["total_warnings"] += len(evotransdigi_result.warnings)
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_path: str) -> bool:
        """Save report to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Report saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            return False
    
    def load_config_from_string(self, config_str: str):
        """Load configuration from YAML string"""
        config_data = yaml.safe_load(config_str)
        if config_data:
            self.config = AgentConfig.from_yaml(config_str)
            if self.config.evotransdigi_config:
                self.evotransdigi_validator = EvoTransDigiValidator(self.config)
            self.logger.info("Configuration loaded from string")


# Command-line interface functions
def create_agent_from_cli_args(args) -> InternationalStandardsAgent:
    """Create agent from command-line arguments"""
    return InternationalStandardsAgent(
        config_path=args.get("config"),
        evotransdigi_config=args.get("evotransdigi_config"),
        debug=args.get("debug", False)
    )


def main():
    """Main entry point for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="International Standards Agent for validating drawings"
    )
    parser.add_argument("file", help="Path to the drawing file to validate")
    parser.add_argument("--standard", help="Specific standard to validate against")
    parser.add_argument("--config", help="Path to configuration YAML file")
    parser.add_argument("--evotransdigi", help="Path to EvoTransDigi configuration file")
    parser.add_argument("--compliance-level", default="level_2", 
                        choices=["level_1", "level_2", "level_3"],
                        help="EvoTransDigi compliance level")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--list-standards", action="store_true", 
                        help="List supported standards and exit")
    
    args = parser.parse_args()
    
    if args.list_standards:
        agent = InternationalStandardsAgent(debug=args.debug)
        standards = agent.get_supported_standards()
        print("Supported standards:")
        for standard in standards:
            print(f"  - {standard}")
        return
    
    # Create agent
    agent = InternationalStandardsAgent(
        config_path=args.config,
        evotransdigi_config=args.evotransdigi,
        debug=args.debug
    )
    
    if args.report:
        # Generate comprehensive report
        report = agent.generate_compliance_report(
            args.file,
            compliance_level=args.compliance_level,
            standards=[args.standard] if args.standard else None
        )
        
        if args.output:
            agent.save_report(report, args.output)
            print(f"Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2))
    else:
        # Simple validation
        if args.standard:
            result = agent.validate_drawing(args.file, args.standard)
        else:
            result = agent.validate_drawing(args.file)
        
        print(f"Validation result: {result}")
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")


if __name__ == "__main__":
    main()
