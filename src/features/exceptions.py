from src.core.exceptions import FintechBaseException


class FeatureEngineeringError(FintechBaseException):
    pass


class TransformationError(FeatureEngineeringError):
    pass


class EncodingError(FeatureEngineeringError):
    pass


class ScalingError(FeatureEngineeringError):
    pass


class SelectionError(FeatureEngineeringError):
    pass
