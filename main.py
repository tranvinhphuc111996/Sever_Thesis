# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, session, redirect, escape
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import sqlite3
from flask_socketio import SocketIO, emit
import json
from threading import Thread
DATABASE_FILE = 'database.db'
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(12)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = './static/image'
socketio = SocketIO(app,async_mode= None)
sid_clients = []



def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connectdb():
	conn = sqlite3.connect(DATABASE_FILE, isolation_level = None)
	return conn

def querydb(conn, query, v = tuple()):
	c = conn.cursor()
	c.row_factory = dict_factory
	c.execute(query, v)
	return c.fetchall()


def logged_in():
	if not session.get('logged_in'):
		return 0
	return 1

@app.route('/')
def index():
	if logged_in():
		return render_template('index.html')
	else:
		return redirect('/dang_nhap')

@app.route('/dang_nhap', methods=['GET', 'POST'])
def dang_nhap():
	if request.method == 'GET':
		return render_template('dang_nhap.html')
	else:
		username = request.form.get('username')
		password = request.form.get('password')
		conn = connectdb()
		r = querydb(conn, r"SELECT * FROM Administrator WHERE username=? AND password=?", (username, password))
		if r:
			session['logged_in'] = True
			return redirect('/')
		else:
			return render_template('dang_nhap.html')


@app.route('/dang_xuat')
def dang_xuat():
	session.clear()
	return redirect('/dang_nhap') 

@app.route('/static/<filename>')
def static_file(filename):
	return app.send_static_file(filename)

@app.route('/thong_ke')
def thong_ke():
	if not logged_in():
		return redirect('/dang_nhap')
	return render_template('/thong_ke.html')

@app.route('/json/scan_the', methods=['POST'])
def scan_the():
	'''Lay CardID'''

	json_post_data 	= request.get_json()
	print json_post_data
	DeviceID 		= json_post_data['DeviceID']
	
	ImageID			= json_post_data['ImageID']
	EntryTime 		= json_post_data['EntryTime']
	conn = connectdb()
	if 'CardID' in json_post_data:
		CardID 			= json_post_data['CardID']
		r1 = querydb(conn, r"SELECT * FROM Employee WHERE CardID=?", (CardID, ))
		name_string = querydb(conn, r"SELECT EmployeeName FROM Employee WHERE CardID=?",(CardID,))
		print("CardID ")
		PositionNumber = 0
		if len(r1) > 0:
			'''User da dang ky'''
			respone = {'status': 1}
			
			'''Ghi record vao bang Work'''
			
			querydb(conn, r"INSERT INTO Work(DeviceID,CardID,FingerID,ImageID,EntryTime) VALUES (?,?,?,?,?)", (DeviceID,CardID,PositionNumber,ImageID,EntryTime, ))
			# querydb(conn, r"INSERT INTO Work(DeviceID,CardID,ImageID,EntryTime) VALUES (?,?,?,?)", (DeviceID,CardID,ImageID,EntryTime, ))
			
			

			post_web_data = json.dumps({"NameEmploy": name_string[0]['EmployeeName'],"EntryTime": EntryTime,"ImageID": ImageID})
			print 'post_web_data:', post_web_data
			socketio.emit('my_response', post_web_data , namespace='/tracking')
			return jsonify(respone)
		else:
			'''User chua dang ky'''
			respone = {'status': 0}
			return jsonify(respone)
			
		
	if  'FingerID' in json_post_data:
		PositionNumber		= json_post_data['PositionNumber']
		print(PositionNumber)
		r2 = querydb(conn, r"SELECT * FROM Employee WHERE FingerID=?", (PositionNumber, ))
		name_string = querydb(conn, r"SELECT EmployeeName FROM Employee WHERE FingerID=?",(PositionNumber,))
		print("Finger ID")
		CardID = 0
        if len(r2) > 0 :
            respone = {'status': 1}
            print("haha")
            querydb(conn, r"INSERT INTO Work(DeviceID,CardID,FingerID,ImageID,EntryTime) VALUES (?,?,?,?,?)", (DeviceID,CardID,PositionNumber,ImageID,EntryTime, ))
            # querydb(conn, r"INSERT INTO Work(DeviceID,CardID,ImageID,EntryTime) VALUES (?,?,?,?)", (DeviceID,CardID,ImageID,EntryTime, ))
           
            post_web_data = json.dumps({"NameEmploy": name_string[0]['EmployeeName'],"EntryTime": EntryTime,"ImageID": ImageID})
            print 'post_web_data:', post_web_data
            socketio.emit('my_response', post_web_data , namespace='/tracking')
        else:
        	 respone = {'status' : 0}
	conn.commit()
	conn.close()
	return jsonify(respone)
@app.route('/json/register_tag', methods=['POST'])
def register_the():
	'''Lay CardID'''
	json_post_data 	= request.get_json()

	CardID 			= json_post_data['CardID']
	'''Debug'''
	#socketio.emit('my_response', json_post_data , namespace='/tracking')
	conn = connectdb()
	r = querydb(conn, r"SELECT * FROM Employee WHERE CardID=?", (CardID, ))
	if len(r) > 0:
		respone = 200
		# This is registered in database 
		post_web_data = json.dumps({"CardID" : CardID})
		socketio.emit('get_id_web', post_web_data , namespace='/register')
	else:
		#Unregister
		respone = 200
		post_web_data = json.dumps({"CardID" : CardID})
		socketio.emit('get_id_web', post_web_data , namespace='/register')
	
	return jsonify(respone)	
@app.route('/json/register_finger', methods=['POST'])
def register_finger():
	'''Lay CardID'''
	json_post_data 	= request.get_json()

	FingerID 			= json_post_data['FingerID']
	'''Debug'''
	#socketio.emit('my_response', json_post_data , namespace='/tracking')
	conn = connectdb()
	r = querydb(conn, r"SELECT * FROM Employee WHERE FingerID=?", (FingerID, ))
	if len(r) > 0:
		respone = 200
		# This is registered in database 
		post_web_data = json.dumps({"FingerID" : FingerID})
		socketio.emit('get_finger_web', post_web_data , namespace='/register')
	else:
		#Unregister
		respone = 200
		post_web_data = json.dumps({"FingerID" : FingerID})
		socketio.emit('get_finger_web', post_web_data , namespace='/register')
	
	return jsonify(respone)	

@app.route('/Tracking', methods=['POST', 'GET'])
def tracking():
	return render_template('Tracking.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/rev_image', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post_web_data = json.dumps({"Image_status":"true"})
            socketio.emit('image_response', post_web_data , namespace='/tracking')
            return 'Success'
    return 'Success'



@app.route('/the_moi', methods=['POST', 'GET'])
def the_moi():
	#not implemented
	if not logged_in():
		return redirect('/dang_nhap')
	if request.method == 'GET':
		return render_template('the_moi.html')
	else:
		post_data 			= request.form
		'''TODO
		kiểm tra mã thẻ hợp lệ
		'''
		CardID 				= post_data['mathe'] 
		EmployeeName 		= escape(post_data['hoten'])
		EmployeeBirthDate 	= datetime.strptime(post_data['ngaysinh'], '%d-%m-%Y')
		conn 				= connectdb()
		r 					= querydb(conn, r"INSERT INTO Employee(EmployeeName, CardID, EmployeeBirthDate) VALUES(?,?,?)", (EmployeeName, CardID, EmployeeBirthDate))
		return render_template('the_moi.html')

@app.route('/them_nhan_vien', methods=['POST', 'GET'])
def them_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')

	if request.method == 'GET':
		return render_template('them_nhan_vien.html')
	else:
		if request.form['Submit_button'] == 'Register':
			post_data 			= request.form
			'''TODO
			kiểm tra mã thẻ hợp lệ
			'''
			CardID 				= post_data['mathe'] 
			EmployeeName 		= escape(post_data['hoten'])
			EmployeeBirthDate 	= datetime.strptime(post_data['ngaysinh'], '%d-%m-%Y')
			print(post_data)
			conn 				= connectdb()
			r 					= querydb(conn, r"INSERT INTO Employee(EmployeeName, CardID, EmployeeBirthDate) VALUES(?,?,?)", (EmployeeName, CardID, EmployeeBirthDate))
		return render_template('them_nhan_vien.html')

@app.route('/json/xoa_nhan_vien', methods=['POST'])
def xoa_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')

	json_post_data 		= request.get_json()
	CardID 				= json_post_data['mathe']
	conn 				= connectdb()
	r 					= querydb(conn, r"DELETE FROM Employee WHERE CardID=?", (CardID,))
	return jsonify({'status': 1})

@app.route('/json/sua_thong_tin_nhan_vien', methods=['POST'])
def sua_thong_tin_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')

	json_post_data 		= request.get_json()
	CardID 				= json_post_data['mathe'] 
	EmployeeName 		= escape(json_post_data['hoten'])
	EmployeeBirthDate 	= datetime.strptime(json_post_data['ngaysinh'], '%d-%m-%Y')
	conn 				= connectdb()
	r 					= querydb(conn, r"UPDATE Employee SET EmployeeName=?,EmployeeBirthDate=? WHERE CardID=?", (EmployeeName, EmployeeBirthDate, CardID))
	return jsonify({'status': 1})

# @app.route('/them_thiet_bi', methods=['POST', 'GET'])
# def them_thiet_bi():
# 	if not logged_in():
# 		return redirect('/dang_nhap')

# 	if request.method == 'GET':
# 		return render_template('them_thiet_bi.html')
# 	else:
# 		post_data 	= request.form
# 		DeviceID  	= post_data['deviceid']
# 		SSID 		= ""
# 		description = escape(post_data['description'])
# 		conn 		= connectdb()
# 		r 			= querydb(conn, r"INSERT INTO Device(DeviceID, Description, SSID) VALUES(?,?,?)", (DeviceID, description))
# 		return render_template('them_thiet_bi.html')

@app.route('/danh_sach_nhan_vien', methods=['GET'])
def danh_sach_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')
	'''connect to database'''
	conn 			= connectdb()
	r 				= querydb(conn, r"SELECT * FROM Employee")
	ds_nhanvien 	= []

	for row in r:
		ds_nhanvien.append({'hoten': row['EmployeeName'], 'mathe': row['CardID'], 'ngaysinh': row['EmployeeBirthDate']})
	return render_template('danh_sach_nhan_vien.html', ds_nhanvien=ds_nhanvien)

@app.route('/danh_sach_thiet_bi')
def danh_sach_thiet_bi():
	if not logged_in():
		return redirect('/dang_nhap')

	'''connect to database'''
	conn 			= connectdb()
	r 				= querydb(conn, r"SELECT * FROM Device")
	ds_thietbi 		= []
	for row in r:
		ds_thietbi.append({'deviceid': row['DeviceID'], 'description': row['Description']})
	return render_template('danh_sach_thiet_bi.html', ds_thietbi=ds_thietbi)
@app.route('/danh_sach_tag_ID')
def danh_sach_tag_ID():
	return render_template('danh_sach_tag_ID.html')



@app.route('/json/register_tag', methods=['POST'])
def register_tag():
	'''Lay CardID'''
	json_post_data 	= request.get_json()
	CardID 			= json_post_data['CardID']
	post_web_data = json.dumps({"CardID": CardID}) 
	socketio.emit()

	
	




@socketio.on('submit_sid',namespace='/submit_ssid')
def handle_submit(msg):
	SSID = str(request.sid)
	DeviceID = str(msg['devID'])
	Description = str(msg['Descrip'])
	# Store data to database 
	conn = connectdb()
	result = querydb(conn, r"SELECT * FROM Device WHERE Description=?", (Description, ))
	if len(result) > 0:	
		print("This SSID was connected !!!")
		result = querydb(conn, r"DELETE FROM Device WHERE Description=?", (Description, ))
		querydb(conn, r"INSERT INTO Device(SSID,DeviceID,Description) VALUES (?,?,?)", (SSID,DeviceID,Description, ))
	else:
		querydb(conn, r"INSERT INTO Device(SSID,DeviceID,Description) VALUES (?,?,?)", (SSID,DeviceID,Description, ))
@socketio.on('disconnect')
def on_disconnect():
	SSID = request.sid
	print(str(SSID)+"is disconnect")
	conn = connectdb()
	result = querydb(conn, r"DELETE FROM Device WHERE SSID=?", (SSID, ))
	

	
@socketio.on('get_location_signal', namespace='/register')
def getlocationFromWeb_Register(msg):
	conn = connectdb()
	result = querydb(conn, r"SELECT SSID FROM Device WHERE Description = ?", (str(msg), ))
	print(result)
	for row in result:
		SSID = ''.join(row['SSID'])	
	emit('Register_Signal',namespace='/submit_ssid',room=SSID)

@socketio.on('get_id_signal', namespace='/register')
def getSignalFromWeb_Register():
   	conn = connectdb()
	result = querydb(conn, r"SELECT Description FROM Device")
	
	
	
	emit('get_device',result,namespace='/register')

    

@socketio.on('get_id_from_pi')
def getIdFromPi(msg):
    print('received json: ' + str(msg))   


# # Khong biet da lam gi o day
# @socketio.on('LoadWork_data', namespace='/tracking')
# def handle_load_data():
# 	conn 			= connectdb()
# 	r 				= querydb(conn, r"SELECT * FROM Employee")
# 	ds_nhanvien 	= []
# 	for row in r:
# 		ds_nhanvien.append({'hoten': row['EmployeeName'], 'mathe': row['CardID'], 'ngaysinh': row['EmployeeBirthDate']})
# 	socketio.emit('LoadWork_data', ds_nhanvien, namespace='/tracking')

@socketio.on('connect')
def on_connect():
	print('Client connected :'+ str(request.sid))

@socketio.on('GetDate', namespace="/tracking")
def getdate(msg):
	# print(msg)
	Check_data = '%'+str(msg)+'%'

	conn 			= connectdb()
	r = querydb(conn, r"SELECT * FROM Work WHERE EntryTimeStamp LIKE ? ",(Check_data,))
	for row in r :

		if row['CardID'] != '0' and row['FingerID'] == None:
			r_name = querydb(conn, r"SELECT EmployeeName FROM Employee WHERE CardID=?  ",(row['CardID'],))
			if r_name:
				row.update(r_name[0])
		else:
			r_name = querydb(conn, r"SELECT EmployeeName FROM Employee WHERE FingerID=?  ",(row['FingerID'],))
			if r_name:
				row.update(r_name[0])


	socketio.emit('LoadWork_data', r , namespace='/tracking')

