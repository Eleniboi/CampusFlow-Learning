from datetime import datetime


class Ticket:
    _next_id = 1
    VALID_CATEGORIES = ("network", "hardware", "software", "account")
    VALID_URGENCIES = ("low", "medium", "high")
    DEFAULT_STATUS = "open"
    TIME_FORMAT = "%d %b %Y, %H:%M"

    def __init__(self):
        self.id = f"T{Ticket._next_id:03d}"
        Ticket._next_id += 1

    def create_ticket(self):
        while True:
            title = input("Ticket title: ").strip()
            if title:
                break
            print("Invalid title. The title cannot be empty.")

        while True:
            category = input(
                f"Category ({'/'.join(Ticket.VALID_CATEGORIES)}): "
            ).strip().lower()
            if category in Ticket.VALID_CATEGORIES:
                break
            print(f"Invalid category '{category}'. Please enter one of: "
                  f"{', '.join(Ticket.VALID_CATEGORIES)}.")

        while True:
            urgency = input("Urgency (low/medium/high): ").strip().lower()
            if urgency in Ticket.VALID_URGENCIES:
                break
            print(f"Invalid urgency '{urgency}'. Please enter one of: "
                  f"{', '.join(Ticket.VALID_URGENCIES)}.")

        while True:
            raw = input("Affected users: ").strip()
            try:
                affected_users = int(raw)
            except ValueError:
                print(f"Invalid affected users '{raw}'. Please enter a whole number.")
                continue
            if affected_users <= 0:
                print(f"Invalid affected users '{raw}'. The number must be positive.")
                continue
            break

        ticket = {
            "id": self.id,
            "title": title,
            "category": category,
            "urgency": urgency,
            "affected_users": affected_users,
            "status": Ticket.DEFAULT_STATUS,
            "created_at": datetime.now().strftime(Ticket.TIME_FORMAT),
        }
        return ticket