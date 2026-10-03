"""
Web interface for the International Standards Agent.

Provides a Flask web app that lets users validate drawing metadata
against international standards (ISO, EN, DIN, ANSI, BSI) and
EvoTransDigi-specific requirements.
"""

import json
import os
import sys

from flask import Flask, request, jsonify, render_template

# Ensure repo root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.international_standards.agent import InternationalStandardsAgent

app = Flask(__name__)

# Initialize agent with both config files
agent = InternationalStandardsAgent(
    config_path="src/config/standards_config.yaml",
    evotransdigi_config="src/config/evotransdigi_config.yaml",
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/standards")
def get_standards():
    """Return all supported standard versions."""
    standards = agent.get_supported_standards()
    return jsonify({"standards": standards})


@app.route("/api/standard-categories")
def get_standard_categories():
    """Return standards grouped by category with their validation rules."""
    categories = {}
    for name, config_key in [
        ("ISO", "iso"), ("EN", "en"), ("DIN", "din"),
        ("ANSI", "ansi"), ("BSI", "bsi"),
    ]:
        cfg = getattr(agent.config, f"{config_key}_config")
        categories[name] = {
            "versions": cfg.versions,
            "required_fields": cfg.required_fields,
            "optional_fields": cfg.optional_fields,
            "enabled": cfg.enabled,
        }
    if agent.config.evotransdigi_config:
        etd = agent.config.evotransdigi_config
        categories["EvoTransDigi"] = {
            "versions": etd.get("specific_standards", []),
            "required_fields": etd.get("validation_rules", {}).get("metadata", {}).get("required", []),
            "optional_fields": etd.get("validation_rules", {}).get("metadata", {}).get("optional", []),
            "enabled": etd.get("enabled", True),
        }
    return jsonify(categories)


@app.route("/api/compliance-levels")
def get_compliance_levels():
    """Return EvoTransDigi compliance level definitions."""
    if agent.config.evotransdigi_config:
        levels = agent.config.evotransdigi_config.get("compliance_levels", {})
        return jsonify(levels)
    return jsonify({})


@app.route("/api/validate", methods=["POST"])
def validate():
    """Validate metadata against a single standard."""
    data = request.get_json(force=True)
    metadata = data.get("metadata", {})
    standard = data.get("standard")
    if not standard:
        return jsonify({"error": "No standard specified"}), 400
    result = agent._validate_against_standard(metadata, standard)
    return jsonify(result.to_dict())


@app.route("/api/validate-all", methods=["POST"])
def validate_all():
    """Validate metadata against every supported standard."""
    data = request.get_json(force=True)
    metadata = data.get("metadata", {})
    standards = agent.get_supported_standards()
    results = {}
    for s in standards:
        result = agent._validate_against_standard(metadata, s)
        results[s] = result.to_dict()
    return jsonify(results)


@app.route("/api/validate-evotransdigi", methods=["POST"])
def validate_evotransdigi():
    """Validate metadata against EvoTransDigi requirements."""
    data = request.get_json(force=True)
    metadata = data.get("metadata", {})
    compliance_level = data.get("compliance_level", "level_2")
    if not agent.evotransdigi_validator:
        return jsonify({"error": "EvoTransDigi validator not initialized"}), 400
    result = agent.evotransdigi_validator.validate_metadata(metadata, compliance_level)
    return jsonify(result.to_dict())


@app.route("/api/example")
def get_example():
    """Return the sample configuration for quick loading."""
    example_path = os.path.join(os.path.dirname(__file__), "examples", "sample_config.json")
    with open(example_path, "r") as f:
        return jsonify(json.load(f))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
