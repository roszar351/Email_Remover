# Email Remover
Connects to provided email service with the given username and password then goes through all emails(starting with newest) and asks user if they want to delete the email, ignore it or add the contact that sent the email to ignore list, or add it to remove list and then deletes any email sent from a contact that is in the remove list, program can be stopped early by pressing sending a keyboard interupt(ctrl+c) and will save the lists to files which will be loaded next time the program is executed.

## 2-step authentication problem
If your email is protected by a 2-step authentication, you might not be able to log in or be required to set up a special password that lets you log in e.g. gmail(https://support.google.com/accounts/answer/185833)
