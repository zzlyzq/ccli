import re
import pexpect
import tempfile
import shutil
import time
import os

class s5148:
	def __init__(self,ip,username,password):
		self.ip = ip 
		self.username = username
		self.password = password
		self.timewait = 20
		self.expectData1 = [ 'yes/no.*', 'password:.*', '\<[\w\-]+\>.*','\[[\w\-]+\].*','---- More ----.*','closed.*','asdf234234sdfsdf','asdfasdf234sdf','pexpect.EOF', 'pexect.TIMEOUT.' ]
		self.pexpect1 = pexpect.spawn("ssh %s@%s"%(self.username,self.ip),timeout=self.timewait)

	def conn(self):
		#print "START CONN"
		backData1 = self.pexpect1.expect(self.expectData1)
		if backData1 == 0 or backData1 == 1:
			if backData1 == 0:
				#print "GET YES/NO"
				self.pexpect1.sendline("yes")
				backData12 = self.pexpect1.expect(self.expectData1)
				if backData12 == 1:
					pass
				else:
					print "Error"
					return 0
			if backData1 == 1 or (isset(backData12)):
				#print "GET PASSWROD PRMOMPT"
				#print "SENDING PASSWORD"
				self.pexpect1.sendline(password)
				backData2 = self.pexpect1.expect(self.expectData1)
				if backData2 == 2:
					#print "GET > PRMPT, WE ARE LOGIN"
					return self.pexpect1
					time.sleep(5)
		else:
			print "Error"
			return 0
	def getiplist(self):	
		print "START GET IP LIST"

	def getconfig(self):
		#print "START GETCONFIG"
		type = "getconfig"
		cmd = "display current-configuration"
		self.exe(type,cmd)	

        def getmaclist(self):
                #print "START GET MAC LIST"
                type = "getmaclist"
                cmd = "display mac-address"
                resultfile = self.exe(type,cmd)
		#resultfile = "./getmaclist/172.20.3.201.txt"
		for line in open(resultfile):
			lineparts = re.findall("(\S+)+",line)
			#print lineparts
			if len(lineparts) >= 4:
				portindex = re.findall("(GigabitEthernet1\/0\/)(\d+)",lineparts[3])
				#print "AAA", portindex
				if len(portindex) == 1:
					if len(portindex[0]) == 2:
						#print portindex
						if int(portindex[0][1]) <= 44:
							print lineparts[0],lineparts[1], self.ip, lineparts[3]
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass


        def exe(self,type,cmd):
                recvdata = ""
                self.pexpect1.sendline("%s"%cmd)
                while 1:
                        backUserData1 = self.pexpect1.expect(self.expectData1)
                        if backUserData1 == 2:
                                recvdata += self.pexpect1.before
                                recvdata += self.pexpect1.after
                                break
                        elif backUserData1 == 4:
                                recvdata +=self.pexpect1.before
                                recvdata +=self.pexpect1.after
                                self.pexpect1.send(" ")
                        else:
                                print backUserData1
                                print "Error A"
                                return 0
                resultfile = "./%s/%s.txt"%(type, self.ip)
                resultfilehandle = open(resultfile,'w')
                resultfilehandle.write(recvdata)
                resultfilehandle.close()
                self.cleanfile(resultfile)
                self.cleanfilemore(resultfile)
                self.formatfile(resultfile)
		print "RESULT SAVED TO > %s"%resultfile
                return resultfile

        def getversion(self):
                self.pexpect1.sendline("display version")
                backUserData1 = self.pexpect1.expect(self.expectData1)
                if backUserData1 == 2:
                        result = re.findall(r"(Comware Software, Version \S+, Release \S+)",self.pexpect1.before)
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
		#print "START GET PORT FREE"
		# "dis interface brief"
		#print "s5148 GE1/0/1 - GE1/0/48 PORT STATUS"
		type = "getportfree"
		cmd = "display brief interface"
		resultfile = self.exe(type,cmd)
		number = 0
	        for line in open(resultfile):
	                lineparts = re.findall(r"(\S+)+",line)
	                #print lineparts
	                if len(lineparts):
	                        portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)',line)
	                        if len(portinfo) == 1:
					#print portinfo
	                                portpart1 = portinfo[0][0]
	                                portpart2 = portinfo[0][1]
	                                portstatus = portinfo[0][2]
	                                if int(portpart2) <= 44:
	                                        if portstatus == "DOWN":
	                                                number += 1
		print self.ip, "PORT ETA: ", number
	        return number

        def formatfile(self,filename):
                temp = tempfile.TemporaryFile()
                temphandle = open(temp.name,'w')
                for line in open(filename):
                        #linepart = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
                        linepart = re.findall(r"([\S]+)",line)
                        if len(linepart) == 0:
                                continue
                        if linepart[0] == 'return':
                                break
                        temphandle.write(' '.join(linepart))
                        temphandle.write('\n')
                temphandle.close()
                shutil.copyfile(temp.name,filename)
                temp.close()
		os.unlink(temp.name)
                return 1

        def cleanfile(self,filename):
                temp = tempfile.TemporaryFile()
                temphandle = open(temp.name,'w')
                filehandle = open(filename,'r')
                for line in filehandle:
                        result = re.findall(r"\x1b\x5b\x34\x32\x44",line)
                        if len(result) != 0:
                                line2 = line.replace('\x1b\x5b\x34\x32\x44',"")
                                temphandle.write(line2)
                        else:
                                temphandle.write(line)
                filehandle.close()
                temphandle.close()
                #os.remove(filename)
                shutil.copyfile(temp.name,filename)
                temp.close()
		os.unlink(temp.name)
                return 1

        def cleanfilemore(self,filename):
                temp = tempfile.TemporaryFile()
                temphandle = open(temp.name,'w')
                filehandle = open(filename,'r')
                for line in filehandle:
                        result = re.findall(r"---- More ----",line)
                        if len(result) != 0:
                                line2 = line.replace('---- More ----',"")
                                temphandle.write(line2)
                        else:
                                temphandle.write(line)
                filehandle.close()
                temphandle.close()
                #os.remove(filename)
                shutil.copyfile(temp.name,filename)
                temp.close()
		os.unlink(temp.name)
                return 1

	def quit(self):
		#print "QUIT"
		self.pexpect1.sendline("quit")
		backUserData1 = self.pexpect1.expect(self.expectData1)
		#print "AAAA",backUserData1,"AAAA"
	

username = "yourusername"
password = "yourpassword"
ip = "172.20.3.201"

test = s5148(ip,username,password)
test.conn()
#test.getconfig()
#test.getportfree()
#test.getversion()
#test.getmaclist()
test.quit()

