def isNameExist(name):
    from sqlite3 import connect
    con=connect('Project.db')
    cur=con.cursor()
    try:
        cur.execute('CREATE TABLE AcDetail\
                    (Username Text Unique,\
                    Password Text)')
        con.commit()
    except:
        pass
    cur.execute('SELECT Username FROM ACDetail')
    for i in cur.fetchall():
        if i[0]==name:
            con.close()
            return True
    con.close()
    return False

def validPassword(pwd):
    from string import punctuation
    if len(pwd)>5:
        for i in pwd:
            if i in punctuation:
                return True
    return False

def storeDetails(name,pwd):
    from sqlite3 import connect
    con=connect('Project.db')
    cur=con.cursor()
    try:
        cur.execute('CREATE TABLE AcDetail\
                    (Username Text Unique,\
                    Password Text)')
    except:
        pass
    cur.execute('INSERT INTO AcDetail VALUES(?,?)',(name,pwd))
    con.commit()
    con.close()
    return True            

def checkPassword(name,pwd):
    from sqlite3 import connect
    con=connect('Project.db')
    cur=con.cursor()
    try:
        cur.execute('CREATE TABLE AcDetail\
                    (Username Text Unique,\
                    Password Text)')
        con.commit()
    except:
        pass
    cur.execute('SELECT Password FROM ACDetail WHEN\
                Username=?',name)
    if cur.fetchone()[0]==pwd:
        return True
    return False
if __name__=='__main__':
    print(checkPassword('adi@123'))
