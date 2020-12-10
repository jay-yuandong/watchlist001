#视图函数
from flask import render_template,redirect,request,flash,url_for
from flask_login import login_user,login_required,logout_user,current_user
from watchlist import app,db
from watchlist.models import User,Movie

#首页
@app.route('/',methods=['POST','GET'])
def index():
    if request.method=='POST':
        #判断当前用户是否授权
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        #已授权并且是post请求,获取请求中的信息
        title=request.form['title']
        year=request.form['year']
        #判断请求中的信息是否符合要求
        if not title or not year or  len(year)>4 or len(title)>60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        #将数据写入数据库
        movie=Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    #获取所有电影信息
    movies=Movie.query.all()
    return render_template('index.html',movies=movies)

#编辑按钮
@app.route('/movie/edit/<int:movie_id>',methods=['POST','GET'])
@login_required  #编辑需要先登录
def edit(movie_id):
    #如果movie_id查不到就跳到404
    movie=Movie.query.get_or_404(movie_id)
    if request.method=='POST':
        title=request.form['title']
        year=request.form['year']

        if not title or not year or len(year)>4 or len(title)>60:
            flash('Invalid input.')
            return redirect(url_for('edit',movie_id=movie_id))

        movie.title=title
        movie.year=year
        db.session.commit()
        flash('Item update.')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

#删除按钮
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required
def delete(movie_id):
    movie=Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

#设置用户信息按钮
@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    if request.method=='POST':
        name=request.form['name']
        if not name or len(name)>20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user=User.query.first()
        user.name=name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')

#登录按钮
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user=User.query.first()
        #验证用户名和密码
        if username==user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        #否则继续登录
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')

#退出
@app.route('/logout')
@login_required
def logout():
    logout_user()#登出
    flash('Goodbye.')
    return redirect(url_for('index'))



