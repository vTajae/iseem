class BaseService:
    def copy_non_null_properties(self, source, target):
        for key, value in vars(source).items():
            if value is not None:
                setattr(target, key, value)
