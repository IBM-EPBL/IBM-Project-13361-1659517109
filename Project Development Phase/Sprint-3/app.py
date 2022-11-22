from flask import Flask, redirect, url_for, request, render_template, session, flash
import ibm_db
from datetime import date
import re
from sendgrid_integration import *

today = date.today()

conn = ibm_db.connect("insert_your_DB_configurations",'','')

app = Flask(__name__)
app.secret_key = '20z435'

name = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/registration_page',methods=['GET','POST'])
def register():
    msg = ''
    nme = ''
    usr = ''
    pwd = ''
    conpwd = ''
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['email']
        username = request.form['user']
        pwd = request.form['pass']
        conpwd = request.form['conpass']
        mobile = request.form['mobile']
        sql = "SELECT * FROM USERS WHERE EMAIL=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,mail)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print('success1')
        if account:
            msg = "Account already exists with the Email address"
            print('success2')
            return render_template('registration.html',msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', mail):
            msg='Please enter a valid email address'
            return render_template('registration.html',msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg='name must contain only character and number'
            return render_template('registration.html',msg=msg)
        else:
            sql = "INSERT INTO USERS VALUES (?,?,?,?,?)"
            stmt1 = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt1,1,name)
            ibm_db.bind_param(stmt1,2,mail)
            ibm_db.bind_param(stmt1,3,username)
            ibm_db.bind_param(stmt1,4,pwd)
            ibm_db.bind_param(stmt1,5,mobile)
            ibm_db.execute(stmt1)
            msg='You have successfully registered click signin!!'
            print('success')
            return redirect(url_for('login'))
        print('success3')
        msg="fill out the form first!"
        return render_template('registration.html',msg=msg)
    return render_template('registration.html')
    
@app.route('/login_page')
def login():
    return render_template('login.html')

@app.route('/validate',methods=['GET','POST'])
def validate():
    global userid, name
    msg = ''
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['pass']
        
        sql = 'SELECT * FROM USERS WHERE USERNAME=? AND PASSWORD=?'
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['logged_in'] = True
            session['id'] = account['USERNAME']
            userid = account['USERNAME']
            name = account['NAME']
            session['username'] = account['USERNAME']
            msg = "Login Successfull!!"
            return redirect(url_for('dashboard',name=name))
        else:
            msg = "Incorrect password/username"
            return render_template('login.html',msg=msg)

@app.route('/dashboard')
def dashboard():
    sql = 'SELECT * FROM PRODUCT'
    stmt = ibm_db.prepare(conn, sql)
    result = ibm_db.execute(stmt)
    print(result)
    products = []
    row = ibm_db.fetch_assoc(stmt)
    print(row)
    i = 0
    while(i < 5):
        products.append(row)
        row = ibm_db.fetch_assoc(stmt)
        print(row)
        i+=1
    products=tuple(products)
    print(products)
    if row:
        return render_template("dashboard.html",user_name=name,products=products)
    else:
        return render_template("dashboard.html",user_name=name,products=False)


@app.route('/view_inventory')
def view_inventory():
    sql = 'SELECT * FROM PRODUCT'
    stmt = ibm_db.prepare(conn, sql)
    result = ibm_db.execute(stmt)
    print(result)
    products = []
    row = ibm_db.fetch_assoc(stmt)
    print(row)
    while(row):
        products.append(row)
        row = ibm_db.fetch_assoc(stmt)
        print(row)
    products=tuple(products)
    print(products)

    if result>0:
        return render_template('view_inventory.html', products = products,user_name=name)
    else:
        return render_template('view_inventory.html',user_name=name)

@app.route('/add_items', methods=['POST','GET'])
def add_items():
    msg = ''
    if request.method == 'POST':
        pid = request.form['pid']
        pname = request.form['pname']
        qty = request.form['qty']
        pname = pname.upper()
        qty = int(qty)
        dat = str(today.strftime("%d/%m/%Y"))
        sql = 'SELECT * FROM PRODUCT WHERE PID=? or PNAME=?'
        stmt1 = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt1,1,pid)
        ibm_db.bind_param(stmt1,2,pname)
        ibm_db.execute(stmt1)
        account = ibm_db.fetch_assoc(stmt1)
        if account:
            flash('Product already exists!!')
            msg = 'Check your Product ID/Product Name'
        else:
            sql = "INSERT INTO PRODUCT VALUES (?,?,?,?)"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,pid)
            ibm_db.bind_param(stmt,2,pname)
            ibm_db.bind_param(stmt,3,qty)
            ibm_db.bind_param(stmt,4,dat)   
            ibm_db.execute(stmt)
            flash('Product updated succesfully!','info')
            msg='Product added successfully'
        return render_template('add_stock.html',user_name=name,msg = msg)
    return render_template('add_stock.html',user_name=name,msg = msg)

@app.route('/update_item',methods=['GET','POST'])
def update_item():
    sql = 'SELECT * FROM PRODUCT'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    result = ibm_db.fetch_assoc(stmt)
    products = []
    row = ibm_db.fetch_assoc(stmt)
    print(row)
    while(row):
        products.append(row)
        row = ibm_db.fetch_assoc(stmt)
        print(row)
    products=tuple(products)
    print(products)
    return render_template('update_item.html',products=products,user_name=name)
        

@app.route('/update_item_1',methods=['GET','POST'])
def update_item_1():
    sql = 'SELECT * FROM PRODUCT'
    stmtret = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmtret)
    result = ibm_db.fetch_assoc(stmtret)
    products = []
    row = ibm_db.fetch_assoc(stmtret)
    print(row)
    while(row):
        products.append(row)
        row = ibm_db.fetch_assoc(stmtret)
        print(row)
    products=tuple(products)
    pid = request.form['pid']
    qty = request.form['qty']
    pname = request.form['pname']
    if request.method == 'POST':
        if request.form['action'] == 'ADD':
            sql = "SELECT STOCK FROM PRODUCT WHERE PID = ?"
            stmt1 = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt1,1,pid)
            ibm_db.execute(stmt1)
            result1 = ibm_db.fetch_assoc(stmt1)
            qty = result1['STOCK'] + int(qty)
            sql = "UPDATE PRODUCT SET STOCK = ? WHERE PID = ?"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,qty)
            ibm_db.bind_param(stmt,2,pid)
            result = ibm_db.execute(stmt)
            if result:
                msg = 'Value updated successfully!!'
                return render_template('update_item.html',products=product,msg = msg,user_name=name)
            else:
                msg = 'Updation Failed!'
                return render_template('update_item.html',products=products,msg = msg,user_name=name)
        elif request.form['action'] == 'DELETE':
            sql = "SELECT STOCK FROM PRODUCT WHERE PID = ?"
            stmt1 = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt1,1,pid)
            ibm_db.execute(stmt1)
            result1 = ibm_db.fetch_assoc(stmt1)
            if result1['STOCK'] < int(qty):
                msg = 'No stock available!'
                return render_template('update_item.html',products=products,msg = msg,user_name=name)
            else:
                sql = "UPDATE PRODUCT SET STOCK = ? WHERE PID = ?"
                qty = result1['STOCK'] - int(qty)
                stmt = ibm_db.prepare(conn,sql)
                ibm_db.bind_param(stmt,1,qty)
                ibm_db.bind_param(stmt,2,pid)
                result = ibm_db.execute(stmt)
                if result:
                    msg = 'Value updated successfully!!'
                    if qty <= 5:
                        content = 'Low stock product details:\nProduct_ID: {0}\nProduct_Name: {1}\nStock: {2}\nKindly refill the stock!'.format(pid,pname,qty)
                        send_mail(content)
                    return render_template('update_item.html',products=products,msg = msg,user_name=name)
                else:
                    msg = 'Updation Failed!'
                    return render_template('update_item.html',products=products,msg = msg,user_name=name)
        elif request.form['action'] == 'UPDATE':
            sql = 'UPDATE PRODUCT SET STOCK = ? WHERE PID = ?'
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,qty)
            ibm_db.bind_param(stmt,2,pid)
            result = ibm_db.execute(stmt)
            if result:
                msg = 'Value updated successfully!!'
                return render_template('update_item.html',products=products,msg = msg,user_name=name)
            else:
                msg = 'Updation Failed!'
                return render_template('update_item.html',products=products,msg = msg,user_name=name)



@app.route('/go_ui1',methods=['GET','POST'])
def go_ui1():
    pid = request.form['pids']
    sql = 'SELECT * FROM PRODUCT WHERE PID = ?'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,pid)
    ibm_db.execute(stmt)
    result = ibm_db.execute(stmt)
    products = []
    row = ibm_db.fetch_assoc(stmt)
    products.append(row)
    product_id = products[0]['PID']
    product_name = products[0]['PNAME']
    stock = products[0]['STOCK']
    return render_template('update_item_1.html',user_name=name,product_id=product_id,product_name=product_name,stock=stock)

@app.route('/logout')
def logout():
    try:
        name.pop()
    except:
        pass
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')