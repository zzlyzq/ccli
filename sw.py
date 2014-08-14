import re
import pexpect
import tempfile
import shutil
import time
import os
import sys

class dell3548:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 10
        self.expectData1 = [ 'User Name:.*', 'Password:.*', '[^n]> .*', 'asdfasdfasdf', 'One line: <return>.*', '[^n]# .*', '34234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("telnet %s" % (self.ip), timeout=self.timewait)

    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0:
            self.pexpect1.sendline(self.username)
            backData2 = self.pexpect1.expect(self.expectData1)
            if backData2 == 1:
                self.pexpect1.sendline(self.password)
                backData3 = self.pexpect1.expect(self.expectData1)
                if backData3 == 2:
                    self.pexpect1.sendline("enable")    
                    backData4 = self.pexpect1.expect(self.expectData1)
                    if backData4 == 1:
                        self.pexpect1.sendline("admin123")
                        backData5 = self.pexpect1.expect(self.expectData1)
                        # print backData5
                        if backData5 == 5:
                            print "LOGGED IN"
                            print "YOU CAN EXECUTE YOUR COMMAND"
                            return 1
                    else:
                        print "Error D"
                        return 0
                else:
                    print "Error C"
                    return 0
            else:
                print "Error B"
                return 0
        else:
            print "Error A"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"

    def getconfig(self):
        print "START GET CONFIG"
        type = "getconfig"
        cmd = "show running-config"
        resultfile = self.exe(type, cmd)

    def getportfree(self):
        print "START GET PORT FREE"
        type = "getportfree"
        cmd = "show interface status"
#        resultfile = self.exe(type, cmd)
        resultfile = "./getportfree/172.22.3.227.txt"
        number = 0
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) == 9:
                # print lineparts
                if len(re.findall("e\d+", lineparts[0])) == 1:
                    if lineparts[6] != "Up":
                        number += 1
        print self.ip, "PORT ETA :", number
        return number
    
    def getversion(self):
        print "START TO GET VERSION"
        type = "getversion"
        cmd = "show version"
        # resultfile = self.exe(type, cmd)
        resultfile = "./getversion/172.22.3.227.txt"
        for line in open(resultfile):
            result = re.findall("SW *version *(\S+)", line)
            # print result
            if len(result) == 1:
                print self.ip, "VERSION :", result[0]
                return result[0]
            elif len(result) == 0:
                pass
            else:
                print "ErrorA"
                return 0
        
    def getmaclist(self):
        type = "getmaclist"
        cmd = "show bridge address-table"
        resultfile = self.exe(type, cmd)
        # resultfile = "./getmaclist/172.22.3.227.txt"
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip) 
        returnfilehandle = open(getmaclist2, 'w') 
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)    
            if len(lineparts) == 4:
                portindex = re.findall("^e(\d+)", lineparts[2])
                if len(portindex) == 1:
                    if int(portindex[0]) <= 47:
                        resultstring = str(lineparts[1]) + " " + str(lineparts[0]) + " " + str(self.ip) + " " + str(lineparts[2]) + "\n" 
                        print resultstring
                        returnfilehandle.write(resultstring)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        returnfilehandle.close()
            
    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline(cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 5:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.sendline("")
            else:
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        print self.ip, "SAVED TO ", resultfile
        return resultfile

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
                if linepart[0] == 'return':
                    break
                temphandle.write(' '.join(linepart))
                temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x30\x6d", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x30\x6d', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"More: <space>,  Quit: q, One line: <return>", line)
            if len(result) != 0:
                line2 = line.replace('More: <space>,  Quit: q, One line: <return>', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
    
class ex:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\S+\@\S+>.*', '#.*', '---\(more[\ \d\%]*\)---.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)

    def conn(self):
        print "START:CONN",
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    # print "GET PASWORD PROMPT backData12"
                    # print dir().count("backData12")
                    # print dir()
                    pass
                else:
                    print "Error CONN A"
                    return 0
            # if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                #print "GET PASSWROD PRMOMPT backData1 or backData12"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    print "LOGIN:OK",
                    return 1
        else:
            print backData1
            print "Error conn A"
            return 0

    def findportconfig(self, swport):
        print "FINDPORTCONFIG:START",
        portconflist = []
        filename = "./getconfig/%s.txt" % self.ip
        for line in open(filename):
            if re.findall(swport, line):
                portconflist.append('%s' % line)
            else:
                pass
        return portconflist

    def enterpri(self):
        self.pexpect1.sendline("edit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 3:
            print "ENTPRI:OK",
            return 1
        else:
            pass
            return 0

    def commit(self):
        self.pexpect1.sendline("commit")
        backUserData1 = self.pexpect1.expect(self.expectData1, timeout=15)
        if backUserData1 == 3:
            if re.findall("commit complete", self.pexpect1.before):
                print "COMMIT:OK",
                return 1
            else:
                print "ErrorcommitA"
                print self.pexpect1.before
                return 0
        else:
            return 0

    def setportvlan(self, hostvlan, swport):
        print "CMD:setportvlan",
        self.getconfig()
        portconflist = self.findportconfig(swport)
        # print portconflist
        print "portConfLength:", len(portconflist),
        self.enterpri()
        for portconf in portconflist:
            if re.findall("set interface", portconf):
                continue
            portconf2 = portconf.replace("set", "delete")
            portconf3 = portconf2.replace("\n", "")
	    print "deleteCommand:(", portconf3, ")",
            if re.findall('%s' % swport, portconf3):
                self.pexpect1.sendline(portconf3)
                backUserData1 = self.pexpect1.expect(self.expectData1)
                if backUserData1 == 3:
                    pass
                else:
                    print "Error"
                    return 0
            else:
                print "Error"
                return 0
        # Sendin port configure
        # self.pexpect1.sendline("set interface %s unit 0 family ethernet-switching"%swport)
        # backUserData2 = self.pexpect1.expect(self.expectData1)
        # if backUserData2 == 3:
        #    print "INFCONFFAM:OK"
        # else:
        #    print "ErrorC"
        #    return 0
        command = "set vlans vlan%s interface %s.0" % (hostvlan, swport)
        print "setCommand:(", command, ")",
        self.pexpect1.sendline(command)
        backUserData3 = self.pexpect1.expect(self.expectData1)
        if backUserData3 == 3:
            print "VLANCONF:OK",
        else:
            print "ErrorD"
            return 0
        # self.commit()
        self.pexpect1.sendline('commit')
        backUserData4 = self.pexpect1.expect(self.expectData1, timeout=15)
        if backUserData4 == 3:
            #print self.pexpect1.before
            #print self.pexpect1.after
            #print "DDDD"
            if re.findall('commit complete', self.pexpect1.before):
                print "COMMIT:OK",
            else:
                return 0
        else:
            return 0
        return 1
    
    def getiplist(self):    
        print "START GET IP LIST"
        # Not Complete
        # Do not need this method
        self.pexpect1.sendline("show interfaces terse | match inet")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        print backUserData1
        if backUserData1 == 2:
            print self.pexpect1.before
            result = re.findall('vlan', self.pexpect1.before)
            print result
        else:
            print "Error"
            return 0

    def getmaclist(self):
        print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "show ethernet-switching table"
        resultfile = self.exe(type, cmd)
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, 'w')
        for line in open(resultfile):
            if re.findall("ge-", line):  # Find ge-
                lineparts = re.findall('(\S+)+', line)
                resultstring = str(lineparts[1]) + " " + str(lineparts[0]) + " " + str(self.ip) + " " + str(lineparts[4]) + "\n"
                print resultstring
                returnfilehandle.write(resultstring)
        returnfilehandle.close()

    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        return resultfile
    
    def getconfig(self):
        print "GETCONFIG:START",
        type = "getconfig"
        cmd = "show configuration | display set"
        print self.exe(type, cmd)

    def getversion(self):
        self.pexpect1.sendline("show version")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print backUserData1
        if backUserData1 == 2:
            result = re.findall("JUNOS Base OS boot \[(\S+)\]", self.pexpect1.before)
            if len(result) == 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print "ErrorB"
                return 0
        else:
            print "ErrorA"
            return 0
    
    def getportfree(self):
        # print "START GET PORT FREE"
        # "dis interface brief"
        # print "ex GE1/0/1 - GE1/0/48 PORT STATUS"
        type = "getportfree"
        cmd = "show interface brief"
        resultfile = self.exe(type, cmd)
        freenumber = 0
        # resultfile = "./getportfree/172.20.4.50.txt"
        for line in open(resultfile):
            result = re.findall("Physical interface: (ge-0\/0\/\d+), Enabled, Physical link is (\S+)", line)
            if len(result) == 1: 
                if len(result[0]) == 2:
                    print result[0][0], "PORT STATUS:", result[0][1]
                    if result[0][1] == "Down":
                        freenumber += 1
                else:
                    pass
            else:
                pass
        print "PORT ETA: ", freenumber
        return freenumber
            

    def findportfree(self, filename):
        number = 0
        file = filename
        for line in open(file):
            lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)', line)
                if len(portinfo) == 1:
                    portsubs = portinfo[0]
                    portpart1 = portsubs[0]
                    portpart2 = portsubs[1]
                    portstatus = portsubs[2]
                    if int(portpart2) <= 44:
                        if portstatus == "DOWN":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
            if linepart[0] == 'return':
                break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x0d", line)
            if len(result) != 0:
                line2 = line.replace("\x0d", "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            # result = re.findall(r"---\(more[ \d\%]*\)---",line)
            result = re.findall(r"---\(more", line)
            # print result
            if len(result) != 0:
                line2 = re.sub("---\(more\)---", "", line)
                line2 = re.sub("---\(more \d+\%\)---", "", line2)
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
    
class s16:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 10
        self.expectData1 = [ 'sername.*', 'assword:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'ENTER.*', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("telnet %s" % (self.ip), timeout=self.timewait)

    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0:
            self.pexpect1.send(self.username)
            self.pexpect1.send('\r')
            backData2 = self.pexpect1.expect(self.expectData1)
            if backData2 == 1:
                self.pexpect1.send(self.password)
                self.pexpect1.send('\r')
                backData3 = self.pexpect1.expect(self.expectData1)
                if backData3 == 6:
                    self.pexpect1.send('\r')
                    backData4 = self.pexpect1.expect(self.expectData1)
                    if backData4 == 2:
                        print "LOGGED IN"
                        print "YOU CAN EXECUTE YOUR COMMAND NOW"
                    else:
                        print "Error"
                        return 0
                else:
                    print "Error"
                    return 0
            else:
                print "Error"
                return 0
        else:
            print "Error"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"

    def getconfig(self):
        print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        self.exe(type, cmd)

    def getversion(self):
        self.pexpect1.send("display version\r")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            result = re.findall(r"(S1650 Product Version \S+)", self.pexpect1.before)
            if len(result) == 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print "ErrorB"
                return 0
        else:
            print self.pexpect1.before
            print "ErrorA"
            return 0

    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
       	getmaclist2 = "./%s2/%s" % (type, self.ip)
        returnfilehandle = open(getmaclist, 'w')
        # resultfile = "./getmaclist/172.20.3.201.txt"
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) == 5:
                portindex = re.findall("(Ethernet0\/)(\d+)", lineparts[3])
                # print "AAA", portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                    # print portindex
                        if int(portindex[0][1]) <= 48:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[3]) + "\n"
                            #print resultstring
                            returnfilehandle.write(resultstring)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        returnfilehandle.close()

    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.send("%s\r" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send("\r")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        print "RESULT SAVED TO > %s" % resultfile
        return resultfile

    def getportfree(self):
        print "START GET PORT FREE"
        # "dis interface brief"
        # print "s16 GE1/0/1 - GE1/0/48 PORT STATUS"
        number = 0
        for portid in range(1, 50 + 1):
            # print "PORTID", portid
            recvdata = ""
            self.pexpect1.send("dis interface ethernet0/%d\r" % portid)
            while 1:
                backUserData1 = self.pexpect1.expect(self.expectData1)
                # print backUserData1
                if backUserData1 == 2:
                    recvdata += self.pexpect1.before
                    break
                elif backUserData1 == 4:
                    recvdata += self.pexpect1.before
                    self.pexpect1.send(" ")
                else:
                    print "ErrorA"
                    return 0
            # print recvdata
            # print "ENT THIS PORT"
            result = re.findall(r"current state: *(\S+)", recvdata)
            if len(result) == 1:
                if result[0] != "UP":
                    number += 1
                else:
                    pass
            else:
                print result
                print "ErrorB"
                return 0
        print self.ip, "PORT ETA", number
            
    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
            if linepart[0] == 'return':
                break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x0d\x0d", line)
            if len(result) != 0:
                line2 = line.replace('\x0d\x0d', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----\x00\x0d\x1b\x5b\x4d", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----\x00\x0d\x1b\x5b\x4d', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.send("quit\r")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
    
class s2752:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.version = ""
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)

    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                # print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    pass
                else:
                    print "Error"
                    return 0
            # if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                # print "GET PASSWROD PRMOMPT"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    # print "GET > PRMPT, WE ARE LOGIN"
                    return self.pexpect1
                    time.sleep(5)
        else:
            print "Error"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"
        self.pexpect1.sendline("dis ip interface brief")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            print self.pexpect1.before
        else:
            print "Error"
            return 0

    def getconfig(self):
        # print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        resultfile = self.exe(type, cmd)


    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, "w")
        # resultfile = "./getmaclist/172.20.3.201.txt"
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) == 7:
                portindex = re.findall("(Eth0\/0\/)(\d+)", lineparts[4])
                # print "AAA", portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                        # print portindex
                        if int(portindex[0][1]) <= 47:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[4]) + "\n"
                            print resultstring
                            returnfilehandle.write(resultstring)
        returnfilehandle.close()

    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        print "RESULT SAVED TO > %s" % resultfile
        return resultfile
    
    def getportfree(self):
        type = "getportfree"
        cmd = "dis interface brief"
        resultfile = self.exe(type, cmd)
        number = 0
        for line in open(resultfile):
            lineparts = re.findall(r"(\S+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(Ethernet0\/0\/)(\d+) +([updown]+)', line)
                if len(portinfo) == 1:
                    portsubs = portinfo[0]
                    portpart1 = portsubs[0]
                    portpart2 = portsubs[1]
                    portstatus = portsubs[2]
                    if int(portpart2) <= 48:
                        if portstatus == "down":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number
    
    def getversion(self):
        self.pexpect1.sendline("display current-configuration")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 4:
            result = re.findall(r"Software Version (\S+)", self.pexpect1.before)
            if len(result) == 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print "ErrorB"
                return0
        else:
            print "ErrorA"
            return 0
            

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
            if linepart[0] == 'return':
                break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x34\x32\x44", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x34\x32\x44', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
    

class s5148:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)

    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                # print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    pass
                else:
                    print "Error"
                    return 0
#            if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                # print "GET PASSWROD PRMOMPT"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    # print "GET > PRMPT, WE ARE LOGIN"
                    return self.pexpect1
                    time.sleep(5)
        else:
            print "Error"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"

    def getconfig(self):
        # print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        self.exe(type, cmd)    

    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, 'w')
        # resultfile = "./getmaclist/172.20.3.201.txt"
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) >= 4:
                portindex = re.findall("(GigabitEthernet1\/0\/)(\d+)", lineparts[3])
                # print "AAA", portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                        # print portindex
                        if int(portindex[0][1]) <= 44:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[3]) + "\n"
                            print resultstring
                            returnfilehandle.write(resultstring)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        returnfilehandle.close()

    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        print "RESULT SAVED TO > %s" % resultfile
        return resultfile

    def getversion(self):
        self.pexpect1.sendline("display version")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            result = re.findall(r"(Comware Software, Version \S+, Release \S+)", self.pexpect1.before)
            if len(result) == 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print "ErrorB"
                return 0
        else:
            print "ErrorA"
            return 0

    def getportfree(self):
        # print "START GET PORT FREE"
        # "dis interface brief"
        # print "s5148 GE1/0/1 - GE1/0/48 PORT STATUS"
        type = "getportfree"
        cmd = "display brief interface"
        resultfile = self.exe(type, cmd)
        number = 0
        for line in open(resultfile):
            lineparts = re.findall(r"(\S+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)', line)
                if len(portinfo) == 1:
                # print portinfo
                    portpart1 = portinfo[0][0]
                    portpart2 = portinfo[0][1]
                    portstatus = portinfo[0][2]
                    if int(portpart2) <= 44:
                        if portstatus == "DOWN":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
        # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
            if linepart[0] == 'return':
                break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x34\x32\x44", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x34\x32\x44', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
    
class s5152:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)
    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                # print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    pass
                else:
                    print "Error"
                    return 0
#            if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                # print "GET PASSWROD PRMOMPT"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    # print "GET > PRMPT, WE ARE LOGIN"
                    return self.pexpect1
                    time.sleep(5)
        else:
            print "Error"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"
        self.pexpect1.sendline("dis ip interface brief")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            print self.pexpect1.before
        else:
            print "Error"
            return 0

    def getconfig(self):
        # print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        self.exe(type, cmd)

    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, 'w')
        # resultfile = "./getmaclist/172.20.3.201.txt"
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) >= 4:
                portindex = re.findall("(GigabitEthernet1\/0\/)(\d+)", lineparts[3])
                # print "AAA", portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                        # print portindex
                        if int(portindex[0][1]) <= 48:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[3]) + "\n"
                            #print resultstring
                            returnfilehandle.write(resultstring)
        returnfilehandle.close()


    def getversion(self):
        self.pexpect1.sendline("display current-configuration")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 4:
            result = re.findall(r"(version \S+, Release \S+)", self.pexpect1.before)
            if len(result) == 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print "ErrorB"
                return 0
        else:
            print "ErrorA"
            return 0
    
    def getportfree(self):
        # print "START GET PORT FREE"
        # "dis interface brief"
        type = "getportfree"
        cmd = "display interface brief"
        resultfile = self.exe(type, cmd)
        number = 0
        for line in open(resultfile):
            lineparts = re.findall(r"(\S+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)', line)
                if len(portinfo) == 1:
                    # print portinfo
                    portpart1 = portinfo[0][0]
                    portpart2 = portinfo[0][1]
                    portstatus = portinfo[0][2]
                    if int(portpart2) <= 48:
                        if portstatus == "DOWN":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number
        
    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        print "RESULT SAVED TO > %s" % resultfile
        return resultfile

    def findportfree(self, filename):
        number = 0
        file = filename
        for line in open(file):
            lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)', line)
                if len(portinfo) == 1:
                    portsubs = portinfo[0]
                    portpart1 = portsubs[0]
                    portpart2 = portsubs[1]
                    portstatus = portsubs[2]
                    if int(portpart2) <= 48:
                        if portstatus == "DOWN":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
                if linepart[0] == 'return':
                    break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x31\x36\x44", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x31\x36\x44', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"

class s5124:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)

    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                # print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    pass
                else:
                    print "Error"
                    return 0
#            if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                # print "GET PASSWROD PRMOMPT"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    # print "GET > PRMPT, WE ARE LOGIN"
                    return self.pexpect1
                    time.sleep(5)
        else:
            print "Error"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"
        self.pexpect1.sendline("dis ip interface brief")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            print self.pexpect1.before
        else:
            print "Error"
            return 0

    def getconfig(self):
        # print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        self.exe(type, cmd)

    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, 'w')
        # resultfile = "./getmaclist/172.20.3.201.txt"
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) >= 4:
                portindex = re.findall("(GigabitEthernet1\/0\/)(\d+)", lineparts[3])
                # print "AAA", portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                    # print portindex
                        if int(portindex[0][1]) <= 48:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[3]) + "\n"
                            print resultstring
                            returnfilehandle.write(resultstring)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
    	returnfilehandle.close()

    def getversion(self):
        self.pexpect1.sendline("display current-configuration")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 4:
            result = re.findall(r"(version \S+, Release \S+)", self.pexpect1.before)
            if len(result) == 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print "ErrorB"
                return 0
        else:
            print "ErrorA"
            return 0

    def getportfree(self):
        # print "START GET PORT FREE"
        # "dis interface brief"
        type = "getportfree"
        cmd = "display interface brief"
        resultfile = self.exe(type, cmd)
        number = 0
        for line in open(resultfile):
            lineparts = re.findall(r"(\S+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)', line)
                if len(portinfo) == 1:
                    # print portinfo
                    portpart1 = portinfo[0][0]
                    portpart2 = portinfo[0][1]
                    portstatus = portinfo[0][2]
                    if int(portpart2) <= 48:
                        if portstatus == "DOWN":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number
    
    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        print "RESULT SAVED TO > %s" % resultfile
        return resultfile

    def findportfree(self, filename):
        number = 0
        file = filename
        for line in open(file):
            lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)', line)
                if len(portinfo) == 1:
                    portsubs = portinfo[0]
                    portpart1 = portsubs[0]
                    portpart2 = portsubs[1]
                    portstatus = portsubs[2]
                    if int(portpart2) <= 48:
                        if portstatus == "DOWN":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
                if linepart[0] == 'return':
                    break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x31\x36\x44", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x31\x36\x44', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
            filehandle.close()
            temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"

class s5352:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)
    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                # print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    pass
                else:
                    print "Error"
                    return 0
#            if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                # print "GET PASSWROD PRMOMPT"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    # print "GET > PRMPT, WE ARE LOGIN"
                    return self.pexpect1
                    time.sleep(5)
        else:
            print "Error"
            return 0

    def setportvlan(self, vlan, swport):
        print "CMD:setportvlan",
        self.pexpect1.sendline('system-view')
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 3:
            print "EnterPrvi:OK ",
            self.pexpect1.sendline('vlan %s' % vlan)
            backUserData2 = self.pexpect1.expect(self.expectData1)
            if backUserData2 == 3:
                print "VlanCommand:OK",
                self.pexpect1.sendline('port %s' % swport)
                backUserData3 = self.pexpect1.expect(self.expectData1)
                if backUserData3 == 3:
                    print "PortCommand:OK",
                    return 1
                else:
                    print "ErrorC"
                    return 0
            else:
                print "ErrorB"
                return 0
        else:
            print "ErrorA"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"
        self.pexpect1.sendline("dis ip interface brief")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            print self.pexpect1.before
        else:
            print "Error"
            return 0

    def getconfig(self):
        # print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        self.exe(type, cmd)
    
    def getportfree(self):
        # print "START GET PORT FREE"
        # "dis interface brief"
        type = "getportfree"
        cmd = "display interface brief"
        resultfile = self.exe(type, cmd)
        number = 0
        for line in open(resultfile):
            lineparts = re.findall(r"(\S+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GigabitEthernet0\/0\/)(\d+) ([updown]+)', line)
                if len(portinfo) == 1:
                    # print portinfo
                    portpart1 = portinfo[0][0]
                    portpart2 = portinfo[0][1]
                    portstatus = portinfo[0][2]
                    if int(portpart2) <= 48:
                        if portstatus == "down":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number
    
    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
        # resultfile = "./getmaclist/172.20.3.182.txt"
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, 'w')
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) == 5:
                # print lineparts
                portindex = re.findall("(GigabitEthernet0\/0\/)(\d+)", lineparts[2])
                # print portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                        # print portindex
                        if int(portindex[0][1]) <= 48:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[2]) + "\n"
                            print resultstring
                            returnfilehandle.write(resultstring)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        returnfilehandle.close()

    def getversion(self):
        self.pexpect1.sendline("display version")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 4:
            result = re.findall("(VRP \(R\) Software, Version \S+ \(S5300 \S+\))", self.pexpect1.before)
            if len(result) >= 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print self.pexpect1.before
                print "getversion ErrorB"
                return 0
        else:
            print "getversion ErrorA"
            return 0

    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        #print "RESULT SAVED TO > %s" % resultfile
        return resultfile

    def findportfree(self, filename):
        number = 0
        file = filename
        for line in open(file):
            lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GigabitEthernet0\/0\/)(\d+) ([updown]+)', line)
                if len(portinfo) == 1:
                    portsubs = portinfo[0]
                    portpart1 = portsubs[0]
                    portpart2 = portsubs[1]
                    portstatus = portsubs[2]
                    if int(portpart2) <= 48:
                        if portstatus == "down":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
            if linepart[0] == 'return':
                break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x34\x32\x44", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x34\x32\x44', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
    


class s5748:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)
    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                # print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    pass
                else:
                    print "Error"
                    return 0
            # if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                # print "GET PASSWROD PRMOMPT"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    # print "GET > PRMPT, WE ARE LOGIN"
                    return self.pexpect1
                    time.sleep(5)
        else:
            print "Error"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"
        self.pexpect1.sendline("dis ip interface brief")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            print self.pexpect1.before
        else:
            print "Error"
            return 0

    def getversion(self):
        self.pexpect1.sendline("display current-configuration")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 4:
            result = re.findall(r"Software Version (\S+)", self.pexpect1.before)
            if len(result) == 1:
                print self.ip, "Version :", result[0]
                self.pexpect1.sendline('q')
                return result[0]
            else:
                print "ErrorB"
                return0
        else:
            print "ErrorA"
            return 0

    def getconfig(self):
        # print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        self.exe(type, cmd)

    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, "w")
        # resultfile = "./getmaclist/172.20.3.172.txt"
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) == 7:
                portindex = re.findall("(GE0\/0\/)(\d+)", lineparts[4])
                # print "AAA", portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                        # print portindex
                        if int(portindex[0][1]) <= 44:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[4]) + "\n"
                            print resultstring
                            returnfilehandle.write(resultstring)
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
    	returnfilehandle.close()

    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        print "RESULT SAVED TO > %s" % resultfile
        return resultfile

    def getportfree(self):
        # print "START GET PORT FREE"
        # "dis interface brief"
        type = "getportfree"
        cmd = "display interface brief"
        resultfile = self.exe(type, cmd)
        # resultfile = "./getportfree/172.20.3.172.txt"
        number = 0
        for line in open(resultfile):
            lineparts = re.findall(r"(\S+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GigabitEthernet0\/0\/)(\d+) ([updown]+)', line)
                if len(portinfo) == 1:
                    # print portinfo
                    portpart1 = portinfo[0][0]
                    portpart2 = portinfo[0][1]
                    portstatus = portinfo[0][2]
                    if int(portpart2) <= 44:
                        if portstatus == "down":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def findportfree(self, filename):
        number = 0
        file = filename
        for line in open(file):
            lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GigabitEthernet0\/0\/)(\d+) ([updown]+)', line)
                if len(portinfo) == 1:
                    portsubs = portinfo[0]
                    portpart1 = portsubs[0]
                    portpart2 = portsubs[1]
                    portstatus = portsubs[2]
                    if int(portpart2) <= 44:
                        if portstatus == "down":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
            if linepart[0] == 'return':
                break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x34\x32\x44", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x34\x32\x44', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
    

class s5752:
    def __init__(self, ip, username, password):
        self.ip = ip 
        self.username = username
        self.password = password
        self.timewait = 20
        self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*', '\[[\w\-]+\].*', '---- More ----.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
        self.pexpect1 = pexpect.spawn("ssh %s@%s" % (self.username, self.ip), timeout=self.timewait)
    def conn(self):
        # print "START CONN"
        backData1 = self.pexpect1.expect(self.expectData1)
        if backData1 == 0 or backData1 == 1:
            if backData1 == 0:
                # print "GET YES/NO"
                self.pexpect1.sendline("yes")
                backData12 = self.pexpect1.expect(self.expectData1)
                if backData12 == 1:
                    pass
                else:
                    print "Error"
                    return 0
#            if backData1 == 1 or (isset(backData12)):
            if backData1 == 1 or dir().count("backData12") == 1:
                # print "GET PASSWROD PRMOMPT"
                # print "SENDING PASSWORD"
                self.pexpect1.sendline(self.password)
                backData2 = self.pexpect1.expect(self.expectData1)
                if backData2 == 2:
                    # print "GET > PRMPT, WE ARE LOGIN"
                    return self.pexpect1
                    time.sleep(5)
        else:
            print "Error"
            return 0

    def setportvlan(self, vlan, swport):
        print "CMD:setportvlan",
        self.pexpect1.sendline('system-view')
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 3:
            print "EnterPrvi:OK ",
            self.pexpect1.sendline('vlan %s' % vlan)
            backUserData2 = self.pexpect1.expect(self.expectData1)
            if backUserData2 == 3:
                print "VlanCommand:OK",
                self.pexpect1.sendline('port %s' % swport)
                backUserData3 = self.pexpect1.expect(self.expectData1)
                if backUserData3 == 3:
                    print "PortCommand:OK",
                    return 1
                else:
                    print "ErrorC"
                    return 0
            else:
                print "ErrorB"
                return 0
        else:
            print "ErrorA"
            return 0

    def getiplist(self):    
        print "START GET IP LIST"
        self.pexpect1.sendline("dis ip interface brief")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        if backUserData1 == 2:
            print self.pexpect1.before
        else:
            print "Error"
            return 0

        def getversion(self):
            self.pexpect1.sendline("display current-configuration")
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 4:
                result = re.findall(r"Software Version (\S+)", self.pexpect1.before)
                if len(result) == 1:
                    print self.ip, "Version :", result[0]
                    self.pexpect1.sendline('q')
                    return result[0]
                else:
                    print "ErrorB"
                    return0
            else:
                print "ErrorA"
                return 0


    def getconfig(self):
        # print "START GETCONFIG"
        type = "getconfig"
        cmd = "display current-configuration"
        self.exe(type, cmd)

    def getmaclist(self):
        # print "START GET MAC LIST"
        type = "getmaclist"
        cmd = "display mac-address"
        resultfile = self.exe(type, cmd)
        getmaclist2 = "./%s2/%s.txt" % (type, self.ip)
        returnfilehandle = open(getmaclist2, "w")
        # resultfile = "./getmaclist/172.20.3.172.txt"
        for line in open(resultfile):
            lineparts = re.findall("(\S+)+", line)
            # print lineparts
            if len(lineparts) == 7:
                portindex = re.findall("(GE0\/0\/)(\d+)", lineparts[4])
                # print "AAA", portindex
                if len(portindex) == 1:
                    if len(portindex[0]) == 2:
                    # print portindex
                        if int(portindex[0][1]) <= 48:
                            resultstring = str(lineparts[0]) + " " + str(lineparts[1]) + " " + str(self.ip) + " " + str(lineparts[4]) + "\n"
                            #print resultstring
                            returnfilehandle.write(resultstring)
        returnfilehandle.close()

    def exe(self, type, cmd):
        recvdata = ""
        self.pexpect1.sendline("%s" % cmd)
        while 1:
            backUserData1 = self.pexpect1.expect(self.expectData1)
            if backUserData1 == 2:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                break
            elif backUserData1 == 4:
                recvdata += self.pexpect1.before
                recvdata += self.pexpect1.after
                self.pexpect1.send(" ")
            else:
                print backUserData1
                print "Error A"
                return 0
        resultfile = "./%s/%s.txt" % (type, self.ip)
        resultfilehandle = open(resultfile, 'w')
        resultfilehandle.write(recvdata)
        resultfilehandle.close()
        self.cleanfile(resultfile)
        self.cleanfilemore(resultfile)
        self.formatfile(resultfile)
        #print "RESULT SAVED TO > %s" % resultfile
        return resultfile

    def getportfree(self):
        # print "START GET PORT FREE"
        # "dis interface brief"
        type = "getportfree"
        cmd = "display interface brief"
        resultfile = self.exe(type, cmd)
        # resultfile = "./getportfree/172.20.3.172.txt"
        number = 0
        for line in open(resultfile):
            lineparts = re.findall(r"(\S+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GigabitEthernet0\/0\/)(\d+) ([updown]+)', line)
                if len(portinfo) == 1:
                    # print portinfo
                    portpart1 = portinfo[0][0]
                    portpart2 = portinfo[0][1]
                    portstatus = portinfo[0][2]
                    if int(portpart2) <= 48:
                        if portstatus == "down":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def findportfree(self, filename):
        number = 0
        file = filename
        for line in open(file):
            lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+", line)
            # print lineparts
            if len(lineparts):
                portinfo = re.findall('^(GigabitEthernet0\/0\/)(\d+) ([updown]+)', line)
                if len(portinfo) == 1:
                    portsubs = portinfo[0]
                    portpart1 = portsubs[0]
                    portpart2 = portsubs[1]
                    portstatus = portsubs[2]
                    if int(portpart2) <= 44:
                        if portstatus == "down":
                            number += 1
        print self.ip, "PORT ETA: ", number
        return number

    def formatfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        for line in open(filename):
            # linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
            linepart = re.findall(r"([\S]+)", line)
            if len(linepart) == 0:
                continue
            if linepart[0] == 'return':
                break
            temphandle.write(' '.join(linepart))
            temphandle.write('\n')
        temphandle.close()
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfile(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"\x1b\x5b\x34\x32\x44", line)
            if len(result) != 0:
                line2 = line.replace('\x1b\x5b\x34\x32\x44', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def cleanfilemore(self, filename):
        temp = tempfile.TemporaryFile()
        temphandle = open(temp.name, 'w')
        filehandle = open(filename, 'r')
        for line in filehandle:
            result = re.findall(r"---- More ----", line)
            if len(result) != 0:
                line2 = line.replace('---- More ----', "")
                temphandle.write(line2)
            else:
                temphandle.write(line)
        filehandle.close()
        temphandle.close()
        # os.remove(filename)
        shutil.copyfile(temp.name, filename)
        temp.close()
        os.unlink(temp.name)
        return 1

    def quit(self):
        # print "QUIT"
        self.pexpect1.sendline("quit")
        backUserData1 = self.pexpect1.expect(self.expectData1)
        # print "AAAA",backUserData1,"AAAA"
