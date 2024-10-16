# set-Executionpolicy -scope process -Executionpolicy Bypass  
# env\Scripts\activate
import random
from flask import Flask, render_template, url_for, request, session, redirect, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import input_required, length, ValidationError
from flask_bcrypt import Bcrypt
from sqlalchemy import func
import base64
import os

#----------------------------------------INIT AREA------------------------------------------


#flask init
app = Flask(__name__)
#SQL init
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'GTA_6_WILL_RELEASE_NEXT_YEAR'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#----------------------------globle variable and funtion------------------------------------------------

class Create_Accout_form1(FlaskForm):
    name = StringField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"tên tài khoản"})
    passworld = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"mật khẩu"})
    retypePassworld = PasswordField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"nhập lại mật khẩu"})
    submit = SubmitField("tạo tài khoản")
    def validate_passworld(self, passworld):
        if passworld.data != self.retypePassworld.data:
            raise ValidationError("mật khẩu không trùng khớp, vui lòng nhập lại")
    def validate_name(self, name):
        exitting_name = AccoutManager.query.filter_by(name = name.data).first()
        if exitting_name:
            raise ValidationError("tên tài khoản đã tồn tại vui lòng chọn một tên khác")
        

class create_student_Data_form(FlaskForm):
    MSSV = StringField(validators = [input_required(), length(min=10, max=10)], render_kw={"placeholder":"mã số sinh viên"})
    name = StringField(validators = [input_required(), length(min=1, max=128)], render_kw={"placeholder":"tên sinh viên"})
    RFID = StringField(validators = [length(min=1, max=128)], render_kw={"placeholder":"RFID"})
    submit = SubmitField("tạo")


class test_form(FlaskForm):
    RFID = StringField(validators = [input_required(), length(min=10, max=10)], render_kw={"placeholder":"mã số sinh viên"})
    submit = SubmitField("tạo")


class login_form(FlaskForm):
    name = StringField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"tài khoản"})
    passworld = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"mật khẩu"})
    submit = SubmitField("đăng nhập")


            
class sessionHandleSimple():
    accname = ""
    def logout(self):
        self.accName = ""
    def isLogOn(self):
        try:
            if self.accName != "":
                acc = AccoutManager.query.filter_by(name = self.accName).first
                if acc:
                    return True
                else:
                    return False
        except:
            return False
    def update(self):
        self.accName = session["user"]

SH = sessionHandleSimple()


#----------------------------------------SQL AREA------------------------------------------

class AccoutManager(db.Model):
    __tablename__ = "accoutManager"
    name = db.Column(db.String(128), nullable = False, primary_key = True, unique = True)
    password = db.Column(db.String(128), nullable = False)
    def __repr__(self):
        return f'<Accout: {self.name}>'
    

class RollcallHistory(db.Model):
    __tablename__ = "rollcallhistory"
    id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    date_create = db.Column(db.DateTime, default = datetime.now(tz=None))
    studentdata = db.Column(db.String(10), db.ForeignKey("studentData.MSSV"), nullable = True)
    def __repr__(self):
        return f'<Accout: {self.name}>'


class StudentData(db.Model):
    __tablename__ = "studentData"
    MSSV = db.Column(db.String(10), primary_key = True, nullable = False, unique = True)
    name = db.Column(db.String(128), nullable = False)
    RFID = db.relationship('RFID', backref = 'studentData')
    rollcallHistory = db.relationship('RollcallHistory', backref = 'studentData')
    def __repr__(self):
        return f'<Student: {self.name}>'


class RFID(db.Model):
    __tablename__ = "rfid"
    id = db.Column(db.String(16), primary_key = True, nullable = False, unique = True)
    fingerId = db.relationship('FingerPrintData1', backref = 'rfid')
    student_data = db.Column(db.String(10),db.ForeignKey("studentData.MSSV"), nullable = True)
    def __repr__(self):
        return f'<Accout: {self.name}>'


class FingerPrintData1(db.Model):
    __tablename__ = "fingerPrintData"
    fingerId = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    FingerPrintTemplate = db.Column(db.String(1024), nullable = True)
    RFID = db.Column(db.String(16), db.ForeignKey("rfid.id"), nullable = True)
    def __repr__(self):
        return f'<Accout: {self.name}>'
    
    
with app.app_context():
    db.create_all()  

#-------------------------------------------CLIENT COMMUNICATION AREA-------------------------------------------

@app.route('/upload_fingerprint', methods=['GET','POST'])
def upload_fingerprint():
    try:
        data = request.json
        fingerprint_base64 = data.get('fingerprint')
        filename=data.get('filename')
        
        if not fingerprint_base64 or not filename:
            return jsonify({'error': 'Fingerprint data or filename is missing'}), 400
        
        # Giai ma base64 du lieu nhan
        fingerprint_data = base64.b64decode(fingerprint_base64)


        #kiểm tra xem RFID có tồn tại không
        check_RFID = RFID.query.filter_by(id = filename)
        #RFID chưa tồn tại thì tạo một cái
        if(not check_RFID):
            make_new_RFID = RFID(id = filename)
            db.session.add(make_new_RFID)
            db.session.commit()

        #giờ đã chắc chắn có RFID giờ là lúc tạo fingerPrintData1
        #tạo hàng cho bảng fingerPrintData gắn với RFID đã tạo/có sẵn từ trước
        new_Finger_data = FingerPrintData1(FingerPrintTemplate = fingerprint_data, RFID = filename)
        db.session.add(new_Finger_data)
        #lấy id này làm tên file luôn cho tiện
        db.session.flush()
        number = new_Finger_data.fingerId
        filepath = "fingerFile/" + filename + "/" + str(number)
        #thêm vào cơ sỡ dữ liệu
        db.session.commit()
        #luu data ra file
        folderPath = "fingerFile/" + filename

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        with open(filepath, 'wb') as f:
            f.write(fingerprint_data)

        return jsonify({'message': 'Fingerprint data received successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    
@app.route('/download_fingerprint', methods=['GET','POST'])
def download_fingerprint():
    try:        
        file_name = request.args.get('file')
        file_id = request.args.get('fileId')
        filepath = "fingerFile/" + file_name + "/" + file_id 


        if not os.path.exists(filepath):
            return jsonify({'error': 'Fingerprint data not found'}), 404
        response=send_file(filepath, as_attachment=True)        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/check_next_finger_id', methods=['GET','POST'])
def check_next_finger_id():
    try:        
        file_name = request.args.get('file')
        file_id = request.args.get('fileId')
        path = "fingerFile/" + file_name

        dir_list = os.listdir(path)
        files_list = [f for f in dir_list if os.path.isfile(path + '/' + f)]

        nextValue = 0 #id file cần trả về
        find_id = False 

        if not files_list: #nếu list rỗng thì return -1 nghĩa là không có data
            return "-1"

        for i in files_list:
            if(int(file_id) == -1): # yêu  cầu từ client là -1 tức là cần tìm data đầu tiên
                return int(i)
            if(find_id): #nếu đã khớp id trong vòng lập trước thì trong vòng lập này trả về id hiện tại
                nextValue = int(file_id)
                return str(nextValue)
            if(int(i) == file_id):# nếu khớp id thì find_id True để vòng lập sau trả về id tiếp theo
                find_id = True
        return "-1" # nếu không còn id để kiểm tra nữa thì trả về -1 tức là hết id
    except:
        return "-1"
    

@app.route('/rollCall', methods=['GET','POST'])
def rollCall():
    try:        
        file_name = request.args.get('RFID')
        studentRollCall = StudentData.query.filter(StudentData.RFID.has(id = file_name)).first()
        if(studentRollCall):
            history = RollcallHistory(studentData = studentRollCall)
            db.session.add(history)
            db.session.commit()
            return "1"
        return "-1"
    except:
        return "-1"

 #-------------------------------------------ACTUAL ROUTE AREA-------------------------------------------       


#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
@app.route('/testPage', methods = ['POST','GET'])
def testPage():
    form = test_form()
    if form.validate_on_submit():
        fingerprint_data = "QWERTYUIOPASDFGHJKLZXCVBNM="
        filename = form.RFID.data

        new_RFID = RFID.query.filter_by(id = filename).first()
        if(not new_RFID):
            make_new_RFID = RFID(id = filename)
            db.session.add(make_new_RFID)
            db.session.commit()
        new_RFID = RFID.query.filter_by(id = filename)
        new_Finger_data = FingerPrintData1(FingerPrintTemplate = fingerprint_data, RFID = filename)
        db.session.add(new_Finger_data)

        db.session.flush()
        number = new_Finger_data.fingerId

        folderPath = "fingerFile/" + filename
        filepath = "fingerFile/" + filename + "/" + str(number)

        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        with open(filepath, 'wb') as f:
            f.write(str.encode(fingerprint_data)) #str.encode for test only

        db.session.commit()


    return render_template('testPage.html', form = form, SH = SH)



@app.route('/testPage1', methods = ['POST','GET'])
def testPage1():
    form = test_form()
    if form.validate_on_submit():
        file_name = form.RFID.data
        studentRollCall = StudentData.query.filter(StudentData.RFID.any(id = file_name)).first()
        if(studentRollCall):
            history = RollcallHistory(studentdata = studentRollCall.MSSV)
            db.session.add(history)
            db.session.commit()

        db.session.commit()


    return render_template('testPage.html', form = form, SH = SH)
    


@app.route('/login1', methods = ['POST','GET'])
def login1():
    form = login_form()
    if form.validate_on_submit():
        accName = AccoutManager.query.filter_by(name = form.name.data).first()
        if accName:
            if bcrypt.check_password_hash(accName.password, form.passworld.data):
                session["user"] = accName.name
                SH.update()
                return redirect('/')
    return render_template('login.html', form = form, SH = SH)



@app.route('/register1', methods = ['POST','GET'])
def register1():
#    if SH.isLogOn():
        form = Create_Accout_form1()
        if form.validate_on_submit():
            encryPassWorld = bcrypt.generate_password_hash(form.passworld.data)
            new_acc = AccoutManager(name = form.name.data, password = encryPassWorld)
            db.session.add(new_acc)
            db.session.commit()
            return redirect('/login1')
            
        return render_template('new_accout.html', form = form, SH = SH)


@app.route('/fingerPrintPage1', methods = ['POST','GET'])
def fingerPrintPage1():
#    if SH.isLogOn():
#        if SH.permissionList["SEE::FINGERPRINTPAGE"] == False:
#            return redirect('/NO PERMISSON')

        FingerPrints = FingerPrintData1.query.order_by(FingerPrintData1.fingerId).all()
        return render_template('fingerPrint1.html', FingerPrints = FingerPrints, SH = SH)

#    else:
#       return redirect('/login')


@app.route('/RFIDPage', methods = ['POST','GET'])
def RFIDPage():
#    if SH.isLogOn():
#        if SH.permissionList["SEE::FINGERPRINTPAGE"] == False:
#            return redirect('/NO PERMISSON')

        RFIDs = RFID.query.order_by(RFID.id).all()
        return render_template('RFIDPage.html', RFIDs = RFIDs, SH = SH)

#    else:
#       return redirect('/login')


@app.route('/CreateNewStudent', methods = ['POST','GET'])
def CreateNewStudent():
#    if SH.isLogOn():
#        if SH.permissionList["CREATE::STUDENT"] == False:
#            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        form = create_student_Data_form()
        if form.validate_on_submit():
            new_stu = StudentData(MSSV = form.MSSV.data, name = form.name.data)
            db.session.add(new_stu)
            new_stu.RFID.append(RFID.query.filter_by(id =form.RFID.data).first())
            db.session.commit()
            return redirect('/')
            
        return render_template('CreateNewStudent.html', form = form, SH = SH)
        #----------------------------------------------------------------------------------------
#    else:
#        return redirect('/login')



@app.route('/pageStudent', methods = ['POST','GET'])
def pageStudent():
#    if SH.isLogOn():
#        if SH.permissionList["SEE::STUDENTPAGE"] == False:
#            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        Students = StudentData.query.order_by(StudentData.MSSV).all()
        return render_template('pageStudent.html', Students = Students, SH = SH)
        #----------------------------------------------------------------------------------------
#    else:
#       return redirect('/login')


@app.route('/historyPage', methods = ['POST','GET'])
def historyPage():
#    if SH.isLogOn():
#        if SH.permissionList["SEE::STUDENTPAGE"] == False:
#            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        historyList = RollcallHistory.query.order_by(RollcallHistory.date_create).all()
        return render_template('historyList.html', historyList = historyList, SH = SH)
        #----------------------------------------------------------------------------------------
#    else:
#       return redirect('/login')


@app.route('/deleteThing/<string:what>/<string:id>')
def deleteThing(id,what):
#    if SH.isLogOn():
#        if SH.permissionList["SEE::MAINPAGE"] == False:
#            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        if what == "student":
            student_to_delete = StudentData.query.get_or_404(id)
            db.session.delete(student_to_delete)
            db.session.commit()
            return redirect('/pageStudent')
        elif what == "RFID":
            RFID_to_delete = RFID.query.get_or_404(id)
            db.session.delete(RFID_to_delete)
            db.session.commit()
            return redirect('/RFIDPage')
        elif what == "finger":
            finger_to_delete = FingerPrintData1.query.get_or_404(id)
            db.session.delete(finger_to_delete)
            db.session.commit()
            return redirect('/fingerPrintPage1')
        #----------------------------------------------------------------------------------------
#    else:
#        return redirect('/login')


@app.route('/updatething/<string:what>/<string:id>', methods = ['POST','GET'])
def updatething(id,what):
#    if SH.isLogOn():
#        if SH.permissionList["SEE::MAINPAGE"] == False:
#            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        if what == "student":
            student_to_update = StudentData.query.get_or_404(id)
            form = create_student_Data_form()
            if request.method == 'POST':
                student_to_update.MSSV = form.MSSV.data
                student_to_update.name = form.name.data
                student_to_update.RFID.clear()
                student_to_update.RFID.append(form.RFID.data)
                try:
                    db.session.commit()
                    return redirect('/pageStudent')
                except:
                    return 'something stopping us to do this action'
            else:
                return render_template('updateStudent.html', student_to_update = student_to_update, form = form, SH = SH)
        #----------------------------------------------------------------------------------------
#    else:
#        return redirect('/login')

@app.route('/', methods = ['POST','GET'])
def index():
    return render_template('mainPage.html', SH = SH)

@app.route('/logout')
def logout():
    SH.logout()
    return redirect('/')


#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

#-------------------------------------------MAIN RUN -------------------------------------------

if __name__ == "__main__":
    app.run(debug = True)#, host = '172.20.10.9', port  = 5000) 
# host = '0.0.0.0', port = '5000'
