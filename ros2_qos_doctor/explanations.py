from typing import Iterable, List

from ros2_qos_doctor.compatibility import CompatibilityIssue


def problem_lines(issues: Iterable[CompatibilityIssue]) -> List[str]:
    return [issue.message for issue in issues]


def suggested_fix_lines(issues: Iterable[CompatibilityIssue]) -> List[str]:
    seen = set()
    fixes: List[str] = []
    for issue in issues:
        if issue.suggested_fix not in seen:
            fixes.append(issue.suggested_fix)
            seen.add(issue.suggested_fix)
    return fixes
