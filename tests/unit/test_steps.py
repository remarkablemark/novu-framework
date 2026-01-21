from novu_framework.steps.email import EmailStep
from novu_framework.steps.in_app import InAppStep
from novu_framework.steps.push import PushStep
from novu_framework.steps.sms import SmsStep


def test_email_step_initialization():
    """Test EmailStep initialization."""

    def resolver():
        return {"email": "sent"}

    options = {"provider": "sendgrid"}
    step = EmailStep("email-step", resolver, options)

    assert step.step_id == "email-step"
    assert step.resolver == resolver
    assert step.options == options
    assert step.step_type == "EMAIL"


def test_email_step_initialization_minimal():
    """Test EmailStep initialization with minimal parameters."""

    def resolver():
        return {"email": "sent"}

    step = EmailStep("minimal-email", resolver)

    assert step.step_id == "minimal-email"
    assert step.resolver == resolver
    assert step.options == {}


def test_in_app_step_initialization():
    """Test InAppStep initialization."""

    def resolver():
        return {"in_app": "notification"}

    step = InAppStep("inapp-step", resolver)

    assert step.step_id == "inapp-step"
    assert step.resolver == resolver
    assert step.options == {}
    assert step.step_type == "IN_APP"


def test_push_step_initialization():
    """Test PushStep initialization."""

    def resolver():
        return {"push": "notification"}

    step = PushStep("push-step", resolver)

    assert step.step_id == "push-step"
    assert step.resolver == resolver
    assert step.options == {}
    assert step.step_type == "PUSH"


def test_sms_step_initialization():
    """Test SmsStep initialization."""

    def resolver():
        return {"sms": "sent"}

    step = SmsStep("sms-step", resolver)

    assert step.step_id == "sms-step"
    assert step.resolver == resolver
    assert step.options == {}
    assert step.step_type == "SMS"
