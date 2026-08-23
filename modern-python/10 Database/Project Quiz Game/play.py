import sqlite3
import sys
def admin_operation():
    print("1. Add Question \n2. Amend Question \n3. Amend Answer \n4. Amend Options")
    ch= int(input("Choose Option: "))
    try:
        con = sqlite3.connect("Storage.db")
        cur=con.cursor()
        cur.execute("CREATE DATABASE quiz")
        con.commit()
        con.close()
    except:
        pass
    
    try:
        con = sqlit3.connect("Storage.db")
        cur=con.cursor()
        cur.execute('''CREATE TABLE science(SrNo INT(5),Question TEXT,
                       Option1 VARCHAR(30), Option2 VARCHAR(30),
                       Option3 VARCHAR(30), Option4 VARCHAR(30),
                       Answer INT(5))''')
        con.commit()
        con.close()
    except:
        pass
    if ch==1:
        qno = input("Enter the question no.: ")
        ques = input("Enter the question: ")
        opt1,opt2,opt3,opt4 = input("Enter all 4 options: ").split(',')
        ans = input("Enter correct option no.: ")
        con = sqlite3.connect('Storage.db')
        cur = con.cursor()
        cur.execute(f"INSERT INTO science VALUES({qno},'{ques}','{opt1}','{opt2}','{opt3}','{opt4}',{ans})")
        #cur.execute("INSERT INTO science VALUES("+qno+",'"+ques+"','"+opt1+"','"+opt2+"','"+opt3+"','"+opt4+"','"+ans+"')")
        con.commit()
        con.close()
    elif ch==2:
        qno = int(input("Enter the question no.: "))
        cur.execute(f"SELECT * FROM science WHERE SrNo={qno}")
        for i in cursor:
            print(f"SrNo{i[0]}: {i[1]}")
        que = input("Enter correct question: ")
        con = sqlite3.connect('Storage.db')
        cur = con.cursor()
        cur.execute(f"UPDATE science SET Question ='{que}' WHERE SrNo={qno}")
        con.commit()
        con.close()
    elif ch==3:
        qno = int(input("Enter the Question No."))
        cur.execute(f"SELECT * FROM science WHERE SrNo={qno}")
        for i in cursor:
            print(f"SrNo{i[0]}: {i[1]} \nOption1:{i[2]} \nOption2:{i[3]} \nOption3:{i[4]} \nOption4:{i[5]} \nAnswer:{i[6]}")
        ans = input("Enter correct option no.: ")
        sqlite3.connect('Storage.db')
        cur = con.cursor()
        cur.execute(f"UPDATE science SET Answer ={ans} WHERE SrNo={qno}")
        con.commit()
        con.close()
    elif ch==4:
        con = sqlite3.connect('Storage.db')
        cur = con.cursor()
        qno = int(input("Enter the Question No.: "))
        cur.execute(f"SELECT * FROM science WHERE SrNo={qno}")
        for i in cursor:
            print(f"SrNo{i[0]}: {i[1]} \nOption1:{i[2]} \nOption2:{i[3]} \nOption3:{i[4]} \nOption4:{i[5]}")
        ano = int(input("Enter option No.: "))
        optn = input("Enter correct option:")
        cur.execute(f"UPDATE science SET Option{ano} ='{optn}' WHERE SrNo={qno}")
        con.commit()
        con.close()    
    else:
        print("Invalid Choice")
        admin_operation()

def play_Quiz():
    con = sqlite3.connect('Storage.db')
    cur = con.cursor()
    cur.execute(f"SELECT * from Science")
    for i in cur.fetchall():
        print(f"SrNo{i[0]}: {i[1]} \nOption1:{i[2]} \nOption2:{i[3]} \nOption3:{i[4]} \nOption4:{i[5]}")
        opn = int(input("Choose option no.: "))
        if opn== i[6]:
            print("Correct")
        else:
            print("Incorrect")
    con.commit()
    con.close()

def first_window():
    print('1. Admin Login \n2. Play Quiz \n3. Exit')
    ch= int(input('Choose Option: ' ))
    if ch==1:
        pwd = input('Enter password: ')
        if pwd == admin_pwd:
            print("Access Granted")
            admin_operation()
        else:
            print("Access Denied")
            first_window()
    elif ch==2:
        play_Quiz()

    else:
        sys.exit()

first_window()



















''''
q = [
    "Q1. Capital of India?",
    "Q2. What are the symptoms of suffering from kidney disease?",
    "Q3.  If a person is put on dialysis, he is suffering from?",
    "Q4.  What is the shape of the kidney?",
    "Q5.  Secondary air pollutant is ?",
]

options = [
    ["Delhi", "Mumbai", "Kolkata", "Chennai"],
    ["High blood pressure", "Respiration problem", "Swelling on face, legs etc", "All of the above"],
    ["Heart disease", "Kidney disease", "Respiratory problem", "None of the above"],
    ["It is an oval shaped organ", "It is bean shaped organ", "It is rectangular in shape", "It has no fixed shape"],
    ["Ozone", "Carbon monoxide", "Nitrogen Dioxide", "Sulphur dioxide"],
]

a = [1, 4, 2, 2, 1]

class Quiz:
    def __init__(self, master):
        self.opt_selected = IntVar()
        self.qn = 0
        self.correct = 0
        self.ques = self.create_q(master, self.qn)
        self.opts = self.create_options(master, 4)
        self.display_q(self.qn)
        self.button = Button(master, text="Back", command=self.back_btn)
        self.button.pack(side=BOTTOM)
        self.button = Button(master, text="Next", command=self.next_btn)
        self.button.pack(side=BOTTOM)

    def create_q(self, master, qn):
        w = Label(master, text=q[qn])
        w.pack(side=TOP)
        return w

    def create_options(self, master, n):
        b_val = 0
        b = []
        while b_val < n:
            btn = Radiobutton(master, text="foo", variable=self.opt_selected, value=b_val+1)
            b.append(btn)
            btn.pack(side=TOP, anchor="w")
            b_val = b_val + 1
        return b

    def display_q(self, qn):
        b_val = 0
        self.opt_selected.set(0)
        self.ques['text'] = q[qn]
        for op in options[qn]:
            self.opts[b_val]['text'] = op
            b_val = b_val + 1

    def check_q(self, qn):
        if self.opt_selected.get() == a[qn]:
            return True
        return False

    def print_results(self):
        print("Score: ", self.correct, "/", len(q))

    def back_btn(self):
        print("go back")

    def next_btn(self):
        if self.check_q(self.qn):
            print("Correct")
            self.correct += 1
        else:
            print("Wrong")
        self.qn = self.qn + 1
        if self.qn >= len(q):
            self.print_results()
            root.destroy()
        else:
            self.display_q(self.qn)

root = Tk()
root.geometry("500x300")
root.title("Simple Quiz App")
app = Quiz(root)
root.mainloop()
'''
