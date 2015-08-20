from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity
from yowsup.layers.protocol_media.protocolentities       import *
from yowsup.layers.protocol_media.mediauploader import MediaUploader
import os
import logging
from yowsup.layers.protocol_receipts.protocolentities import *
from yowsup.layers.protocol_groups.protocolentities import *
from yowsup.layers.protocol_presence.protocolentities import *
from yowsup.layers.protocol_messages.protocolentities import *
from yowsup.layers.protocol_acks.protocolentities import *
from yowsup.layers.protocol_ib.protocolentities import *
from yowsup.layers.protocol_iq.protocolentities import *
from yowsup.layers.protocol_contacts.protocolentities import *
from yowsup.layers.protocol_profiles.protocolentities import *
from yowsup.layers.protocol_chatstate.protocolentities import *
from yowsup.layers.protocol_privacy.protocolentities import *
from yowsup.layers.protocol_media.protocolentities import *
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.layers.axolotl.protocolentities.iq_key_get import GetKeysIqProtocolEntity
import threading

import time
import datetime
import json
import requests
from html2text import html2text as h
import os
#import unirest

# openshift is our PAAS for now.
ON_PAAS = 'OPENSHIFT_REPO_DIR' in os.environ
DATA_DIR = os.getenv("OPENSHIFT_DATA_DIR")


jid = "%s@s.whatsapp.net" % '9198XXXXXX94'
path = "http://cookingshooking.com/wp-content/uploads/2015/04/TCIcecream21-300x169.jpg"
filepath = "http://cookingshooking.com/wp-content/uploads/2015/04/TCIcecream21-300x169.jpg"


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
                presentDateTime = datetime.datetime.now().strftime('%d-%b-%Y|%H:%M:%S')
                print (recipeId + " " + requesterName + " " + requesterNumber)
                #response = self.GetCurrentScore(recipeId,requesterName,requesterNumber,presentDateTime)
                response = self.send_image(recipeId,requesterName,requesterNumber,presentDateTime)
            else :
                wrongInputMessage = messageProtocolEntity.getBody()
                requesterNumber = messageProtocolEntity.getFrom().split('@')[0]
                presentDateTime = datetime.datetime.now().strftime('%d-%b-%Y|%H:%M:%S')
                if ON_PAAS:
                    f = open(os.path.join(DATA_DIR, 'WrongInput.txt'), 'a')
                    f.write(wrongInputMessage + "|" + requesterNumber + "|"+ presentDateTime + "\n")
                    f.close()
                else:
                    f = open('WrongInput.txt', 'a')
                    f.write(wrongInputMessage + "|" + requesterNumber + "|"+ presentDateTime + "\n")
                    f.close()
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

    def GetCurrentScore(self,recipeId,requesterName,requesterNumber,presentDateTime):
        try:
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
            if ON_PAAS:
                    f = open(os.path.join(DATA_DIR, 'SentSuccess.txt'), 'a')
                    f.write(recipeId + "|" + requesterName + "|" + requesterNumber + "|"+ presentDateTime + "\n")
                    f.close()
            else:
                f = open('SentSuccess.txt', 'a')
                f.write(recipeId + "|" + requesterName + "|" + requesterNumber +"|"+ presentDateTime + "\n")
                f.close()
            return data2
            #+ str(data1)
            #return string(data1)
        except:
            if ON_PAAS:
                    f = open(os.path.join(DATA_DIR, 'WrongRecipeId.txt'), 'a')
                    f.write(recipeId + "|" + requesterName + "|" + requesterNumber + "|"+ presentDateTime + "\n")
                    f.close()
            else:
                f = open('WrongRecipeId.txt', 'a')
                f.write(recipeId + "|" + requesterName + "|" + requesterNumber +"|"+ presentDateTime + "\n")
                f.close()
            errormessage="Hi "+ str(requesterName) + ", Please check the Recipe ID, Looks like Recipe Id '" + str(recipeId) +"' is not valid"
            return errormessage


    def send_image(self,recipeId,requesterName,requesterNumber,presentDateTime):
        entity = RequestUploadIqProtocolEntity(RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, filePath=path)
        successFn = lambda successEntity, originalEntity: self.onRequestUploadResult(jid, path, successEntity, originalEntity)
        errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(jid, path, errorEntity, originalEntity)
        self._sendIq(entity, successFn, errorFn)


    def doSendImage(self, filePath, url, to, ip = None):
        entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to)
        self.toLower(entity)

    def onRequestUploadResult(self, jid, filePath, resultRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity):
        if resultRequestUploadIqProtocolEntity.isDuplicate():
            self.doSendImage(filePath, resultRequestUploadIqProtocolEntity.getUrl(), jid,
                             resultRequestUploadIqProtocolEntity.getIp())
        else:
            # successFn = lambda filePath, jid, url: self.onUploadSuccess(filePath, jid, url, resultRequestUploadIqProtocolEntity.getIp())
            mediaUploader = MediaUploader(jid, self.getOwnJid(), filePath,
                                      resultRequestUploadIqProtocolEntity.getUrl(),
                                      resultRequestUploadIqProtocolEntity.getResumeOffset(),
                                      self.onUploadSuccess, self.onUploadError, self.onUploadProgress, async=False)
            mediaUploader.start()

    def onRequestUploadError(self, jid, path, errorRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity):
        logger.error("Request upload for file %s for %s failed" % (path, jid))

    def onUploadSuccess(self, filePath, jid, url):
        self.doSendImage(filePath, url, jid)

    def onUploadError(self, filePath, jid, url):
        logger.error("Upload file %s to %s for %s failed!" % (filePath, url, jid))

    def onUploadProgress(self, filePath, jid, url, progress):
        sys.stdout.write("%s => %s, %d%% \r" % (os.path.basename(filePath), jid, progress))
        sys.stdout.flush()
