# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, render_template, session, redirect, escape
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta
import calendar
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
app.config['UPLOAD_FOLDER_IMAGE'] = './static/image_employ'
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
	print (json_post_data)
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
			print ('post_web_data:', post_web_data)
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
			print ('post_web_data:', post_web_data)
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



@app.route('/them_nhan_vien', methods=['POST', 'GET'])
def them_nhan_vien():
	if not logged_in():
		return redirect('/dang_nhap')

	if request.method == 'GET':
		return render_template('them_nhan_vien.html')
	else:
		if request.form['Submit_button'] == 'Register':
			post_data 			= request.form
			file = request.files['upanh']
			'''TODO
			kiểm tra mã thẻ hợp lệ
			'''
			CardID 				= post_data['mathe'] 
			# FingerID			= post_data['FingerID']
			EmployeeName 		= escape(post_data['hoten'])
			EmployeeBirthDate 	= datetime.strptime(post_data['ngaysinh'], '%d-%m-%Y')
			print(post_data)
			conn 				= connectdb()
			r 					= querydb(conn, r"INSERT INTO Employee(EmployeeName, CardID, EmployeeBirthDate,PicName) VALUES(?,?,?,?)", (EmployeeName, CardID,PicName, EmployeeBirthDate,))
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], filename))
				
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
		ds_nhanvien.append({'hoten': row['EmployeeName'], 'mathe': row['CardID'], 'ngaysinh': row['EmployeeBirthDate'],'PicName': row['PicName']})
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
@app.route('/bang_cham_cong', methods=['POST','GET'])
def bang_cham_cong():
	return render_template('bang_cham_cong.html')
	
	




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

		if row['CardID'] != '0' and row['FingerID'] == '0':
			r_name = querydb(conn, r"SELECT EmployeeName FROM Employee WHERE CardID=?  ",(row['CardID'],))
			if r_name:
				row.update(r_name[0])
		else:
			r_name = querydb(conn, r"SELECT EmployeeName FROM Employee WHERE FingerID=?  ",(row['FingerID'],))
			if r_name:
				row.update(r_name[0])


	socketio.emit('LoadWork_data', r , namespace='/tracking')

@socketio.on('gui-thong-tin-bang-cham-cong', namespace = "/cham_cong")
def handle_chamcong(hotentext,year_get,month_get):
	conn 			= connectdb()
	CardID = querydb(conn, r"SELECT CardID FROM Employee WHERE EmployeeName=? ",(str(hotentext),))
	result_work = []
	print(CardID)
	if len(CardID) != 0:

		day_array = []

		
		data_fromWork = querydb(conn, r"SELECT EntryTime FROM Work WHERE CardID=? ",(CardID[0]['CardID'],))
		print(data_fromWork)
		day_work = get_day_work_in_month(int(month_get),data_fromWork)
		print(day_work)
		for day in day_work:
			get_day  = datetime.strptime(str(day), '%H:%M:%S-%d/%m/%Y')
			if get_day.day in day_array:
				pass 
			else:	
				day_array.append(get_day.day)
		
		for day in day_array:
			time_work = get_time_work_in_day(day,day_work)
			time_of_phase1 = get_phase1(time_work)
			time_of_phase2 = get_phase2(time_work)
			time_of_phase3 = get_phase3(time_work)
			result_factor = caculate_WorkingTime(time_of_phase1,time_of_phase2,time_of_phase3)
			result_work.append({"day" : day , "factor" : result_factor})
	else:
		print("This is not our Employee")
	print(result_work)
	emit('nhan-thong-tin-bang-cham-cong',result_work,namespace='/cham_cong')




def get_day_work_in_month(month,data_fromWork):
	array_day_work = [] 
	for Data_val in data_fromWork:
		datetime_object = datetime.strptime(str(Data_val['EntryTime']), '%H:%M:%S-%d/%m/%Y')
		if (datetime_object.month == month):
			array_day_work.append(Data_val['EntryTime'])
		# fit time 
	return array_day_work
def get_time_work_in_day(day,data_fromWork):
	array_time_in_day_work = [] 
	for Data_val in data_fromWork:
		datetime_object = datetime.strptime(str(Data_val), '%H:%M:%S-%d/%m/%Y')
		if (datetime_object.day == day):
			array_time_in_day_work.append(Data_val)
		# fit time 
	return array_time_in_day_work
def get_phase1(time_array):
	time_of_phase1=[]
	second = 00
	begin_hourinsession1 = 7 
	begin_minutesinsession1 = 30
	end_hourinsession1 = 11
	end_mininsession1 = 30
	begin_hourinsession2 = 12
	begin_minutesinsession2 = 00
	datetime_object = datetime.strptime(str(time_array[0]), '%H:%M:%S-%d/%m/%Y') 
	begin_phase1 =str(begin_hourinsession1) + ":" + str(begin_minutesinsession1) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_session1 = datetime.strptime(begin_phase1, '%H:%M:%S-%d/%m/%Y')
	end_phase1 =str(end_hourinsession1) + ":" + str(end_mininsession1) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_endsession1 = datetime.strptime(end_phase1, '%H:%M:%S-%d/%m/%Y')
	begin_phase2 =str(begin_hourinsession2) + ":" + str(begin_minutesinsession2) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_session2 = datetime.strptime(begin_phase2, '%H:%M:%S-%d/%m/%Y')
	for time in time_array:
		time = datetime.strptime(str(time), '%H:%M:%S-%d/%m/%Y') 
		if time < compare_session1:
			time_of_phase1.append(time)
		# if time > compare_session1 and time < compare_session2:
		# 	time_of_phase1.append(time)	
	return time_of_phase1

def get_phase2(time_array):
	time_of_phase2=[]
	second = 00
	end_hourinsession1 = 13
	end_mininsession1 = 00
	begin_hourinsession2 = 14
	begin_minutesinsession2 = 00
	end_hourinsession2 = 17
	end_mininsession2 = 00 
	begin_hourinsession3 = 18
	begin_minutesinsession3 = 00

	datetime_object = datetime.strptime(str(time_array[0]), '%H:%M:%S-%d/%m/%Y') 
	end_phase1 =str(end_hourinsession1) + ":" + str(end_mininsession1) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_endsession1 = datetime.strptime(end_phase1, '%H:%M:%S-%d/%m/%Y')
	begin_phase2 =str(begin_hourinsession2) + ":" + str(begin_minutesinsession2) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	end_phase2 =str(end_hourinsession2) + ":" + str(end_mininsession2) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	
	begin_phase2 =str(begin_hourinsession2) + ":" + str(begin_minutesinsession2) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_session2 = datetime.strptime(begin_phase2, '%H:%M:%S-%d/%m/%Y')
	end_phase2 =str(end_hourinsession2) + ":" + str(end_mininsession2) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_endsession2 = datetime.strptime(end_phase2, '%H:%M:%S-%d/%m/%Y')
	begin_phase3 =str(begin_hourinsession3) + ":" + str(begin_minutesinsession3) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_endsession3 = datetime.strptime(begin_phase3, '%H:%M:%S-%d/%m/%Y')
	for time in time_array:
		time = datetime.strptime(time, '%H:%M:%S-%d/%m/%Y') 
		if time < compare_session2 and time > compare_endsession1:
			time_of_phase2.append(time)
		# if time > compare_endsession2 and time < compare_endsession3:
		# 	time_of_phase2.append(time)	
	return time_of_phase2

def get_phase3(time_array):
	time_of_phase3=[]
	second = 00
	begin_hourinsession3 = 18
	begin_minutesinsession3 = 00
	end_hourinsession3 = 21
	end_mininsession3 = 00 
	end_hourinsession2 = 17
	end_mininsession2 = 00 
	
	datetime_object = datetime.strptime(str(time_array[0]), '%H:%M:%S-%d/%m/%Y') 
	end_phase2 =str(end_hourinsession2) + ":" + str(end_mininsession2) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_endsession2 = datetime.strptime(end_phase2, '%H:%M:%S-%d/%m/%Y')
	
	begin_phase3 =str(begin_hourinsession3) + ":" + str(begin_minutesinsession3) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_session3 = datetime.strptime(begin_phase3, '%H:%M:%S-%d/%m/%Y')
	end_phase3 =str(end_hourinsession3) + ":" + str(end_mininsession3) + ':' + str(second) + "-" + str(datetime_object.day) + "/" + str(datetime_object.month) + "/" + str(datetime_object.year)
	compare_endsession3 = datetime.strptime(end_phase3, '%H:%M:%S-%d/%m/%Y')
	for time in time_array:
		time = datetime.strptime(time, '%H:%M:%S-%d/%m/%Y')
		# if time < compare_session3 and time > compare_endsession2:
		# 	time_of_phase3.append(time)
		if time > compare_endsession3:
			time_of_phase3.append(time)
	return time_of_phase3
def caculate_WorkingTime(time_of_phase1,time_of_phase2,time_of_phase3):
	non_time = datetime(1990, 1, 1, 0, 0, 0, 0)

	length_time1 = len(time_of_phase1)
	length_time2 = len(time_of_phase2)
	length_time3 = len(time_of_phase3)
	factor_phase1 = 0
	factor_phase2 = 0
	factor_phase3 = 0
	if length_time1 > 0:
		# workingtime1 = time_of_phase1[len(time_of_phase1)-1] - time_of_phase1[0]
		workingtime1 = time_of_phase1[0]
	else:
		workingtime1 = non_time

	if length_time2 > 0:
		# workingtime2 = time_of_phase2[len(time_of_phase2)-1] - time_of_phase2[0]
		workingtime2 = time_of_phase2[0]
	else:
		workingtime2 = non_time

	if length_time3 > 0:
		# workingtime3 = time_of_phase3[len(time_of_phase3)-1] - time_of_phase3[0]
		workingtime3 = time_of_phase3[0]
	else:
		workingtime3 = non_time 

	if (workingtime1 > non_time):
		factor_phase1 = factor_phase1 + 1
	if (workingtime2 > non_time):
		factor_phase2 = factor_phase2 + 1
	if (workingtime3 > non_time):
		factor_phase3 = factor_phase3 + 1		
	Total_factor = factor_phase1 + factor_phase2+factor_phase3
	return(Total_factor) 
