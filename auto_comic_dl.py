import urllib2
import os
from PIL import Image
from fpdf import FPDF
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


cl = open('/home/pi/comic_send/comic_list.txt')
new_cl = open('/home/pi/comic_send/new_comic_list.txt', 'w')
for title in cl.readlines():
    name = title.split("~")[0]
    issue = title.split("~")[1].strip()
    issue = str(int(issue)+1)
    url = "http://readcomics.tv/"+name+"/chapter-"+issue+"/full"
    print("Downloading " + name + " issue #" + issue)
    req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = str(urllib2.urlopen(req).read())
    except:
        print("\t...Unable to download " + name + " issue #" + issue)
        new_cl.write(name+"~"+str(int(issue)-1)+"\n")
        continue
    x = html.find(".jpg")
    pics = []
    while(x != -1 and html.find("http://www.readcomics.tv/images") != -1):
        y = html.rfind("src=", 0, x)
        pics.append(html[y+5: x+4])
        html = html[x+5:]
        x = html.find(".jpg")
    i = 1
    if len(pics) <= 0:
        print("\t..." + name + " issue #" + issue + " may not be released yet")
        new_cl.write(name+"~"+str(int(issue)-1)+"\n")
        continue
    new_cl.write(name+"~"+issue+"\n")

    for p in pics:
        try:
            req = urllib2.Request(str(p))
            req.add_header('User-Agent', 'Mozilla/5.0')
            imgData = urllib2.urlopen(req).read()
            fo = open("/home/pi/comics/page"+str(i)+".jpg", 'wb')
            fo.write(imgData)
            fo.close()
            i += 1
        except:
            pass
    pageCount = i
    pdf = FPDF('P', 'pt', (1800*.80,2768*.80))
    for i in range(1, pageCount):
        pdf.add_page()
        imagePath = "/home/pi/comics/page"+str(i)+".jpg"
        im = Image.open(imagePath)
        size = im.size[0] * .80, im.size[1] * .80
        im.thumbnail(size, Image.ANTIALIAS)
        newImagePath = "/home/pi/comics/newpage"+str(i)+".jpg"
        im.save(newImagePath, "JPEG")
        pdf.image(newImagePath, x=0, y=0, w=size[0], h=size[1], type='JPG')
        i += 1
    pdf.output("/home/pi/comic_send/"+name+"_"+issue+".pdf", "F")
    for i in range(1, pageCount):
        os.remove("/home/pi/comics/page"+str(i)+".jpg")
        os.remove("/home/pi/comics/newpage"+str(i)+".jpg")
    fromaddr = "alexortizzle@gmail.com"
    toaddr = "aorti017@ucr.edu"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = '[Comics] ' + name + ' issue #' + issue
    body = ''
    msg.attach(MIMEText(body, 'plain'))
    filename = name+"_"+issue+".pdf"
    attachment = open('/home/pi/comic_send/'+name+'_'+issue+'.pdf', 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part) 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "monkey6939")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    #os.remove('/home/pi/comic_send/'+name+'_'+issue+'.pdf')
new_cl.close()
cl.close()
os.remove('/home/pi/comic_send/comic_list.txt')
os.rename('/home/pi/comic_send/new_comic_list.txt', '/home/pi/comic_send/comic_list.txt')
