# coding=utf-8

# system module for resolving command line arguments, etc
import  sys
reload(sys)
sys.setdefaultencoding("utf-8")
# operating system module for opening files, etc
import  os
# trace back for exception processing and debugging
import  traceback
# logging configuration
import  logging
logging.basicConfig(format="%(levelname)-9s[%(asctime)s][%(filename)s:%(funcName)s:%(lineno)d] %(message)s \\EOF", level=logging.WARNING);
# string processing
import  string
# time processing and thread sleeping
import  time
try:
    import  schedule
except:
    logging.fatal('No schedule module installed. Try "pip install schedule" first.')
# http request
import  urllib
import  urllib2
import  httplib
import  cookielib
# json codec
import  json
# regress expression
import  re
# qrcode generation, requires installation
# furthermore, for generated images, PIL or Pillow is required
try:
    import  qrcode
except:
    logging.fatal('No qrcode module installed. Try "pip install qrcode" first.')
try:
    import  PIL
    from    PIL import  Image
except:
    logging.warning('No PIL module installed, QRCode will be displayed in the tty mode. Try "pip install PIL/pillow" to solve this problem.')
# xml module for xml file parsing
import  xml.dom.minidom
# random module for generating random strings
import  random
# thread module for multi-thread message recieving and sending
import  threading

def _conv_list(data):

    retVal = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _conv_list(item)
        elif isinstance(item, dict):
            item = _conv_dict(item)
        retVal.append(item)

    return  retVal

def _conv_dict(data):

    retVal = {}
    for key, val in data.iteritems():
            
        if isinstance(key, unicode):
            key = key.encode('utf-8')
            
        if isinstance(val, unicode):
            val = val.encode('utf-8')
        elif isinstance(val, list):
            val = _conv_list(val)
        elif isinstance(val, dict):
            val = _conv_dict(val)
            
        retVal[key] = val

    return  retVal

class WechatBot(object):

    def __init__(self):

        self._conf = {
                "AppID"             : "wx782c26e4c19acffb",
                "Lang"              : "zh_CN",
                "DeviceID"          : "e" + repr(random.random())[2 : 17],
                "MessageSyncInterval"   : 1,
                "LogLevel"          : logging.INFO,
                "EventConfFile"     : "",
            }
        self._uuid  = ""
        self._uri   = ""
        self._syncHost = ""
        self._passTicket    =   ""
        self._baseRequest   =   {
                "Uin"   :   "",
                "Sid"   :   "",
                "Skey"  :   "",
                "DeviceID"  :   "",
            }
        self._SyncKey   = []
        self._synckey   = ""
        self._User  = []
        self._ContactList = []
        self._GroupList = []
        self._NonContactList = []

        self._isRunning =   False
        self._cookie = cookielib.CookieJar()
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor(self._cookie)))
        
        self._logger = logging.Logger("WechatBot")
        loghandler = logging.StreamHandler()
        loghandler.setFormatter(logging.Formatter("%(levelname)-9s[%(asctime)s][%(filename)s:%(funcName)s:%(lineno)d] %(message)s \\EOF"))
        self._logger.setLevel(self._conf["LogLevel"])
        self._logger.addHandler(loghandler)

        self._logger.debug("WechatBot inited.")

        return

    def __del__(self):

        self._logger.debug("WechatBot deleted.")

        return
    
    def __str__(self):

        wechatbotStr = "\n" + \
            "==========WechatBot==========\n" + \
            "Configuration  :   " + self._conf.__str__() + "\n" + \
            "-----------------------------\n" + \
            "UUID           :   " + self._uuid + "\n" + \
            "URI            :   " + self._uri + "\n" + \
            "Sync Host      :   " + self._syncHost + "\n" + \
            "Pass Ticket    :   " + self._passTicket + "\n" + \
            "Base Request   :   " + self._baseRequest.__str__() + "\n" + \
            "SyncKey        :   " + self._SyncKey.__str__() + "\n" + \
            "synckey        :   " + self._synckey + "\n" + \
            "User           :   " + self._User.__str__() + "\n" + \
            "Contacts       :   " + len(self._ContactList).__str__() + " contacts. " + self._ContactList.__str__() + "\n" + \
            "Groups         :   " + len(self._GroupList).__str__() + " groups. " + self._GroupList.__str__() + "\n" + \
            "Non-contacts   :   " + len(self._NonContactList).__str__() + " non-contact users. " + self._NonContactList.__str__() + "\n" + \
            "=============================\n"

        return  wechatbotStr

    def run(self, conf = {}):

        # process configuration
        for key in conf.keys():
            if (self._conf.has_key(key)):
                self._conf[key] = conf[key]
            else:
                self._logger.warning("Invalid configuration: (%s : %s), ignored.", key, conf[key])

        # get UUID
        if not self._getUUID():
            self._logger.error("Failed to get UUID.")
            return  False

        # get QRCode
        if not self._getQRCode():
            self._logger.error("Failed to generate QRCode.")
            return  False
        else:
            self._logger.info("Please scan the QRCode to login.")

        # login
        if not self._login():
            self._logger.error("Failed to login.")
            return  False
        else:
            self._logger.debug("Login successfully.")

        # initialize Wechat and regist status notification
        if not self._initWechat():
            self._logger.error("Failed to initialize Wechat.")
            return  False
        else:
            self._logger.debug("Initialize successfully.")

        # get contacts and groups
        if not self._getContacts():
            self._logger.error("Failed to get contact and group information.")
            return  False

        # print wechat information
        self._logger.info("WechatBot started successfully. %s", self.__str__())

        # handle input and process message
        self._isRunning = True

        try:

            recvThread = threading.Thread(target = self._recvMsg)
            recvThread.setDaemon(True)
            recvThread.start()
            scheThread = threading.Thread(target = self._scheMsg)
            scheThread.setDaemon(True)
            scheThread.start()

            while self._isRunning:

                try:
                    cmd = raw_input("Press h for help, q to quit:\n")
    
                    if "q" == cmd:
                        self._isRunning = False
                    elif "h" == cmd:
                        self.help()
                    elif "si" == cmd:
                        id = raw_input("Please input target ID, enter to confirm:")
                        content = raw_input("Please input message text, enter to send:")
                        self.sendMsgTextByID(id, content)
                    elif "sn" == cmd:
                        id = raw_input("Please input target name, enter to confirm:")
                        content = raw_input("Please input message text, enter to send:")
                        self.sendMsgTextByName(id, content)
                    else:
                        self._logger.warning("Unknown command %s, ignored.", cmd)
                except EOFError, e:
                    time.sleep(1)
                except Exception:
                    self._logger.error("Unexpected exception: %s", traceback.format_exc())
                    time.sleep(1)

            scheThread.join()
            recvThread.join()

        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())
            return  False

        # print wechat information
        self._logger.info("WechatBot exited successfully. %s", self.__str__())

        return  True

    def help(self):

        self._logger.critical(
"""
==========WechatBot==========
Help information:
q   :   quit
h   :   print this help information
si  :   send text message by ID
sn  :   send text message by name
============================="""
            )

        return
    
    def getGrpNameByID(self, id):

        for group in self._GroupList:
            if id == group["UserName"]:
                if "" == group["NickName"]:
                    return  "Group Chat (" + len(group["MemberList"]).__str__() + ") " + id[2:10]
                else:
                    return  group["NickName"]

        for group in self._getContactsBatch([id]):
            self._GroupList.append(group)
            if id == group["UserName"]:
                if "" == group["NickName"]:
                    return  "Group Chat (" + len(group["MemberList"]).__str__() + ") " + id[2:10]
                else:
                    return  group["NickName"]

        return  "Unknown"

    def getUsrNameByID(self, id):
        
        if id == self._User["UserName"]:
            return  self._User["NickName"]

        for user in self._ContactList:
            if id == user["UserName"]:
                if user["RemarkName"]:
                    return  user["RemarkName"]
                else:
                    return  user["NickName"]

        for user in self._NonContactList:
            if id == user["UserName"]:
                if user["RemarkName"]:
                    return  user["RemarkName"]
                else:
                    return  user["NickName"]

        for group in self._GroupList:
            for user in group["MemberList"]:
                if id == user["UserName"]:
                    if user["DisplayName"]:
                        return  user["DisplayName"]
                    else:
                        return  user["NickName"]

        self._logger.warning("Unknown user id %s", id)
        return  "Unknown"

    def getIDByName(self, name):

        for user in self._ContactList:
            if name == user["RemarkName"] or name == user["NickName"]:
                return  user["UserName"]

        for user in self._NonContactList:
            if name == user["RemarkName"] or name == user["NickName"]:
                return  user["UserName"]

        for group in self._GroupList:
            if name == group["NickName"]:
                return  group["UserName"]

        return  "No ID: " + name    

    def sendMsgTextByID(self, id, content):

        clientMsgID = str(int(time.time() * 1000)) + str(random.random())[:5].replace(".", "")
        url = self._uri + "/webwxsendmsg?pass_ticket=%s" % (self._passTicket)
        prm = {
                "BaseRequest"   : self._baseRequest,
                "Msg"           : {
                        "Type"  : 1,
                        "Content"   : content,
                        "FromUserName"  : self._User["UserName"],
                        "ToUserName"    : id,
                        "LocalID"   : clientMsgID,
                        "ClientMsgId"   : clientMsgID,
                    }
            }

        data = self._post(url, prm)

        try:
            if 0 == data["BaseResponse"]["Ret"]:
                if "@@" == id[:2]:
                    grpName = self.getGrpNameByID(id)
                    self._logger.info("Sent a message in group [%s]:\n%s", grpName, content)
                elif "@" == id[:1]:
                    usrName = self.getUsrNameByID(id)
                    self._logger.info("Sent a message to [%s]:\n%s", usrName, content)
                else:
                    self._logger.info("Sent a message to ID[%s]:\n%s", id, content)

                return  True

            else:
                self._logger.warning("Failed to send a message to ID[%s]:\n%s", id, content)
    
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())
        
        return  False

    def sendMsgTextByName(self, name, content):

        return  self.sendMsgTextByID(self.getIDByName(name), content)

    def procMsgText(self, grpName, usrName, content, msg):

        # an example
        """
        if usrName != self._User["NickName"]:
            if "" != grpName:
                self.sendMsgTextByName(grpName, "At " + str(time.asctime(time.localtime(time.time()))) + ", " + usrName + " says : " + content)
            else:
                self.sendMsgTextByName(usrName, "[" + str(time.asctime(time.localtime(time.time()))) + "][Auto reply]您的消息我已收到。")
        """
        return

    def procMsgImage(self, grpName, usrName, content, msg):

        return

    def procMsgVoice(self, grpName, usrName, content, msg):

        return

    def procMsgCard(self, grpName, usrName, content, msg):

        return

    def procMsgEmoji(self, grpName, usrName, content, msg):

        return

    def procMsgAppLink(self, grpName, usrName, content, msg):

        return

    def procMsgVideo(self, grpName, usrName, content, msg):

        return

    def procMsgRecall(self, grpName, usrName, content, msg):

        return
    
    def scheJob(self):

        # an example
        """
        (t_year, t_month, t_day, t_hour, t_minute, t_second, t_weekday, t_yearday, t_isdst) = time.localtime(time.time())

        # embeded events
        if 8 == t_hour and 0 == t_minute:
            self.sendMsgTextByID("filehelper", "[" + time.asctime(time.localtime(time.time())).__str__() + "]" + "08:00 定时消息")
        elif 23 == t_hour and 0 == t_minute:
            self.sendMsgTextByID("filehelper", "[" + time.asctime(time.localtime(time.time())).__str__() + "]" + "23:00 定时消息")

        # events from configure file
        # event configure file is organized as the following format (json):
        #   {
        #       "Events":
        #       [
        #
        #           {
        #               "MsgType"       : 1,
        #               "TargetID"      : "filehelper",
        #               "MsgContent"    : "A scheduled message (every hour).",
        #               "Year"          : -1,
        #               "Month"         : -1,
        #               "Day"           : -1,
        #               "Hour"          : -1,
        #               "Minute"        : 0,
        #               "Weekday"       : -1,
        #               "Yearday"       : -1
        #           }
        #       ]
        #   }
        # 
        if "" != self._conf["EventConfFile"]:
            try:
                file = open(self._conf["EventConfFile"], "r")
                data = json.loads(file.read(), object_hook = wechatbot._conv_dict)
                file.close()
                for event in data["Events"]:
                    if (-1 == event["Year"] or t_year == event["Year"]) \
                        and (-1 == event["Month"] or t_month == event["Month"]) \
                        and (-1 == event["Day"] or t_day == event["Day"]) \
                        and (-1 == event["Hour"] or t_hour == event["Hour"]) \
                        and (-1 == event["Minute"] or t_minute == event["Minute"]) \
                        and (-1 == event["Weekday"] or t_weekday == event["Weekday"]) \
                        and (-1 == event["Yearday"] or t_yearday == event["Yearday"]):
                        if 1 == event["MsgType"]:
                            self.sendMsgTextByID(event["TargetID"], event["MsgContent"])
                        else:
                            self._logger.warning("Unsupported message type %d.", event["MsgType"])
            except Exception:
                self._logger.error("Unexpected exception: %s", traceback.format_exc())
        """
        return    

    def _post(self, url, prm, jsonFmt = True):

        try:
            if jsonFmt:
                request = urllib2.Request(url = url, data = json.dumps(prm, ensure_ascii = False).encode("utf8"))
                request.add_header("ContentType", "application/json; charset=UTF-8")
            else:
                request = urllib2.Request(url = url, data = urllib.urlencode(prm))

            response = urllib2.urlopen(request)
            data = response.read()
            if jsonFmt:
                data = json.loads(data, object_hook = _conv_dict)

            self._logger.debug(data.__str__())
            return  data
        except urllib2.HTTPError, e:
            self._logger.error("HTTPError: %s", e.code.__str__())
        except urllib2.URLError, e:
            self._logger.error("URLError: %s", e.reason.__str__())
        except httplib.HTTPException, e:
            self._logger.error("HTTPException: %s", e.__str__())
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())

        return  ""

    def _get(self, url, type = None):

        request = urllib2.Request(url = url)
        request.add_header("Referer", r"https://wx.qq.com/")
        if "webwxgetvoice" == type:
            request.add_header("Range", "bytes=0-")
        elif "webwxgetvideo" == type:
            request.add_header("Range", "bytes=0-")
        else:
            pass

        try:
            response = urllib2.urlopen(request)
            data = response.read()
            self._logger.debug(data.__str__())
            return  data
        except urllib2.HTTPError, e:
            self._logger.error("HTTPError: %s", e.code.__str__())
        except urllib2.URLError, e:
            self._logger.error("URLError: %s", e.reason.__str__())
        except httplib.HTTPException, e:
            self._logger.error("HTTPException: %s", e.__str__())
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())

        return  ""

    def _getUUID(self):
        
        self._uuid = ""

        url = r"https://login.weixin.qq.com/jslogin"
        prm = {
                "appid" : self._conf["AppID"],
                "fun"   : "new",
                "lang"  : self._conf["Lang"],
                "_"     : int(time.time()),
            }
        data = re.search(r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"', self._post(url, prm, False))

        if data:
            if "200" == data.group(1):
                self._uuid = data.group(2)
                return  True

        return  False

    def _getQRCode(self):

        url = r"https://login.weixin.qq.com/l/"
            
        qr = qrcode.QRCode(border = 1)
        qr.add_data(url + self._uuid)
        qr.make()
        try:
            img = qr.make_image()
            img.show()
            return  True
        except Exception:
            self._logger.debug("Failed to display qrcode image due to exception: %s \nTrying to display qrcode in tty mode.", traceback.format_exc())
            try:
                qr.print_ascii(invert = True)
                return  True
            except Exception:
                self._logger.error("Unexpected exception: %s", traceback.format_exc())

        return  False

    def _login(self):

        redirect_uri = ""
        
        stat = "-1"
        url = "https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s" % (0, self._uuid, int(time.time()))
        while "" == redirect_uri:
            info = self._get(url)
            data = re.search(r"window.code=(\d+);", info)
            if data:
                stat = data.group(1)
                if "200" == stat:
                    data = re.search(r'window.redirect_uri="(\S+?)";', info)
                    if data:
                        redirect_uri = data.group(1) + "&fun=new"
                        self._uri = redirect_uri[:redirect_uri.rfind("/")]
                    else:
                        self._logger.error("Failed to parse redirect uri from data %s.", info)
                        break;
                elif "201" == stat:
                    self._logger.info("Please confirm login on your cellphone.")
                elif "408" == stat:
                    self._logger.error("Login timeout.")
                    break
                else:
                    self._logger.error("Login error with error code %s.", stat)
                    break;
            time.sleep(1)
        else:
            data = self._get(redirect_uri)
            if "" != data:
                doc = xml.dom.minidom.parseString(data)
                root = doc.documentElement
                for node in root.childNodes:
                    if "skey" == node.nodeName:
                        self._baseRequest["Skey"] = node.childNodes[0].data
                    elif "wxsid" == node.nodeName:
                        self._baseRequest["Sid"] = node.childNodes[0].data
                    elif "wxuin" == node.nodeName:
                        self._baseRequest["Uin"] = int(node.childNodes[0].data)
                    elif "pass_ticket" == node.nodeName:
                        self._passTicket = node.childNodes[0].data
                self._baseRequest["DeviceID"] = self._conf["DeviceID"]

                if ("" not in self._baseRequest.values()) and ("" != self._passTicket):
                    return  True

        return  False

    def _initWechat(self):

        url = self._uri + "/webwxinit?pass_ticket=%s&skey=%s&r=%s" % (self._passTicket, self._baseRequest["Skey"], int(time.time()))
        prm = {
                "BaseRequest"   :   self._baseRequest,
            }
        data = self._post(url, prm)

        try:
            self._SyncKey = data["SyncKey"]
            self._synckey = "|".join([str(keyVal["Key"]) + "_" + str(keyVal["Val"]) for keyVal in self._SyncKey["List"]])
            self._User = data["User"]

            # regist status notification
            if 0 == data["BaseResponse"]["Ret"]:
                url = self._uri + "/webwxstatusnotify?lang=%s&pass_ticket=%s" % (self._conf["Lang"], self._passTicket)
                prm = {
                        "BaseRequest"   : self._baseRequest,
                        "Code"          : 3,
                        "FromUserName"  : self._User["UserName"],
                        "ToUserName"    : self._User["UserName"],
                        "ClientMsgId"   : int(time.time()),
                    }
                data = self._post(url, prm)

                return  0 == data["BaseResponse"]["Ret"]
                
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())

        return  False
    
    def _getContacts(self):

        url = self._uri + "/webwxgetcontact?pass_ticket=%s&r=%s" % (self._passTicket, int(time.time()))
        prm = {
                "BaseRequest"   : self._baseRequest,
            }
        data = self._post(url, prm)

        try:
            if data["MemberCount"] != len(data["MemberList"]):
                self._logger.warning("MemberCount %d and MemberList length %d not equal.", (data["MemberCount"], len(data["MemberList"])))
            for contact in data["MemberList"]:
                # Public/Service Account
                if contact["VerifyFlag"] & 0x08 != 0:
                    self._NonContactList.append(contact)
                # Group
                elif "@@" == contact["UserName"][:2]:
                    self._GroupList.append(contact)
                # Self
                elif contact["UserName"] == self._User["UserName"]:
                    pass
                # Contact
                else:
                    self._ContactList.append(contact)
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())
            return  False

        if len(self._GroupList) > 0:

            url = self._uri + "/webwxbatchgetcontact?type=ex&pass_ticket=%s&r=%s" % (self._passTicket, int(time.time()))
            prm = {
                    "BaseRequest"   : self._baseRequest,
                    "Count"         : len(self._GroupList),
                    "List"          : [{"UserName" : group["UserName"], "EncryChatRoomId" : ""} for group in self._GroupList]
                }
            data = self._post(url, prm)

            try:
                self._GroupList = data["ContactList"]
            except Exception:
                self._logger.error("Unexpected exception: %s", traceback.format_exc())
                return  False

        return  True

    def _getContactsBatch(self, idList):

        url = self._uri + "/webwxbatchgetcontact?type=ex&pass_ticket=%s&r=%s" % (self._passTicket, int(time.time()))
        prm = {
                "BaseRequest"   : self._baseRequest,
                "Count"         : len(idList),
                "List"          : [{"UserName" : item, "EncryChatRoomId" : ""} for item in idList]
            }
        data = self._post(url, prm)

        try:
            return  data["ContactList"]
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())
            return  None

    def _syncCheck(self):

        if "" == self._syncHost:

            syncHostList = [
                    "https://webpush.wx.qq.com",
                ]

            for host in syncHostList:
                self._syncHost = host
                [ret, sel] = self._syncCheck()
                if "0" == ret:
                    return  [ret, sel]

            self._logger.error("No available sync host found.")
            self._syncHost = ""
            return  [-1, -1]

        else:
            prm = {
                    "r"     : int(time.time()),
                    "sid"   : self._baseRequest["Sid"],
                    "uin"   : self._baseRequest["Uin"].__str__(),
                    "skey"  : self._baseRequest["Skey"],
                    "deviceid"  : self._baseRequest["DeviceID"],
                    "synckey"   : self._synckey,
                    "_"     : int(time.time()),
                }
            url = self._syncHost + "/cgi-bin/mmwebwx-bin/synccheck?" + urllib.urlencode(prm)
            data = self._get(url)

            if "" != data:
                try:
                    data = re.search(r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', data)
                    return  [data.group(1), data.group(2)]
                except Exception:
                    self._logger.warning("Unexpected exception while checking url %s : %s", url, traceback.format_exc())
            
            self._syncHost = ""
            return  [-1, -1]
            
    def _sync(self):

        url = self._uri + "/webwxsync?pass_ticket=%s" % (self._passTicket)
        prm = {
                "BaseRequest"   : self._baseRequest,
                "SyncKey"       : self._SyncKey,
                "rr"            : ~int(time.time())
            }
        data = self._post(url, prm)

        try:
            if 0 == data["BaseResponse"]["Ret"]:
                self._SyncKey = data["SyncKey"]
                self._synckey = "|".join([str(keyVal["Key"]) + "_" + str(keyVal["Val"])for keyVal in self._SyncKey["List"]])
            
            return  data
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())
            return  None    

    def _procMsg(self, data):

        try:
            for msg in data["AddMsgList"]:

                msgType = msg["MsgType"]
                # process message content
                msg["Content"] = msg["Content"].replace("&lt;", "<").replace("&gt;", ">")
                # check group message
                grpName = ""
                usrName = ""
                content = ""
                if "@@" == msg["FromUserName"][:2]:
                    grpName = self.getGrpNameByID(msg["FromUserName"])
                    if "@" == msg["Content"][:1]:
                        usrName = self.getUsrNameByID(msg["Content"][:msg["Content"].find(":")])
                        content = msg["Content"][(msg["Content"].find(":") + 6) :]
                    else:
                        content = msg["Content"]
                elif "@@" == msg["ToUserName"][:2]:
                    grpName = self.getGrpNameByID(msg["ToUserName"])
                    usrName = self.getUsrNameByID(msg["FromUserName"])
                    if "@" == msg["Content"][:1]:
                        content = msg["Content"][(msg["Content"].find(":") + 6) :]
                    else:
                        content = msg["Content"]
                else:
                    usrName = self.getUsrNameByID(msg["FromUserName"])
                    content = msg["Content"]

                # standard text message
                if 1 == msgType:
                    if "" == grpName:
                        self._logger.info("Received a message from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received a message in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgText(grpName, usrName, content, msg)
                # image message
                elif 3 == msgType:
                    if "" == grpName:
                        self._logger.info("Received an image from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received an image in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgImage(grpName, usrName, content, msg)
                # voice message
                elif 34 == msgType:
                    if "" == grpName:
                        self._logger.info("Received a voice message from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received a voice message in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgVoice(grpName, usrName, content, msg)
                # card message
                elif 42 == msgType:
                    if "" == grpName:
                        self._logger.info("Received a card message from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received a card message in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgCard(grpName, usrName, content, msg)
                # emoji message
                elif 47 == msgType:
                    if "" == grpName:
                        self._logger.info("Received an emoji from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received an emoji in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgEmoji(grpName, usrName, content, msg)
                # shared app link message
                elif 49 == msgType:
                    if "" == grpName:
                        self._logger.info("Received an app link message from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received an app link message in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgAppLink(grpName, usrName, content, msg)
                # contact information update
                elif 51 == msgType:
                    # content organized in xml format as the following (<br/> are removed)
                    """
                    <msg>
	                    <op id="4">
		                    <username>filehelper,...,weixin</username>
		                    <unreadchatlist></unreadchatlist>
		                    <unreadfunctionlist>
			                </unreadfunctionlist>
	                    </op>
                    </msg>
                    """
                    # doc = xml.dom.minidom.parseString(content)
                    # self._logger.info(doc.toprettyxml())
                    pass
                # video message
                elif 62 == msgType:
                    if "" == grpName:
                        self._logger.info("Received a video message from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received a video message in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgVideo(grpName, usrName, content, msg)
                # group rename
                elif 10000 == msgType:
                    self._logger.info("Group name change in group ID[%s]: %s", msg["FromUserName"], content)
                # recall message
                elif 10002 == msgType:
                    if "" == grpName:
                        self._logger.info("Received a message recall from [%s] :\n%s", usrName, content)
                    else:
                        self._logger.info("Received a message recall in group [%s] from [%s] :\n%s", grpName, usrName, content)
                    self.procMsgRecall(grpName, usrName, content, msg)
                # unknown message type
                else:
                    if "" == grpName:
                        self._logger.warning("Received a message from [%s] of unknown type %d.", usrName, msgType)
                    else:
                        self._logger.warning("Received a message in group [%s] from [%s] of unknown type %d", grpName, usrName, msgType)

        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())

        return    

    def _recvMsg(self):

        while self._isRunning:

            lastCheckTime = time.time()

            [ret, sel] = self._syncCheck()
            if "1100" == ret:
                self._logger.info("Logout on the cellphone. The WechatBot is forced to quit.")
                self._isRunning = False
            elif "1101" == ret:
                self._logger.info("Wechat (web) login at other place. The WechatBot is forced to quit.")
                self._isRunning = False
            elif "0" == ret:
                if "0" == sel:
                    pass
                elif "2" == sel:
                    self._logger.debug("Message received.")
                    data = self._sync()
                    self._procMsg(data)
                elif "7" == sel:
                    self._logger.debug("Activity using cellphone detected.")
                    data = self._sync()
                    self._procMsg(data)
                else:
                    self._logger.warning("Unknown selector code: %s. Ignored.", sel)
            else:
                self._logger.warning("Unknown return code pair: %s, %s. Ignored.", ret, sel)

            if time.time() - lastCheckTime <= self._conf["MessageSyncInterval"]:
                time.sleep(self._conf["MessageSyncInterval"] - (time.time() - lastCheckTime))

        return

    def _scheMsg(self):

        try:
            schedule.every().minute.do(self.scheJob)
            while self._isRunning:
                schedule.run_pending()
                time.sleep(1)
        except Exception:
            self._logger.error("Unexpected exception: %s", traceback.format_exc())

        return    
