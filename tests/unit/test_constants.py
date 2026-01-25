from novu_framework import constants


class TestConstants:
    """Test cases for constants defined in novu_framework.constants."""

    def test_sdk_version_matches_package_version(self):
        """Test that SDK_VERSION matches the package __version__."""
        # Import the package version to compare
        from novu_framework import __version__

        assert constants.SDK_VERSION == __version__

    def test_framework_version_value(self):
        """Test that FRAMEWORK_VERSION has the expected value."""
        assert constants.FRAMEWORK_VERSION == "2024-06-26"

    def test_get_action_enum_values(self):
        """Test GetActionEnum has all expected values."""
        assert constants.GetActionEnum.DISCOVER == "discover"
        assert constants.GetActionEnum.HEALTH_CHECK == "health-check"
        assert constants.GetActionEnum.CODE == "code"

    def test_get_action_enum_is_string_enum(self):
        """Test that GetActionEnum is a string enum."""
        assert issubclass(constants.GetActionEnum, str)
        assert str(constants.GetActionEnum.DISCOVER.value) == "discover"
