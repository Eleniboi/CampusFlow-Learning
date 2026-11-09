"""Reporting for CampusFlow: counts tickets by status and priority."""

from .workflow import VALID_STATUSES

# DECISION: display order for each breakdown (fixed, so output is predictable).
STATUS_ORDER = ("open", "in_progress", "resolved")
PRIORITY_ORDER = ("critical", "high", "medium", "low")


def build_report(tickets):
    """
    Count tickets by status and priority.

    Returns a dict (easy to unit test):
        {
            "total": int,
            "by_status": {"open": int, "in_progress": int, "resolved": int},
            "by_priority": {"critical": int, "high": int, "medium": int, "low": int},
        }

    Raises:
        ValueError: If the collection is not a list, or a ticket is
                    malformed (not a dict, bad status, or bad priority).
    """

    if not isinstance(tickets, list):
        raise ValueError("Tickets must be stored in a list")

    # DECISION: every status/priority starts at 0, so an empty list still
    # produces a full report instead of an empty one.
    by_status = {status: 0 for status in STATUS_ORDER}
    by_priority = {priority: 0 for priority in PRIORITY_ORDER}

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Every ticket must be a dictionary")

        status = ticket.get("status")
        priority = ticket.get("priority")

        # DECISION: bad data raises an error (same style as workflow.py)
        # instead of being silently counted as "unknown".
        if status not in VALID_STATUSES:
            raise ValueError(f"Ticket has an invalid status: {status}")

        if priority not in by_priority:
            raise ValueError(f"Ticket has an invalid priority: {priority}")

        by_status[status] += 1
        by_priority[priority] += 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }


def format_report(report):
    """Turn a report dict from build_report() into printable text."""

    lines = [f"Total tickets: {report['total']}", "", "By status:"]

    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")

    lines.append("")
    lines.append("By priority:")

    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")

    return "\n".join(lines)