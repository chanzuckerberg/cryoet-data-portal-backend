ANGLE_TOLERANCE = 0.05


# TODO FIXME account for double 0 sample
def helper_angles_injection_errors(
    domain_angles: list[float],
    codomain_angles: list[float],
    domain_name: str,
    codomain_name: str,
    angle_tolerance: float = ANGLE_TOLERANCE,
) -> list[str]:
    """Helper function to check if all angles in the domain are in the codomain."""
    errors = []
    remaining_angles = codomain_angles.copy()
    for domain_angle in domain_angles:
        found_match = False
        for codomain_angle in codomain_angles:
            if abs(domain_angle - codomain_angle) < angle_tolerance:
                found_match = True
                remaining_angles.remove(codomain_angle)
                break
        if not found_match:
            errors.append(
                f"No match found: Looking for angle {domain_angle} (from {domain_name}) in {codomain_name}",
            )
    if len(domain_angles) > len(codomain_angles):
        errors.append(
            f"More angles in {domain_name} than in {codomain_name} ({len(domain_angles)} vs {len(codomain_angles)})",
        )
    return errors
