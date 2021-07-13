
class NonInstantiableClass(Exception):
    """
    This error is thrown, whenever a static class is initialized
    """
    def __init__(self, class_name: str):
        self.message = f"{class_name} cannot be instantiated as it is a static class"
        super().__init__(self.message)
