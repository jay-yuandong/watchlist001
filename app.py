from flask import Flask,render_template,request,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
import os,sys,click
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)
#判断当前操作系统
win=sys.platform.startswith('win')
if win: #是windows就使用三个斜线
    prefix='sqlite:///'
else:
    prefix='sqlite:////'
#配置数据库的地址
app.config['SQLALCHEMY_DATABASE_URI']=prefix+os.path.join(app.root_path,'data.db')
#关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#装饰器为这个函数绑定url，访问时触发这个函数的返回值
app.config['SECRET_KEY']='dev'

#初始化扩展，传入程序实例app
db=SQLAlchemy(app)
login_manage=LoginManager(app)
login_manage.login_view='login'



#创建user表
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))
    username=db.Column(db.String(20))
    password_hash=db.Column(db.String(128))
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)
# 创建movie表
class Movie(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(60))
    year=db.Column(db.String(4))


@login_manage.user_loader
def load_user(user_id): #创建用户加载回调函数
    user = User.query.get(int(user_id))
    return user

#添加数据命令
@app.cli.command()
def forge():
    """Generate fake data. """
    db.create_all()
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user=User(name=name)
    db.session.add(user)
    for m in movies:
        movie=Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('done.')

#用于修改表结构后的命令
@app.cli.command()
@click.option("--drop",is_flag=True,help='create after drop.')
def initdb(drop):
    """Initialize the datebase"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized datebase.')

@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login.')
@click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True,help='The password used to login.')
def admin(username,password):
    """create user"""
    db.create_all()
    user=User.query.first()
    if user is not None:
        click.echo('Updating user')
        user.username=username
        user.set_password(password)
    else:
        click.echo('Creating user')
        user=User(username=username)
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')

#上下文处理函数
@app.context_processor
def inject_user():
    user=User.query.first()
    print(user)
    return dict(user=user)

@app.route('/',methods=['GET','POST'])
def index():
    #创建电影
    if request.method=='POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        #获取前端输入的信息
        title=request.form.get('title')
        year=request.form.get('year')
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input') #flash一个错误提示
            return redirect(url_for('index')) #返回重定向的index页
        movie=Movie(title=title,year=year) #创建提交的信息
        db.session.add(movie)
        db.session.commit()
        flash('Item created')
        return redirect(url_for('index'))
    movies=Movie.query.all()
    print(movies)
    return render_template('index.html',movies=movies)

#注册一个错误处理函数,404错误会触发
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

#编辑电影
@app.route('/moive/edit/<int:movie_id>',methods=['GET','POST'])
@login_required
def edit(movie_id):
    #没有找到，则返回 404 错误响应
    movie=Movie.query.get_or_404(movie_id)
    if request.method=='POST':
        title=request.form['title']
        year=request.form['year']
        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input')
            return redirect(url_for('edit',movie_id=movie_id))
        movie.title=title
        movie.year=year
        db.session.commit()
        flash('Item update')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

#删除电影
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required
def delete(movie_id):
    movie=Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

#用户登录
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user=User.query.first()
        if username==user.username and user.validate_password(password):
            login_user(user)#登录用户
            flash('Login success')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')

#登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

#用户改名字
@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    if request.method=='POST':
        name=request.form['name']
        if not name or len(name)>20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        #current_user 返回当前登录用户的数据库记录对象,然后修改name值
        current_user.name=name
        db.session.commit()
        flash('Settings update')
        return redirect(url_for('index'))
    return render_template('settings.html')

