from typing import Dict, Any, Tuple

VALIDATED_DOMAINS = {
    "wall_thickness": (0.05, 0.80),
    "roof_thickness": (0.05, 0.60),
    "length": (2.0, 18.0),
    "width": (2.0, 15.0),
    "height": (2.0, 5.5),
    "orientation": (0.0, 360.0),
    "insulation_thickness": (0.0, 0.25),
    "outdoor_temperature": (-30.0, 50.0),
    "humidity": (5.0, 95.0),
    "solar_radiation": (0.0, 1200.0),
    "wind_speed": (0.0, 35.0)
}

def check_input_domain(inputs: Dict[str, Any]) -> Tuple[bool, str]:
    violations = []
    for param, (min_val, max_val) in VALIDATED_DOMAINS.items():
        if param in inputs:
            val = float(inputs[param])
            if val < min_val or val > max_val:
                violations.append(f"{param} ({val}) is outside validated domain [{min_val}, {max_val}]")

    if violations:
        msg = "Warning: Candidate inputs extend outside validated surrogate model domain: " + "; ".join(violations)
        return True, msg
    return False, ""
