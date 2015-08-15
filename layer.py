from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity

import time
import datetime
import json
import requests
from html2text import html2text as h
#import unirest

current_score = ['0', '']

# Text Message to check
message = 'YO'

# World Cup series id for massap up
WORLDCUP_ID = '2223'

# Timer to update the score
SCORE_TIMER = 5

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        #send receipt otherwise we keep receiving the same message over and over

        if True:
            receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom())
            inputMessage = messageProtocolEntity.getBody().split()


            if (inputMessage[0].isdigit() and len(inputMessage)==2) :
                recipeId = inputMessage[0]
                requesterName = inputMessage[1]
                requesterNumber = messageProtocolEntity.getFrom().split('@')[0]
                print (recipeId + " " + requesterName + " " + requesterNumber)
                response = self.GetCurrentScore(recipeId,requesterName)
                #response = self.image_send('919844041494',"http://cookingshooking.com/wp-content/uploads/2015/04/TCIcecream21-300x169.jpg")
            else :
                response = "Please send Message as RecipeId<space>YourName"

            outgoingMessageProtocolEntity = TextMessageProtocolEntity(
                response,
                to = messageProtocolEntity.getFrom())

            self.toLower(receipt)
            self.toLower(outgoingMessageProtocolEntity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        #ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", "delivery",entity.getFrom())
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

    def GetCurrentScore(self,recipeId,requesterName):
        text_response = 'Test Message \n Test Message \n Test Message \n Test Message'
		#Return details
##        try:
        resp = requests.get('http://cookingshooking.com/wp-json/posts/' + str(recipeId))
        data = resp.json()
        #print (data["ID"],data["excerpt"], data["myextradata"]["bgimage"])
        #data1=str(h(data["title"])).strip()
        #data1=str(h(data["excerpt"])).strip()
        data1=str(h(data["title"])).strip().encode('utf-8')
        data3=data1.decode('utf-8','ignore')
        data4=data["myextradata"]["instructions"]
        data5=[]
        for i in data4:
            data7=str(h(i['description'])).strip().replace('¾','0.75')#.encode('utf-8')
            data7=data7.replace('½','0.50')
            data7=data7.replace('¼','0.25')
            data7=data7.encode('utf-8')
            data8=data7.decode('utf-8', 'ignore')
            data6=str(data4.index(i)+ 1) +". " + data8
            #data7=data6.decode('ascii')
            data5.append(data6)
        data9=str(h(data["myextradata"]["recipe_notes"])).strip().replace('¾','0.75')
        data9=data9.replace('½','0.50')
        data9=data9.replace('¼','0.25')
        data9=data9.encode('utf-8')
        data9=data9.decode('utf-8', 'ignore')
        data10=data["myextradata"]["recipe_ingredients"]
        data11=[]
        for i in data10:
            if (i['notes']==""):
                data12=str(str(i['amount_normalized']) + " " + str(i['unit']) + " " +  str(i['ingredient']))
            else:
                data12=str(str(i['amount_normalized']) +" " + str(i['unit']) +" " +  str(i['ingredient']) +" ( " +  str(i['notes']) +" )")

            #data12=data12.encode('utf-8')
            #data12=data12.decode('utf-8','ignore')
            data11.append(data12)

        data2 = "Hi "+ str(requesterName) + ", Below is your requested Recipe \n \n" + data3 +"\n \n INGREDIENTS: \n\n" + '\n'.join(data11) +"\n \n INSTRUCTIONS: \n\n" + '\n'.join(data5) +"\n \n RECIPE NOTES: \n\n" + data9
        return data2
            #+ str(data1)
            #return string(data1)
##        except:
##            errormessage="Hi "+ str(requesterName) + ", Please check the Recipe ID, Looks like Recipe Id '" + str(recipeId) +"' is not valid"
##            return errormessage

    def image_send(self, number, path):
        self.jidAliases = {
            # "NAME": "PHONE@s.whatsapp.net"
        }

        def normalizeJid(number):
            if '@' in number:
                return number
            elif "-" in number:
                return "%s@g.us" % number

            return "%s@s.whatsapp.net" % number

        def aliasToJid(self, calias):
            for alias, ajid in self.jidAliases.items():
                if calias.lower() == alias.lower():
                    return normalizeJid(ajid)

            return normalizeJid(calias)

        jid = aliasToJid(self,number)
        entity = RequestUploadIqProtocolEntity(RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, filePath=path)
        successFn = lambda successEntity, originalEntity: self.onRequestUploadResultImage(jid, path, successEntity, originalEntity)
        errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(jid, path, errorEntity, originalEntity)

        self._sendIq(entity, successFn, errorFn)

    def doSendImage(self, filePath, url, mediaType, to, ip = None):
        caption = ""
        entity = DownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, mediaType, ip, to, caption)
        self.toLower(entity)

    def onRequestUploadResultImage(self, jid, filePath, resultRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity):
        if resultRequestUploadIqProtocolEntity.isDuplicate():
            self.doSendImage(filePath, resultRequestUploadIqProtocolEntity.getUrl(), "image", jid,
                             resultRequestUploadIqProtocolEntity.getIp())
        else:
            mediaUploader = MediaUploader(jid, self.getOwnJid(), filePath,
                                      resultRequestUploadIqProtocolEntity.getUrl(),
                                      resultRequestUploadIqProtocolEntity.getResumeOffset(),
                                      self.onUploadSuccessImage, self.onUploadError, self.onUploadProgress, async=False)
            mediaUploader.start()

    def onUploadSuccessImage(self, filePath, jid, url):
        self.doSendImage(filePath, url, "audio", jid)




