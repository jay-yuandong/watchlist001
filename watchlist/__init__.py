#创建程序实例
import os,sys
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy




win=sys.platform.startswith('win')
if win:  # 是windows就使用三个斜线
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app=Flask(__name__)
app.config['SECRET_KEY']='dev'
app.config['SQLALCHEMY_DATABASE_URI']=prefix+os.path.join(os.path.dirname(app.root_path),'data.db')
app.config['SQLALCHEMY_TRACK_MODIFCATIONS']=False

db=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id): #创建用户加载回调函数
    from watchlist.models import User
    user=User.query.get(int(user_id))
    return user

#上下文处理器，返回的字典key值作为变量所有模板可见
@app.context_processor
def inject_user():
    from watchlist.models import User
    user=User.query.first()
    return dict(user=user)

from watchlist import views,errors,commands