"""Ticket assignment and status workflow rules for CampusFlow."""

VALID_STATUSES = {"open", "in_progress", "resolved"}

VALID_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},
}


def find_ticket(tickets, ticket_id):
    """
    Find a ticket by ID.

    Raises:
        ValueError: If the collection or ID is invalid,
                    or if duplicate IDs make the result ambiguous.

    Returns:
        The matching ticket dictionary, or None if not found.
    """

    if not isinstance(tickets, list):
        raise ValueError("Tickets must be stored in a list")

    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID cannot be blank")

    ticket_id = ticket_id.strip()
    matches = []

    seen_ids = set()

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Every ticket must be a dictionary")

        current_id = ticket.get("id")

        if not isinstance(current_id, str) or not current_id.strip():
            raise ValueError("Every ticket must have a valid ID")

        if current_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID detected: {current_id}")

        seen_ids.add(current_id)

        if current_id == ticket_id:
            matches.append(ticket)

    if len(matches) > 1:
        raise ValueError(f"Multiple tickets found with ID {ticket_id}")

    return matches[0] if matches else None


def _validate_ticket_status(ticket):
    """Ensure the ticket has a valid current status."""

    status = ticket.get("status")

    if not isinstance(status, str) or status not in VALID_STATUSES:
        raise ValueError("Ticket has an invalid current status")

    return status


def _has_assignee(ticket):
    """Check whether a ticket has a valid staff assignment."""

    staff = ticket.get("assigned_to")

    return isinstance(staff, str) and bool(staff.strip())


def assign_ticket(tickets, ticket_id, staff_name):
    """
    Assign or reassign an active ticket to a staff member.

    Resolved tickets must be reopened before reassignment.
    """

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be blank")

    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError(f"Ticket {ticket_id} not found")

    status = _validate_ticket_status(ticket)

    if status == "resolved":
        raise ValueError(
            "Cannot change assignment on a resolved ticket; reopen it first"
        )

    ticket["assigned_to"] = staff_name.strip()

    return ticket


def change_status(tickets, ticket_id, new_status):
    """
    Change a ticket's status according to the allowed lifecycle.

    Allowed transitions:
        open -> in_progress
        in_progress -> resolved
        resolved -> open
    """

    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError(f"Ticket {ticket_id} not found")

    if not isinstance(new_status, str):
        raise ValueError("Status must be a string")

    new_status = new_status.strip().lower()

    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")

    current_status = _validate_ticket_status(ticket)

    allowed_transitions = VALID_TRANSITIONS[current_status]

    if new_status not in allowed_transitions:
        raise ValueError(
            f"Cannot move ticket from '{current_status}' to '{new_status}'"
        )

    # A ticket cannot begin work without an assignee.
    if new_status == "in_progress" and not _has_assignee(ticket):
        raise ValueError("Cannot start work on an unassigned ticket")

    # A ticket cannot be resolved without an assignee.
    if new_status == "resolved" and not _has_assignee(ticket):
        raise ValueError("Cannot resolve an unassigned ticket")

    # Mutate only after all validation succeeds.
    ticket["status"] = new_status

    return ticket