import re
import pexpect
import tempfile
import shutil
import time
import os

class s16:
	def __init__(self,ip,username,password):
		self.ip = ip 
		self.username = username
		self.password = password
		self.timewait = 10
		self.expectData1 = [ 'sername.*', 'assword:.*', '\<[\w\-]+\>.*','\[[\w\-]+\].*','---- More ----.*','closed.*','ENTER.*','asdfasdf234sdf','pexpect.EOF', 'pexect.TIMEOUT.' ]
		self.pexpect1 = pexpect.spawn("telnet %s"%(self.ip),timeout=self.timewait)

	def conn(self):
		#print "START CONN"
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
		self.exe(type,cmd)

        def getversion(self):
                self.pexpect1.send("display version\r")
                backUserData1 = self.pexpect1.expect(self.expectData1)
                if backUserData1 == 2:
                        result = re.findall(r"(S1650 Product Version \S+)",self.pexpect1.before)
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
                #print "START GET MAC LIST"
                type = "getmaclist"
                cmd = "display mac-address"
                resultfile = self.exe(type,cmd)
                # resultfile = "./getmaclist/172.20.3.201.txt"
                for line in open(resultfile):
                        lineparts = re.findall("(\S+)+",line)
                        #print lineparts
                        if len(lineparts) == 5:
                                portindex = re.findall("(Ethernet0\/)(\d+)",lineparts[3])
                                #print "AAA", portindex
                                if len(portindex) == 1:
                                        if len(portindex[0]) == 2:
                                                #print portindex
                                                if int(portindex[0][1]) <= 48:
                                                        print lineparts[0],lineparts[1], self.ip, lineparts[3]
                                                else:
                                                        pass
                                        else:
                                                pass
                                else:
                                        pass
                        else:
                                pass

        def exe(self, type, cmd):
                recvdata = ""
                self.pexpect1.send("%s\r"%cmd)
                while 1:
                        backUserData1 = self.pexpect1.expect(self.expectData1)
                        if backUserData1 == 2:
                                recvdata += self.pexpect1.before
                                recvdata += self.pexpect1.after
                                break
                        elif backUserData1 == 4:
                                recvdata +=self.pexpect1.before
                                recvdata +=self.pexpect1.after
                                self.pexpect1.send("\r")
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

	def getportfree(self):
		print "START GET PORT FREE"
		# "dis interface brief"
		#print "s16 GE1/0/1 - GE1/0/48 PORT STATUS"
		number = 0
		for portid in range(1,50+1):
			#print "PORTID", portid
			recvdata = ""
			self.pexpect1.send("dis interface ethernet0/%d\r"%portid)
			while 1:
				backUserData1 = self.pexpect1.expect(self.expectData1)
				#print backUserData1
				if backUserData1 == 2:
					recvdata += self.pexpect1.before
					break
				elif backUserData1 == 4:
					recvdata += self.pexpect1.before
					self.pexpect1.send(" ")
				else:
					print "ErrorA"
					return 0
			#print recvdata
			#print "ENT THIS PORT"
			result = re.findall(r"current state: *(\S+)",recvdata)
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
	                                if int(portpart2) <= 48:
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
                        result = re.findall(r"\x0d\x0d",line)
                        if len(result) != 0:
                                line2 = line.replace('\x0d\x0d',"")
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
                        result = re.findall(r"---- More ----\x00\x0d\x1b\x5b\x4d",line)
                        if len(result) != 0:
                                line2 = line.replace('---- More ----\x00\x0d\x1b\x5b\x4d',"")
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
		self.pexpect1.send("quit\r")
		backUserData1 = self.pexpect1.expect(self.expectData1)
		#print "AAAA",backUserData1,"AAAA"
	

username = "admin"
password = "admin"
#username = "yourusername"
#password = "yourpassword"

ip = "172.22.3.171"
test = s16(ip,username,password)
test.conn()
#test.getconfig()
#test.getportfree()
#test.getmaclist()
test.getversion()
test.quit()
