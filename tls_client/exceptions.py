class TLSClientException(IOError):
    """General error with the TLS client"""


class TLSClientExeption(IOError):
    """General error with the TLS client"""

    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn("TLSClientExeption is deprecated, use TLSClientException instead")
        super().__init__(*args, **kwargs)
