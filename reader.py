import email, poplib, getpass
import re
from email.header import decode_header
from email import parser


poplib._MAXLINE=20480
emailWebsite = input("Enter your email website: ")
username = input("Enter your username: ")
password = getpass.getpass("Enter password: ")
loggedIn = True

try:
    pop_conn = poplib.POP3_SSL(emailWebsite)
    pop_conn.user(username)
    pop_conn.pass_(password)
except poplib.error_proto as detail:
    print("Failed to connect to email")
    print("ERROR: ", detail)
    loggedIn = False
    pop_conn.quit()

if loggedIn:
    deleted = 0

    contactsToRemove = []
    contactsToIgnore = []
    try:
        with open("remove_list.txt", 'r') as f:
            contactsToRemove = [line.rstrip('\n') for line in f]

        with open("ignore_list.txt", 'r') as f:
            contactsToIgnore = [line.rstrip('\n') for line in f]
    except FileNotFoundError:
        print("Nothing to load...Continuing")

    numMessages = len(pop_conn.list()[1])
    print("You have {} messages".format(numMessages))

    try:
        for i in range(numMessages, 1, -1):
            userInput = ""
            
            raw_email  = b"\n".join(pop_conn.retr(i)[1])
            parsed_email = email.message_from_bytes(raw_email)
            
            # print(parsed_email['From'])
            
            fromEmail = re.search(r'<.*>', parsed_email['From'])
            if(fromEmail != None):
                fromEmail = fromEmail.group(0)
            else:
                fromEmail = parsed_email['From']

            if fromEmail not in contactsToIgnore and fromEmail not in contactsToRemove:
                print(parsed_email['From'])
                print(parsed_email['Subject'])
                userInput = str(input("I - add to ignore list\nR - add to remove list\nD - delete this email\nAnything else - do nothing\n-> "))
                if userInput.lower() == "i":
                    contactsToIgnore.append(fromEmail)
                elif userInput.lower() == "r":
                    contactsToRemove.append(fromEmail)
                elif userInput.lower() == "d":
                    pop_conn.dele(i)
                    deleted += 1

            if fromEmail in contactsToRemove:
                pop_conn.dele(i)
                deleted += 1
            
            if i % 500 == 0:
                print("Currently on message %d" % i)
            
            #if userInput.lower() == "stop":
            #    break
    except KeyboardInterrupt:
        print("Interrupted program")
    finally:
        print("Deleted {} messages!".format(deleted))
        pop_conn.quit()
        with open('remove_list.txt', 'w') as f:
            for item in contactsToRemove:
                f.write("%s\n" % item)
        with open('ignore_list.txt', 'w') as f:
            for item in contactsToIgnore:
                f.write("%s\n" % item)
