def validate_bool_kwarg(value, arg_name):
    """
    Ensures that argument passed in arg_name is of type bool.
    """
    if not (isinstance(value, bool) or value is None):
        raise ValueError(
            f'For argument "{arg_name}" expected type bool, received '
            f"type {type(value).__name__}."
        )
    return value
