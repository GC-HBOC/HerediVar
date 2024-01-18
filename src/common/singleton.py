class Singleton(type):
    _instances = {}
    # override call method: how is the class instantiated
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Build new instance if we did not build one before
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            instance = cls._instances[cls]
            # neat little service:
            # reinitialization if the class has the attribute __allow_reinitialization set to true
            if hasattr(cls, '__allow_reinitialization') and cls.__allow_reinitialization:
                instance.__init__(*args, **kwargs)
        return instance