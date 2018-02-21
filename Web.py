import os
from flask import Flask,render_template,request,redirect,url_for,session
import config
from models import User,Question,Answer
from exts import db
from decoretors import login_required


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    context = {
        'questions':Question.query.order_by('-create_time').all()
    }
    return render_template('index.html',**context)

@app.route('/question/',methods=['GET','POST'])
@login_required
def question():
    if request.method == 'GET':
        return  render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question=Question(title=title,content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id== user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        email= request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter(User.email == email,User.password==password).first()
        if user:
            session['user_id']=user.id
            session.permenent = True
            return redirect(request.args.get('next') or url_for('index'))
        else:
            return '账号或者手机号码错误，请重新输入'


@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html',question=question_model)

@app.route('/add_answer/',methods=["POST"])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')
    answer = Answer(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    question = Question.query.filter(Question.id==question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id=question_id))



@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method =='GET':
        return render_template('regist.html')
    else :
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user=User.query.filter(User.email==email).first()
        if user:
            return '该邮箱已经被注册，请登录'
        else:
            if password1 != password2:
                return "两次密码不一致，请重新输入"
            else:
                user=User(email=email,username=username,password=password2)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
