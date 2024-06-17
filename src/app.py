# set-Executionpolicy -scope process -Executionpolicy Bypass  
# env\Scripts\activate
import random
from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from flask_sock import Sock
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import input_required, length, ValidationError
from flask_bcrypt import Bcrypt
from sqlalchemy import func

#----------------------------------------INIT AREA------------------------------------------


#flask init
app = Flask(__name__)
sock = Sock(app)
#SQL init
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'GTA_6_WILL_RELEASE_NEXT_YEAR'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#----------------------------globle variable and funtion------------------------------------------------
class Create_Accout_form(FlaskForm):
    name = StringField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"tên tài khoản"})
    passworld = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"mật khẩu"})
    retypePassworld = PasswordField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"nhập lại mật khẩu"})
    permissionLevel = SelectField("loại tài khoản", choices=["học sinh","giáo viên","quản lý","phụ huynh"])
    submit = SubmitField("tạo tài khoản")
    def validate_passworld(self, passworld):
        if passworld.data != self.retypePassworld.data:
            raise ValidationError("mật khẩu không trùng khớp, vui lòng nhập lại")
    def validate_name(self, name):
        exitting_name = Accout.query.filter_by(name = name.data).first()
        if exitting_name:
            raise ValidationError("tên tài khoản đã tồn tại vui lòng chọn một tên khác")



class passworld_change_form(FlaskForm):
    oldPass = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"nhập mật khẩu cũ"})
    newPass = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"mật khẩu mới"})
    retypePass = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":" nhập lại mật khẩu mới"})
    submit = SubmitField("đổi mật khẩu")
    def validate_newPass(self, newPass):
        if newPass.data != self.retypePass.data:
            raise ValidationError("mật khẩu không trùng khớp, vui lòng nhập lại")
    def validate_oldPass(self, oldPass):
        accName = Accout.query.filter_by(name = SH.accName).first()
        if not bcrypt.check_password_hash(accName.password, oldPass.data):
            raise ValidationError("mật khẩu sai bét")

        

        
class login_form(FlaskForm):
    name = StringField(validators = [input_required(), length(min=4, max=20)], render_kw={"placeholder":"tài khoản"})
    passworld = PasswordField(validators = [input_required(), length(min=4, max=128)], render_kw={"placeholder":"mật khẩu"})
    submit = SubmitField("đăng nhập")



class create_student_form(FlaskForm):
    MSSV = StringField(validators = [input_required(), length(min=10, max=10)], render_kw={"placeholder":"mã số sinh viên"})
    name = StringField(validators = [input_required(), length(min=1, max=128)], render_kw={"placeholder":"tên sinh viên"})
    FingerId = IntegerField(render_kw={"placeholder":"ID vân tay "})
    className = StringField(validators = [length(min=1, max=128)], render_kw={"placeholder":"tên lớp học"})
    birthDay =  DateField(format = '%Y-%m-%d')
    acclinking = StringField(validators = [ length(min=1, max=128)], render_kw={"placeholder":"tên tài khoản liên kết"})
    submit = SubmitField("tạo")
    def validate_acclinking(self, acclinking):
        exitting_acc = Accout.query.filter_by(name = acclinking.data).first()
        acc_type = Accout.query.filter_by(name = acclinking.data).first().type
        already_linked = Accout.query.filter_by(name = acclinking.data).first().student
        if not exitting_acc:
            raise ValidationError("kiếm đâu ra cái tên tài khoản vậy, chưa đăng ký đúng ko?")
        elif acc_type != "học sinh":
            raise ValidationError("tài khoản không dành cho học sinh")
        elif already_linked:
            raise ValidationError("tài khoản này đã được sử dụng cho một sinh viên khác")
    def validate_FingerId(self, FingerId):
        exitting_FingerId = FingerPrint.query.filter_by(ID = FingerId.data).first()
        if not exitting_FingerId:
            raise ValidationError("ID vân tay ko tồn tại")
    def validate_className(self, className):
        exitting_className = ClassRom.query.filter_by(name = className.data).first()
        if not exitting_className:
            raise ValidationError("lớp không tồn tại")
        

class create_class_form(FlaskForm):
    name = StringField(validators = [input_required(), length(min=0, max=16)], render_kw={"placeholder":"tên lớp"})
    department = SelectField("khoa", choices=["Điện-Điện tử","Công nghệ thông tin","quản trị","thiết kế","xây dựng","cơ khí","thực phẩm"])
    teacher = StringField(validators = [length(min=10, max=10)], render_kw={"placeholder":"id giáo viên"})
    submit = SubmitField("tạo")
    def validate_name(self,name):
        exitting_name = ClassRom.query.filter_by(name = name.data).first()
        if exitting_name:
            raise ValidationError("ủa, cái lớp này có rồi, tạo chi nữa v:")
    def validate_teacher(self,teacher):
        exitting_teacher = Teacher.query.filter_by(ID = teacher.data).first()
        if not exitting_teacher:
            raise ValidationError("giáo viên này hiện đang không công tác tại trường")
        


class create_teacher_form(FlaskForm):
    ID = StringField(validators = [input_required(), length(min=10, max=10)], render_kw={"placeholder":"id giáo viên"})
    name = StringField(validators = [input_required(), length(min=0, max=16)], render_kw={"placeholder":"tên giáo viên"})
    acclinking = StringField(validators = [ length(min=1, max=128)], render_kw={"placeholder":"tên tài khoản liên kết"})
    submit = SubmitField("tạo")
    def validate_ID(self,ID):
        exitting_ID = Teacher.query.filter_by(ID = ID.data).first()
        if exitting_ID:
            raise ValidationError("trùng ID giáo viên, chọn ID khác")
    def validate_acclinking(self, acclinking):
        exitting_acc = Accout.query.filter_by(name = acclinking.data).first()
        acc_type = Accout.query.filter_by(name = acclinking.data).first().type 
        if not exitting_acc:
            raise ValidationError("kiếm đâu ra cái tên tài khoản vậy, chưa đăng ký đúng ko?")
        elif acc_type != "giáo viên":
            raise ValidationError("tài khoản không dành cho giáo viên")
        
class codetest(FlaskForm):
    stringdata = StringField(validators = [input_required(), length(min=0, max=256)], render_kw={"placeholder":"viết cái j đó"})
    submit = SubmitField("xem kết quả")


class sessionHandle():
    accName = ""
    accRight = ""
    permissionList = {
        "SEE::MAINPAGE":False,
#        "SEE::DEVICEPAGE":False,
        "SEE::REGISTERPAGE":False,
        "SEE::CLASSPAGE":False,
        "SEE::STUDENTPAGE":False,
        "SEE::FINGERPRINTPAGE":False,
        "SEE::TEACHERPAGE":False,
        "SEE::MANAGERPAGE":False,
        "SEE::PROFILE":False,
        "CREATE::STUDENT":False,
        "CREATE::TEACHER":False,
        "CREATE::CLASS":False,
#        "CREATE::MANAGER":False,
#        "CHANGE::SELF::USERNAME":False,
        "CHANGE::SELF::PASSWORD":False,
        "CHANGE::STUDENT::USERNAME":False,
        "CHANGE::STUDENT::PASSWORD":False,
        "CHANGE::TEACHER::USERNAME":False,
        "CHANGE::TEACHER::PASSWORD":False,
        "CHANGE::MANAGERPAGE::USERNAME":False,
        "CHANGE::MANAGERPAGE::PASSWORD":False,
        "CHANGE::ACCRIGHT":False,
    }
    accTypeToCreate = []
    def update(self):
        self.accName = session["user"]
        self.accRight = session["right"]
        self.permissionUpdate()
            
    # thiết lập quyền:
    def permissionUpdate(self):
        self.permissionList.update({
                    "SEE::MAINPAGE":False,
                    "SEE::DEVICEPAGE":False,
                    "SEE::REGISTERPAGE":False,
                    "SEE::CLASSPAGE":False,
                    "SEE::STUDENTPAGE":False,
                    "SEE::TEACHERPAGE":False,
                    "SEE::MANAGERPAGE":False,
                    "SEE::PROFILE":False,
                    "CREATE::STUDENT":False,
                    "CREATE::TEACHER":False,
                    "CREATE::MANAGER":False,
                    "CHANGE::SELF::USERNAME":False,
                    "CHANGE::SELF::PASSWORD":False,
                    "CHANGE::STUDENT::USERNAME":False,
                    "CHANGE::STUDENT::PASSWORD":False,
                    "CHANGE::TEACHER::USERNAME":False,
                    "CHANGE::TEACHER::PASSWORD":False,
                    "CHANGE::MANAGERPAGE::USERNAME":False,
                    "CHANGE::MANAGERPAGE::PASSWORD":False,
                    "CHANGE::ACCRIGHT":False,
                })
        match self.accRight:
            case "học sinh":
                self.permissionList.update({
                    "SEE::PROFILE":True,
                    "SEE::MAINPAGE":True,
                })
            case "giáo viên":
                self.permissionList.update({
                    "SEE::MAINPAGE":True,
                    "SEE::REGISTERPAGE":True,
                    "CHANGE::SELF::PASSWORD":True,
                    "CHANGE::STUDENT::USERNAME":True,
                    "SEE::PROFILE":True,
                    "CHANGE::STUDENT::PASSWORD":True,
                })
            case "quản lý":
                self.permissionList.update({
                    "SEE::MAINPAGE":True,
                    "SEE::DEVICEPAGE":True,
                    "SEE::REGISTERPAGE":True,
                    "SEE::CLASSPAGE":True,
                    "SEE::STUDENTPAGE":True,
                    "SEE::FINGERPRINTPAGE":True,
                    "SEE::TEACHERPAGE":True,
                    "SEE::MANAGERPAGE":True,
                    "SEE::PROFILE":True,
                    "CREATE::STUDENT":True,
                    "CREATE::TEACHER":True,
                    "CREATE::CLASS":True,
                    "CREATE::MANAGER":True,
                    "CHANGE::SELF::USERNAME":True,
                    "CHANGE::SELF::PASSWORD":True,
                    "CHANGE::STUDENT::USERNAME":True,
                    "CHANGE::STUDENT::PASSWORD":True,
                    "CHANGE::TEACHER::USERNAME":True,
                    "CHANGE::TEACHER::PASSWORD":True,
                    "CHANGE::MANAGERPAGE::USERNAME":True,
                    "CHANGE::MANAGERPAGE::PASSWORD":True,
                    "CHANGE::ACCRIGHT":True,
                })
            case _:
                self.permissionList.update({
                    "SEE::MAINPAGE":False,
                    "SEE::DEVICEPAGE":False,
                    "SEE::REGISTERPAGE":False,
                    "SEE::CLASSPAGE":False,
                    "SEE::STUDENTPAGE":False,
                    "SEE::TEACHERPAGE":False,
                    "SEE::MANAGERPAGE":False,
                    "SEE::PROFILE":False,
                    "CREATE::STUDENT":False,
                    "CREATE::TEACHER":False,
                    "CREATE::MANAGER":False,
                    "CHANGE::SELF::USERNAME":False,
                    "CHANGE::SELF::PASSWORD":False,
                    "CHANGE::STUDENT::USERNAME":False,
                    "CHANGE::STUDENT::PASSWORD":False,
                    "CHANGE::TEACHER::USERNAME":False,
                    "CHANGE::TEACHER::PASSWORD":False,
                    "CHANGE::MANAGERPAGE::USERNAME":False,
                    "CHANGE::MANAGERPAGE::PASSWORD":False,
                    "CHANGE::ACCRIGHT":False,
                })

    def logout(self):
        self.accName = ""
        self.accRight = ""
    
    def isLogOn(self):
        try:
            if self.accName != "":
                acc = Accout.query.filter_by(name = self.accName).first
                if acc:
                    return True
                else:
                    return False
        except:
            return False

SH = sessionHandle()


#----------------------------------------SQL AREA------------------------------------------
classRoom_subject = db.Table('classRoom_subject',
                             db.Column('classRoom_id',db.Integer,db.ForeignKey('classRom.name')),
                             db.Column('subject_id',db.Integer,db.ForeignKey('subject.ID'))
                             )
classTime_student = db.Table('classTime_student',
                             db.Column('classTime_id',db.Integer,db.ForeignKey('classTime.ID')),
                             db.Column('student_mssv',db.Integer,db.ForeignKey('student.MSSV'))
                             )




class Accout(db.Model):
    __tablename__ = "accout"
    name = db.Column(db.String(128), nullable = False, primary_key = True, unique = True)
    password = db.Column(db.String(128), nullable = False)
    type = db.Column(db.String(16), nullable = False, default = "NONE")
    date_create = db.Column(db.DateTime, default = datetime.now(tz=None))
    student = db.relationship('Student', backref = 'accout')
    teacher = db.relationship('Teacher', backref = 'accout')
    def __repr__(self):
        return f'<Accout: {self.name}>'


class ClassRom(db.Model):
    __tablename__ = "classRom"
    name = db.Column(db.String(128), nullable = False, unique = True, primary_key = True)
    Teacher = db.Column(db.Integer, db.ForeignKey('teacher.ID'))
    department = db.Column(db.String(128), nullable = False)
    number = db.Column(db.Integer)
    Subject = db.Column(db.String(128))
    student = db.relationship('Student', backref = 'classrom')
    classtime = db.relationship('ClassTime', backref = 'classrom')
    classSubject = db.relationship("Subject",secondary = classRoom_subject, backref = 'class_subject')
    def __repr__(self):
        return f'<ClassRom: {self.name}>'
    

class Student(db.Model):
    __tablename__ = "student"
    MSSV = db.Column(db.String(10), primary_key = True, nullable = False, unique = True)
    name = db.Column(db.String(128), nullable = False)
    classId = db.Column(db.Integer, db.ForeignKey('classRom.name'))
    birthDay = db.Column(db.DateTime, nullable = False)
    fingerPrintId = db.Column(db.String(128), db.ForeignKey("fingerPrint.ID"))
    Accout_name = db.Column(db.String(128), db.ForeignKey("accout.name"))
    rollcall = db.relationship('RollCall', backref = 'student')
    def __repr__(self):
        return f'<Student: {self.name}>'
    
class FingerPrint(db.Model):
    __tablename__ = "fingerPrint"
    ID = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    fingerPrintTemplate = db.Column(db.String(128), unique = True)
    descreption = db.Column(db.String(128))    
    student = db.relationship('Student', backref = 'fingerPrint')                     
                             
class Teacher(db.Model):
    __tablename__ = "teacher"
    ID = db.Column(db.String(10), primary_key = True, nullable = False, unique = True)
    name = db.Column(db.String(128), nullable = False)
    Accout_name = db.Column(db.String(128), db.ForeignKey('accout.name'))
    classid = db.relationship('ClassRom', backref = 'teacher')
    clastime = db.relationship('ClassTime', backref = 'teacher')
    def __repr__(self):
        return f'<Teacher: {self.name}>'


class Subject(db.Model):
    __tablename__ = "subject"
    ID = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    name = db.Column(db.String(128), nullable = False)
    classtime = db.relationship('ClassTime', backref = 'subject')
    def __repr__(self):
        return f'<Subject: {self.name}>'


class ClassTime(db.Model):
    __tablename__ = "classTime"
    ID = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    Room = db.Column(db.String(128), nullable = False)
    Time = db.Column(db.Integer, nullable = False)
    subjectId = db.Column(db.Integer, db.ForeignKey('subject.ID'))
    classId = db.Column(db.Integer, db.ForeignKey('classRom.name'))
    Teacher = db.Column(db.Integer, db.ForeignKey('teacher.ID'))
    Student = db.Column(db.Integer, nullable = True)
    classSubject = db.relationship("Student",secondary = classTime_student , backref = 'time_student')
    def __repr__(self):
        return f'<ClassTime: {self.ID}>'


class RollCall(db.Model):
    __tablename__ = "rollCal"
    ID = db.Column(db.Integer, primary_key = True, nullable = False, unique = True) 
    student_MSSV = db.Column(db.String(10), db.ForeignKey('student.MSSV'))
    student_name = db.Column(db.String(128))
    student_class = db.Column(db.String(128))
    date_create = db.Column(db.DateTime, default = datetime.now(tz=None) )
   # student_name = db.column(db.String(10), db.ForeignKey(Student.MSSV))
    def __repr__(self):
        return f'<RollCall: {self.ID}>'



with app.app_context():
    db.create_all()  

#-------------------------------------------CLIENT COMMUNICATION AREA-------------------------------------------
def dataToCommand(datastring):
    comandString = ""
    PragramString = ["","","",""]
    getComand = False
    getparam = False
    currentParam = 0
    for s in datastring:
        if s == ' ' and getComand == True:
            continue
        elif s == '<':
            getComand = True
        elif s == '>':
            getparam = True
            getComand = False
        elif getparam == True and s == ';':
            currentParam += 1
        else:
            if getComand == True:
                comandString += s
            elif getparam == True:
                PragramString[currentParam] += s
    return (comandString, PragramString)

        
def handleCommand(commad1,param):
    handleState = ""
    match commad1: 
        #điểm danh thử nghiệm (tên, mssv)
        case  'FREEID':
            for i in range(128):
                id_exit = FingerPrint.query.filter_by(ID = i).first()
                if not id_exit:
                    handleState = i
                    break
        case  'FINGERNEW':
            if(param[2] != ""):
                new_FINGER = FingerPrint(ID = int(param[0]),fingerPrintTemplate = param[1], descreption = param[2])
                handleState = "dấu vân tay được đăng ký với ID:" + param[0] + ", mẫu vân tay\n: " + param[1] + "\n mô tả: " + param[2]
            else:
                new_FINGER = FingerPrint(fingerPrintTemplate = param[0], descreption = param[1])
                handleState = "dấu vân tay được đăng ký với mẫu vân tay: " + param[0] + "\n mô tả: " + param[1]
            db.session.add(new_FINGER)
            db.session.commit()
        #điểm danh (mã vân tay)
        case  'ROLLCALL':#<ROLLCALL>1
            stu = Student.query.filter_by(fingerPrintId = param[0]).first_or_404()
            if stu:
                new_RollCall = RollCall(student = stu, student_name = stu.name, student_class = stu.classId)
                db.session.add(new_RollCall)
                db.session.commit()
                handleState = "name: " + stu.name + ", MSSV: " + stu.MSSV
            else:
                handleState = "no student found"
        #xóa điểm danh (tùy chọn: tất cả, mới nhất,theo id, theo mssv; id,mssv)
        case 'ECHO':
            handleState = param[0]
        case 'GACHA':
            hoi = ["trọc cả đầu", "níu kéo được vài cọng tóc", "sáng bóng!!!", "50%", "còn tóc","tóc bạn ko đủ dài để hớt kiểu đầu đinh", "full 100%", "yes","còn j nữa đâu mà khóc với sầu"]
            general = ["nam", "nữ", "gay", "less", "vô tính", "hỗn hợp", "có cả hai", "bạn ko có hai thứ đó", "không thể dự đoán"]
            possible_choise = ["tuổi thọ của bạn là: "+str(random.randint(18, 120)), 
                               "bạn còn sống được "+str(random.randint(0, 100))+" năm", 
                               "tỷ lệ có người yêu của bạn là: "+str(random.randint(0, 100))+"%",
                               "iq của bạn là: "+str(random.randint(-200, 200)),
                               "giới tính của bạn là: "+random.choice(general),
                               "bạn học ở trường: STU (sai thế đéo nào đc)",
                               "link bí mật: https://www.youtube.com/watch?v=oHg5SJYRHA0",
                               "liệu bạn có bị hói hay không: "+random.choice(hoi)]
            handleState = random.choice(possible_choise)
        case 'KEOBUABAO':
            possible_actions = ["rock", "paper", "scissors"]
            computer_action = random.choice(possible_actions)
            match param[0]:
                case 'KEO':
                    if(computer_action == "rock" ):
                        handleState = "bạn: kéo; computer: búa --- thua rồi, đồ thất bại"
                    if(computer_action == "paper" ):
                        handleState = "bạn: kéo; computer: bao --- m chỉ may mắn được lần nay thôi"
                    if(computer_action == "scissors" ):
                        handleState = "bạn: kéo; computer: kéo --- có cố gắng nhưng dây là gới hạn của m"
                case 'BUA':
                    if(computer_action == "rock" ):
                        handleState = "bạn: búa; computer: búa --- đồ bắt chước"
                    if(computer_action == "paper" ):
                        handleState = "bạn: búa; computer: bao --- đây là tất cả những gì m có sao"
                    if(computer_action == "scissors" ):
                        handleState = "bạn: búa; computer: kéo --- cái j, không thể nào, sao t thua đc"
                case 'BAO':
                    if(computer_action == "rock" ):
                        handleState = "bạn: bao; computer: búa --- m ăn gian đúng ko, khai thiệt đi"
                    if(computer_action == "paper" ):
                        handleState = "bạn: bao; computer: bao --- chán"
                    if(computer_action == "scissors" ):
                        handleState = "bạn: bao; computer: kéo --- easy, too easy"
        case _:
            handleState = "unknow command"
    return handleState

@sock.route('/echo')
def echo(ws):
    while True:
        data = ws.receive()
        c, p, = dataToCommand(data)
        state = handleCommand(c,p)
        ws.send(state)
        if state == '<EXIT>':
            break






 #-------------------------------------------ACTUAL ROUTE AREA-------------------------------------------       



@app.route('/codeTest', methods = ['POST','GET'])
def codeTest():
    if SH.isLogOn():
        
        if SH.permissionList["SEE::MAINPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        form = codetest()
        state = "nothing here"
        if form.validate_on_submit():
            c, p = dataToCommand(form.stringdata.data)
            state = handleCommand(c,p)
            return render_template('codeTest.html', form = form, state = state, SH = SH)
        return render_template('codeTest.html', form = form, state = state, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')



@app.route('/', methods = ['POST','GET'])
def index():
    if SH.isLogOn():
        
        if SH.permissionList["SEE::MAINPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        return render_template('mainPage.html', SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')




@app.route('/login', methods = ['POST','GET'])
def login():
    form = login_form()
    if form.validate_on_submit():
        accName = Accout.query.filter_by(name = form.name.data).first()
        if accName:
            if bcrypt.check_password_hash(accName.password, form.passworld.data):
                session["user"] = accName.name
                session["right"] = accName.type
                SH.update()
                return redirect('/')
    return render_template('login.html', form = form, SH = SH)


@app.route('/register', methods = ['POST','GET'])
def register():
#    if SH.isLogOn():
#        if SH.permissionList["SEE::REGISTERPAGE"] == False:
 #           return redirect('/NO PERMISSON')
        form = Create_Accout_form()
        if form.validate_on_submit():
            encryPassWorld = bcrypt.generate_password_hash(form.passworld.data)
            new_acc = Accout(name = form.name.data, password = encryPassWorld, type = form.permissionLevel.data)
            db.session.add(new_acc)
            db.session.commit()
            return redirect('/login')
            
        return render_template('new_accout.html', form = form, SH = SH)
#    else:
 #       return redirect('/login')

@app.route('/<string:userName>/changePassworld', methods = ['POST','GET'])
def changePassworld(userName):
    if SH.isLogOn():
        if SH.permissionList["CHANGE::SELF::PASSWORD"] == False:
            return redirect('/NO PERMISSON')
        if SH.accName != userName:
            return redirect('/login')
        else:
        #---------------------------------------------------------------------------------------
            form = passworld_change_form()
            acc = Accout.query.filter_by(name = userName).first()
            if form.validate_on_submit():
                encryPassWorld = bcrypt.generate_password_hash(form.newPass.data)
                acc.password = encryPassWorld
                db.session.commit()
                return redirect(f'/Profile/{userName}')
            return render_template('changepass.html', form = form, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')
    

@app.route('/NO PERMISSON')
def NOpermission():
    return render_template('access_denied.html', SH = SH)

@app.route('/Profile/<string:userName>', methods = ['POST','GET'])
def ProfilePage(userName):
    if SH.isLogOn():
        if SH.permissionList["SEE::PROFILE"] == False:
            return redirect('/NO PERMISSON')
        if SH.accName != userName:
            return redirect('/login')
        else:
        #---------------------------------------------------------------------------------------
            acc = Accout.query.filter_by(name = userName).first()
            if SH.accRight == "học sinh":
                stu = Student.query.filter_by(Accout_name = acc.name).first_or_404()
                rollcallData = RollCall.query.filter_by(student_MSSV = stu.MSSV).all()
                return render_template('StudentProfile.html', SH = SH, acc = acc, student = stu, rollcalls = rollcallData)
            elif SH.accRight == "giáo viên":
                tc = Teacher.query.filter_by(Accout_name = acc.name).first_or_404()
                rollcallData = []
                countData = []
                count = 0
                for a_class in tc.classid:
                    classData =  RollCall.query.filter(RollCall.student_class == a_class.name, func.date(RollCall.date_create) == datetime.now(tz=None).date()).all()
                    for cd in classData:
                        countData.append(cd.student_MSSV)
                    countData = list(set(countData))
                    count = len(countData)
                    countData = []
                    a = list((classData,count,a_class))
                    rollcallData.append(a)
                return render_template('TeacherProfile.html', SH = SH, acc = acc, Teacher = tc, rollcalls = rollcallData)
            elif SH.accRight == "quản lý":
                return render_template('ManagerProfile.html', SH = SH, acc = acc)

        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')

@app.route('/studentPage', methods = ['POST','GET'])
def studentPage():
    if SH.isLogOn():
        if SH.permissionList["SEE::STUDENTPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        Students = Student.query.order_by(Student.MSSV).all()
        return render_template('student.html', Students = Students, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')

@app.route('/rollcall', methods = ['POST','GET'])
def rollcall():
    if SH.isLogOn():
        if SH.permissionList["SEE::MAINPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        RollCalls = RollCall.query.order_by(RollCall.date_create).all()
        return render_template('rollcallList.html', RollCalls = RollCalls, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login',)
    
@app.route('/teacherPage', methods = ['POST','GET'])
def teacherPage():
    if SH.isLogOn():
        if SH.permissionList["SEE::TEACHERPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        Teachers = Teacher.query.order_by(Teacher.ID).all()
        return render_template('teacherPage.html', Teachers = Teachers, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')


@app.route('/classPage', methods = ['POST','GET'])
def classPage():
    if SH.isLogOn():
        if SH.permissionList["SEE::CLASSPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        ClassRoms = ClassRom.query.order_by(ClassRom.name).all()
        return render_template('ClassRoom.html', ClassRoms = ClassRoms, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')
    
@app.route('/fingerPrintPage', methods = ['POST','GET'])
def fingerPrintPage():
    if SH.isLogOn():
        if SH.permissionList["SEE::FINGERPRINTPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        FingerPrints = FingerPrint.query.order_by(FingerPrint.ID).all()
        return render_template('fingerPrint.html', FingerPrints = FingerPrints, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')

@app.route('/newClass', methods = ['POST','GET'])
def newClass():
    if SH.isLogOn():
        if SH.permissionList["CREATE::CLASS"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        form = create_class_form()
        if form.validate_on_submit():
            link_tc = Teacher.query.filter_by(ID = form.teacher.data).first_or_404()
            new_cl = ClassRom(name = form.name.data, department = form.department.data, teacher = link_tc, number = 0)
            db.session.add(new_cl)
            db.session.commit()
            return redirect('/classPage')
        return render_template('CreateClass.html', form = form, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')
    
def updateClassCount(name):
    count = ClassRom.query.get_or_404(name)
    num = Student.query.filter_by(classId = name).count()
    count.number = num
    db.session.commit()

@app.route('/newStudent', methods = ['POST','GET'])
def newStudent():
    if SH.isLogOn():
        if SH.permissionList["CREATE::STUDENT"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        form = create_student_form()
        if form.validate_on_submit():
            acc_link = Accout.query.filter_by(name = form.acclinking.data).first_or_404()
            finger_link = FingerPrint.query.filter_by(ID = form.FingerId.data).first_or_404()
            class_link = ClassRom.query.filter_by(name = form.className.data).first_or_404()
            new_stu = Student(MSSV = form.MSSV.data, name = form.name.data, birthDay = form.birthDay.data, accout = acc_link, fingerPrint = finger_link, classrom = class_link)
            db.session.add(new_stu)
            db.session.commit()
            updateClassCount(str(form.className.data))
            return redirect('/studentPage')
            
        return render_template('CreateStudent.html', form = form, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')


@app.route('/newTeacher', methods = ['POST','GET'])
def newTeacher():
    if SH.isLogOn():
        if SH.permissionList["CREATE::TEACHER"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        form = create_teacher_form()
        if form.validate_on_submit():
            acc_link = Accout.query.filter_by(name = form.acclinking.data).first_or_404()
            new_tc = Teacher(ID = form.ID.data, name = form.name.data, accout = acc_link)
            db.session.add(new_tc)
            db.session.commit()
            return redirect('/teacherPage')
            
        return render_template('newTeacher.html', form = form, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')


@app.route('/accManager', methods = ['POST','GET'])
def accList():
    if SH.isLogOn():
        if SH.permissionList["SEE::MAINPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        Accouts = Accout.query.order_by(Accout.name).all()
        return render_template('accManager.html', Accouts = Accouts, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')
    
#-----------------------------------function row area----------------------------------------------------------------------------------------

@app.route('/logout')
def logout():
    SH.logout()
    return redirect('/')

@app.route('/deleteSTU/<string:what>/<string:MSSV>')
def deleteSTU(MSSV,what):
    if SH.isLogOn():
        if SH.permissionList["SEE::MAINPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        if what == "student":
            class_to_delete = Student.query.get_or_404(MSSV)
            db.session.delete(class_to_delete)
            db.session.commit()
            updateClassCount(ClassRom.query.filter_by(name = class_to_delete.classId).first_or_404().name)
            return redirect('/studentPage')
        elif what == "teacher":
            class_to_delete = Teacher.query.get_or_404(MSSV)
            db.session.delete(class_to_delete)
            db.session.commit()
            return redirect('/teacherPage')
        elif what == "class":
            class_to_delete = ClassRom.query.get_or_404(MSSV)
            db.session.delete(class_to_delete)
            db.session.commit()
            return redirect('/classPage')
        elif what == "finger":
            class_to_delete = FingerPrint.query.get_or_404(MSSV)
            db.session.delete(class_to_delete)
            db.session.commit()
            return redirect('/fingerPrintPage')
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')
    
@app.route('/updateSTU/<string:what>/<string:MSSV>', methods = ['POST','GET'])
def updateSTU(MSSV,what):
    if SH.isLogOn():
        if SH.permissionList["SEE::MAINPAGE"] == False:
            return redirect('/NO PERMISSON')
        #-------------------------------------------------------------------------------------
        if what == "student":
            class_to_update = Student.query.get_or_404(MSSV)
            form = create_student_form()
            if request.method == 'POST':
                class_to_update.MSSV = form.MSSV.data
                class_to_update.name = form.name.data
                class_to_update.fingerPrintId = form.FingerId.data
                class_to_update.classId = form.className.data
                class_to_update.birthDay = form.birthDay.data
                class_to_update.Accout_name = form.acclinking.data
                try:
                    db.session.commit()
                    return redirect('/studentPage')
                except:
                    return 'something stopping us to do this action'
            else:
                return render_template('updateSTU.html', class_to_update = class_to_update, form = form, SH = SH)
        elif what == "teacher":
            class_to_update = Teacher.query.get_or_404(MSSV)
            form = create_teacher_form()
            if request.method == 'POST':
                class_to_update.ID = form.ID.data
                class_to_update.name = form.name.data
                class_to_update.Accout_name = form.acclinking.data
                try:
                    db.session.commit()
                    return redirect('/teacherPage')
                except:
                    return 'something stopping us to do this action'
            else:
                return render_template('updateTeacher.html', class_to_update = class_to_update, form = form, SH = SH)
        elif what == "class":
            class_to_update = ClassRom.query.get_or_404(MSSV)
            form = create_class_form()
            if request.method == 'POST':
                class_to_update.name = form.name.data
                class_to_update.department = form.department.data
                class_to_update.Teacher = form.teacher.data
                try:
                    db.session.commit()
                    return redirect('/classPage')
                except:
                    return 'something stopping us to do this action'
            else:
                return render_template('updateClass.html', class_to_update = class_to_update, form = form, SH = SH)
        #----------------------------------------------------------------------------------------
    else:
        return redirect('/login')
    
#-------------------------------------------MAIN RUN -------------------------------------------

if __name__ == "__main__":
    app.run(debug = True)#, host = '172.20.10.9', port  = 5000) 
# host = '0.0.0.0', port = '5000'
