# coding=utf-8

# system module for resolving command line arguments, etc
import  sys
reload(sys)
sys.setdefaultencoding("utf-8")
# trace back for exception processing and debugging
import  traceback
# logging configuration
import  logging
logging.basicConfig(format="%(levelname)-9s[%(asctime)s][%(filename)s:%(funcName)s:%(lineno)d] %(message)s \\EOF", level=logging.WARNING);
# json codec
import  json
# time processing and thread sleeping
import  time
# random module for generating random strings
import  random

# wechatbot
import  wechatbot

class WechatBotDemo(wechatbot.WechatBot):

    """
    Supported public functions:

        run(conf)           : start the wechatbot with configuration conf (dict)
        
        help()              : print help information
        
        getGrpNameByID(id)  : obtain a group's nickname by its ID (a.k.a. UserName, string)
        getUsrNameByID(id)  : obtain a contact's remark name (if valid) or nickname by its ID (a.k.a. UserName, string)
        getIDByName(id)     : obtain a group/contact's ID by its remark name (contact only) or nickname

        sendMsgTextByID(id, content)        : send a plain text message content to the group/contact with ID id
        sendMsgTextByName(name, content)    : send a plain text message content to the group/contact with remark name or nickname name

        procMsgText(self, grpName, usrName, content, msg)   : process a plain text message content, sent by user usrName, in group grpName (if not empty); original message is provided in msg
        procMsgImage(self, grpName, usrName, content, msg)  : process an image content, sent by user usrName, in group grpName (if not empty); original message is provided in msg
        procMsgVoice(self, grpName, usrName, content, msg)  : process a voice message content, sent by user usrName, in group grpName (if not empty); original message is provided in msg
        procMsgCard(self, grpName, usrName, content, msg)   : process a card message content, sent by user usrName, in group grpName (if not empty); original message is provided in msg
        procMsgEmoji(self, grpName, usrName, content, msg)  : process an emoji content, sent by user usrName, in group grpName (if not empty); original message is provided in msg
        procMsgAppLink(self, grpName, usrName, content, msg)    : process an app link message content, sent by user usrName, in group grpName (if not empty); original message is provided in msg
        procMsgVideo(self, grpName, usrName, content, msg)  : process a video message content, sent by user usrName, in group grpName (if not empty); original message is provided in msg
        procMsgRecall(self, grpName, usrName, content, msg) : process a message recalled content, sent by user usrName, in group grpName (if not empty); original message is provided in msg

        scheJob(self)       : check pending jobs per minute and execute them
    """

    # override processing function
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

    # override processing function
    def procMsgImage(self, grpName, usrName, content, msg):

        return

    # override processing function
    def procMsgVoice(self, grpName, usrName, content, msg):

        return

    # override processing function
    def procMsgCard(self, grpName, usrName, content, msg):

        return

    # override processing function
    def procMsgEmoji(self, grpName, usrName, content, msg):

        return

    # override processing function
    def procMsgAppLink(self, grpName, usrName, content, msg):

        return

    # override processing function
    def procMsgVideo(self, grpName, usrName, content, msg):

        return

    # override processing function
    def procMsgRecall(self, grpName, usrName, content, msg):

        return

    # override scheduling function
    def scheJob(self):

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
                self._logger.error("Unexpected expection: %s", traceback.format_exc())

        return
        
def main():

    # default configuration
    conf = {
            #"AppID"             : "wx782c26e4c19acffb",
            #"Lang"              : "zh_CN",
            #"DeviceID"          : "e" + repr(random.random())[2 : 17],
            #"MessageSyncInterval"   : 1,
            #"LogLevel"          : logging.INFO,
            "EventConfFile"     : "sampleEvents.conf",
        }

    # configuration in command line arguments
    for i in range(1, len(sys.argv)):
        logging.debug("Argument : %s", sys.argv[i])
        arg = string.split(sys.argv[i], "=", 1)
        if 1 == len(arg):
            conf[arg[0]] = True
        else:
            conf[arg[0]] = arg[1]
    
    # wechat bot
    wbot = WechatBotDemo()
    wbot.run(conf)

    return
    
if __name__ == "__main__" :

    main()
