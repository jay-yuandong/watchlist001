from flask import Flask,escape,url_for
app=Flask(__name__)
#装饰器为这个函数绑定url，访问时触发这个函数的返回值
@app.route('/')
def hello():
    return 'hello'

@app.route('/user/<name>')
def user_page(name):
    return 'user: %s' % escape(name)

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page',name='grey'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))
    return 'test page'