# Agent-Infra-V1.0.1 - International Standards Agent

Ein Agent zur Überprüfung von Zeichnungsnormen in Architektur und Infrastrukturplanungen mit Fokus auf internationale Standards.

## Beschreibung

Dieser Agent unterstützt bei der Validierung und Überprüfung von Planungsdokumenten gegen internationale Normen und Standards wie:
- **ISO** (International Organization for Standardization)
- **EN** (Europäische Normen)
- **DIN** (Deutsches Institut für Normung)
- **ANSI** (American National Standards Institute)
- **BSI** (British Standards Institution)
- **EvoTransDigi** spezifische Anforderungen

## Struktur

```
Agent-Infra-V1.0.1/
├── agents/
│   └── international_standards/
│       ├── __init__.py
│       ├── agent.py          # Haupt-Agenten-Logik
│       └── standards/
│           ├── iso.py        # ISO-Standards
│           ├── en.py         # Europäische Normen
│           ├── din.py        # DIN-Normen
│           ├── ansi.py       # ANSI-Standards
│           └── bsi.py        # BSI-Standards
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── standards_config.yaml
│   │   └── evotransdigi_config.yaml
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_parser.py
│   │   ├── logger.py
│   │   └── helpers.py
│   └── validators/
│       ├── __init__.py
│       ├── drawing_validator.py
│       ├── norm_validator.py
│       └── schema_validator.py
├── docs/
│   ├── usage.md
│   ├── standards.md
│   └── evotransdigi_integration.md
├── examples/
│   ├── sample_drawing.dwg
│   ├── sample_config.json
│   └── validation_report.json
└── tests/
    ├── __init__.py
    ├── test_agent.py
    └── test_validators.py
```

## Installation

```bash
# Klonen des Repositorys
git clone https://github.com/btsniegel-evotransdigi/Agent-Infra-V1.0.1.git
cd Agent-Infra-V1.0.1

# Erstellen einer virtuellen Umgebung
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Installation der Abhängigkeiten
pip install -r requirements.txt
```

## Verwendung

### Grundlegende Verwendung

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Agent initialisieren
agent = InternationalStandardsAgent(config_path="src/config/standards_config.yaml")

# Zeichnung validieren
result = agent.validate_drawing("path/to/your/drawing.dwg")
print(result)
```

### Mit EvoTransDigi-Integration

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Agent mit EvoTransDigi-Konfiguration
agent = InternationalStandardsAgent(
    config_path="src/config/standards_config.yaml",
    evotransdigi_config="src/config/evotransdigi_config.yaml"
)

# Validierung mit EvoTransDigi-spezifischen Standards
result = agent.validate_with_evotransdigi("path/to/drawing.dwg")
```

## Konfiguration

### Standards-Konfiguration

Die Datei `src/config/standards_config.yaml` enthält die Definitionen der unterstützten Standards:

```yaml
standards:
  iso:
    enabled: true
    versions:
      - "ISO 19115:2003"
      - "ISO 19115-1:2014"
      - "ISO 19115-2:2019"
    required_fields:
      - title
      - abstract
      - date
      - organization
  
  en:
    enabled: true
    versions:
      - "EN ISO 19115:2005"
      - "EN 1991-1-1:2002"
    required_fields:
      - standard_number
      - publication_date
      - scope
  
  din:
    enabled: true
    versions:
      - "DIN EN ISO 19115:2005"
      - "DIN 1356-1:1995"
    required_fields:
      - norm_number
      - title
      - validity
  
  ansi:
    enabled: false
    versions:
      - "ANSI Z1.1-1996"
    required_fields:
      - standard_id
      - description
  
  bsi:
    enabled: false
    versions:
      - "BS EN ISO 19115:2005"
    required_fields:
      - standard_ref
      - issue_date
```

### EvoTransDigi-Konfiguration

Die Datei `src/config/evotransdigi_config.yaml` enthält EvoTransDigi-spezifische Anforderungen:

```yaml
evotransdigi:
  enabled: true
  
  # Spezifische Normen für EvoTransDigi
  specific_standards:
    - "EvoTransDigi-STD-001:2024"
    - "EvoTransDigi-STD-002:2024"
  
  # Erweiterte Validierungsregeln
  validation_rules:
    metadata:
      required:
        - project_id
        - version
        - timestamp
        - responsible_engineer
      optional:
        - review_status
        - approval_date
    
    drawing:
      required_layers:
        - "INFRASTRUCTURE"
        - "TRANSPORTATION"
        - "UTILITIES"
      required_attributes:
        - scale
        - coordinate_system
        - projection
    
  # Compliance-Ebenen
  compliance_levels:
    level_1:
      description: "Grundlegende Compliance"
      checks:
        - metadata_complete
        - required_layers_present
    
    level_2:
      description: "Erweiterte Compliance"
      checks:
        - all_level_1_checks
        - attribute_validation
        - geometric_accuracy
    
    level_3:
      description: "Volle Compliance"
      checks:
        - all_level_2_checks
        - semantic_validation
        - cross_reference_check
```

## Validierungsprozess

### 1. Metadaten-Validierung
- Überprüfung der erforderlichen Metadatenfelder
- Validierung der Standard-Versionen
- Zeitstempel- und Versionsprüfung

### 2. Zeichnungs-Validierung
- Vorhandensein der erforderlichen Layer
- Attributvalidierung
- Geometrische Genauigkeitsprüfung

### 3. Semantische Validierung
- Kreuzreferenzprüfung
- Konsistenzprüfung zwischen verschiedenen Zeichnungselementen
- Validierung gegen Domänen-spezifische Regeln

### 4. EvoTransDigi-spezifische Validierung
- Compliance mit EvoTransDigi-Standards
- Projekte-spezifische Anforderungen
- Erweiterte Metadaten-Validierung

## Beispiele

### Beispiel 1: Einfache Validierung

```python
from agents.international_standards.agent import InternationalStandardsAgent

agent = InternationalStandardsAgent()
result = agent.validate_drawing("examples/sample_drawing.dwg")

if result["valid"]:
    print("✓ Zeichnung ist gültig")
else:
    print("✗ Validierungsfehler:")
    for error in result["errors"]:
        print(f"  - {error}")
```

### Beispiel 2: Detaillierter Validierungsbericht

```python
from agents.international_standards.agent import InternationalStandardsAgent
import json

agent = InternationalStandardsAgent()
result = agent.validate_drawing(
    "examples/sample_drawing.dwg",
    generate_report=True
)

# Speichern des Berichts
with open("validation_report.json", "w") as f:
    json.dump(result, f, indent=2)

print("Validierungsbericht generiert!")
```

### Beispiel 3: Batch-Validierung

```python
from agents.international_standards.agent import InternationalStandardsAgent
import os

agent = InternationalStandardsAgent()
drawings_dir = "path/to/drawings"

# Alle DWG-Dateien im Verzeichnis validieren
for filename in os.listdir(drawings_dir):
    if filename.endswith(".dwg"):
        filepath = os.path.join(drawings_dir, filename)
        result = agent.validate_drawing(filepath)
        
        print(f"{filename}: {'✓ VALID' if result['valid'] else '✗ INVALID'}")
        if not result["valid"]:
            for error in result["errors"]:
                print(f"    - {error}")
```

## API-Referenz

### InternationalStandardsAgent

#### Methoden

- `__init__(config_path=None, evotransdigi_config=None)`: Initialisiert den Agenten
- `validate_drawing(filepath, standard=None, generate_report=False)`: Validiert eine Zeichnung
- `validate_with_evotransdigi(filepath, compliance_level="level_2")`: Validiert mit EvoTransDigi
- `get_supported_standards()`: Gibt unterstützte Standards zurück
- `get_validation_rules(standard)`: Gibt Validierungsregeln für einen Standard zurück
- `generate_compliance_report(filepath, compliance_level="level_3")`: Generiert einen Compliance-Bericht

#### Attribute

- `config`: Aktuelle Konfiguration
- `evotransdigi_config`: EvoTransDigi-Konfiguration
- `logger`: Logger-Instanz

## Fehlersuche

### Häufige Probleme

1. **Fehlende Metadaten**: Stellen Sie sicher, dass alle erforderlichen Metadatenfelder vorhanden sind
2. **Ungültige Standard-Version**: Überprüfen Sie, ob die angegebene Standard-Version unterstützt wird
3. **Fehlende Layer**: Die Zeichnung muss alle erforderlichen Layer enthalten
4. **Geometrische Ungenauigkeiten**: Die Koordinaten müssen den Genauigkeitsanforderungen entsprechen

### Debug-Modus

```python
from agents.international_standards.agent import InternationalStandardsAgent

# Debug-Modus aktivieren
agent = InternationalStandardsAgent(debug=True)
result = agent.validate_drawing("path/to/drawing.dwg")

# Detaillierte Debug-Informationen
print(agent.logger.get_debug_info())
```

## Mitwirken

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/neue-funktion`)
3. Commiten Sie Ihre Änderungen (`git commit -m 'Neue Funktion hinzugefügt'`)
4. Pushen Sie zum Branch (`git push origin feature/neue-funktion`)
5. Erstellen Sie einen Pull Request

## Lizenz

Dieses Projekt ist lizenziert unter der MIT-Lizenz - siehe die Datei [LICENSE](LICENSE) für Details.

## Kontakt

Für Fragen und Unterstützung:
- E-Mail: support@evotransdigi.de
- Website: https://www.evotransdigi.de

---

© 2024 EvoTransDigi. Alle Rechte vorbehalten.
