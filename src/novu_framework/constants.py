from enum import Enum

from . import __version__

SDK_VERSION = __version__

# https://github.com/novuhq/novu/blob/next/packages/framework/tsup.config.ts#L18
FRAMEWORK_VERSION = "2024-06-26"


class GetActionEnum(str, Enum):
    """Enumeration of supported GET actions."""

    DISCOVER = "discover"
    HEALTH_CHECK = "health-check"
    CODE = "code"
