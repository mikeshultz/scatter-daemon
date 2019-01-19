# flake8: noqa
class ScatterError(Exception): pass
class ConfigurationError(ScatterError): pass
class StorageError(ScatterError): pass
class ValidatorError(ScatterError): pass
