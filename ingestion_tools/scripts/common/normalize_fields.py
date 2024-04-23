def normalize_fiducial_alignment(status: bool | str) -> str:
    # Grant jensen configs use true/false
    if status is True or status == "True":
        return "FIDUCIAL"
    if status is False or status == "False":
        return "NON_FIDUCIAL"
    # Everybody else uses proper values
    if status.upper() in ["FIDUCIAL", "NON_FIDUCIAL"]:
        return status.upper()
    # Any other values are not allowed.
    raise Exception("Fiducial alignment status must be FIDUCIAL or NON_FIDUCIAL")


def normalize_to_none_str(value: str) -> str:
    return value if value else "None"
