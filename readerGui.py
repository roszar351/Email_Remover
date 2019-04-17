import email, poplib, getpass
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkm
import re
from tkinter.messagebox import showinfo
from time import sleep
from email.header import decode_header
from email import parser

class loginWindow(tk.Frame):

    def __init__(self, master):
        super().__init__(master)
        #self.mast = master
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack(expand=True, fill=tk.BOTH)

        self.labelFrame = tk.Frame(self.mainFrame)
        self.labelFrame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.l1 = tk.Label(self.labelFrame, text="Email website: ")
        self.l1.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.l2 = tk.Label(self.labelFrame, text="Username: ")
        self.l2.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.l3 = tk.Label(self.labelFrame, text="Password: ")
        self.l3.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.entryFrame = tk.Frame(self.mainFrame)
        self.entryFrame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.e1 = tk.Entry(self.entryFrame)
        self.e1.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.e2 = tk.Entry(self.entryFrame)
        self.e2.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.e3 = tk.Entry(self.entryFrame, show='*')
        self.e3.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.b1 = tk.Button(self.labelFrame, text="Login", command=self.loginIntoEmail)
        self.b1.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.b2 = tk.Button(self.entryFrame, text="Quit", command=self.quit)
        self.b2.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.pack()

    def loginIntoEmail(self):
        try:
            pop_conn = poplib.POP3_SSL(self.e1.get())
            pop_conn.user(self.e2.get())
            pop_conn.pass_(self.e3.get())
            self.destroy()
            self = mainWindow(self.master, pop_conn)
        except poplib.error_proto as detail:
            print("Failed to connect to email")
            print("ERROR: ", detail)
            top = tk.Toplevel()
            top.title("ERROR")
            msg = tk.Message(top, text="Failed to log in...\nCheck console for more details.")
            msg.pack(expand=True, fill=tk.BOTH)
            button = tk.Button(top, text="Close", command=top.destroy)
            button.pack(expand=True, fill=tk.BOTH)
            pop_conn.quit()
        #except:
        #    print("I don't know what happened :(")
    def on_closing(self):
        self.master.delete()
        self.quit()
        self.destroy()

class mainWindow(tk.Frame):

    def __init__(self, master, pop_conn):
        super().__init__(master)
        
        self.needAction = False
        self.fromEmail = ""
        self.indOfCurrentMsg = 0
        self.deleted = 0
        self.contactsToRemove = []
        self.contactsToIgnore = []

        self.whichButton = [False for i in range(4)]
        self.pop_conn = pop_conn
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack(expand=True, fill=tk.BOTH)

        self.mainLabel = tk.Label(self.mainFrame, text="Hello Im a placeholder text!")
        self.mainLabel.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.progress = ttk.Progressbar(self.mainFrame, mode="determinate")
        self.progress.pack(side=tk.TOP, expand=True, fill=tk.X)

        self.buttonFrame1 = tk.Frame(self.mainFrame)
        self.buttonFrame1.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.buttonFrame2 = tk.Frame(self.mainFrame)
        self.buttonFrame2.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.b1 = tk.Button(self.buttonFrame1, text="Add to remove", state=tk.DISABLED, command=self.addToRemove)
        self.b1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.b2 = tk.Button(self.buttonFrame1, text="Add to ignore", state=tk.DISABLED, command=self.addToIgnore)
        self.b2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.b3 = tk.Button(self.buttonFrame1, text="Delete", state=tk.DISABLED, command=self.deleteM)
        self.b3.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.b4 = tk.Button(self.buttonFrame2, text="Continue", state=tk.DISABLED, command=self.continueM)
        self.b4.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.pack()
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        master.bind('r', self.addToRemove)
        master.bind('d', self.deleteM)
        master.bind('c', self.continueM)
        master.bind('i', self.addToIgnore)
        self.master = master
        self.startReading()
        self.nextMessage()
    
    def startReading(self):
        try:
            with open("remove_list.txt", 'r') as f:
                self.contactsToRemove = [line.rstrip('\n') for line in f]

            with open("ignore_list.txt", 'r') as f:
                self.contactsToIgnore = [line.rstrip('\n') for line in f]
        except FileNotFoundError:
            print("Nothing to load...Continuing")

        numMessages = len(self.pop_conn.list()[1])
        self.progress["maximum"] = numMessages
        self.indOfCurrentMsg = numMessages

    def nextMessage(self):
        if not self.needAction:
            self.mainLabel.config(text="Currently on message {}, deleted {}\nNo action required.".format(self.progress['maximum'] - self.indOfCurrentMsg, self.deleted))
            self.update()
            raw_email  = b"\n".join(self.pop_conn.retr(self.indOfCurrentMsg)[1])
            parsed_email = email.message_from_bytes(raw_email)

            self.fromEmail = re.search(r'<.*>', str(parsed_email['From']))
            if(self.fromEmail != None):
                self.fromEmail = self.fromEmail.group(0)
            else:
                self.fromEmail = parsed_email['From']

            # Action needed
            if self.fromEmail not in self.contactsToIgnore and self.fromEmail not in self.contactsToRemove:
                self.mainLabel.config(text=parsed_email['From'] + "\n" + parsed_email['Subject'])
                self.activateAllButtons()
                self.needAction = True
                self.nextMessage()
            else:
                if self.fromEmail in self.contactsToRemove:
                    self.pop_conn.dele(self.indOfCurrentMsg)
                    self.deleted += 1

                self.indOfCurrentMsg -= 1
                self.progress["value"] = self.progress["maximum"] - self.indOfCurrentMsg

                if self.indOfCurrentMsg <= 0:
                    self.mainLabel.config(text="Deleted {} messages!".format(self.deleted))
                    self.pop_conn.quit()
                    self.saveToFile()
                    self.deactivateAllButtons()
                
                self.nextMessage()
        else:
            if self.whichButton[3]:
                self.contactsToIgnore.append(self.fromEmail)
                self.needAction = False
                self.whichButton[3] = False
                self.saveToFile()
            elif self.whichButton[2]:
                self.contactsToRemove.append(self.fromEmail)
                self.needAction = False
                self.whichButton[2] = False
                self.saveToFile()
            elif self.whichButton[1]:
                self.pop_conn.dele(self.indOfCurrentMsg)
                self.deleted += 1
                self.needAction = False
                self.whichButton[1] = False
            elif self.whichButton[0]:
                self.needAction = False
                self.whichButton[2] = False

            if not self.needAction:
                if self.fromEmail in self.contactsToRemove:
                    self.pop_conn.dele(self.indOfCurrentMsg)
                    self.deleted += 1

                self.indOfCurrentMsg -= 1
                self.progress["value"] = self.progress["maximum"] - self.indOfCurrentMsg

                if self.indOfCurrentMsg <= 0:
                    self.mainLabel.config(text="Deleted {} messages!".format(self.deleted))
                    self.pop_conn.quit()
                    self.saveToFile()
                    self.deactivateAllButtons()
                
                self.nextMessage()

        pass
        
    def saveToFile(self):
        try:
            with open('remove_list.txt', 'w') as f:
                    for item in self.contactsToRemove:
                        f.write("%s\n" % item)
            with open('ignore_list.txt', 'w') as f:
                for item in self.contactsToIgnore:
                    f.write("%s\n" % item)
        except:
            print("Failed to save to file")
            
        pass
    
    def activateAllButtons(self):
        self.b1.config(state=tk.NORMAL)
        self.b2.config(state=tk.NORMAL)
        self.b3.config(state=tk.NORMAL)
        self.b4.config(state=tk.NORMAL)
        pass

    def deactivateAllButtons(self):
        self.b1.config(state=tk.DISABLED)
        self.b2.config(state=tk.DISABLED)
        self.b3.config(state=tk.DISABLED)
        self.b4.config(state=tk.DISABLED)
        pass

    # b3
    def deleteM(self, _event=None):
        if self.b3['state'] != 'disabled':
            self.deactivateAllButtons()
            self.whichButton[1] = True
            self.nextMessage()
        pass

    # b1
    def addToRemove(self, _event=None):
        if self.b1['state'] != 'disabled':
            self.deactivateAllButtons()
            self.whichButton[2] = True
            self.nextMessage()
        pass

    # b2
    def addToIgnore(self, _event=None):
        if self.b2['state'] != 'disabled':
            self.deactivateAllButtons()
            self.whichButton[3] = True
            self.nextMessage()
        pass

    # b4
    def continueM(self, _event=None):
        if self.b4['state'] != 'disabled':
            self.deactivateAllButtons()
            self.whichButton[0] = True
            self.nextMessage()
        pass

    def on_closing(self):
        self.mainLabel.config(text="Deleted {} messages!".format(self.deleted))
        print("Deleted {} messages!".format(self.deleted))
        self.saveToFile()
        self.pop_conn.quit()
        self.quit()
        self.destroy()

if __name__ == "__main__":
    poplib._MAXLINE=20480

    root = tk.Tk()
    lf = loginWindow(root)
    #lf = mainWindow(root)

    root.mainloop()
    pass
