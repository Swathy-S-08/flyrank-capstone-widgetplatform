class NotFoundError(Exception):
    pass


class ValidationFailed(Exception):
    def __init__(self, fields: dict[str, str]):
        self.fields = fields
        super().__init__("Validation failed")
