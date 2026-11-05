import copy
import unittest

from campusflow.ticket import create_ticket
from campusflow.workflow import (
    find_ticket,
    assign_ticket,
    change_status,
)


class WorkflowTestCase(unittest.TestCase):

    def setUp(self):
        self.tickets = []

        self.ticket = create_ticket(
            self.tickets,
            "Campus Wi-Fi is down",
            "Network",
            "high",
            15
        )

    def make_ticket_in_progress(self):
        assign_ticket(self.tickets, "T001", "Samuel")
        change_status(self.tickets, "T001", "in_progress")

    def make_ticket_resolved(self):
        self.make_ticket_in_progress()
        change_status(self.tickets, "T001", "resolved")


class TestFindTicket(WorkflowTestCase):

    def test_find_existing_ticket(self):
        result = find_ticket(self.tickets, "T001")
        self.assertIs(result, self.ticket)

    def test_find_unknown_ticket(self):
        result = find_ticket(self.tickets, "T999")
        self.assertIsNone(result)

    def test_blank_ticket_id_rejected(self):
        with self.assertRaises(ValueError):
            find_ticket(self.tickets, " ")

    def test_invalid_ticket_id_type_rejected(self):
        with self.assertRaises(ValueError):
            find_ticket(self.tickets, None)

    def test_invalid_collection_rejected(self):
        with self.assertRaises(ValueError):
            find_ticket(None, "T001")

    def test_malformed_ticket_record_rejected(self):
        with self.assertRaises(ValueError):
            find_ticket([{"title": "Missing ID"}], "T001")

    def test_duplicate_ticket_ids_rejected(self):
        duplicate = copy.deepcopy(self.ticket)
        self.tickets.append(duplicate)

        with self.assertRaises(ValueError):
            find_ticket(self.tickets, "T001")


class TestTicketAssignment(WorkflowTestCase):

    def test_assign_ticket(self):
        result = assign_ticket(self.tickets, "T001", "Samuel")

        self.assertEqual(result["assigned_to"], "Samuel")

    def test_staff_name_is_trimmed(self):
        assign_ticket(self.tickets, "T001", "  Samuel  ")

        self.assertEqual(self.ticket["assigned_to"], "Samuel")

    def test_reassign_active_ticket(self):
        assign_ticket(self.tickets, "T001", "Samuel")
        assign_ticket(self.tickets, "T001", "James")

        self.assertEqual(self.ticket["assigned_to"], "James")

    def test_blank_staff_name_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", " ")

    def test_non_string_staff_name_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", None)

    def test_unknown_ticket_assignment_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T999", "Samuel")

    def test_resolved_ticket_cannot_be_reassigned(self):
        self.make_ticket_resolved()
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "James")

        self.assertEqual(self.tickets, before)

    def test_assignment_to_in_progress_ticket_allowed(self):
        self.make_ticket_in_progress()

        assign_ticket(self.tickets, "T001", "James")

        self.assertEqual(self.ticket["assigned_to"], "James")


class TestStatusTransitions(WorkflowTestCase):

    def test_unassigned_ticket_cannot_start(self):
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets, before)

    def test_assigned_ticket_can_start(self):
        assign_ticket(self.tickets, "T001", "Samuel")

        result = change_status(
            self.tickets, "T001", "in_progress"
        )

        self.assertEqual(result["status"], "in_progress")

    def test_open_ticket_cannot_skip_to_resolved(self):
        assign_ticket(self.tickets, "T001", "Samuel")
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "resolved")

        self.assertEqual(self.tickets, before)

    def test_ticket_can_be_resolved_after_work_starts(self):
        self.make_ticket_in_progress()

        result = change_status(
            self.tickets, "T001", "resolved"
        )

        self.assertEqual(result["status"], "resolved")

    def test_resolved_ticket_can_be_reopened(self):
        self.make_ticket_resolved()

        result = change_status(
            self.tickets, "T001", "open"
        )

        self.assertEqual(result["status"], "open")

    def test_reopening_preserves_assignee(self):
        self.make_ticket_resolved()

        change_status(self.tickets, "T001", "open")

        self.assertEqual(self.ticket["assigned_to"], "Samuel")

    def test_in_progress_ticket_cannot_return_to_open(self):
        self.make_ticket_in_progress()
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "open")

        self.assertEqual(self.tickets, before)

    def test_resolved_ticket_cannot_move_directly_to_in_progress(self):
        self.make_ticket_resolved()
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets, before)

    def test_repeated_status_transition_rejected(self):
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "open")

        self.assertEqual(self.tickets, before)

    def test_invalid_status_rejected(self):
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "pending")

        self.assertEqual(self.tickets, before)

    def test_non_string_status_rejected(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", None)

    def test_status_input_is_normalized(self):
        assign_ticket(self.tickets, "T001", "Samuel")

        change_status(self.tickets, "T001", " IN_PROGRESS ")

        self.assertEqual(self.ticket["status"], "in_progress")

    def test_unknown_ticket_status_change_rejected(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T999", "resolved")

    def test_invalid_existing_status_rejected(self):
        self.ticket["status"] = "pending"
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "open")

        self.assertEqual(self.tickets, before)

    def test_resolving_without_assignee_rejected(self):
        self.ticket["status"] = "in_progress"
        self.ticket["assigned_to"] = None
        before = copy.deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "resolved")

        self.assertEqual(self.tickets, before)


if __name__ == "__main__":
    unittest.main()