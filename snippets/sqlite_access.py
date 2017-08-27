class dbconnector(object):
   """
   Class that enables access to a sqlite database. Supposed to be used to store and array
   of records, and/or to read the records from the DB and return them as a numpy array of tuples.

   Example of use:

   with dbconnector( <dbfile> ) as dbObj:
      if not dbObj.db_is_initialized:
         <...... GET THE DATA FROM WHEREVER.>
         # quotes is an array of tuples, on for each field of the database record
         dbObj.save_data(quotes)
      else:
         <...... RETURNS THE DATA>
         # quotes is an array of tuples, on for each field of the database record
         quotes = dbObj.load_data()
   """

   def __init__(self, fname):
      self.con, self._db_is_initialized = self.connect_to_db(fname)

   @property
   def db_is_initialized(self):
      return self._db_is_initialized

   def __enter__(self):
      return self

   def __exit__(self, exc_type, exc_value, traceback):
         self.close_db()

   def connect_to_db(self, fname):
      import sqlite3 as lite
   
      con = None
   
      # connect to the database, will be created if not existent
      try:
         con = lite.connect(fname)
         c = con.cursor()
      except lite.Error, e:
         print "Error %s:" % e.args[0]
         sys.exit(1)
   
      sql_create_data_table = """ CREATE TABLE IF NOT EXISTS samples (
                                          ts real PRIMARY KEY,
                                          open real,
                                          high real,
                                          low real,
                                          close real,
                                          volume real
                                      ); """
   
      # create the table for the data, if it does not exist
      try:
         c.execute(sql_create_data_table)
      except Error as e:
         print(e)
         sys.exit(1)
   
      # get the number of rows (to find if db is initialized or not)
      try:
         c.execute('SELECT Count(*) FROM samples')
         data = c.fetchone()[0]
      except Error as e:
         print(e)
         sys.exit(1)
   
      # return the conection, and a boolean indicating if there is data in the database
      return con, data > 0

   def close_db(self):
      if self.con:
         self.con.close()

   def save_data(self, quotes):
      cur = self.con.cursor()
      cur.executemany("INSERT INTO samples VALUES(?, ?, ?, ?, ?, ?)", map(tuple, quotes.tolist()))
      self.con.commit()
   
   def load_data(self):
      import numpy as np
      cur = self.con.cursor()
   
      # get the number of rows
      try:
         cur.execute('SELECT Count(*) FROM samples')
         nrows = cur.fetchone()[0]
      except Error as e:
         print(e)
         sys.exit(1)
   
      quotes = np.empty(shape=(nrows,6), dtype = float)
   
      try:
         cur.execute('SELECT * FROM samples')
         records = cur.fetchall()
      except Error as e:
         print(e)
         sys.exit(1)
   
      for idx,record in enumerate(records):
         quotes[idx][:] = record
   
      return np.rec.array(quotes, dtype = [ ('ts','f8'), ('open','f8'), ('high','f8'), ('low','f8'), ('close','f8'), ('volume','f8') ])

