# WechatBot

WechatBot serves as a basic tool for automatical Wechat message processing (receiving and sending) based on Web Wechat APIs using Python.

We note that no official Web Wechat APIs are available, thus the stability of the project is not guaranteed.

We would thank https://github.com/liuwons/wxBot and https://github.com/Urinx/WeixinBot for their work on Python based Web Wechat projects. Most APIs in this project are implemented according to their work.

## Usage

qrcode is required to use WechatBot. schedule is required for event scheduling and timed task. PIL or pillow is optional.

A user can run main.py directly for a simple WechatBot demo, which supports:

- Receiving all messages, printing plain text ones, and saving image, voice, video ones as files.
- Manual message sending.
- (Commented in the demo main.py) Auto replying received plain text messages (except the ones sent by itself).
- Reading scheduled events in sampleEvents.conf and sending plain text at scheduled time.

After starting up, the demo demonstrates a QRcode for cellphone scanning, and manual confirmation on the cellphone is required. Afterwards, one can type 'h', 'q', 'si', or 'sn' in the terminal, for 'help', 'quit', 'send message by ID', or 'send message by name', respectively.

Sepcially, for online distribution, two bash scripts are provided for background running and logging (start_wechatbot.sh) and status monitoring (watch_wechatbot.sh). Manual message sending and other interactive functions are disabled for background running.

## Extension

The WechatBot is designed for easy and flexible extension. Message processing and / or sending extensions can be added to the framework by overriding the following functions:

- run(conf)           : start the wechatbot with configuration conf (dict)
- help()              : print help information
- sendMsgTextByID(id, content)        : send a plain text message content to the group/contact with ID id
- sendMsgTextByName(name, content)    : send a plain text message content to the group/contact with remark name or nickname name
- procMsgText(self, grpName, ufrName, utoName, content, msg)   : process a plain text message content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
- procMsgImage(self, grpName, ufrName, utoName, msg)  : process an image, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
- procMsgVoice(self, grpName, ufrName, utoName, msg)  : process a voice message, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
- procMsgCard(self, grpName, ufrName, utoName, msg)   : process a card message, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
- procMsgEmoji(self, grpName, ufrName, utoName, msg)  : process an emoji, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
- procMsgAppLink(self, grpName, ufrName, utoName, content, msg)    : process an app link message content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
- procMsgVideo(self, grpName, ufrName, utoName, msg)  : process a video message, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg, and the data is saved under configured folder in the name of msg["MsgId"].ext
- procMsgGroupRename(self, grpName, ufrName, utoName, content, msg)    : process a group rename message content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg
- procMsgRecall(self, grpName, ufrName, utoName, content, msg) : process a message recalled content, sent by user ufrName, to user utoName, in group grpName (if not empty); original message is provided in msg

By default, content provides processed message body (such as plain text, xml data, image url, etc.), and msg provides the raw message in json format.

The following functions are provided for convenience:

- getGrpNameByID(id)  : obtain a group's nickname by its ID (a.k.a. UserName, string)
- getUsrNameByID(id)  : obtain a contact's remark name (if valid) or nickname by its ID (a.k.a. UserName, string)
- getIDByName(id)     : obtain a group/contact's ID by its remark name (contact only) or nickname

The scheduled job processing function is:

- scheJob()           : check pending jobs per minute and execute them

Furthermore, more sendMsg functions can be defined.

## Notes

- UserName returned by Wechat server changes per login.
