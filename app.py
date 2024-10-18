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
from random import choice
from string import ascii_letters

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
    name = StringField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"account name"})
    passworld = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"Password"})
    retypePassworld = PasswordField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"Retype Password"})
    submit = SubmitField("create")
    def validate_passworld(self, passworld):
        if passworld.data != self.retypePassworld.data:
            raise ValidationError("Password does not match, please re-enter")
    def validate_name(self, name):
        exitting_name = AccoutManager.query.filter_by(name = name.data).first()
        if exitting_name:
            raise ValidationError("The account name already exists, please choose another name")
        

class create_student_Data_form(FlaskForm):
    MSSV = StringField(validators = [input_required(), length(min=8, max=16)], render_kw={"placeholder":"Student ID"})
    name = StringField(validators = [input_required(), length(min=1, max=128)], render_kw={"placeholder":"tên sinh viên"})
    RFID = StringField(validators = [length(min=1, max=32)], render_kw={"placeholder":"RFID"})
    Class = StringField(validators = [input_required(), length(min=1, max=16)], render_kw={"placeholder":"tên lớp"})
    submit = SubmitField("create")
    def validate_MSSV(self, MSSV):
        exitting_MSSV = StudentData.query.filter_by(MSSV = MSSV.data).first()
        if exitting_MSSV:
            raise ValidationError("Student code already exists")


class create_class_form(FlaskForm):
    id = StringField(validators = [input_required(), length(min=1, max=16)], render_kw={"placeholder":"Subject id"})
    name = StringField(validators = [input_required(), length(min=1, max=128)], render_kw={"placeholder":"Subject name"})
    teacher = StringField(validators = [input_required(), length(min=10, max=16)], render_kw={"placeholder":"Teacher ID"})
    submit = SubmitField("create")
    def validate_name(self, id):
        exitting_name = ClassData.query.filter_by(id = id.data).first()
        if exitting_name:
            raise ValidationError("class id already exists")


class create_teacher_form(FlaskForm):
    id = StringField(validators = [input_required(), length(min=8, max=16)], render_kw={"placeholder":"Teacher ID"})
    name = StringField(validators = [input_required(), length(min=1, max=128)], render_kw={"placeholder":"Teacher name"})
    submit = SubmitField("create")
    def validate_id(self, id):
        exitting_id = Teacher.query.filter_by(id = id.data).first()
        if exitting_id:
            raise ValidationError("Teacher code already exists")
        
class add_student_form(FlaskForm):
    MSSV = StringField(validators = [input_required(), length(min=8, max=16)], render_kw={"placeholder":"Student ID"})
    submit = SubmitField("Add")

class add_class_form(FlaskForm):
    id = StringField(validators = [input_required(), length(min=1, max=16)], render_kw={"placeholder":"Subject id"})
    submit = SubmitField("Add")

class test_form(FlaskForm):
    RFID = StringField(validators = [input_required(), length(min=1, max=16)], render_kw={"placeholder":"Enter RFID"})
    submit = SubmitField("create")


class login_form(FlaskForm):
    name = StringField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"Accout"})
    passworld = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"Passworld"})
    submit = SubmitField("log in")


            
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

Student_Subject = db.Table(
    'Student_Subject',
    db.Column('SubjectId',db.String(16), db.ForeignKey("classData.id")),
    db.Column('StudentId',db.String(16), db.ForeignKey("studentData.MSSV"))

)

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

class Teacher(db.Model):
    __tablename__ = "teacher"
    id = db.Column(db.String(16), primary_key = True, nullable = False, unique = True)
    name = db.Column(db.String(128), nullable = False)
    className = db.relationship('ClassData', backref = 'teacher')
    def __repr__(self):
        return f'<Teacher: {self.name}>'



class ClassData(db.Model):
    __tablename__ = "classData"
    id = db.Column(db.String(16), primary_key = True, nullable = False, unique = True)
    name = db.Column(db.String(128), primary_key = True, nullable = False, unique = True)
    student = db.relationship('StudentData', secondary = Student_Subject, backref = 'ClassData')
    teacherId = db.Column(db.String(16), db.ForeignKey("teacher.id"), nullable = True)
    def __repr__(self):
        return f'<Class: {self.name}>'



class StudentData(db.Model):
    __tablename__ = "studentData"
    MSSV = db.Column(db.String(16), primary_key = True, nullable = False, unique = True)
    name = db.Column(db.String(128), nullable = False)
    RFID = db.relationship('RFID', backref = 'studentData')
    rollcallHistory = db.relationship('RollcallHistory', backref = 'studentData')
    def __repr__(self):
        return f'<Student: {self.name}>'


class RFID(db.Model):
    __tablename__ = "rfid"
    id = db.Column(db.String(32), primary_key = True, nullable = False, unique = True)
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
       
        fingerprint_data_compact = ""
        fingerprint_data_compact = str(fingerprint_base64)[:32] + " ... " + str(fingerprint_base64)[len(str(fingerprint_base64))-32:]
        fingerprint_data = base64.b64decode(fingerprint_base64)
        #kiểm tra xem RFID có tồn tại không
        check_RFID = RFID.query.filter_by(id = filename).first()
        #RFID chưa tồn tại thì tạo một cái
        if(not check_RFID):
            make_new_RFID = RFID(id = filename)
            db.session.add(make_new_RFID)
            db.session.commit()
        #giờ đã chắc chắn có RFID giờ là lúc tạo fingerPrintData1
        #tạo hàng cho bảng fingerPrintData gắn với RFID đã tạo/có sẵn từ trước
        new_Finger_data = FingerPrintData1(FingerPrintTemplate = fingerprint_data_compact, RFID = filename)
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
        print(file_name)
        print(file_id)
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
                return str(i)
            if(find_id): #nếu đã khớp id trong vòng lập trước thì trong vòng lập này trả về id hiện tại
                nextValue = i
                return str(nextValue)
            if(int(i) == int(file_id)):# nếu khớp id thì find_id True để vòng lập sau trả về id tiếp theo
                find_id = True
        return "-1" # nếu không còn id để kiểm tra nữa thì trả svề -1 tức là hết id
    except:
        return "-1"
    

@app.route('/rollCall', methods=['GET','POST'])
def rollCall():
    try:        
        file_name = request.args.get('RFID')
        print(file_name)
        studentRollCall = StudentData.query.filter(StudentData.RFID.any(id = file_name)).first()
        print("query pass")
        if(studentRollCall):
            history = RollcallHistory(studentData = studentRollCall)
            print("create pass")
            db.session.add(history)
            db.session.commit()
            print("complete")
            return "1"
        print("not found")
        return "-1"
    except:
        print("error")
        return "-1"

 #-------------------------------------------ACTUAL ROUTE AREA-------------------------------------------       


#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
@app.route('/testPage', methods = ['POST','GET'])
def testPage():
    form = test_form()
    if form.validate_on_submit():
        fingerprint_data = ''.join(choice(ascii_letters) for i in range(256))
        if (len(fingerprint_data) > 64):
            fingerprint_data_compact = fingerprint_data[:32] + " ... " + fingerprint_data[len(fingerprint_data)-32:]
        filename = form.RFID.data
        new_RFID = RFID.query.filter_by(id = filename).first()
        if(not new_RFID):
            make_new_RFID = RFID(id = filename)
            db.session.add(make_new_RFID)
            db.session.commit()
        new_RFID = RFID.query.filter_by(id = filename)
        new_Finger_data = FingerPrintData1(FingerPrintTemplate = fingerprint_data_compact, RFID = filename)
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
    

 
@app.route('/login', methods = ['POST','GET'])
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



@app.route('/register', methods = ['POST','GET'])
def register1():
    form = Create_Accout_form1()
    if form.validate_on_submit():
        encryPassWorld = bcrypt.generate_password_hash(form.passworld.data)
        new_acc = AccoutManager(name = form.name.data, password = encryPassWorld)
        db.session.add(new_acc)
        db.session.commit()
        return redirect('/login')
    return render_template('new_accout.html', form = form, SH = SH)



@app.route('/ClassPage',methods = ['POST','GET'])
def ClassPage():
    classes = ClassData.query.order_by(ClassData.id).all()
    return render_template('ClassPage.html', classes = classes, SH = SH)


@app.route('/CreateNewClass',methods = ['POST','GET'])
def CreateNewClass():
    form = create_class_form()
    if form.validate_on_submit():
        new_class = ClassData(id = form.id.data ,name = form.name.data, teacherId = form.teacher.data)
        db.session.add(new_class)
        db.session.commit()
        return redirect('/ClassPage')
    return render_template('CreateNewClass.html', form = form, SH = SH)


@app.route('/TeacherPage',methods = ['POST','GET'])
def TeacherPage():
    teachers = Teacher.query.order_by(Teacher.id).all()
    return render_template('teacherPage.html', teachers = teachers, SH = SH)


@app.route('/CreateNewTeacher',methods = ['POST','GET'])
def CreateNewTeacher():
    form = create_teacher_form()
    if form.validate_on_submit():
        new_teacher = Teacher(name = form.name.data, id = form.id.data)
        db.session.add(new_teacher)
        db.session.commit()
        return redirect('/TeacherPage')
    return render_template('CreateNewTeacher.html', form = form, SH = SH)


@app.route('/fingerPrintPage1', methods = ['POST','GET'])
def fingerPrintPage1():
        FingerPrints = FingerPrintData1.query.order_by(FingerPrintData1.fingerId).all()
        return render_template('fingerPrint1.html', FingerPrints = FingerPrints, SH = SH)

@app.route('/RFIDPage', methods = ['POST','GET'])
def RFIDPage():
        RFIDs = RFID.query.order_by(RFID.id).all()
        return render_template('RFIDPage.html', RFIDs = RFIDs, SH = SH)

@app.route('/CreateNewStudent', methods = ['POST','GET'])
def CreateNewStudent():
        form = create_student_Data_form()
        if form.validate_on_submit():
            classRoom = ClassData.query.filter_by(id = form.Class.data).first_or_404()
            new_stu = StudentData(MSSV = form.MSSV.data, name = form.name.data)
            new_stu.ClassData.append(classRoom)
            db.session.add(new_stu)
            RFID_exit = RFID.query.filter_by(id = form.RFID.data).first_or_404()
            if (RFID_exit):
                new_stu.RFID.append(RFID_exit)
            db.session.commit()
            return redirect('/pageStudent')
            
        return render_template('CreateNewStudent.html', form = form, SH = SH)

@app.route('/pageStudent', methods = ['POST','GET'])
def pageStudent():
        Students = StudentData.query.order_by(StudentData.MSSV).all()
        return render_template('pageStudent.html', Students = Students, SH = SH)

@app.route('/historyPage', methods = ['POST','GET'])
def historyPage():
        historyList = RollcallHistory.query.order_by(RollcallHistory.date_create).all()
        return render_template('historyList.html', historyList = historyList, SH = SH)

@app.route('/deleteThing/<string:what>/<string:id>')
def deleteThing(id,what):
        if what == "student":
            student_to_delete = StudentData.query.get_or_404(id)
            db.session.delete(student_to_delete)
            db.session.commit()
            return redirect('/pageStudent')
        elif what == "RFID":
            RFID_to_delete = RFID.query.get_or_404(id)
            Child_Finger = FingerPrintData1.query.filter_by(RFID = id).all()
            for CF in Child_Finger:
                path ="fingerFile/" + id + "/" + str(CF.fingerId)
                if os.path.exists(path):
                    os.remove(path)
                finger_to_delete = FingerPrintData1.query.get_or_404(CF.fingerId)
                db.session.delete(finger_to_delete)
            db.session.delete(RFID_to_delete)
            db.session.commit()
            return redirect('/RFIDPage')
        elif what == "finger":
            file_name = RFID.query.filter(RFID.fingerId.any(fingerId = id)).first()
            if (file_name):
                path ="fingerFile/" + file_name.id + "/" + id
                if os.path.exists(path):
                    os.remove(path)
            finger_to_delete = FingerPrintData1.query.get_or_404(id)
            db.session.delete(finger_to_delete)
            db.session.commit()
            return redirect('/fingerPrintPage1')
        elif what == "class":
            class_to_delete = ClassData.query.get_or_404(id)
            db.session.delete(class_to_delete)
            db.session.commit()
            return redirect('/ClassPage')
        elif what == "teacher":
            teacher_to_delete = Teacher.query.get_or_404(id)
            db.session.delete(teacher_to_delete)
            db.session.commit()
            return redirect('/TeacherPage')
        
@app.route('/addThing/<string:what>/<string:id>', methods = ['POST','GET'])
def addThing(id,what):
    if what == "student":
        student_to_update = StudentData.query.get_or_404(id)
        form = add_class_form()
        if form.validate_on_submit():
            class_to_add = ClassData.query.filter_by(id = form.id.data).first_or_404()
            student_to_update.ClassData.append(class_to_add)
            db.session.commit()
            return redirect('/pageStudent')
        else:
            return render_template('addStudent.html', student_to_update = student_to_update, form = form, SH = SH)
 
@app.route('/updateThing/<string:what>/<string:id>', methods = ['POST','GET'])
def updatething(id,what):
        if what == "student":
            student_to_update = StudentData.query.get_or_404(id)
            form = create_student_Data_form()
            if request.method == 'POST':
                student_to_update.MSSV = form.MSSV.data
                student_to_update.name = form.name.data
                RFID_exit = RFID.query.filter_by(id = form.RFID.data).first_or_404()
                if (RFID_exit):
                    student_to_update.RFID.clear()
                    student_to_update.RFID.append(RFID_exit)
                try:
                    db.session.commit()
                    return redirect('/pageStudent')
                except:
                    return 'something stopping us to do this action'
            else:
                return render_template('updateStudent.html', student_to_update = student_to_update, form = form, SH = SH)
            
        if what == "class":
            class_to_update = ClassData.query.filter_by(id = id).first_or_404()
            form = create_class_form()
            if request.method == 'POST':
                class_to_update.teacherId = form.teacher.data
                class_to_update.name = form.name.data
                try:
                    db.session.commit()
                    return redirect('/ClassPage')
                except:
                    return 'something stopping us to do this action'
            else:
                return render_template('updateClass.html', class_to_update = class_to_update, form = form, SH = SH)
            
        if what == "teacher":
            teacher_to_update = Teacher.query.get_or_404(id)
            form = create_teacher_form()
            if request.method == 'POST':
                teacher_to_update.id = form.id.data
                teacher_to_update.name = form.name.data
                try:
                    db.session.commit()
                    return redirect('/TeacherPage')
                except:
                    return 'something stopping us to do this action'
            else:
                return render_template('updateTeacher.html', teacher_to_update = teacher_to_update, form = form, SH = SH)

@app.route('/', methods = ['POST','GET'])
def index():
    return render_template('mainPage.html', SH = SH)

@app.route('/logout')
def logout():
    SH.logout()
    return redirect('/')


#-------------------------------------------MAIN RUN -------------------------------------------

if __name__ == "__main__":
    app.run(debug = True)#, host = '172.20.10.9', port  = 5000) 
# host = '0.0.0.0', port = '5000'
