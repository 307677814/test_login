from wxpy import *
import time
import re
from selenium import webdriver
import os

    

driver = webdriver.Chrome() 

d = []
ans = []
class autoChoose(object):
    def __init__(self, account, password, cource):
        self.account = account
        self.password = password
        self.cource = cource
        self.checked = 0



    def wxlogin(self):
        self.bot = Bot()
        self.xc = self.bot.mps().search("校查")[0]
        self.bot.enable_puid('wxpy_puid.pkl')
        #self.xc = self.bot.search(puid="f98059b9") #校查puid

        @self.bot.register(self.xc)
        def print_others(msg):
            #print(msg)
            if(msg.type == 'Sharing'):
                d.append(msg)
                print("open saveAnswer! %d" % (self.sjnum))
                self.saveAnswer(msg)

    def saveAnswer(self,msg):
        title = driver.execute_script("return document.querySelectorAll('.infoList > ul > li> span')[0].innerText")
        chapter = driver.execute_script("return document.querySelectorAll('.infoList > ul > li> span')[1].innerText")
        print("====save then find====")
        mystr = msg.raw['Content']
        try:
            pat = re.compile(r'\[(.*?)\n参考答案：(.*?)]]')
            q = pat.search(mystr)
            if q is None:
                pat = re.compile(r'\n参考答案：(.*?)]]')
                q = pat.search(mystr)
                l = re.split(r'[╔ \x01]+', q.group(1))
                rq = re.search(r'CDATA(.*)', mystr).group(0)
            else:
                l = re.split(r'[╔ \x01]+', q.group(2))
                pat1 = re.compile(r'CDATA.*\[CDATA\[(.*)')
                rq = pat1.search(q.group(1)).group(1)

            if(len(l) == 0):
                r = re.findall("(.*)\n答案；(.*)", mystr)[0]
                rq = r[0]
                l = re.split(r'[~]+', r[1])
                l.pop() #dele the lasted empty element
        except:
            print("Failed", l)
            print(msg.raw['Content'])
            time.sleep(5)
        finally:
            print("After reg:", rq, l)

        if(len(l) == 0):
            print("resend", self.rq)
            self.xc.send_msg(self.rq)
            

        print(">>>Reply:",self.rq, l)
        if(not os.path.exists(title)):
            os.makedirs(title)
        print("***********GET SJNUM %d **********" % (self.sjnum))
        with open('./' + title + '/' + title + chapter + '.txt', 'a+', encoding='utf-8') as f:
            f.write("题目:" + self.st[self.sjnum].text + '\n' "答案:")
            for i in l:
                f.write(i + " ")
            f.write("\n\n")
        #self.rq = rq
        self.l = l
        print("l",len(l), l)
        print("self.l",len(self.l), self.l)
        print("Opening findAnswer()...")
        self.findAnswer()



    def findAnswer(self):
        print("====findAnswer=====")
        #print("findAnswer:",self.rq, self.l, self.sjnum)
        if(len(self.l) == 0) :
            print("Empty answer!", self.l)
            return
        print("Choosing...:")

        self.sjtc = driver.execute_script("return $('.subject_node')[%d].getElementsByClassName('nodeLab')" % (self.sjnum))
        self.checked = 0
        try:
            for j in self.l:
                i = 0
                while(i < len(self.sjtc)):
                    #print(self.sjtc[i].text.split('\n').pop(1), j)
                    if(self.sjtc[i].text.split('\n').pop(1) == j):
                        self.sjtc[i].click()
                        print("checked:",self.rq,j)
                    i+=1
                    if(i>=len(self.sjtc)):
                        self.checked = 1
        except:
            print("Somethin wrong in checked, refind now")
            self.findAnswer()
        finally:
            if(self.checked == 0):
                print("Refind Answer!")
                self.xc.send_msg(self.rq)
            else:
                print("ok", self.rq)


    #Clear all answer
    def cleanCheck(self):
        mycheckjs = """
        var ac = document.getElementsByClassName("examquestions-answer");
        for(var i = 0; i < ac.length; i++) {
            ac[i].previousElementSibling.firstElementChild.checked = false;
        }
        """
        driver.execute_script(mycheckjs)


    def handlefun(self,changeTo):
        handles = driver.window_handles
        #print("handlefun:", handles)
        driver.switch_to_window(handles[changeTo])

    def courseLogin(self):
        zhsLoginUrl = "https://passport.zhihuishu.com/login?service=http://online.zhihuishu.com/onlineSchool/"
        driver.get(zhsLoginUrl)
        driver.find_element_by_id('lUsername').send_keys(self.account) #account
        driver.find_element_by_id('lPassword').send_keys(self.password)  #password
        driver.execute_script("formSignUp()")
        time.sleep(3)
        driver.execute_script(self.cource)
        #driver.find_element_by_xpath('//*[@id="j-assess-criteria_popup"]/div[9]/div/a').click()
        #driver.find_elements_by_class_name("j-popup-close")
        #1 is video page
        self.handlefun(1)
        time.sleep(3)
        driver.execute_script('document.getElementsByClassName("popbtn_yes")[0].click()')
        driver.execute_script('document.getElementsByClassName("j-popup-close")[1].click()')



    def openCource(self, num):
        self.chooseFinish = 0
        print("========================This is page %s =================================" % (num))
        print("===opencource switch to 2====")
        self.handlefun(2)
        self.cleanCheck()
        time.sleep(3)
        #single page subject descrube
        self.sj = driver.find_elements_by_class_name("subject_describe")
        self.st = driver.execute_script("return $('.subject_stem')")
        
        time.sleep(3)
        i = 0
        while(i < len(self.sj)):
            #patsj = re.compile(r'\n(.*)$') 
            #sj_str = patsj.search(self.sj[i].text).group(1) #match subject
            sj_str = self.sj[i].text
            print(sj_str)
            # 保持i一致以便于查找题目对应的选项
            #print("openCource: ", sj_str ,"number: ", i)
            #l, rq清空一次
            self.l = []
            self.rq = ''

            self.sjnum = i
            print("***********SET SJNUM %d **********" % (self.sjnum))
            time.sleep(1)
            self.rq = sj_str
            self.checked = 0
            self.xc.send_msg(sj_str) # 收到答案后再执行findAnswer()
            k = 0
            while(self.checked!=1):
                time.sleep(1)
                k+=1
                if(k >= 30):
                    print("Timeout a checked!")
                    print("Resent", sj_str)
                    self.xc.send_msg(sj_str) # 收到答案后再执行findAnswer()

            i+=1
            if(i >= len(self.sj)):
                self.chooseFinish = 1
                print("FINISH FLAG:", self.chooseFinish)


    def saveTest(self):
            driver.execute_script("""
            submitAnswer(1);
            document.getElementsByClassName("popbtn_yes")[0].click();
            """)
    
    def loopOpenCourse(self):
        self.tp = driver.find_elements_by_class_name("name") 
        time.sleep(2)
        i = 0
        while(i < len(self.tp)):
        #while(i<= 0):
            print("\n\n========================PAGE %d START========================\n\n" % (i))
            self.tp[i].click()
            time.sleep(3)
            self.openCource(i)
            time.sleep(5)
            k = 0
            while(self.chooseFinish != 1):
                time.sleep(1)
                k+=1
                if(k>40):
                    print("Timeout page submit!")
                    break
            if(self.chooseFinish == 1):
                self.saveTest()
                #driver.close()
                print("===loopOpenCourse switch to 1====")
                print("\n\n========================PAGE %d FINISH========================\n\n" % (i))
                self.handlefun(1)
                i+=1
            else:
                print("PAGE NOT FINISH, RELOOP NOW")



    def main(self):
        self.wxlogin()
        self.courseLogin()
        self.loopOpenCourse()

        
if __name__=='__main__':
    account = "13226304166"
    password = "z656477z"
    #cource = "openVideo('2027882','7954','0');" #书法
    #cource = "openVideo('2022880','6532','1');"
    cource = "openVideo('2027843','7926','0');"
    dt = autoChoose(account, password, cource)
    dt.main()