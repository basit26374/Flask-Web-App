from flask import Flask, render_template, request,send_file, Response
from flask_mail import Mail, Message
import sqlite3 as sql
import os
import threading
import cv2
from main import GUI
import time
import datetime
import numpy as np
from skimage import measure
from new import VideoCamera

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kmuhammadannas@gmail.com'
app.config['MAIL_PASSWORD'] = 'therko5991!@#)(*'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_ASCII_ATTACHMENTS'] = True
mail = Mail(app)

def img_fill(im_in, n):  # n = binary image threshold
    th, im_th = cv2.threshold(im_in, n, 255, cv2.THRESH_BINARY);

    # Copy the thresholded image.
    im_floodfill = im_th.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = im_th.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0, 0), 255);

    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Combine the two images to get the foreground.
    fill_image = im_th | im_floodfill_inv

    return fill_image

def imclearborder(imgBW, radius):

    # Given a black and white image, first find all of its contours
    imgBWcopy = imgBW.copy()
    _,contours,hierarchy = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST, 
        cv2.CHAIN_APPROX_SIMPLE)

    # Get dimensions of image
    imgRows = imgBW.shape[0]
    imgCols = imgBW.shape[1]    

    contourList = [] # ID list of contours that touch the border

    # For each contour...
    for idx in np.arange(len(contours)):
        # Get the i'th contour
        cnt = contours[idx]

        # Look at each point in the contour
        for pt in cnt:
            rowCnt = pt[0][1]
            colCnt = pt[0][0]

            # If this is within the radius of the border
            # this contour goes bye bye!
            check1 = (rowCnt >= 0 and rowCnt < radius) or (rowCnt >= imgRows-1-radius and rowCnt < imgRows)
            check2 = (colCnt >= 0 and colCnt < radius) or (colCnt >= imgCols-1-radius and colCnt < imgCols)

            if check1 or check2:
                contourList.append(idx)
                break

    for idx in contourList:
        cv2.drawContours(imgBWcopy, contours, idx, (0,0,0), -1)

    return imgBWcopy

def sort_lot(data):
    newlist = [0,0,0,0,0,0]
    num_data = len (data)
    
    for i in range(1,num_data):
        if data[i][0] > 10 and data[i][0] < 290:
            if data[i][1] < 200:
#                print('a')
                newlist[0] = 1
            else:
#                print('d')
                newlist[3] = 1
                
        elif data[i][0] > 300 and data[i][0] < 500:
            if data[i][1] < 200:
#                print('b')
                newlist[1] = 1
            else:
#                print('e')
                newlist[4] = 1
                
        elif data[i][0] > 500 and data[i][0] < 630:
            if data[i][1] < 200:
#                print('c')
                newlist[2] = 1
            else:
#                print('f')
                newlist[5] = 1
                
#        else:
#            print('nothing')
    return newlist

def Create_main():
    conn = sql.connect('main.sqlite')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS main (
        id integer PRIMARY KEY,
        day integer,
        lota integer,
        lotb integer,
        lotc integer,
        lotd integer,
        lote integer,
        lotf integer
        )""") 
    conn.commit()
    
def Create_user():
    co = sql.connect('user.sqlite')
    c = co.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS persons(
            id integer PRIMARY KEY,
            name text,
            address text,
            phone text,
            email text,
            cnic  text,
            charges integer
            )""")
    co.commit()
    
def insert_empty():      
    id_num = get_id()
    print("id_num" + str(id_num))
    if (id_num == 1):
        conn = sql.connect('main.sqlite')
        cur = conn.cursor()
        print("All slots are Empty")
        j = 1
        for i in range(30):
            # i starts iteration from 0 to 29
            #print(j)
            try:
                cur.execute("INSERT INTO main (id,day,lota,lotb,lotc,lotd,lote,lotf) VALUES(?,?,?,?,?,?,?,?)",(i+1, i+1, 0, 0, 0, 0, 0, 0))
                j = j +1
                #print(cur.lastrowid,j)
            except:
                print("Already Empty Main Table Exist")
                break
                    
                
        conn.commit()

def get_id():
    with sql.connect("user.sqlite") as con:
        cur = con.cursor()
        cursor = cur.execute("SELECT max(id) FROM persons")  # Search last/Maximum Id
        max_id = cursor.fetchone()[0]
        try:
            return int(max_id + 1)      # When restart after close the program
        except TypeError:
            return 1
        
def search_empty_lots(lots):    # Take list input in form of 0, 1, 2, 3, 4, 5 means lota, lotb, lotc, lotd, lote, lotf
    iteration = len(lots[0])    # lots[0] means only first row access, lots is a list datatype access by list[][]
    if 0 in lots[0]:            # This function is only work in asinglr list means only one day data or single row
        lis = []
        for  i in range(iteration):
            if lots[0][i] == 0:
                lis.append(i)   # create list of empty lots indexes
        return lis              # Return the index list of empty slots
    else:
        return print("No slots avilble in this date")
    
def conv_num2str(array):
    iteration = len(array)
    new_list = []
    for i in range(iteration):
        if array[i] == 0:
            new_list.append('lota')
        elif array[i] == 1:
            new_list.append('lotb')
        elif array[i] == 2:
            new_list.append('lotc')
        elif array[i] == 3:
            new_list.append('lotd')
        elif array[i] == 4:
            new_list.append('lote')
        elif array[i] == 5:
            new_list.append('lotf')
    return new_list

def search_Lots(date):
        #date = str(date)
#        cur.execute(" SELECT lota, lotb, lotc, lotd, lote, lotf FROM main WHERE day=?",[date])
    con = sql.connect("main.sqlite")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(" SELECT lota, lotb, lotc, lotd, lote, lotf FROM main WHERE (lota = 0 OR lotb = 0 OR lotc = 0 OR lotd = 0 OR lote = 0 OR lotf = 0) AND day=?", [date])
    all_lots = cur.fetchall()
    print(all_lots)
#        for row in all_lots:
#            print('{0}, {1}, {2}, {3}, {4}, {5}'.format(row[0], row[1], row[2], row[3],row[4],row[5]))
#        print(type(all_lots))
    if all_lots == []:
        print("if condition")
        return all_lots
    else:
        print("else condition")
#        empty = search_empty_lots(all_lots)
#        alpha = conv_num2str(empty)
        return all_lots

def Check_specific_lot(date,select):
    con = sql.connect("main.sqlite")
    cur = con.cursor()
    cur.execute("SELECT " +select+ " FROM main WHERE day = "+date+" ")
    all_rows = cur.fetchone()[0]
    return all_rows

def User_info():
    con = sql.connect("user.sqlite")
    cur = con.cursor()
#    print("User info function")
    cursor = cur.execute("SELECT max(id) FROM persons")
    max_id = cursor.fetchone()[0]
#    print(type(max_id))
#    print(max_id)
    identity = int(max_id)
    cur.execute("SELECT id, name, address, phone, email, cnic, charges FROM persons WHERE id = ? ",(identity,))
    all_rows = cur.fetchall()   
    return all_rows

def Update_user_lot(id,name,cnic,date,info):
    date = int(date)
    con = sql.connect("main.sqlite")
    cur = con.cursor()
    cur.execute("UPDATE main SET " +info+ " = ? WHERE day = ?",(id, date))
    cur.execute("SELECT id,day,lota,lotb,lotc,lotd,lote,lotf FROM main")
    all_lots = cur.fetchall()
    for row in all_lots:
         print('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(row[0], row[1], row[2], row[3],row[4],row[5],row[6],row[7]))
    con.commit()
    
def search_id(info_id):
    con = sql.connect("main.sqlite")
    cur = con.cursor()
    info_id = str(info_id)
    cur.execute(" SELECT day,lota, lotb, lotc, lotd, lote, lotf FROM main WHERE lota = "+info_id+" OR lotb = "+info_id+" OR lotc = "+info_id+" OR lotd = "+info_id+" OR lote = "+info_id+" OR lotf = "+info_id+"")
#        user1 = cur.fetchone()
#        print(user1[0])
    all_rows = cur.fetchall()
    print(all_rows)
    n_days = len(all_rows)
    day_list = []
    j = 1
    for i in all_rows:
        day_list.append(all_rows[j-1][0])
        j = j + 1
        
    cur.execute(" SELECT lota, lotb, lotc, lotd, lote, lotf FROM main WHERE lota = "+info_id+" OR lotb = "+info_id+" OR lotc = "+info_id+" OR lotd = "+info_id+" OR lote = "+info_id+" OR lotf = "+info_id+"")    
    all_rows = cur.fetchall()
    slot_list = []
    j = 1
    info_id = int(info_id)
    for i in all_rows:
        temp = all_rows[j-1].index(info_id)
        slot_list.append(temp)
        j = j + 1
    
    return n_days,day_list,slot_list

def Update_user_charges(id,rupee):
    con = sql.connect("user.sqlite")
    cur = con.cursor()
    cur.execute("UPDATE persons SET charges = ? WHERE id = ? ", (rupee,id))
    cur.execute("SELECT id,name, address, phone, email, cnic, charges FROM persons")
    all_rows = cur.fetchall()
    print(all_rows)
    print("*****************************")    
    con.commit()
    
def print_voucher(name,address,phone,email,cnic,charges,total_days,days,lots):
    
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    charges = str(charges)
    total_days = str(total_days)
    days = str(days)
    #days = ' '.join(days)
    lots = ' '.join(lots)
    
    pdf_name = ""+name+"_"+cnic+".pdf"
    
    save_name = os.path.join(os.path.expanduser("~"), "C:/Users/User/Desktop/Easy Park Final/templates/", pdf_name)
    
    canvas = canvas.Canvas(save_name, pagesize=letter)
    canvas.setLineWidth(.3)
    canvas.setFont('Helvetica', 12)
    
#    name = "Abdul Basit"
#    address = 'Krachi'
#    phone = '0311'
#    email = 'basit@mail.com'
#    cnic = '42201'
#    charges = 100
#    total_days = 5
    
    #canvas.setTitle("SZABIST UNIVERSITY")
    canvas.drawString(250, 750, "SZABIST UNIVERSITY")
    canvas.drawString(260, 730, "Car Parking Chalan")
    canvas.drawString(260, 650, "USER INFORMATION")
    
    canvas.drawString(50, 600,"User Name")
    canvas.drawString(50, 560,"Address")
    canvas.drawString(50, 520,"Phone Number")
    canvas.drawString(50, 480,"Email")
    canvas.drawString(50, 440,"CNIC")
    
    canvas.drawString(200, 600, ":")
    canvas.drawString(200, 560, ":")
    canvas.drawString(200, 520, ":")
    canvas.drawString(200, 480, ":")
    canvas.drawString(200, 440, ":")
    
    canvas.drawString(250, 600, name)
    canvas.drawString(250, 560, address)
    canvas.drawString(250, 520, phone)
    canvas.drawString(250, 480, email)
    canvas.drawString(250, 440, cnic)
    
    canvas.line(0,400,700,400)
    
    canvas.drawString(50, 360, "Total Number of Days")
    canvas.drawString(200, 360, ":")
    canvas.drawString(250, 360, total_days)
    canvas.drawString(50, 320, "Booking Dates")
    canvas.drawString(200, 320, ":")
    canvas.drawString(250, 320, days)
    canvas.drawString(50, 280, "Booking Slots on Dates")
    canvas.drawString(200, 280, ":")
    canvas.drawString(250, 280, lots)
    canvas.drawString(50, 240, "Total Charges")
    canvas.drawString(200, 240, ":")
    canvas.drawString(250, 240, charges)
    
    canvas.line(50,150,200,150)
    canvas.drawString(50, 130, "User Signature")
    canvas.line(425,150,575,150)
    canvas.drawString(425, 130, "Incharge Signature")
    
    canvas.save()

@app.route('/',methods=['POST', 'GET'])
def home():
    return render_template('home.html')


@app.route('/enternew')
def new_student():
    return render_template('student.html')

@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            name = request.form['name']
            address = request.form['address']
            phone = request.form['phone']
            email = request.form['email']
            cnic = request.form['cnic']
           
            print("NAME :" + " " + name)
            print(" ")


            if name == "":
                name = "null"
            if address == "":
                address = "null"
            if phone == "":
                phone = "null"
            if email == "":
                email = "null"
            if cnic  == "":
                cnic = "null"   

            with sql.connect("user.sqlite") as con:
                cur = con.cursor()
              #   c = conn.cursor()
#                conn = sql.connect("user.sqlite")
#                cur  = conn.cursor()
                iden = get_id()
                cur.execute("INSERT INTO persons (id,name,address,phone,email,cnic) VALUES(?, ?, ?, ?, ?, ?)",(iden, name, address, phone , email, cnic ) )

                con.commit()
#                conn.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("daterec.html", msg=msg)
            con.close()

#C:/Users/spectrum/Desktop/flask-sqlite3-crud-example/main.sqlite     
@app.route('/date',methods=['POST', 'GET'])
def check():
    if request.method == 'POST':
        try:
            date = request.form['date']
            print("Date :" + " " + date)
            print(" ")


            if date == "":
                date = "1" 
                
            date = int(date)
            lis_empty_lots = search_Lots(date)
            
            if len(lis_empty_lots) == 0:
                print("No lots Available at date "+ str(date))
                msg = "No lots Available at date "+ str(date)
                return render_template("error.html",msg=msg)
            else:
                return render_template("daterec.html", rows=lis_empty_lots)
            

        except:
            msg = "Error in lots checking "
            print("Error in lots checking ")
            return render_template("error.html",msg=msg)

#        finally:
#            print("Received")
#            return render_template("daterec.html", rows=lis_empty_lots)
            
    
@app.route('/booked',methods=['POST', 'GET'])
def booked():
    if request.method == 'POST':
        try:
            date = request.form['date']
            lot_name = request.form['lot_name']
            print("Date :" + " " + date)
            print(" ")
            print("Lot name :" + " " + lot_name)
            print(" ")


            if date == "" or lot_name == "":
                print("Date or lot fiels is Empty")
                
            else:
                check = Check_specific_lot(date,lot_name)
                print(check)
                
                if check > 0:
                    print(lot_name +" is Already Booked")
                    msg = lot_name +" is Already Booked"
                    return render_template("error.html",msg=msg)
                else:
                    info = User_info()
#                    print(info)
#                    date = int(date)
                    Update_user_lot(info[0][0],info[0][1],info[0][5],date,lot_name)
                    print( "Dear Customer ! Your Booking is Successfuly Done")
                    return render_template("daterec.html")
#                if check[0][0] > 0:
#                    print( "Dear Customer", "This lot is already Booked")
#                else:
#                    info = User_info()
#                    print(info)
#                    date = int(date)
#                    Update_user_lot(info[0][0],info[0][1],info[0][5],date,lot_name)
#                    print( "Dear Customer", "Your Booking is Successfuly Done")


        except:
            msg = "Booking is not done successfully"
            print("Booking is not done successfully")
            return render_template("error.html",msg=msg)
#        finally:
#            print("Please book new slots or Pay the Challan")
#            return render_template("daterec.html",msg=msg)


@app.route('/list_main')
def list_main():
    con = sql.connect("main.sqlite")
    con.row_factory = sql.Row
    print(con.row_factory)
    cur = con.cursor()
    cur.execute("SELECT id,day,lota,lotb,lotc,lotd,lote,lotf FROM main")

    rows = cur.fetchall();
    return render_template("days.html", rows=rows)

@app.route('/list_user')
def list_user():
    con = sql.connect("user.sqlite")
    con.row_factory = sql.Row
    print(con.row_factory)
    cur = con.cursor()
    cur.execute("SELECT id,name, address, phone, email, cnic, charges FROM persons")

    rows = cur.fetchall();
    return render_template("list.html", rows=rows)

@app.route('/pay',methods=['POST', 'GET'])
def pay():
    
    try:
        print("in try  scope")
        charge_per_day = 50
        info = User_info()
        temp = search_id(info[0][0])
        charges = charge_per_day * temp[0]
        Update_user_charges(info[0][0], charges)
        slots = conv_num2str(temp[2])
        charges = charge_per_day * temp[0]
        print_voucher(info[0][1], info[0][2], info[0][3], info[0][4], info[0][5], charges, temp[0], temp[1], slots)
        msg = "Your Challan is ready to download and send on your email address as well"
#        file_name = str(info[0][1]) + "_" +str(info[0][5]) + ".pdf"
        file_name = str(info[0][1]) + "_" +str(info[0][5])
        print(file_name)
        mesg = Message('Easy Park', sender = 'kmuhammadannas@gmail.com', recipients = ['kmuhammadannas@gmail.com'])
        mesg.body = "Congratulations !!! Your Challan is ready for print."
        with app.open_resource("C:/Users/User/Desktop/Easy Park Final/templates/"+file_name+".pdf") as fp:
            mesg.attach(""+file_name+".pdf", ""+file_name+"/pdf", fp.read())
            
        with app.app_context():
            mail.send(mesg)
        
        return render_template("congrats.html", msg=msg,file_name=file_name)
    except:
        print("Have some error")

@app.route('/return-files/',methods=['POST', 'GET'])
def return_files_tut():	 
    try:
        print("file file")
        info = User_info()
        file_name = str(info[0][1]) + "_" +str(info[0][5]) + ".pdf"
        print(file_name)
#        file_name=abc
       # return send_file('C:/Users/spectrum/Desktop/flask-sqlite3-crud-example/templates/'+file_name , attachment_filename=file_name)
       # return send_file(file_name, attachment_filename=file_name)
       # save_name = os.path.join(os.path.expanduser("~"), "C:/Users/spectrum/Desktop/flask-sqlite3-crud-example/templates/",file_name)
    
        #return send_file(directory=save_name, attachment_filename=file_name)
        return send_file(os.path.join("C:/Users/User/Desktop/Easy Park Final/templates/"+file_name+""), as_attachment=True)
        print(" file")
    except:
    	print("no file")
        
@app.route('/admin')
def admin():
    con = sql.connect('admin.sqlite')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS admin(
            id integer PRIMARY KEY,
            user text,
            password text
            )""")
    user = "admin"
    password = "admin"
    try:
#        cur.execute("SELECT * FROM member WHERE username = 'a' AND password = 'a'")
#        cur.execute("SELECT mem_id,username, password FROM member")
        cur.execute("SELECT WHERE user = "+user+" AND password = "+password+" FROM admin")
        print(cur.fetchone())
        print("admin try")
    
#    if cur.fetchone() is None:
    except:
        cur.execute("INSERT INTO admin (user, password) VALUES(?,?)", (user,password))
        cur.execute("SELECT id,user, password FROM admin")
        print(cur.fetchall())
        print("admin except")
#    cursor.execute("SELECT * FROM `member` WHERE `username` = 'a' AND `password` = 'a'")
#    if cur.fetchone() is None:
#        cur.execute("INSERT INTO `member` (username, password) VALUES('a', 'a')")

    return render_template('admin.html')

@app.route('/log',methods=['POST', 'GET'])
def log():
    if request.method == 'POST':
#        try:
        name = request.form['name']
        password = request.form['password']
        
        print(type(name))
        print(type(password))
        
        print("Name : " + name)
        print("Password : " + password)
        
        if name == "admin" and password == "admin":
            msg = "Correct"
            return render_template('page.html')
        else:
            msg = "Wrong"
            return render_template('error.html', msg=msg)
        
@app.route('/User_info_by_id',methods=['POST', 'GET'])
def User_info_by_id():
    if request.method == 'POST':
        
        con = sql.connect('user.sqlite')
        con.row_factory = sql.Row
        cur = con.cursor()
        identity = int(request.form['id'])
        cur.execute("SELECT id, name, address, phone, email, cnic, charges FROM persons WHERE id = ? ",(identity,))
        rows = cur.fetchall() 
        return render_template("page.html", rows=rows)
    
@app.route('/User_info_by_name_cnic',methods=['POST', 'GET'])
def User_info_by_name_cnic():
    if request.method == 'POST':
        
        con = sql.connect('user.sqlite')
        con.row_factory = sql.Row
        cur = con.cursor()
        name = request.form['name']
        cnic = int(request.form['cnic'])
        cur.execute("SELECT id, name, address, phone, email, cnic, charges FROM persons WHERE name = ? AND cnic = ? ",(name,cnic))
        all_rows = cur.fetchall()
        return render_template("page.html", rows=all_rows)
    
    
@app.route('/delete_all')
def delete_all():

   con = sql.connect('main.sqlite')
   cur = con.cursor()
   cur.execute("DROP TABLE main")
   
   con = sql.connect('user.sqlite')
   cur = con.cursor()
   cur.execute("DROP TABLE persons")
   
   Create_user()
   Create_main()
   insert_empty()
   return render_template("page.html")
    

@app.route('/stream')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def Day_info(day):
    con = sql.connect('main.sqlite')
    cur = con.cursor()
    day = str(day)
    cur.execute("SELECT lota,lotb,lotc,lotd,lote,lotf FROM main WHERE day = "+day+"")
    all_rows = cur.fetchall()
    return all_rows

def process_image(img):
#    global img, data
    pos = [[110, 30, 120+110, 150+30], [310, 30, 140+310, 150+30], [520, 30, 90+520, 150+30], [110, 250, 120+110, 150+250], [310, 250, 140+310, 150+250], [520, 250, 90+520, 150+250]]
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    thresh =   255 - thresh
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
    sure_bg = cv2.dilate(thresh,kernel,iterations=4)
    check = sure_bg
    sure_bg = imclearborder(sure_bg,1)
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
    
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    
    fill = img_fill(sure_bg,0)
    labels = measure.label(fill, neighbors=8, background=0)
    mask = np.zeros(fill.shape, dtype="uint8")
        # loop over the unique components
    for label in np.unique(labels):
    	# if this is the background label, ignore it
    	if label == 0:
    		continue
     
    	# otherwise, construct the label mask and count the
    	# number of pixels 
    	labelMask = np.zeros(fill.shape, dtype="uint8")
    	labelMask[labels == label] = 255
    	numPixels = cv2.countNonZero(labelMask)
     
    	# if the number of pixels in the component is sufficiently
    	# large, then add it to our mask of "large blobs"
    	if numPixels > 600 and numPixels < 70000:
    		mask = cv2.add(mask, labelMask)
            
    connectivity = 8  
    output = cv2.connectedComponentsWithStats(mask, connectivity, cv2.CV_32S)
    
    num_labels = output[0]
    stats = output[2]
    car_pos = sort_lot(stats)
#    print(sort_lot(stats))
#    print(stats)
    i = 0
#    for label in range(1,num_labels):
#        blob_area = stats[label, cv2.CC_STAT_AREA]
#        blob_width = stats[label, cv2.CC_STAT_WIDTH]
#        blob_height = stats[label, cv2.CC_STAT_HEIGHT]
#        img = cv2.rectangle(img, (stats[i][0],stats[i][1]), (stats[i][0]+blob_width , stats[i][1] + blob_height), (0,255,0), 5)
#        i = i +1
     
    day = int(datetime.datetime.now().strftime("%d"))
    data = Day_info(day)
    for Lab in range(1,7):
        if data[0][i] > 0:
#            print("BLUE")
            cv2.rectangle(img,(pos[i][0],pos[i][1]),(pos[i][2],pos[i][3]),(0,0,255),-1)
        elif car_pos[i] > 0:
#            print("RED")
            cv2.rectangle(img,(pos[i][0],pos[i][1]),(pos[i][2],pos[i][3]),(255,0,0),-1)
        else:
#            print("GREEN")
            cv2.rectangle(img,(pos[i][0],pos[i][1]),(pos[i][2],pos[i][3]),(0,255,0),-1)
        i = i + 1
        
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    cv2.putText(img,text ,(60,450), font, 0.7,(255,0,0),2,cv2.LINE_AA)   
    return img                                     
#    a = Image.fromarray(img)
#    b = ImageTk.PhotoImage(image=a)
#    image_label.config(image=b)
#    image_label._image_cache = b  # avoid garbage collection


def gen():
    camera=cv2.VideoCapture(0)
    """Video streaming generator function."""
    while True:
        ret,frame = camera.read()
        pro_frame = process_image(frame)
#        retval, frame = camera.read()
        imgencode=cv2.imencode('.jpg',pro_frame)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stringData + b'\r\n')
        
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()
    
    
#if __name__ == '__main__':
#    t1 = threading.Thread(target=GUI)
#    t1.start()
#    app.run(host = '0.0.0.0', port = 8080)
