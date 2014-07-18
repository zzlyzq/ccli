import re
import pexpect
import tempfile
import shutil
import time
import os

class dell3548:
	def __init__(self,ip,username,password):
		self.ip = ip 
		self.username = username
		self.password = password
		self.timewait = 10
		self.expectData1 = [ 'User Name:.*', 'Password:.*', '[^n]> .*', 'asdfasdfasdf', 'One line: <return>.*','[^n]# .*','34234sdfsdf','asdfasdf234sdf','pexpect.EOF', 'pexect.TIMEOUT.' ]
		self.pexpect1 = pexpect.spawn("telnet %s"%(self.ip),timeout=self.timewait)

	def conn(self):
		#print "START CONN"
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
						#print backData5
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
		resultfile = self.exe(type,cmd)

	def getportfree(self):
		print "START GET PORT FREE"
		type = "getportfree"
		cmd = "show interface status"
#		resultfile = self.exe(type, cmd)
		resultfile = "./getportfree/172.22.3.227.txt"
		number = 0
		for line in open(resultfile):
			lineparts = re.findall("(\S+)+",line)
			#print lineparts
			if len(lineparts) == 9:
				#print lineparts
				if len(re.findall("e\d+", lineparts[0])) == 1:
					if lineparts[6] != "Up":
						number += 1
		print self.ip, "PORT ETA :", number
		return number
	
	def getversion(self):
		print "START TO GET VERSION"
		type = "getversion"
		cmd = "show version"
		#resultfile = self.exe(type, cmd)
		resultfile = "./getversion/172.22.3.227.txt"
		for line in open(resultfile):
			result = re.findall("SW *version *(\S+)", line)
			#print result
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
		#resultfile = "./getmaclist/172.22.3.227.txt"
		for line in open(resultfile):
			lineparts = re.findall("(\S+)+", line)	
			if len(lineparts) == 4:
				portindex = re.findall("^e(\d+)", lineparts[2])
				if len(portindex) == 1:
					if int(portindex[0]) <= 47:
						print lineparts[1], lineparts[0], self.ip, lineparts[2]
					else:
						pass
				else:
					pass
			else:
				pass
			
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
                                recvdata +=self.pexpect1.before
                                recvdata +=self.pexpect1.after
                                self.pexpect1.sendline("")
                        else:
                                print "Error A"
                                return 0
                resultfile = "./%s/%s.txt"%(type,self.ip)
                resultfilehandle = open(resultfile,'w')
                resultfilehandle.write(recvdata)
                resultfilehandle.close()
                self.cleanfile(resultfile)
                self.cleanfilemore(resultfile)
                self.formatfile(resultfile)
                print self.ip, "SAVED TO ", resultfile
		return resultfile

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
                        result = re.findall(r"\x1b\x5b\x30\x6d",line)
                        if len(result) != 0:
                                line2 = line.replace('\x1b\x5b\x30\x6d',"")
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
                        result = re.findall(r"More: <space>,  Quit: q, One line: <return>",line)
                        if len(result) != 0:
                                line2 = line.replace('More: <space>,  Quit: q, One line: <return>',"")
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
	
