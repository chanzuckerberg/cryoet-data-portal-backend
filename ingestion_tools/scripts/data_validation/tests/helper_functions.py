from typing import List

ANGLE_TOLERANCE = 0.01


def helper_angles_injection(
    domain_angles: List[float],
    codomain_angles: List[float],
    domain_name: str,
    codomain_name: str,
) -> List[str]:
    """Helper function to check if all angles in the domain are in the codomain."""
    errors = []
    remaining_angles = codomain_angles.copy()
    for domain_angle in domain_angles:
        found_match = False
        for codomain_angle in codomain_angles:
            if abs(domain_angle - codomain_angle) < ANGLE_TOLERANCE:
                found_match = True
                remaining_angles.remove(codomain_angle)
                break
        if not found_match:
            errors.append(f"No match found: Looking for angle {domain_angle} (from {domain_name}) in {codomain_name}")
    if len(domain_angles) > len(codomain_angles):
        errors.append(
            f"More angles in {domain_name} than in {codomain_name} ({len(domain_angles)} vs {len(codomain_angles)})",
        )
    return errors


def helper_angles_one_to_one(
    domain_angles: List[float],
    codomain_angles: List[float],
    domain_name: str,
    codomain_name: str,
) -> List[str]:
    """Helper function to check if all angles in the domain are in the codomain and vice versa."""
    injection_errors = helper_angles_injection(domain_angles, codomain_angles, domain_name, codomain_name)
    surjection_errors = helper_angles_injection(codomain_angles, domain_angles, codomain_name, domain_name)
    return injection_errors + surjection_errors
