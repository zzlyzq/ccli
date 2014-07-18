import re
import pexpect
import tempfile
import shutil
import time
import os

class s27:
	def __init__(self,ip,username,password):
		self.ip = ip 
		self.username = username
		self.password = password
		self.timewait = 20
		self.version = ""
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
		self.pexpect1.sendline("dis ip interface brief")
		backUserData1 = self.pexpect1.expect(self.expectData1)
		if backUserData1 == 2:
			print self.pexpect1.before
		else:
			print "Error"
			return 0

	def getconfig(self):
		#print "START GETCONFIG"
		self.pexpect1.sendline("display current-configuration")
		conffile = "./config/%s.txt"%(self.ip)
		conffilehandle = open(conffile,'w')
		while 1:
			backUserData1 = self.pexpect1.expect(self.expectData1)
			conffilehandle.write(self.pexpect1.before)
			conffilehandle.write(self.pexpect1.after)
			if backUserData1 == 2:
				conffilehandle.close()
				self.cleanfile(conffile)
				self.cleanfilemore(conffile)
				self.formatfile(conffile)
				print self.ip, "SAVED TO > ",conffile
				return 1
			elif backUserData1 == 4:
				self.pexpect1.sendline(" ")
			else:
				print "Error"
				return 0

	
	def getportfree(self):
		#print "START GET PORT FREE"
		# "dis interface brief"
                conffile = "./getportfree/%s.txt"%(self.ip)
                conffilehandle = open(conffile,'w')
		self.pexpect1.sendline("dis interface brief")
		while 1:
			backUserData1 = self.pexpect1.expect(self.expectData1)
			#print self.pexpect1.before
			conffilehandle.write(self.pexpect1.before)
			conffilehandle.write(self.pexpect1.after)
			if backUserData1 == 2:
				#print "END"
				conffilehandle.close()
				self.cleanfile(conffile)
				self.cleanfilemore(conffile)
				self.formatfile(conffile)
				self.findportfree(conffile)
				return 1
			elif backUserData1 == 4:
				self.pexpect1.sendline(" ")
			else:
				print "Error"

	def findportfree(self,filename):
	        number = 0
	        file = filename
	        for line in open(file):
	                lineparts = re.findall(r"([\(\)\#\`\=\&\"\!\^$\w\.\/\-]+)+",line)
	                #print lineparts
	                if len(lineparts):
	                        portinfo = re.findall('^(Ethernet0\/0\/)(\d+) +([updown]+)',line)
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
			result = re.findall(r"Software Version (\S+)",self.pexpect1.before)
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
	
