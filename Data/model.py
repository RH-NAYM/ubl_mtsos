from ultralytics import YOLO

daModel = YOLO("AI_Models/ublDA_v2.2.pt").cuda() # added 3 hair care and 1 horlicks stage 1
qpdsModel = YOLO("AI_Models/ublQPDS_ST_v1.2.pt").cuda()
sosModel = YOLO("AI_Models/ublSOS_v1.2.pt").cuda()
mtSOSModel = YOLO("AI_Models/ublSOS_v1.2.pt").cuda()

daModel.to(device=0)
qpdsModel.to(device=0)
sosModel.to(device=0)
mtSOSModel.to(device=0)