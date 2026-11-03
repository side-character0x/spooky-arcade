import sqlite3

class Database:
    def __init__(self):
        self.conn=sqlite3.connect("halloween.db")
        self.conn.row_factory=sqlite3.Row
        self.cur=self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS auth(id INTEGER PRIMARY KEY, username TEXT, pin TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS data(username TEXT, candies INTEGER)")

    def check_username(self,username):
        username=self.cur.execute("SELECT * FROM auth WHERE username=?",(username,)).fetchall()
        self.conn.close()
        if username is None:
            return True
        else:
            return False
    def add_user(self,username,pin):
        self.cur.execute("INSERT INTO auth(username,pin) VALUES(?,?)",(username,pin))
        self.cur.execute("INSERT INTO data(username,candies) VALUES(?,?)",(username,0))
        self.conn.commit()
        self.conn.close()

    def check_user(self,username,pin):
        db_pin=self.cur.execute("SELECT pin FROM auth WHERE username=?",(username,)).fetchone()
        self.conn.close()
        if db_pin is None:
            return False
        if db_pin["pin"]==pin:
            return True
        else:
            return False

