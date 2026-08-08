from app.issue_intake import IssueIntake


def test_issue_intake_classifies_wrong_output() -> None:
    issue = IssueIntake().parse("Wrong output\nExpected None but got ZeroDivisionError")
    assert issue.title == "Wrong output"
    assert "wrong-output" in issue.labels or "runtime-error" in issue.labels
