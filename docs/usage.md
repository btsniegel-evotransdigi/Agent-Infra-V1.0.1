# Usage Guide - International Standards Agent

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/btsniegel-evotransdigi/Agent-Infra-V1.0.1.git
cd Agent-Infra-V1.0.1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Initialize agent
agent = InternationalStandardsAgent()

# Validate a drawing
result = agent.validate_drawing("path/to/drawing.dwg")

if result.valid:
    print("✓ Drawing is valid")
else:
    print("✗ Validation errors:")
    for error in result.errors:
        print(f"  - {error}")
```

### With Configuration

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Initialize with configuration files
agent = InternationalStandardsAgent(
    config_path="src/config/standards_config.yaml",
    evotransdigi_config="src/config/evotransdigi_config.yaml"
)

# Validate with specific standard
result = agent.validate_drawing(
    "path/to/drawing.dwg",
    standard="ISO 19115:2003"
)
```

### EvoTransDigi Validation

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Initialize agent
agent = InternationalStandardsAgent(
    evotransdigi_config="src/config/evotransdigi_config.yaml"
)

# Validate with EvoTransDigi compliance level
result = agent.validate_with_evotransdigi(
    "path/to/drawing.dwg",
    compliance_level="level_3"  # level_1, level_2, or level_3
)

print(f"Compliance Level: {result.compliance_level}")
print(f"Valid: {result.valid}")
```

### Multiple Standards Validation

```python
from agents.international_standards.agent import InternationalStandardsAgent

agent = InternationalStandardsAgent()

# Validate against multiple standards
standards = ["ISO 19115:2003", "EN ISO 19115:2005", "DIN 1356-1:1995"]
results = agent.validate_against_multiple_standards(
    "path/to/drawing.dwg",
    standards
)

for standard, result in results.items():
    print(f"{standard}: {'✓ VALID' if result.valid else '✗ INVALID'}")
```

### Generate Compliance Report

```python
from agents.international_standards.agent import InternationalStandardsAgent
import json

agent = InternationalStandardsAgent()

# Generate comprehensive compliance report
report = agent.generate_compliance_report(
    "path/to/drawing.dwg",
    compliance_level="level_3"
)

# Save report to file
with open("logs/compliance_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("Compliance report generated!")
```

## Command Line Interface

### Validate a Drawing

```bash
python -m agents.international_standards.agent path/to/drawing.dwg
```

### Validate with Specific Standard

```bash
python -m agents.international_standards.agent path/to/drawing.dwg --standard "ISO 19115:2003"
```

### Generate Report

```bash
python -m agents.international_standards.agent path/to/drawing.dwg --report --output logs/report.json
```

### List Supported Standards

```bash
python -m agents.international_standards.agent --list-standards
```

### Full Command Line Options

```bash
python -m agents.international_standards.agent \
    path/to/drawing.dwg \
    --standard "ISO 19115:2003" \
    --config src/config/standards_config.yaml \
    --evotransdigi src/config/evotransdigi_config.yaml \
    --compliance-level level_3 \
    --report \
    --output logs/report.json \
    --debug
```

## Configuration

### Standards Configuration

Edit `src/config/standards_config.yaml` to enable/disable standards:

```yaml
standards:
  iso:
    enabled: true
    versions:
      - "ISO 19115:2003"
      - "ISO 19115-1:2014"
    required_fields:
      - title
      - abstract
      - date
  
  en:
    enabled: true
    versions:
      - "EN ISO 19115:2005"
      - "EN 1992-1-1:2004"
    required_fields:
      - standard_number
      - publication_date
      - scope
```

### EvoTransDigi Configuration

Edit `src/config/evotransdigi_config.yaml` for project-specific requirements:

```yaml
evotransdigi:
  enabled: true
  specific_standards:
    - "EvoTransDigi-STD-001:2024"
    - "EvoTransDigi-STD-002:2024"
  
  validation_rules:
    metadata:
      required:
        - project_id
        - version
        - timestamp
    
    drawing:
      required_layers:
        - "INFRASTRUCTURE"
        - "TRANSPORTATION"
        - "UTILITIES"
  
  compliance_levels:
    level_1:
      description: "Basic Compliance"
      checks:
        - metadata_complete
        - required_layers_present
    
    level_2:
      description: "Standard Compliance"
      checks:
        - all_level_1_checks
        - attribute_validation
        - geometric_accuracy
    
    level_3:
      description: "Advanced Compliance"
      checks:
        - all_level_2_checks
        - semantic_validation
        - cross_reference_check
```

## Work Protocols

### Automatic Protocol Generation

All validation activities are automatically logged to work protocols:

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Protocols are automatically generated
agent = InternationalStandardsAgent()
result = agent.validate_drawing("path/to/drawing.dwg")

# Protocols are saved in the logs/ directory
```

### Manual Protocol Management

```python
from src.utils.logger import start_protocol_session, end_protocol_session

# Start a new protocol session
session_id = start_protocol_session("validation_session_001")

# Perform validations
# ...

# End and save the session
protocol_path = end_protocol_session("validation_session_001")
print(f"Protocol saved to: {protocol_path}")
```

### Protocol File Format

Protocols are saved in both JSON and text formats:

**JSON Format (`logs/protocol_YYYYMMDD_HHMMSS.json`):**
```json
{
  "session": {
    "start_time": "2024-10-01T10:00:00",
    "end_time": "2024-10-01T10:05:00",
    "duration_seconds": 300
  },
  "entries": [
    {
      "timestamp": "2024-10-01T10:00:00",
      "level": "INFO",
      "logger": "InternationalStandardsAgent",
      "message": "Validation started",
      "module": "agent",
      "function": "validate_drawing",
      "line": 123
    }
  ]
}
```

**Text Format (`logs/protocol_YYYYMMDD_HHMMSS.txt`):**
```
================================================================================
WORK PROTOCOL - Agent-Infra-V1.0.1
================================================================================
Session: validation_session_001
Start Time: 2024-10-01T10:00:00
End Time: 2024-10-01T10:05:00
Duration: 300.00 seconds
================================================================================

PROTOCOL ENTRIES:
--------------------------------------------------------------------------------
[2024-10-01T10:00:00] INFO - Validation started
[2024-10-01T10:00:01] INFO - File format validated
[2024-10-01T10:00:02] INFO - Metadata extracted
[2024-10-01T10:00:03] INFO - ISO 19115 validation passed

--------------------------------------------------------------------------------
Total Entries: 4
================================================================================
```

## Examples

### Example 1: Simple Validation

```python
from agents.international_standards.agent import InternationalStandardsAgent

agent = InternationalStandardsAgent()
result = agent.validate_drawing("examples/sample.dwg")

print(f"Valid: {result.valid}")
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")
```

### Example 2: Batch Validation

```python
from agents.international_standards.agent import InternationalStandardsAgent
import os

agent = InternationalStandardsAgent()
drawings_dir = "drawings/"

for filename in os.listdir(drawings_dir):
    if filename.endswith(".dwg"):
        filepath = os.path.join(drawings_dir, filename)
        result = agent.validate_drawing(filepath)
        
        print(f"{filename}: {'✓ VALID' if result.valid else '✗ INVALID'}")
        if not result.valid:
            for error in result.errors:
                print(f"    - {error}")
```

### Example 3: Custom Configuration

```python
from agents.international_standards.agent import InternationalStandardsAgent, AgentConfig

# Create custom configuration
config = AgentConfig(
    default_standard="ISO 19115:2003",
    default_compliance_level="level_2",
    debug=True
)

# Initialize agent with configuration
agent = InternationalStandardsAgent()
agent.config = config

# Validate with custom settings
result = agent.validate_drawing("path/to/drawing.dwg")
```

### Example 4: Direct Standard Validation

```python
from agents.international_standards.standards.iso import ISOStandard

# Create ISO standard validator
iso_standard = ISOStandard(
    standard_number="ISO 19115:2003",
    title="Geographic Information - Metadata",
    publication_date="2003-01-01"
)

# Validate metadata
metadata = {
    "title": "Sample Drawing",
    "abstract": "A sample drawing for testing",
    "date": "2024-10-01",
    "organization": "EvoTransDigi"
}

result = iso_standard.validate_metadata(metadata)
print(f"ISO 19115 Validation: {result}")
```

## Troubleshooting

### Common Issues

1. **File Not Found**
   - Ensure the file path is correct
   - Check file permissions

2. **Unsupported File Format**
   - Supported formats: DWG, DXF, PDF, SVG, STEP, IGES
   - Install required libraries for specific formats

3. **Missing Required Fields**
   - Check the standard configuration for required fields
   - Add missing metadata to your drawing

4. **Invalid Standard**
   - List supported standards with `--list-standards`
   - Use a supported standard name

### Debug Mode

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Enable debug mode
agent = InternationalStandardsAgent(debug=True)
result = agent.validate_drawing("path/to/drawing.dwg")

# Debug information is logged to console
```

### Enable Detailed Logging

```python
from src.utils.logger import setup_logger
import logging

# Setup detailed logging
logger = setup_logger(
    name="AgentInfra",
    log_level=logging.DEBUG,
    log_file="logs/debug.log",
    console=True,
    protocol=True
)
```

## API Reference

### InternationalStandardsAgent

#### Methods

- `__init__(config_path=None, evotransdigi_config=None, debug=False)`: Initialize the agent
- `validate_drawing(filepath, standard=None, generate_report=False)`: Validate a drawing file
- `validate_with_evotransdigi(filepath, compliance_level="level_2")`: Validate with EvoTransDigi requirements
- `validate_against_multiple_standards(filepath, standards)`: Validate against multiple standards
- `generate_compliance_report(filepath, compliance_level="level_3", standards=None)`: Generate comprehensive report
- `save_report(report, output_path)`: Save report to file
- `get_supported_standards()`: Get list of supported standards
- `get_validation_rules(standard)`: Get validation rules for a standard

#### Attributes

- `config`: Current configuration
- `logger`: Logger instance
- `standards`: Dictionary of standard implementations
- `drawing_validator`: Drawing file validator
- `evotransdigi_validator`: EvoTransDigi validator

### Standard Classes

All standard classes (ISO, EN, DIN, ANSI, BSI) support:

- `validate_metadata(metadata)`: Validate metadata against standard
- `validate_coordinate_system(coordinate_system)`: Validate coordinate system
- `validate_quality(quality_data)`: Validate quality information
- `get_metadata_template()`: Get metadata template for the standard
- `from_dict(data)`: Create instance from dictionary
- `to_dict()`: Convert to dictionary

## Best Practices

1. **Always validate file format first**
2. **Use specific standards when possible**
3. **Start with lower compliance levels and increase**
4. **Review warnings for potential improvements**
5. **Save protocols for audit purposes**
6. **Use debug mode for troubleshooting**
7. **Regularly update configurations**

## Performance Tips

1. **Batch processing**: Validate multiple drawings in sequence
2. **Caching**: Cache validation results for unchanged files
3. **Parallel processing**: Use threading for large batch validations
4. **Selective validation**: Only validate against needed standards

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
