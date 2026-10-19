import json 

class Ticket:


    def create_ticket():
        ticket_map = {}

        title = input("enter title: ")
        categories = input("choose categories(Hardware/software/Electronic/Other): ")
        urgency = input("Urgency (low/high/critical): ")
        affected_users = input("affected users: ")

        ticket_map = {

            "title":title
            "categories":categories
            "urgency":urgency
            "affected_users":affected_users
        }
