from app.privacy_auditor import PrivacyAuditor


def test_privacy_auditor_detects_email() -> None:
    report = PrivacyAuditor().audit_trace(({"message": "contact me at user@example.com"},))
    assert report.leakage_count == 1
    assert report.privacy_score < 1.0
