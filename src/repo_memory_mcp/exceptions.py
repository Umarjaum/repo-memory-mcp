class RepoMemoryError(Exception):
    """Base error for expected application failures."""
class DuplicateMemoryError(RepoMemoryError): pass
class MemoryNotFoundError(RepoMemoryError): pass
class SecretDetectedError(RepoMemoryError): pass
class InvalidImportError(RepoMemoryError): pass
class RepositoryDetectionError(RepoMemoryError): pass
