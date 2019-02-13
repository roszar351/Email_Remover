import email, poplib
from email.header import decode_header
from email import parser

try:
    pop_conn = poplib.POP3_SSL('link to email e.g. "https://mail.google.com"')
    pop_conn.user('username')
    pop_conn.pass_('password')
except poplib.error_proto:
    print("Failed to connect to email")
    pop_conn.quit()

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
        
        #print(parsed_email['From'])
        
        if parsed_email['From'] not in contactsToIgnore and parsed_email['From'] not in contactsToRemove:
            print(parsed_email['From'])
            print(parsed_email['Subject'])
            userInput = str(input("I - add to ignore list\nR - add to remove list\nD - delete this email\nAnything else - do nothing\n-> "))
            if userInput.lower() == "i":
                contactsToIgnore.append(parsed_email['From'])
            elif userInput.lower() == "r":
                contactsToRemove.append(parsed_email['From'])
            elif userInput.lower() == "d":
                pop_conn.dele(i)
                deleted += 1

        if parsed_email['From'] in contactsToRemove:
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
