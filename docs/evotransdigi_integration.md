# EvoTransDigi Integration Guide

## Overview

This document describes the integration of the International Standards Agent with EvoTransDigi-specific requirements and workflows.

## Table of Contents

1. [EvoTransDigi Standards](#evotransdigi-standards)
2. [Configuration](#configuration)
3. [Compliance Levels](#compliance-levels)
4. [Validation Rules](#validation-rules)
5. [Integration Methods](#integration-methods)
6. [Work Protocols](#work-protocols)
7. [Reporting](#reporting)
8. [Best Practices](#best-practices)

---

## EvoTransDigi Standards

EvoTransDigi has defined a set of project-specific standards that extend and complement international norms:

### Standard Documents

| Standard ID | Title | Version | Publication Date | Scope |
|-------------|-------|---------|------------------|-------|
| EvoTransDigi-STD-001:2024 | Metadata Requirements for Infrastructure Drawings | 1.0 | 2024-01-01 | All infrastructure and transportation planning drawings |
| EvoTransDigi-STD-002:2024 | Layer Naming Conventions | 1.0 | 2024-01-01 | All CAD drawings in EvoTransDigi projects |
| EvoTransDigi-STD-003:2024 | Quality Assurance Procedures | 1.0 | 2024-01-01 | All drawing validation processes |
| EvoTransDigi-STD-004:2024 | Coordinate System Requirements | 1.0 | 2024-01-01 | All geospatial drawings |
| EvoTransDigi-STD-005:2024 | Compliance Reporting Format | 1.0 | 2024-01-01 | All compliance reports |

### Standard Hierarchy

```
EvoTransDigi Standards
├── STD-001: Metadata Requirements
│   ├── Required Fields
│   ├── Optional Fields
│   └── Format Specifications
├── STD-002: Layer Naming Conventions
│   ├── Naming Rules
│   ├── Layer Groups
│   └── Sublayer Definitions
├── STD-003: Quality Assurance Procedures
│   ├── Validation Methods
│   ├── Quality Thresholds
│   └── Review Processes
├── STD-004: Coordinate System Requirements
│   ├── Datum Specifications
│   ├── Projection Requirements
│   └── Precision Standards
└── STD-005: Compliance Reporting Format
    ├── Report Structure
    ├── Content Requirements
    └── Format Specifications
```

---

## Configuration

### EvoTransDigi Configuration File

The EvoTransDigi configuration is defined in `src/config/evotransdigi_config.yaml`:

```yaml
evotransdigi:
  enabled: true
  project_name: "EvoTransDigi Infrastructure Validation"
  project_id: "EVOTRANSDIGI-2024"
  version: "1.0.1"
  description: "Configuration for EvoTransDigi-specific validation requirements"
  
  specific_standards:
    - "EvoTransDigi-STD-001:2024"
    - "EvoTransDigi-STD-002:2024"
    - "EvoTransDigi-STD-003:2024"
    - "EvoTransDigi-STD-004:2024"
    - "EvoTransDigi-STD-005:2024"
```

### Standard References

Each EvoTransDigi standard has detailed specifications:

```yaml
standard_references:
  EvoTransDigi-STD-001:2024:
    title: "Metadata Requirements for Infrastructure Drawings"
    description: "Standard for metadata structure and content in infrastructure drawings"
    version: "1.0"
    publication_date: "2024-01-01"
    scope: "All infrastructure and transportation planning drawings"
```

### Project Settings

```yaml
project:
  default_coordinate_system: "ETRS89 / UTM Zone 32N"
  default_units: "meters"
  default_precision: 0.001
  default_scale: "1:1000"
  
  team:
    organization: "EvoTransDigi"
    department: "Infrastructure Planning"
    contact_email: "support@evotransdigi.de"
```

---

## Compliance Levels

EvoTransDigi defines three levels of compliance for drawing validation:

### Level 1: Basic Compliance

**Description**: Essential requirements for basic compliance with EvoTransDigi standards.

**Checks Performed**:
- `metadata_complete`: All required metadata fields are present
- `required_layers_present`: All required layers are present in the drawing
- `file_format_valid`: File is in a supported format
- `basic_geometry_valid`: Basic geometry validation passed

**Requirements**:
- All required metadata fields must be present
- All required layers must be present in the drawing
- File must be in a supported format (DWG, DXF, PDF, SVG, STEP, IGES)
- Basic geometry validation passed

**Use Case**: Quick validation for initial drawing submission

### Level 2: Standard Compliance

**Description**: Full compliance with EvoTransDigi standards and international norms.

**Checks Performed**:
- All Level 1 checks
- `attribute_validation`: All required attributes are present and valid
- `geometric_accuracy`: Geometric accuracy meets minimum requirements
- `coordinate_system_valid`: Coordinate system is properly defined
- `projection_valid`: Projection is valid and appropriate

**Requirements**:
- All Level 1 requirements
- All required attributes must be present and valid
- Geometric accuracy must meet minimum requirements (0.001m precision)
- Coordinate system must be properly defined (ETRS89 recommended)
- Projection must be valid and appropriate (UTM Zone 32N/33N recommended)

**Use Case**: Standard validation for project deliverables

### Level 3: Advanced Compliance

**Description**: Full compliance with extended validation and EvoTransDigi-specific requirements.

**Checks Performed**:
- All Level 2 checks
- `semantic_validation`: Semantic validation passed
- `cross_reference_check`: Cross-references between elements are valid
- `quality_assurance_check`: Quality assurance procedures followed
- `evotransdigi_specific_checks`: EvoTransDigi-specific requirements met

**Requirements**:
- All Level 2 requirements
- Semantic validation must pass (object classification, relationships)
- Cross-references between elements must be valid
- Quality assurance procedures must be followed
- EvoTransDigi-specific requirements must be met (layer naming, metadata structure)

**Use Case**: Final validation for project completion and archiving

---

## Validation Rules

### Metadata Rules

**Required Fields** (STD-001:2024):
```yaml
validation_rules:
  metadata:
    required:
      - project_id
      - version
      - timestamp
      - responsible_engineer
      - drawing_type
      - scale
      - coordinate_system
      - projection
      - units
      - precision
      - software
      - software_version
      - author
      - organization
      - date_created
      - date_modified
```

**Optional Fields**:
```yaml
    optional:
      - description
      - keywords
      - revision
      - approval_status
      - approval_date
      - approver
      - review_status
      - review_comments
      - related_drawings
      - references
      - notes
```

### Drawing Rules

**Required Layers** (STD-002:2024):
```yaml
    drawing:
      required_layers:
        - "INFRASTRUCTURE"
        - "TRANSPORTATION"
        - "UTILITIES"
        - "TOPOGRAPHY"
        - "VEGETATION"
        - "WATER_BODIES"
        - "BUILDINGS"
        - "ANNOTATION"
        - "DIMENSIONS"
        - "BORDERS"
```

**Layer Naming Conventions**:
```yaml
      layer_naming_conventions:
        prefix: "EVTD_"
        separator: "_"
        max_length: 50
        allowed_characters: "[A-Za-z0-9_\-\.]"
```

**Layer Groups**:
```yaml
      layer_groups:
        INFRASTRUCTURE:
          description: "Infrastructure elements"
          sublayers:
            - "ROADS"
            - "BRIDGES"
            - "TUNNELS"
            - "RAILWAYS"
            - "PATHS"
        
        TRANSPORTATION:
          description: "Transportation networks"
          sublayers:
            - "ROAD_NETWORK"
            - "RAIL_NETWORK"
            - "PED_NETWORK"
            - "CYCLE_NETWORK"
            - "PUBLIC_TRANSPORT"
        
        UTILITIES:
          description: "Utility services"
          sublayers:
            - "ELECTRICAL"
            - "WATER"
            - "SEWER"
            - "GAS"
            - "TELECOMMUNICATIONS"
            - "DRAINAGE"
```

**Required Attributes**:
```yaml
      required_attributes:
        - layer_name
        - layer_description
        - color
        - line_type
        - line_weight
        - visibility
        - freeze
        - lock
```

### Geometry Rules

**Precision and Coordinate Requirements** (STD-004:2024):
```yaml
    geometry:
      min_precision: 0.001
      max_coordinate_value: 10000000
      valid_projections:
        - "UTM Zone 32N"
        - "UTM Zone 33N"
        - "ETRS89"
        - "DHDN"
        - "WGS84"
      coordinate_system_requirements:
        required: true
        datum: "ETRS89"
```

### Quality Rules

**Quality Thresholds** (STD-003:2024):
```yaml
  quality_thresholds:
    positional_accuracy: 0.05  # meters
    attribute_completeness: 100  # percent
    geometric_precision: 0.001  # meters
    semantic_accuracy: 95  # percent
```

---

## Integration Methods

### Method 1: Direct Integration

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Initialize agent with EvoTransDigi configuration
agent = InternationalStandardsAgent(
    config_path="src/config/standards_config.yaml",
    evotransdigi_config="src/config/evotransdigi_config.yaml"
)

# Validate with EvoTransDigi requirements
result = agent.validate_with_evotransdigi(
    "path/to/drawing.dwg",
    compliance_level="level_3"
)

print(f"EvoTransDigi Validation: {result.valid}")
print(f"Compliance Level: {result.compliance_level}")
print(f"Errors: {result.errors}")
print(f"Warnings: {result.warnings}")
```

### Method 2: Configuration-Based Integration

```python
from agents.international_standards.agent import InternationalStandardsAgent, AgentConfig

# Load configuration with EvoTransDigi settings
config = AgentConfig.from_yaml("src/config/standards_config.yaml")

# Initialize agent
agent = InternationalStandardsAgent()
agent.config = config

# Validate drawing
result = agent.validate_drawing(
    "path/to/drawing.dwg",
    standard="ISO 19115:2003"
)
```

### Method 3: Programmatic Integration

```python
from agents.international_standards.agent import InternationalStandardsAgent
from src.config import load_evotransdigi_config

# Load EvoTransDigi configuration
config = load_evotransdigi_config()

# Initialize agent
agent = InternationalStandardsAgent()

# Apply EvoTransDigi configuration
agent.config.evotransdigi_config = config

# Validate with EvoTransDigi
result = agent.validate_with_evotransdigi(
    "path/to/drawing.dwg",
    compliance_level="level_2"
)
```

### Method 4: Batch Processing

```python
from agents.international_standards.agent import InternationalStandardsAgent
import os

# Initialize agent
agent = InternationalStandardsAgent(
    evotransdigi_config="src/config/evotransdigi_config.yaml"
)

# Process all drawings in a directory
drawings_dir = "drawings/"
compliance_level = "level_2"

for filename in os.listdir(drawings_dir):
    if filename.endswith(".dwg"):
        filepath = os.path.join(drawings_dir, filename)
        
        # Validate with EvoTransDigi
        result = agent.validate_with_evotransdigi(
            filepath,
            compliance_level
        )
        
        # Save results
        print(f"{filename}: {result.compliance_level} - {'✓ VALID' if result.valid else '✗ INVALID'}")
        
        # Save detailed report
        if not result.valid:
            report = agent.generate_compliance_report(
                filepath,
                compliance_level
            )
            report_path = f"logs/{filename}_report.json"
            agent.save_report(report, report_path)
```

---

## Work Protocols

### Automatic Protocol Generation

All EvoTransDigi validation activities are automatically logged to work protocols:

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Protocols are automatically generated
agent = InternationalStandardsAgent(
    evotransdigi_config="src/config/evotransdigi_config.yaml"
)

# Perform validation
result = agent.validate_with_evotransdigi(
    "path/to/drawing.dwg",
    compliance_level="level_3"
)

# Protocols are saved in the logs/ directory
```

### Manual Protocol Management

```python
from src.utils.logger import (
    AgentLogger,
    start_protocol_session,
    end_protocol_session,
    protocol_manager
)

# Start a new protocol session
session_id = start_protocol_session("evotransdigi_validation_001")

# Initialize logger with protocol
logger = AgentLogger(protocol_enabled=True)
logger.info(f"Starting EvoTransDigi validation for project: EVOTRANSDIGI-2024")

# Perform validations
# ...

# End and save the session
protocol_path = end_protocol_session("evotransdigi_validation_001")
logger.info(f"Protocol saved to: {protocol_path}")
```

### Protocol Content

EvoTransDigi protocols include:

1. **Session Information**:
   - Start and end timestamps
   - Duration
   - Session name

2. **Validation Entries**:
   - Timestamp of each validation
   - Log level (INFO, WARNING, ERROR)
   - Message describing the validation
   - Module, function, and line number

3. **EvoTransDigi-Specific Information**:
   - Compliance level used
   - Standards validated against
   - Validation results
   - Error and warning details

### Protocol File Locations

- **JSON Format**: `logs/protocol_YYYYMMDD_HHMMSS.json`
- **Text Format**: `logs/protocol_YYYYMMDD_HHMMSS.txt`
- **Session Files**: `logs/session_<name>.json` or `logs/session_<name>.txt`

---

## Reporting

### Compliance Report Generation

```python
from agents.international_standards.agent import InternationalStandardsAgent
import json

# Initialize agent
agent = InternationalStandardsAgent(
    evotransdigi_config="src/config/evotransdigi_config.yaml"
)

# Generate comprehensive compliance report
report = agent.generate_compliance_report(
    "path/to/drawing.dwg",
    compliance_level="level_3",
    standards=["ISO 19115:2003", "EN ISO 19115:2005", "EvoTransDigi-STD-001:2024"]
)

# Save report
report_path = "logs/compliance_report.json"
agent.save_report(report, report_path)
```

### Report Structure

EvoTransDigi compliance reports include:

```json
{
  "metadata": {
    "generated_at": "2024-10-01T10:00:00",
    "file": "path/to/drawing.dwg",
    "compliance_level": "level_3",
    "project_id": "EVOTRANSDIGI-2024"
  },
  "standards_validated": [
    {
      "standard": "ISO 19115:2003",
      "valid": true,
      "errors": [],
      "warnings": [],
      "info": ["All required fields present"]
    },
    {
      "standard": "EvoTransDigi-STD-001:2024",
      "valid": true,
      "errors": [],
      "warnings": [],
      "info": ["Metadata validation passed"]
    }
  ],
  "evotransdigi_validation": {
    "valid": true,
    "compliance_level": "level_3",
    "errors": [],
    "warnings": [],
    "info": ["All EvoTransDigi checks passed"]
  },
  "overall_compliance": true,
  "total_errors": 0,
  "total_warnings": 0,
  "recommendations": [
    "All validations passed successfully"
  ],
  "compliance_matrix": {
    "standard": "EvoTransDigi",
    "compliance_level": "level_3",
    "overall_status": "COMPLIANT",
    "requirements": [
      {"field": "project_id", "status": "PRESENT"},
      {"field": "version", "status": "PRESENT"},
      {"field": "timestamp", "status": "PRESENT"}
    ]
  }
}
```

### Custom Report Generation

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Initialize agent
agent = InternationalStandardsAgent()

# Generate report with specific standards
report = agent.generate_compliance_report(
    "path/to/drawing.dwg",
    compliance_level="level_2",
    standards=[
        "EvoTransDigi-STD-001:2024",
        "EvoTransDigi-STD-002:2024",
        "ISO 19115:2003"
    ]
)

# Add custom information to report
report["custom_info"] = {
    "validated_by": "John Doe",
    "validation_date": "2024-10-01",
    "project_phase": "Design Review"
}

# Save custom report
agent.save_report(report, "logs/custom_report.json")
```

---

## Best Practices

### 1. Start with Lower Compliance Levels

Begin validation with Level 1 and progressively move to higher levels:

```python
# Start with Level 1
result_level1 = agent.validate_with_evotransdigi(
    "drawing.dwg",
    compliance_level="level_1"
)

if result_level1.valid:
    # Move to Level 2
    result_level2 = agent.validate_with_evotransdigi(
        "drawing.dwg",
        compliance_level="level_2"
    )
    
    if result_level2.valid:
        # Finally Level 3
        result_level3 = agent.validate_with_evotransdigi(
            "drawing.dwg",
            compliance_level="level_3"
        )
```

### 2. Use Specific Standards When Possible

```python
# Validate against specific EvoTransDigi standards
result = agent.validate_drawing(
    "drawing.dwg",
    standard="EvoTransDigi-STD-001:2024"
)
```

### 3. Implement Validation Workflows

```python
from agents.international_standards.agent import InternationalStandardsAgent
import os

# Define validation workflow
class ValidationWorkflow:
    def __init__(self):
        self.agent = InternationalStandardsAgent(
            evotransdigi_config="src/config/evotransdigi_config.yaml"
        )
    
    def validate_project(self, project_dir):
        """Validate all drawings in a project"""
        results = {}
        
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith(".dwg"):
                    filepath = os.path.join(root, file)
                    
                    # Perform EvoTransDigi validation
                    result = self.agent.validate_with_evotransdigi(
                        filepath,
                        compliance_level="level_2"
                    )
                    
                    results[filepath] = {
                        "valid": result.valid,
                        "compliance_level": result.compliance_level,
                        "errors": result.errors,
                        "warnings": result.warnings
                    }
        
        return results
```

### 4. Automate Protocol Generation

```python
from src.utils.logger import AgentLogger, start_protocol_session, end_protocol_session

# Start protocol session
session_id = start_protocol_session("daily_validation")

# Initialize logger
logger = AgentLogger(protocol_enabled=True)

try:
    # Perform validations
    agent = InternationalStandardsAgent()
    result = agent.validate_drawing("drawing.dwg")
    
    logger.info(f"Validation completed: {result.valid}")
    
finally:
    # Ensure protocol is saved even if errors occur
    protocol_path = end_protocol_session("daily_validation")
    logger.info(f"Daily validation protocol saved to: {protocol_path}")
```

### 5. Use Configuration Management

```python
from src.config import load_evotransdigi_config, save_config

# Load current configuration
config = load_evotransdigi_config()

# Update configuration
config["evotransdigi"]["default_compliance_level"] = "level_3"
config["evotransdigi"]["quality_thresholds"]["positional_accuracy"] = 0.01

# Save updated configuration
save_config(config, "src/config/evotransdigi_config.yaml")
```

### 6. Implement Continuous Validation

```python
from agents.international_standards.agent import InternationalStandardsAgent
import watchdog.events
import watchdog.observers
import time

class DrawingFileHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, agent):
        self.agent = agent
    
    def on_modified(self, event):
        if event.src_path.endswith(".dwg"):
            print(f"Validating modified file: {event.src_path}")
            result = self.agent.validate_with_evotransdigi(
                event.src_path,
                compliance_level="level_2"
            )
            
            if not result.valid:
                print(f"Validation failed for {event.src_path}")
                print(f"Errors: {result.errors}")

# Setup continuous validation
agent = InternationalStandardsAgent()
event_handler = DrawingFileHandler(agent)
observer = watchdog.observers.Observer()
observer.schedule(event_handler, path="drawings/", recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: EvoTransDigi Validation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run EvoTransDigi Validation
      run: |
        python -m agents.international_standards.agent \
          drawings/sample.dwg \
          --evotransdigi src/config/evotransdigi_config.yaml \
          --compliance-level level_3 \
          --report \
          --output validation_report.json
    
    - name: Upload Validation Report
      uses: actions/upload-artifact@v2
      with:
        name: validation-report
        path: validation_report.json
```

### GitLab CI Example

```yaml
stages:
  - validate

validate_drawings:
  stage: validate
  image: python:3.9
  
  before_script:
    - pip install -r requirements.txt
  
  script:
    - python -m agents.international_standards.agent \
        drawings/*.dwg \
        --evotransdigi src/config/evotransdigi_config.yaml \
        --compliance-level level_2 \
        --report \
        --output validation_reports/
  
  artifacts:
    paths:
      - validation_reports/
    expire_in: 1 week
```

---

## Troubleshooting

### Common Issues

1. **EvoTransDigi Configuration Not Found**
   - Ensure `evotransdigi_config.yaml` exists in `src/config/`
   - Verify the path in the agent initialization
   - Check file permissions

2. **Compliance Level Not Recognized**
   - Use only `level_1`, `level_2`, or `level_3`
   - Check for typos in the compliance level name

3. **Missing Required Metadata Fields**
   - Add all required fields to your drawing metadata
   - Refer to STD-001:2024 for required fields
   - Use the metadata template

4. **Layer Naming Violations**
   - Follow the layer naming conventions (STD-002:2024)
   - Use the prefix `EVTD_`
   - Keep layer names under 50 characters
   - Use only allowed characters

5. **Coordinate System Issues**
   - Use ETRS89 datum as default
   - Use UTM Zone 32N or 33N for Germany
   - Ensure projection is properly defined

### Debug Mode

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Enable debug mode
agent = InternationalStandardsAgent(
    evotransdigi_config="src/config/evotransdigi_config.yaml",
    debug=True
)

# Perform validation with detailed output
result = agent.validate_with_evotransdigi(
    "drawing.dwg",
    compliance_level="level_3"
)

# Debug information will be logged to console
```

### Detailed Error Reporting

```python
from agents.international_standards.agent import InternationalStandardsAgent

agent = InternationalStandardsAgent()

# Generate detailed report
report = agent.generate_compliance_report(
    "drawing.dwg",
    compliance_level="level_3"
)

# Print detailed error information
if not report["overall_compliance"]:
    print("VALIDATION FAILED")
    print(f"Total Errors: {report['total_errors']}")
    print(f"Total Warnings: {report['total_warnings']}")
    
    for standard_result in report["standards_validated"]:
        if not standard_result["valid"]:
            print(f"\n{standard_result['standard']}:")
            for error in standard_result["errors"]:
                print(f"  ✗ {error}")
    
    if "evotransdigi_validation" in report:
        ev_result = report["evotransdigi_validation"]
        if not ev_result["valid"]:
            print(f"\nEvoTransDigi Validation:")
            for error in ev_result["errors"]:
                print(f"  ✗ {error}")
```

---

## Support

For support and questions regarding EvoTransDigi integration:

- **Email**: support@evotransdigi.de
- **Documentation**: [EvoTransDigi Documentation](https://www.evotransdigi.de/docs)
- **Repository**: [Agent-Infra-V1.0.1 GitHub](https://github.com/btsniegel-evotransdigi/Agent-Infra-V1.0.1)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial release of EvoTransDigi standards |
| 1.0.1 | 2024-10-01 | Enhanced integration with Agent-Infra-V1.0.1 |

---

## License

The EvoTransDigi integration components are licensed under the same terms as the main Agent-Infra-V1.0.1 project (MIT License).

---

© 2024 EvoTransDigi. All rights reserved.
