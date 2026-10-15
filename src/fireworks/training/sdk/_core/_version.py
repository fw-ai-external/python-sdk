from importlib.metadata import PackageNotFoundError, version

__title__ = "fireworks-ai"
try:
    __version__ = version(__title__)
except PackageNotFoundError:
    # Source-only namespace overlays have no installed distribution metadata.
    # The diagnostic package version is independent of the wire protocol.
    __version__ = "0+unknown"

# Bootstrap uses the existing protocol version until its contract changes.
PROTOCOL_CLIENT_VERSION = "0.23.0"
