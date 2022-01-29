from threading import Thread
import face_recognition
import crawler
import smokesignal

imageComparators=[]

def handleFaceMatch(matchedImage, searchid):
    smokesignal.emit("matchfoundoninitialsearch", matchedImage, searchid)

class ImageCompare:
    def __init__(self, compareWith, searchid):
        self.compareWith=compareWith
        self.searchid=searchid
        self.run=True
    
    def comparetwoimages(self, compareFrom, compareWith):
        try:
            img1=face_recognition.face_encodings(face_recognition.load_image_file(compareFrom['image']))[0]
            results=face_recognition.compare_faces(compareWith, img1)
            if results[0]:
                handleFaceMatch(compareFrom['link'], self.searchid)
        except Exception as err:
            smokesignal.emit("error", "ON_COMPARISON", err)
    
    def startComparison(self):
        imglist=[]
        for image in self.compareWith:
            imglist.append(face_recognition.face_encodings(face_recognition.load_image_file(image))[0])
        for compareFrom in crawler.images:
            if self.run:
                self.comparetwoimages(compareFrom, imglist)
            else:
                break
    
    def stopComparison(self):
        self.run=False

@smokesignal.on('startcomparison')
def handleStartImageComparison(imagepaths, searchid):
    comparator=ImageCompare(imagepaths, searchid)
    comparatorthread=Thread(target=comparator.startComparison)
    comparatorthread.start()
    imageComparators.append(comparator)