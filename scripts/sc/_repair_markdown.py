from __future__ import annotations

from typing import Any


def render_repair_guide_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Repair Guide")
    lines.append("")
    lines.append(f"- status: {payload.get('status', 'unknown')}")
    lines.append(f"- task_id: {payload.get('task_id', '')}")
    lines.append(f"- summary_status: {payload.get('summary_status', '')}")
    lines.append(f"- failed_step: {payload.get('failed_step', '')}")
    lines.append("")
    approval = payload.get("approval") or {}
    approval_status = str(approval.get("status") or "").strip()
    if approval_status and approval_status != "not-needed":
        lines.append("## Approval")
        lines.append(f"- required_action: {approval.get('required_action', '')}")
        lines.append(f"- status: {approval_status}")
        lines.append(f"- decision: {approval.get('decision', '')}")
        reason = str(approval.get("reason") or "").strip()
        if reason:
            lines.append(f"- reason: {reason}")
        request_path = str(approval.get("request_path") or "").strip()
        response_path = str(approval.get("response_path") or "").strip()
        if request_path:
            lines.append(f"- request: `{request_path}`")
        if response_path:
            lines.append(f"- response: `{response_path}`")
        lines.append("")
    recommendations = payload.get("recommendations") or []
    if not recommendations:
        lines.append("No repair action is required. The pipeline either passed or only produced planned/skipped steps.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Recommendations")
    for item in recommendations:
        lines.append(f"- {item.get('id', '')}: {item.get('title', '')}")
        why = str(item.get("why") or "").strip()
        if why:
            lines.append(f"  Why: {why}")
        for command in item.get("commands") or []:
            lines.append(f"  Command: `{command}`")
        for file_path in item.get("files") or []:
            if str(file_path).strip():
                lines.append(f"  File: `{file_path}`")
    lines.append("")
    return "\n".join(lines)
