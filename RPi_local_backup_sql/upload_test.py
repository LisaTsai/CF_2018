#!/usr/bin/env python
import MySQLdb
db=MySQLdb.connect(host="192.168.50.98",user="root",passwd="ntubime405",db="PN_CF", port=3306)
cur=db.cursor()
try:
	cur.execute("""DELETE FROM THI where 1""")
	cur.execute("""INSERT INTO THI values(CURRENT_TIMESTAMP,'22','33','44','9')""")
	db.commit()
	db.close()
except:
	print "Error"
	db.rollback()
