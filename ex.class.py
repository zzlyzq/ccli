import re
import pexpect
import tempfile
import shutil
import time
import os

class ex:
	def __init__(self,ip,username,password):
		self.ip = ip 
		self.username = username
		self.password = password
		self.timewait = 20
		self.expectData1 = [ 'yes/no.*', 'password:.*', '\S+\@\S+>.*', '#.*', '---\(more[\ \d\%]*\)---.*', 'closed.*', 'asdf234234sdfsdf', 'asdfasdf234sdf', 'pexpect.EOF', 'pexect.TIMEOUT.' ]
		self.pexpect1 = pexpect.spawn("ssh %s@%s"%(self.username,self.ip),timeout=self.timewait)

	def conn(self):
		print "START CONN"
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
					print "LOGIN OK"
					print "YOU CAN EXECUTE YOUR COMMAND"
					return 1
		else:
			print backData1
			print "Error A"
			return 0
	
	def getiplist(self):	
		print "START GET IP LIST"
		# Not Complete
		# Do not need this method
		self.pexpect1.sendline("show interfaces terse | match inet")
		backUserData1 = self.pexpect1.expect(self.expectData1)
		print backUserData1
		if backUserData1 == 2:
			print self.pexpect1.before
			result = re.findall('vlan',self.pexpect1.before)
			print result
		else:
			print "Error"
			return 0

	def getmaclist(self):
                print "START GET MAC LIST"
		type = "getmaclist"
		cmd = "show ethernet-switching table"
		resultfile = self.exe(type,cmd)
		for line in open(resultfile):
			if re.findall("ge-",line): # Find ge-
				lineparts = re.findall('(\S+)+',line)
				print lineparts[0], " ", lineparts[1], " ", lineparts[4]
				
		

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
		return resultfile
	
        def getconfig(self):
                print "START GET CONFIG"
		type = "getconfig"
		cmd = "show configuration | display set"
		print self.exe(type,cmd)

        def getversion(self):
                self.pexpect1.sendline("show version")
                backUserData1 = self.pexpect1.expect(self.expectData1)
		#print backUserData1
                if backUserData1 == 2:
                        result = re.findall("JUNOS Base OS boot \[(\S+)\]",self.pexpect1.before)
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
		#print "ex GE1/0/1 - GE1/0/48 PORT STATUS"
		type = "getportfree"
		cmd = "show interface brief"
		resultfile = self.exe(type, cmd)
		freenumber = 0
		#resultfile = "./getportfree/172.20.4.50.txt"
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
			

	def findportfree(self,filename):
	        number = 0
	        file = filename
	        for line in open(file):
	                lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
	                #print lineparts
	                if len(lineparts):
	                        portinfo = re.findall('^(GE1\/0\/)(\d+) ([UPDOWN]+)',line)
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
                        result = re.findall(r"\x0d",line)
                        if len(result) != 0:
                                line2 = line.replace("\x0d","")
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
                        #result = re.findall(r"---\(more[ \d\%]*\)---",line)
                        result = re.findall(r"---\(more",line)
			#print result
                        if len(result) != 0:
				line2 = re.sub("---\(more\)---","",line)
				line2 = re.sub("---\(more \d+\%\)---","",line2)
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
		print "QUIT"
		self.pexpect1.sendline("quit")
		backUserData1 = self.pexpect1.expect(self.expectData1)
		#print "AAAA",backUserData1,"AAAA"
	
