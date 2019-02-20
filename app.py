from flask import Flask, flash, redirect, render_template, request, session, abort, send_file
import MySQLdb
import json
from datetime import datetime, timedelta
import numpy as np 
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = os.urandom(12)

@app.route('/counter', methods=['POST'])
def post():
    if request.method == 'POST':
        db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
        cursor = db.cursor()
        class_name = request.form['class']
        date = request.form['date']

        
        sql = "SELECT * from Class_Attendance where class= '{}' and date = '{}'"
        cursor.execute(sql.format(class_name,date))
        db.commit()
        rows = cursor.fetchall()
        counter = len(rows)

        return len(rows)

        
@app.route('/')
def homepage():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
            
        db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
        cursor = db.cursor()
    
        cursor.execute("SELECT * FROM Classes")
        rows = cursor.fetchall()
    
        classes_data = {
            '12': [],
            '11': [],
            '10': [],
            '9': []
        }
        for elem in rows:
            classes_data[elem[1]].append(elem[2])
            
        print(classes_data)
    
        db.close()
    
        return render_template('index.html', classes_data = classes_data)
    
def idClassMapping(idToClass, value1, value2):
    db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
    cursor = db.cursor()
    
    if idToClass:
        cursor.execute("SELECT className FROM Classes WHERE id = {}".format(value1))
    else:
        cursor.execute("SELECT id FROM Classes WHERE className = '{}' AND Section = '{}'".format(value1, value2))
    
    row = cursor.fetchone()
    
    db.close()
    
    return row
    
@app.route('/gradeData', methods=['GET', 'POST'])
def gradeData():
    if request.method == 'GET':
        grade = request.args.get('grade')
        section = request.args.get('section')
        
        db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
    
        cursor = db.cursor()
        
        # getting all students data
    
        cursor.execute("SELECT * FROM Student_Data WHERE CLASS = '{}'".format(idClassMapping(False, grade, section)[0]))
    
        rows = cursor.fetchall()
        
        final_arr = []
        for elem in rows:
            ins_dict = {
                "id": elem[0],
                "name": elem[1],
                "regno": elem[2],
                "class": idClassMapping(True, str(elem[3]), 0)[0]

            }
            final_arr.append(ins_dict)
            
            print final_arr
    
    
        # getting attendance data for the current day
        
        cursor.execute("SELECT * FROM Attendance")
        
        rows = cursor.fetchall()
        
        
        attendance_arr = []
        for ind in range(len(rows)):
            item = rows[ind]
            student_id = item[1]
            if isStudentInClass(student_id, idClassMapping(False, grade, section)[0]):
                if item[2].date() == datetime.today().date():
                    cursor.execute("SELECT name FROM Student_Data WHERE regno = '{}'".format(student_id))
                    
                    name = cursor.fetchone()[0]

                    item_dict = {
                        "name": name,
                        "student_id": student_id,
                        "attendanceVal": 'Present',
                        "date" : datetime.today().date()
                    }
                    attendance_arr.append(item_dict)
                    
        for elem in final_arr:
            flag = 0
            for item in attendance_arr:
                if elem['regno'] == item['student_id']:
                    flag = 1
                    break
            if flag == 0:
                attendance_arr.append({
                        "name": elem['name'],
                        "student_id": elem['regno'],
                        "attendanceVal": 'Absent',
                        "date": datetime.today().date()
                    })
    
        db.close()
        
        #attendance_num = attendance_arr.split()[0::4]
        #print attendance_arr
        #attendance_count = []
        #for elem in attendance_num:
        #   if elem == 1:
        #        number = {
        #        attendance_count == attendance_count + 1
        #        }
        #        attendance_count.append(number)
        #if attendanceVal == 1:
        #    attendance_count == attendance_count + 1
        
        attendance_count = 0
        x = 0
        for elem in attendance_arr:
            x == x + 1
            if attendance_arr[x].get("attendanceVal") == "Present":
                attendance_count == attendance_count + 1
        total_count = len(final_arr)
        
        #print(final_arr, attendance_arr)
        
        return render_template('class.html', data = {'class_data': final_arr, 'grade': grade, 'section': section, 'attendance_data': attendance_arr, 'attendance_count' : attendance_count, 'total_count' : total_count})
        
def isStudentInClass(student_id, class_id):
    db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
    
    cursor = db.cursor()
        
    cursor.execute("SELECT * FROM Student_Data WHERE regno = '{}' AND class= '{}'".format(student_id, class_id))
    
    rows = cursor.fetchall()
    
    db.close()
    
    if len(rows) == 0:
        return False
    else:
        return True
        

@app.route('/login2')
def home():
    #emailid = request.form['email']
    #print emailid
    #password = request.form['password']
    #print password
    return (render_template('login.html'))
#@app.route('/save-post',methods=['POST', 'GET'])
#def signUp():
#    if request.method=='POST':
       # name=request.form['name']
      #  email=request.form['email']
     #
    #with connection.cursor() as cursor:
   #      sql = "INSERT INTO userdata (emailid, password) VALUES (%s, %s)"
  #       cursor.execute(sql, (emailid, password))
 #        connection.commit()
#    finally:
     #    connection.close()
    #     return "Saved successfully."
    #else:
        #return "error"
        
#'''@app.route('/post', methods=['GET','POST'])
#def app_post(student_id):
 #   db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
  #  cursor = db.cursor()
    
   # cursor.execute("INSERT INTO Attendance (ID, Student_ID, Timestamp, Attendance) VALUES (NULL, '16orb1225', CURRENT_TIMESTAMP, '1')")
    
    #return("Success")
    #'''
    
@app.route('/post', methods=['POST', 'GET'])
def json_post():
    
    req_data = request.get_json()
    db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
    
    cursor = db.cursor()
    print req_data
    student_id = req_data['student_id']

    
    cursor.execute("SELECT * FROM Attendance WHERE Student_ID = '{}' AND DATE(`timestamp`) = CURDATE()".format(student_id))
    
    preexisting_data = cursor.fetchall()
    
    
    if len(preexisting_data) == 0:
        cursor.execute("INSERT INTO Attendance (Student_ID, Attendance) VALUES ('{}', '1')".format(student_id))
        db.commit()
        
        db.close()
        
        return ("INSERT INTO Attendance (Student_ID, Attendance) VALUES ('{}', '1')".format(student_id)) 
    else:
        print("Record for the day already exists", preexisting_data)
        
        return "Record for the day already exists", 403
    
    
    
    
@app.route('/login', methods=['POST'])
def do_admin_login():
    print(request.form)
    if request.form['password'] == 'password' and request.form['email'] == 'gaurangbharti@gmail.com':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return homepage()
    
    #if request.method == 'get':
    # Open database connection
        #db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
        #emailID = request.form['email']
        #print emailID
        #password = request.form['password']
        #print password
        #return render_template('login2.html')
        #query = "SELECT * from Teacher_Credentials where'emailID'= {} and 'password'= {}"
        #cursor = db.cursor()
        #sql = "SELECT * from Teacher_Credentials where'emailID'= {} and 'password'= {} VALUES ({}, %{})"
        #cursor.execute(sql, (emailID, password))
        
        #db.close()

@app.route('/getDateRecords', methods=['POST'])
def date():
    if request.method == 'POST':
        db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
        cursor = db.cursor()
        
        
        print(request.data)
        elems = request.data.split('&')
        grade = elems[0].split('=')[1]
        section = elems[1].split('=')[1]
        
        cursor.execute("SELECT id FROM Classes WHERE className = '{}' AND Section= '{}'".format(grade, section))
        class_id = cursor.fetchone()
        
        import urllib
        
        date = str(urllib.unquote(elems[2].split('=')[1]).decode('utf8'))
        
        from dateutil import parser
        dt = parser.parse(date)
        
        cursor.execute("SELECT * FROM Attendance WHERE DATE(`timestamp`) = '{}'".format(dt))
        
        rows = cursor.fetchall()
        print(rows)
        attendance_arr = []
        for elem in rows:
            student_id = elem[1]
            if isStudentInClass(student_id, int(class_id[0])):
                cursor.execute("SELECT * FROM Student_Data WHERE regno = '{}' AND class= '{}'".format(student_id, int(class_id[0])))
                
                student_entry = cursor.fetchone()
                print(student_entry)
                attendance_arr.append({
                        "name": student_entry[1],
                        "student_id": student_entry[2],
                        "attendanceVal": 'Present',
                        "date": str(dt.date())
                })
                
        cursor.execute("SELECT * FROM Student_Data WHERE CLASS = '{}'".format(idClassMapping(False, grade, section)[0]))
    
        rows = cursor.fetchall()
        
        class_arr = []
        for elem in rows:
            ins_dict = {
                "id": elem[0],
                "name": elem[1],
                "regno": elem[2],
                "class": idClassMapping(True, str(elem[3]), 0)[0]

            }
            class_arr.append(ins_dict)
            
        print class_arr
        
        for elem in class_arr:
            flag = 0
            for item in attendance_arr:
                if elem['regno'] == item['student_id']:
                    flag = 1
                    break
            if flag == 0:
                attendance_arr.append({
                        "name": elem['name'],
                        "student_id": elem['regno'],
                        "attendanceVal": 'Absent',
                        "date": str(dt.date())
                    })
            
        return json.dumps(attendance_arr)
    # student_name = "test"
    # regno = "test"
    # student_class = "test"
    # attendance = "test"
    # date = "test"
    # return render_template('date.html', data = {'student_name' : student_name, 'regno': regno, 'student_class': student_class, 'attendance': attendance, 'date': date})
    
    
@app.route('/weeklyreport', methods=['GET'])
def weeklyReport():
    if request.method == 'GET':
        
        db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM Classes")
        
        rows = cursor.fetchall()
        
        allclasses = []
        
        for elem in rows:
            item = {
                'grade': elem[1],
                'section': elem[2]
            }
            
            allclasses.append(item)
            
        
        
        #total_count = len(final_arr)
        return render_template('weeklyreport.html', data = {'allclasses': allclasses})
    
@app.route('/attendanceGraph', methods=['POST'])
def attendanceGraph():
    if request.method == 'POST':
        db = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
        cursor = db.cursor()
        
        request.data = json.loads(request.data)
        
        date = request.data['date']
        grade = request.data['grade']
        section = request.data['section']
        class_id = int(idClassMapping(0, grade, section)[0])
        
        from dateutil import parser
        dt = parser.parse(date)
        
        dayofweek = dt.strftime("%a")
        
        dateCorrection = {
            'Mon': 0,
            'Tue': -1,
            'Wed': -2, 
            'Thu': -3,
            'Fri': -4,
            'Sat': -5,
            'Sun': -6
        }
        start_date = dt + timedelta(dateCorrection[dayofweek])
        
        attendance_list = []
        for ind in [0, 1, 2, 3, 4]:
            attendance_count = 0
            cur_date = start_date + timedelta(ind)
            print("cur_date: {}".format(cur_date), ind)
            
            cursor.execute("SELECT * FROM Attendance WHERE DATE(`timestamp`) = '{}'".format(cur_date))
        
            rows = cursor.fetchall()
            
            for elem in rows:
                regno = elem[1]
                if isStudentInClass(regno, class_id):
                    attendance_count += 1.0
            attendance_list.append(attendance_count)
        
        print(attendance_list)
                    
        
        cursor.execute("SELECT * FROM Student_Data WHERE class = '{}'".format(class_id))
        
        rows = cursor.fetchall()
        
        print("total: {}".format(len(rows)))
        
        
        
        for i in range(len(attendance_list)):
            print(attendance_list[i], len(rows), float(attendance_list[i] / len(rows)))
            #attendance_list[i] = float((attendance_list[i] / len(rows)) * 100)
        
        print(attendance_list)
        return_data = {'data': attendance_list, 'total_count': len(rows)}
        
        return json.dumps(return_data)
    
    


@app.route('/save-post', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        connection = MySQLdb.connect("localhost","root","gb&cisco","Cisco" )
        cursor = connection.cursor()

        rows = cursor.execute("SELECT * from Teacher_Credentials where email = '{}'".format(email))
        connection.commit()

        if len(rows) == 0:
            cursor.excute("INSERT INTO Teacher_Credentials (email,password) VALUES ('{}','{}')".format(email, password))
            connection.commit()
        else:
            return 'You have already created an account'
            

@app.route('/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        if session.get('logged_in'):
            session['logged_in'] = False
            return homepage()
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)