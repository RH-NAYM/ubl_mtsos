# import json
# import pandas as pd
# from PIL import Image
# from aiohttp import ClientSession
# from io import BytesIO
# from Data.data import convertionData, self_talker, sos_convertion_data
# from Data.model import daModel, qpdsModel, sosModel, mtSOSModel
# from Data.daModelData import da_data_matched_with_mtsos
# from Data.qpdsModelData import qpds_data_matched_with_mtsos
# from Data.sosModelData import sos_data_matched_with_mtsos
# from Data.mtsosModelData import mtsos_convert_data, mtsos_split_data
# import asyncio
# import cv2
# import numpy as np
# import torch
# import re


# class ublFuncAI:
#     def __init__(self):
#         self.all_req = {}

#     async def get_image_data(self, img_url):
#         try:
#             async with ClientSession() as session:
#                 async with session.get(img_url) as response:
#                     response.raise_for_status()
#                     img_data = await response.read()
#                     return BytesIO(img_data)
#         except Exception as e:
#             raise ValueError(f"Error fetching image data: {str(e)}")
        

#     async def process_body(self, post_body):
#         try:
#             for items in post_body.get("job", []):
#                 for key, value in items.items():
#                     if key == "planogram":
#                         for image in value:
#                             store = image.get("slab", "")
#                             img = image.get("image", {}).get("original", "")
#                             if store and img:
#                                 req = {store: img}
#                                 self.all_req.update(req)
#             return self.all_req
#         except Exception as e:
#             raise ValueError(f"Error processing body: {str(e)}")
        

#     async def check_image_quality(self, image_data: BytesIO, min_resolution=800, reflection_threshold=130, shadow_threshold=120):
#         try:
#             image_array = await self.read_image_async(image_data)
#             img = await self.decode_image_async(image_array)
#             blur_value = await self.assess_blur_async(img)
#             resolution_check = await self.assess_resolution_async(img, min_resolution)
#             reflection_check = await self.assess_reflection_async(img, reflection_threshold)
#             shadow_check = await self.assess_shadow_async(img, shadow_threshold)

#             config = {
#                 "blur": "Blurry" if blur_value < 70 else {},
#                 "resolution": resolution_check,
#                 "reflection": reflection_check,
#                 "shadow": shadow_check
#             }
#             listConfig = []
#             for key,value in config.items():
#                 if len(value)>0:
#                     listConfig.append(value)
#             return listConfig
#         except Exception as e:
#             raise ValueError(f"Error checking image quality: {str(e)}")
        

#     async def read_image_async(self, image_data: BytesIO):
#         try:
#             return np.asarray(bytearray(image_data.read()), dtype=np.uint8)
#         except Exception as e:
#             raise ValueError(f"Error read_image_async: {str(e)}")
        

#     async def decode_image_async(self, image_array):
#         try:
#             return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
#         except Exception as e:
#             raise ValueError(f"Error decode_image_async: {str(e)}")
        

#     async def assess_blur_async(self, img):
#         try:
#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             return cv2.Laplacian(gray, cv2.CV_64F).var()
#         except Exception as e:
#             raise ValueError(f"Error assess_blur_async: {str(e)}")
        
#     async def assess_resolution_async(self, img, min_resolution):
#         try:
#             height, width, _ = img.shape
#             return "LowRes" if height < min_resolution or width < min_resolution else {}
#         except Exception as e:
#             raise ValueError(f"Error assess_resolution_async: {str(e)}")
        

#     async def assess_reflection_async(self, img, reflection_threshold):
#         try:
#             avg_intensity = np.mean(img)
#             return "Reflected" if avg_intensity > reflection_threshold else {}
#         except Exception as e:
#             raise ValueError(f"Error assess_reflection_async: {str(e)}")
        

#     async def assess_shadow_async(self, img, shadow_threshold):
#         try:
#             avg_intensity = np.mean(img)
#             return "Shadow" if avg_intensity < shadow_threshold else {}
#         except Exception as e:
#             raise ValueError(f"Error assess_shadow_async: {str(e)}")
    

#     async def object_detection(self, model, img_content,score):
#         try:
#             img = Image.open(img_content)
#             result = model(img,device=0,conf=score)
#             detection = {}
#             data = json.loads(result[0].tojson())
#             if len(data) == 0:
#                 return detection
#             df = pd.DataFrame(data)
#             name_counts = df['name'].value_counts().sort_index()
#             for name, count in name_counts.items():
#                 detection[name] = count
#             return detection
#         except Exception as e:
#             raise ValueError(f"Error in object detection: {str(e)}")
        
#     async def structureResult(self,predefined_data,conversionData,store,all_result,selfTalker,st):
#         try:
#             data = []
#             notDetectedData = {}
#             if store in predefined_data:
#                 for sku,count in predefined_data[store].items():
#                     if sku in conversionData and conversionData[sku] in all_result:
#                         data.append({"name":sku,"plannedQty":count,"detectedQty":all_result[conversionData[sku]]}) 
#                     else:
#                         notDetectedData.update({sku:count})
#             for sku,count in notDetectedData.items():
#                 data.append({"name":sku,"plannedQty":count})
#             if selfTalker in self_talker:
#                 if self_talker[selfTalker] in st:
#                     data.append({"name":"Shelf Talker","detectedQty":"Yes"})
#                 elif self_talker[selfTalker] not in st:
#                     data.append({"name":"Shelf Talker","detectedQty":"No"})
#             return data
#         except Exception as e:
#             raise ValueError(f"Error in Structure Result: {str(e)}")
        


#     async def start_detection(self, predefined_data,store, details, img, selfTalker):
#         try:
#             all_result = {}
#             image = await self.get_image_data(img)
#             report = await self.check_image_quality(image)
#             tasks = [
#                         asyncio.create_task(self.object_detection(daModel, image,0.4)),
#                         asyncio.create_task(self.object_detection(qpdsModel, image,0.4)),
#                         asyncio.create_task(self.object_detection(qpdsModel, image,0.6))
#                     ]
#             da, qpds, st = await asyncio.gather(*tasks)
#             print("Display Audit : ",da)
#             print("QPDS : ", qpds)
#             print("Shelf Talker : ",st)
#             if len(da)>0:
#                 all_result.update(da)
#             if len(qpds)>0:
#                 all_result.update(qpds)
#             final_result = await self.structureResult(predefined_data,convertionData,store,all_result,selfTalker,st)
#             details["image"].update({"quality":report})
#             resultForUser = {"sku":final_result}
#             return resultForUser
#         except Exception as e:
#             raise ValueError(f"Error in start detection: {str(e)}")
        
#     async def removeIntegers(self,input_string):
#         result_string = re.sub(r'\s*\d', '', input_string)
#         return result_string

#     async def SOSstructureResult(self,conversionData,category,result):
#         try:
#             data = []
#             sortedCategory = await self.removeIntegers(category)
#             if sortedCategory in conversionData:
#                 for owner,brands in conversionData[sortedCategory].items():
#                     for sku in brands:
#                         if sku in result:
#                             sosStructure = {
#                                                 "owner":owner,
#                                                 "brand":sku,
#                                                 "quantity":result[sku]
#                                             }
#                             data.append(sosStructure)
#             return data
#         except Exception as e:
#             raise ValueError(f"Error in SOS Structure Result: {str(e)}")

#     async def SOS_start_detection(self, category,details,img):
#         try:
#             image = await self.get_image_data(img)
#             report = await self.check_image_quality(image)
#             sos = await asyncio.create_task(self.object_detection(sosModel, image,0.4))
#             print("SOS : ",sos)
#             final_result = await self.SOSstructureResult(sos_convertion_data,category,sos)
#             details["image"].update({"quality":report})
#             resultForUser = {"sku":final_result}
#             return resultForUser
#         except Exception as e:
#             raise ValueError(f"Error in SOS start detection: {str(e)}")

#     async def mtsos_structure_Result(self,da_data,qpds_data,sos_data,mtsos_data,category):
#         try:
#             result = {}
#             for sku in da_data_matched_with_mtsos:
#                 if sku in da_data:
#                     mtsos_data.update({sku:da_data[sku]})
#             for sku in qpds_data_matched_with_mtsos:
#                 if sku in qpds_data:
#                     mtsos_data.update({sku:qpds_data[sku]})
#             for sku in sos_data_matched_with_mtsos:
#                 if sku in sos_data:
#                     mtsos_data.update({sku:sos_data[sku]})
#             for sku,count in mtsos_data.items():
#                 if sku in mtsos_split_data[category]:
#                     result.update({mtsos_convert_data[sku]:count})
#             return result
#         except Exception as e:
#             raise ValueError(f"Error in MTSOS Structure Result: {str(e)}")
        
#     async def mtsos_start_detection(self, category,details,img):
#         try:
#             image = await self.get_image_data(img)
#             report = await self.check_image_quality(image)
#             tasks = [
#                 asyncio.create_task(self.object_detection(daModel, image, 0.4)),
#                 asyncio.create_task(self.object_detection(qpdsModel, image, 0.4)),
#                 asyncio.create_task(self.object_detection(sosModel, image, 0.4)),
#                 asyncio.create_task(self.object_detection(mtSOSModel, image, 0.4))
#             ]
#             da_data, qpds_data, sos_data, mtsos_data = await asyncio.gather(*tasks)

#             mtsos_result = await asyncio.create_task(self.mtsos_structure_Result(da_data,qpds_data,sos_data,mtsos_data,category))
#             print({"mtsos":mtsos_result})
#             details["shelf"].append({"quality":report})
#             return mtsos_result
#         except Exception as e:
#             raise ValueError(f"Error in MTSOS start detection: {str(e)}")
           
#     def cleanup(self):
#         torch.cuda.empty_cache()        
#         pass


import json
import pandas as pd
from PIL import Image
from aiohttp import ClientSession
from io import BytesIO
from Data.data import convertionData, self_talker, sos_convertion_data
from Data.model import daModel, qpdsModel, sosModel, mtSOSModel
from Data.daModelData import da_data_matched_with_mtsos
from Data.qpdsModelData import qpds_data_matched_with_mtsos
from Data.sosModelData import sos_data_matched_with_mtsos
from Data.mtsosModelData import mtsos_convert_data, mtsos_split_data
import asyncio
import cv2
import numpy as np
import torch
import re


class ublFuncAI:
    def __init__(self):
        self.all_req = {}

    async def get_image_data(self, img_url):
        try:
            async with ClientSession() as session:
                async with session.get(img_url) as response:
                    response.raise_for_status()
                    img_data = await response.read()
                    return BytesIO(img_data)
        except Exception as e:
            raise ValueError(f"Error fetching image data: {str(e)}")

    async def process_body(self, post_body):
        try:
            for items in post_body.get("job", []):
                for key, value in items.items():
                    if key == "planogram":
                        for image in value:
                            store = image.get("slab", "")
                            img = image.get("image", {}).get("original", "")
                            if store and img:
                                req = {store: img}
                                self.all_req.update(req)
            return self.all_req
        except Exception as e:
            raise ValueError(f"Error processing body: {str(e)}")

    async def check_image_quality(self, image_data: BytesIO, min_resolution=800, reflection_threshold=130, shadow_threshold=120):
        try:
            image_array = await self.read_image_async(image_data)
            img = await self.decode_image_async(image_array)
            blur_value = await self.assess_blur_async(img)
            resolution_check = await self.assess_resolution_async(img, min_resolution)
            reflection_check = await self.assess_reflection_async(img, reflection_threshold)
            shadow_check = await self.assess_shadow_async(img, shadow_threshold)

            config = {
                "blur": "Blurry" if blur_value < 70 else {},
                "resolution": resolution_check,
                "reflection": reflection_check,
                "shadow": shadow_check
            }
            listConfig = []
            for key,value in config.items():
                if len(value)>0:
                    listConfig.append(value)
            return listConfig
        except Exception as e:
            raise ValueError(f"Error checking image quality: {str(e)}")

    async def read_image_async(self, image_data: BytesIO):
        try:
            return np.asarray(bytearray(image_data.read()), dtype=np.uint8)
        except Exception as e:
            raise ValueError(f"Error read_image_async: {str(e)}")

    async def decode_image_async(self, image_array):
        try:
            return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        except Exception as e:
            raise ValueError(f"Error decode_image_async: {str(e)}")

    async def assess_blur_async(self, img):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.Laplacian(gray, cv2.CV_64F).var()
        except Exception as e:
            raise ValueError(f"Error assess_blur_async: {str(e)}")

    async def assess_resolution_async(self, img, min_resolution):
        try:
            height, width, _ = img.shape
            return "LowRes" if height < min_resolution or width < min_resolution else {}
        except Exception as e:
            raise ValueError(f"Error assess_resolution_async: {str(e)}")

    async def assess_reflection_async(self, img, reflection_threshold):
        try:
            avg_intensity = np.mean(img)
            return "Reflected" if avg_intensity > reflection_threshold else {}
        except Exception as e:
            raise ValueError(f"Error assess_reflection_async: {str(e)}")

    async def assess_shadow_async(self, img, shadow_threshold):
        try:
            avg_intensity = np.mean(img)
            return "Shadow" if avg_intensity < shadow_threshold else {}
        except Exception as e:
            raise ValueError(f"Error assess_shadow_async: {str(e)}")

    async def object_detection(self, model, img_content, score):
        try:
            img = Image.open(img_content)
            result = model(img, device=0, conf=score)
            detection = {}
            data = json.loads(result[0].tojson())
            if len(data) == 0:
                return detection
            df = pd.DataFrame(data)
            name_counts = df['name'].value_counts().sort_index()
            for name, count in name_counts.items():
                detection[name] = count
            return detection
        except Exception as e:
            raise ValueError(f"Error in object detection: {str(e)}")

    async def structureResult(self, predefined_data, conversionData, store, all_result, selfTalker, st):
        try:
            data = []
            notDetectedData = {}
            if store in predefined_data:
                for sku, count in predefined_data[store].items():
                    if sku in conversionData and conversionData[sku] in all_result:
                        data.append({"name": sku, "plannedQty": count, "detectedQty": all_result[conversionData[sku]]})
                    else:
                        notDetectedData.update({sku: count})
            for sku, count in notDetectedData.items():
                data.append({"name": sku, "plannedQty": count})
            if selfTalker in self_talker:
                if self_talker[selfTalker] in st:
                    data.append({"name": "Shelf Talker", "detectedQty": "Yes"})
                elif self_talker[selfTalker] not in st:
                    data.append({"name": "Shelf Talker", "detectedQty": "No"})
            return data
        except Exception as e:
            raise ValueError(f"Error in Structure Result: {str(e)}")

    async def start_detection(self, predefined_data, store, details, img, selfTalker):
        try:
            all_result = {}
            image = await self.get_image_data(img)
            report = await self.check_image_quality(image)
            tasks = [
                asyncio.create_task(self.object_detection(daModel, image, 0.4)),
                asyncio.create_task(self.object_detection(qpdsModel, image, 0.4)),
                asyncio.create_task(self.object_detection(qpdsModel, image, 0.6))
            ]
            da, qpds, st = await asyncio.gather(*tasks)
            print("Display Audit : ", da)
            print("QPDS : ", qpds)
            print("Shelf Talker : ", st)
            if len(da) > 0:
                all_result.update(da)
            if len(qpds) > 0:
                all_result.update(qpds)
            final_result = await self.structureResult(predefined_data, convertionData, store, all_result, selfTalker, st)
            details["image"].update({"quality": report})
            resultForUser = {"sku": final_result}
            return resultForUser
        except Exception as e:
            raise ValueError(f"Error in start detection: {str(e)}")

    async def removeIntegers(self, input_string):
        result_string = re.sub(r'\s*\d', '', input_string)
        return result_string

    async def SOSstructureResult(self, conversionData, category, result):
        try:
            data = []
            sortedCategory = await self.removeIntegers(category)
            if sortedCategory in conversionData:
                for owner, brands in conversionData[sortedCategory].items():
                    for sku in brands:
                        if sku in result:
                            sosStructure = {
                                "owner": owner,
                                "brand": sku,
                                "quantity": result[sku]
                            }
                            data.append(sosStructure)
            return data
        except Exception as e:
            raise ValueError(f"Error in SOS Structure Result: {str(e)}")

    async def SOS_start_detection(self, category, details, img):
        try:
            image = await self.get_image_data(img)
            report = await self.check_image_quality(image)
            sos = await asyncio.create_task(self.object_detection(sosModel, image, 0.4))
            print("SOS : ", sos)
            final_result = await self.SOSstructureResult(sos_convertion_data, category, sos)
            details["image"].update({"quality": report})
            resultForUser = {"sku": final_result}
            return resultForUser
        except Exception as e:
            raise ValueError(f"Error in SOS start detection: {str(e)}")

    async def mtsos_structure_Result(self, da_data, qpds_data, sos_data, mtsos_data, category):
        try:
            result = {}
            for sku in da_data_matched_with_mtsos:
                if sku in da_data:
                    mtsos_data.update({sku: da_data[sku]})
            for sku in qpds_data_matched_with_mtsos:
                if sku in qpds_data:
                    mtsos_data.update({sku: qpds_data[sku]})
            for sku in sos_data_matched_with_mtsos:
                if sku in sos_data:
                    mtsos_data.update({sku: sos_data[sku]})
            for sku, count in mtsos_data.items():
                if sku in mtsos_split_data[category]:
                    result.update({mtsos_convert_data[sku]: count})
            return result
        except Exception as e:
            raise ValueError(f"Error in MTSOS Structure Result: {str(e)}")

    async def mtsos_start_detection(self, category, img, image_data):
        try:
            image = await self.get_image_data(img)
            report = await self.check_image_quality(image)
            tasks = [
                asyncio.create_task(self.object_detection(daModel, image, 0.4)),
                asyncio.create_task(self.object_detection(qpdsModel, image, 0.4)),
                asyncio.create_task(self.object_detection(sosModel, image, 0.4)),
                asyncio.create_task(self.object_detection(mtSOSModel, image, 0.4))
            ]
            da_data, qpds_data, sos_data, mtsos_data = await asyncio.gather(*tasks)
            print({"mtsos": mtsos_data})
            mtsos_result = await asyncio.create_task(self.mtsos_structure_Result(da_data, qpds_data, sos_data, mtsos_data, category))
            # print({"mtsos": mtsos_result})
            image_data.update({"quality": report})
            return mtsos_result
        except Exception as e:
            raise ValueError(f"Error in MTSOS start detection: {str(e)}")

    def cleanup(self):
        torch.cuda.empty_cache()
        pass
