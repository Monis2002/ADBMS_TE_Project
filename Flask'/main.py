from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/monis"
mongo = PyMongo(app)

# Login Page
@app.route('/',methods=["POST","GET"])
def login():
    #mongo.db.stock.insert_one({"name":"cilacar",'qty':4})
    return render_template('login.html')

@app.route('/login_check',methods=['POST','GET'])
def login_check():
    if request.method=="POST":
        username=request.form.get('username')
        password=int(request.form.get('password'))
        data=mongo.db.login.find({},{'_id':0})
        r='fail'

        for d in data:
            if (d['username']==username and d['password']==password) :
                r='index'
        return redirect(url_for(r))

@app.route('/fail')
def fail():
    return "<h1>Please check your username or email</h1>"

@app.route('/index')
def index():
    # Insert data to database
    #mongo.db.login.insert_one({'username':'monis','password':123})

    return render_template('index.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        medicine_names = request.form.getlist('medicine_name[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')

        data = []
        amount=[int(i)*int(j) for i,j in zip(quantities,prices)]
        total=sum(amount)

        name_of_medicine=''
        message='result'
        for name, quantity, price in zip(medicine_names, quantities, prices):
            stock_data=list(mongo.db.stock.find({'name':name}))
            if len(stock_data)>0:
                for i in stock_data:
                    if i['qty']<int(quantity):
                        message='not_availabel'
                        name_of_medicine=name
                        break
                mongo.db.monis.insert_one({"Name": name, 'quantity': int(quantity), 'price': float(price),'total':float(total)})
                data.append({'name': name, 'quantity': int(quantity), 'price': float(price)})
            else:
                message='not_availabel'
                name_of_medicine=name

        if message=="result":
            # This loop is to update stock after billing process
            for name, quantity, price in zip(medicine_names, quantities, prices):
                stock_data = mongo.db.stock.find({'name': name})
                for i in stock_data:
                    mongo.db.stock.update_one({'name':name},{'$set':{'qty':i['qty']-int(quantity)}})
            # To delete data which quantity is zero
            for name, quantity, price in zip(medicine_names, quantities, prices):
                stock_data = mongo.db.stock.find({'name': name})
                for i in stock_data:
                    if i['qty']==0:
                        mongo.db.stock.delete_one({'qty':0})
            return render_template('result.html', data=data,total=total)
        else:
            return  name_of_medicine+" Medicine is not available"


if __name__ == '__main__':
    app.run(debug=True)
    submit()

