
def main():

    exist = False
    while not exist:
        print("===WECOME TO CAMPUS FLOW NEXT===")
        print("1. Create Ticket")
        print("2. List all tickets")
        print("3. View ticket details")
        print("4. Assign ticket")
        print("5. Change status")
        print("6. Show work queue")
        print("7. Show reports")
        print("8. Exit")

        choice = input("Choose Number 1 to 8 :")

        if choice == "8":
            print("Goodbye!!")
            exist = True

if __name__ == "__main__":
    main()