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

        procMsgText(self, grpName, ufrName, utoName, content, msg)   : process a plain text message content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
        procMsgImage(self, grpName, ufrName, utoName, msg)  : process an image, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
        procMsgVoice(self, grpName, ufrName, utoName, msg)  : process a voice message, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
        procMsgCard(self, grpName, ufrName, utoName, msg)   : process a card message, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
        procMsgEmoji(self, grpName, ufrName, utoName, msg)  : process an emoji, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
        procMsgAppLink(self, grpName, ufrName, utoName, content, msg)    : process an app link message content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
        procMsgVideo(self, grpName, ufrName, utoName, msg)  : process a video message, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
        procMsgGroupRename(self, grpName, ufrName, utoName, content, msg)    : process a group rename message content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
        procMsgRecall(self, grpName, ufrName, utoName, content, msg) : process a message recalled content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg

        scheJob(self)       : check pending jobs per minute and execute them
    """

    # override processing function
    def procMsgText(self, grpName, ufrName, utoName, content, msg):

        # an example
        """
        if ufrName != self._User["NickName"]:
            if "" != grpName:
                self.sendMsgTextByName(grpName, "At " + str(time.asctime(time.localtime(time.time()))) + ", " + ufrName + " says : " + content)
            else:
                self.sendMsgTextByName(ufrName, "[" + str(time.asctime(time.localtime(time.time()))) + "][Auto reply]您的消息我已收到。")
        """


        if ufrName != self._User["NickName"]:
            if "@+Bot" == content[:5]:
                
                url = "http://www.tuling123.com/openapi/api"
                prm = {
                        "key"       : "f4145efed8a0454eb6e44de485535641",
                        "info"      : content[5:],
                        "userid"    : "0",
                        "loc"       : "Beijing",
                    }
                try:
                    ret = self._post(url, prm, False)
                    ret = json.loads(ret)
                    if 100000 == ret["code"]:
                        if "" != grpName:
                            self.sendMsgTextByName(grpName, ret["text"])
                        else:
                            self.sendMsgTextByName(ufrName, ret["text"])
                    elif 200000 == ret["code"]:
                        if "" != grpName:
                            self.sendMsgTextByName(grpName, ret["text"] + " " + ret["url"])
                        else:
                            self.sendMsgTextByName(ufrName, ret["text"] + " " + ret["url"])
                    elif 302000 == ret["code"]:
                        if "" != grpName:
                            self.sendMsgTextByName(grpName, ret["list"].__str__())
                        else:
                            self.sendMsgTextByName(ufrName, ret["list"].__str__())
                    elif 40001 == ret["code"]:
                        self._logger.error("Tuling Robot Error: key error %s.", ret["text"])
                    elif 40002 == ret["code"]:
                        self._logger.error("Tuling Robot Error: empty info %s.", ret["text"])
                    elif 40004 == ret["code"]:
                        if "" != grpName:
                            self.sendMsgTextByName(grpName, "Sorry, I'm toooo tired today, perhaps tomorrow.")
                        else:
                            self.sendMsgTextByName(ufrName, "Sorry, I'm toooo tired today, perhaps tomorrow.")
                    elif 40007 == ret["code"]:
                        self._logger.error("Tuling Robot Error: format error %s.", ret["text"])
                    else:
                        if "" != grpName:
                            self.sendMsgTextByName(grpName, "Sorry, corresponding service unsupported yet.")
                        else:
                            self.sendMsgTextByName(ufrName, "Sorry, corresponding service unsupported yet.")
                except Exception:
                    if "" != grpName:
                        self.sendMsgTextByName(grpName, "Sorry, service failed for unknown reasons. Please contact administrator for further information.")
                    else:
                        self.sendMsgTextByName(ufrName, "Sorry, service failed for unknown reasons. Please contact administrator for further information.")                

        return

    # override processing function
    def procMsgImage(self, grpName, ufrName, utoName, msg):

        return

    # override processing function
    def procMsgVoice(self, grpName, ufrName, utoName, msg):

        return

    # override processing function
    def procMsgCard(self, grpName, ufrName, utoName, msg):

        return

    # override processing function
    def procMsgEmoji(self, grpName, ufrName, utoName, msg):

        return

    # override processing function
    def procMsgAppLink(self, grpName, ufrName, utoName, content, msg):

        return

    # override processing function
    def procMsgVideo(self, grpName, ufrName, utoName, msg):

        return

    # override processing function
    def procMsgGroupRename(self, grpName, ufrName, utoName, content, msg):

        return

    # override processing function
    def procMsgRecall(self, grpName, ufrName, utoName, content, msg):

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
            # wechat configuration
            #"AppID"             : "wx782c26e4c19acffb",
            #"Lang"              : "zh_CN",
            #"DeviceID"          : "e" + repr(random.random())[2 : 17],
            #"MessageSyncInterval"   : 1,
            # log configuration
            "LogLevel"          : logging.INFO,
            # data saving configuration
            "DataImageFolder"   : "dat",
            "DataVoiceFolder"   : "dat",
            "DataVideoFolder"   : "dat",
            "DataEmojiFolder"   : "dat",
            # interactive usage
            "EnableInteracting" : True,
            # scheduled events configuration
            "EnableScheduling"  : True,
            "EventConfFile"     : "sampleEvents.conf",
        }

    # configuration in command line arguments (in json format)
    for i in range(1, len(sys.argv)):
        logging.info("Argument : %s", sys.argv[i])
        try:
            data = json.loads(sys.argv[i], object_hook = wechatbot._conv_dict)
            for key in data.keys():
                conf[key] = data[key]
        except Exception:
            logging.warning("Argument %s cannot be parsed. Ignored.", sys.argv[i])
    
    # wechat bot
    wbot = WechatBotDemo()
    wbot.run(conf)

    return
    
if __name__ == "__main__" :

    main()
