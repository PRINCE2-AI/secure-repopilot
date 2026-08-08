from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.runner import FullCycleRunner


st.set_page_config(page_title="Secure RepoPilot", page_icon="SR", layout="wide")
st.title("Secure RepoPilot")
st.caption("Issue-to-PR coding agent with baseline verification, safety checks, and privacy auditing.")

default_repo = str(Path(__file__).resolve().parents[1] / "examples" / "buggy_python_repo")
repo_path = st.sidebar.text_input("Repository path", value=default_repo)
workspace = st.sidebar.text_input("Scratch workspace", value="")
apply_patch = st.sidebar.checkbox("Apply patch in scratch workspace", value=True)
issue_text = st.text_area(
    "Issue",
    value="Division by zero should return None\n\nThe divide(a, b) helper currently raises ZeroDivisionError when b is 0. Expected behavior is to return None.",
    height=140,
)

if st.button("Run full cycle", type="primary"):
    scratch = workspace.strip() or str(Path(repo_path).resolve().parent / ".repopilot-runs")
    run = FullCycleRunner().run(repo_path, issue_text, apply_patch=apply_patch, workspace=scratch)
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Verdict")
        st.json(
            {
                "verdict": run.judge.verdict.value,
                "confidence": run.judge.confidence,
                "safety_risk": run.safety.risk_score,
                "privacy_score": run.privacy.privacy_score,
            }
        )
        st.subheader("Changed Files")
        st.write(list(run.patch.changed_files) or "No files changed")
    with right:
        st.subheader("Tests")
        st.write("Baseline")
        st.dataframe([test.__dict__ for test in run.reproduction.baseline_runs], use_container_width=True)
        st.write("Patched")
        st.dataframe([test.__dict__ for test in run.patched_runs], use_container_width=True)
    st.subheader("Patch Diff")
    st.code(run.patch.diff or "No diff", language="diff")
    st.subheader("PR Report")
    st.markdown(run.report_markdown)
else:
    st.info("Use the bundled sample repo for a deterministic demo.")
