from typing import ItemsView
from asyncio.tasks import sleep
import cv2
import mediapipe as mp
import asyncio
import pyrebase
from datetime import datetime
from pusher_push_notifications import PushNotifications

# config Firebase
config = {
    "apiKey" : "AIzaSyDkFn3LdpjPly4w31eL6CAQIktzSclaMg0",
    "authDomain" : "astroapp-cbf26.firebaseapp.com",
    "databaseURL" : "https://astroapp-cbf26-default-rtdb.firebaseio.com",
    "projectId" : "astroapp-cbf26",
    "storageBucket" : "astroapp-cbf26.appspot.com",
    "serviceAccount" : r"serviceAccAstro.json"
}

firebaseConnect = pyrebase.initialize_app(config)
db = firebaseConnect.database()

pn_client = PushNotifications(
    instance_id='664b9c5f-0e58-442f-a7e4-4f7c7e0c2b87',
    secret_key='A975DDC2A5253248B6DEA2167B6ADBFC20BE8473F27B671D0D50FF1103EA3F7A',
)

#declare
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
signGesture = [8, 12, 16, 20]
jempol_sign = 4
now = datetime.now() 
time_stamp = now.strftime("%d-%m-%Y %H-%M-%S")
timeNow = now.strftime("%H-%M")
tanggal = now.strftime("%Y-%m-%d")

async def pushInDb(aktivitas):

    db.child("Riwayat Aktivitas")
    dataset = {
        'nama_aktivitas' : aktivitas,
        'jam' : timeNow,
        'tanggal' : tanggal
    }
    await asyncio.sleep(2)
    db.push(dataset)


async def pushNotif(body):
    TOPIC = "aktivitas"
    ALERT_NOTIF = "Report Created"
    TITLE_NOTIF = "Aktivitas Pasien"
    BODY_NOTIF = body
    await asyncio.sleep(2)
    pn_client.publish(
        interests=[TOPIC],
        publish_body={'apns': {'aps': {'alert': ALERT_NOTIF}},
                        'fcm': {'notification': {'title': TITLE_NOTIF, 'body': BODY_NOTIF}}}
    )

def printText(text):
    cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 0, 255), 3)
    print(text)


while True :
    ret, img, = cap.read()
    h, w, c = img.shape
    results = hands.process(img)  
    
    if results.multi_hand_landmarks :
        for hand_landmark in results.multi_hand_landmarks :
            lm_list = []
            for id, lm in enumerate(hand_landmark.landmark) :
                lm_list.append(lm)

            sign_status = []

            for sign in signGesture :
                x, y = int(lm_list[sign].x * w), int(lm_list[sign].y * h)
                cv2.circle(img, (x, y), 15, (255, 0, 0), cv2.FILLED)

                if lm_list[sign].x < lm_list[sign - 3].x :
                     cv2.circle(img, (x, y), 15, (0, 255, 0), cv2.FILLED)
                     sign_status.append(True)
                
                elif lm_list[sign].x < lm_list[sign - 2].x :
                     cv2.circle(img, (x, y), 15, (0, 255, 0), cv2.FILLED)
                     sign_status.append(True)
                
                else :
                    sign_status.append(False)

            if all(sign_status) :
                if lm_list[jempol_sign].y < lm_list[jempol_sign - 1].y < lm_list[jempol_sign - 2].y :
                    printText("MINUM")
                    asyncio.run(pushInDb("Minum"))
                    asyncio.run(pushNotif("Pasien membutuhkan minum"))

            elif sign_status == [True, True, True, False]:
                if lm_list[jempol_sign].y < lm_list[jempol_sign - 1].y < lm_list[jempol_sign - 2].y :
                    printText("MAKAN")
                    asyncio.run(pushInDb("Makan"))
                    asyncio.run(pushNotif("Pasien membutuhkan makan"))

            elif sign_status == [False, True, True, True]:
                if lm_list[jempol_sign].y < lm_list[jempol_sign - 1].y < lm_list[jempol_sign - 2].y :
                    printText("PIPIS")
                    asyncio.run(pushInDb("Pipis"))
                    asyncio.run(pushNotif("Pasien membutuhkan pergi ke kamar mandi"))
            

            elif sign_status == [False, False, True, True]: 
                if lm_list[jempol_sign].y < lm_list[jempol_sign - 1].y < lm_list[jempol_sign - 2].y :
                    printText("PUP")
                    asyncio.run(pushInDb("Pup"))
                    asyncio.run(pushNotif("Pasien membutuhkan pergi ke kamar mandi"))

            
            mp_draw.draw_landmarks(img, hand_landmark,
                                   mp_hands.HAND_CONNECTIONS,
                                   mp_draw.DrawingSpec((0, 0, 255), 2, 2),
                                   mp_draw.DrawingSpec((0, 255, 0), 4, 2)
                                   )

            
    cv2.imshow("ASTRO Sign Language", img)
   
    if cv2.waitKey(1) == ord('q') :
        break
    
