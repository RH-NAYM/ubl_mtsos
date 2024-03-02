import asyncio
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from UBL_Main import ublFuncAI
from datetime import datetime
import pytz
import logging
from Data.mtsosSizeData import mtsos_size_demo

logging.basicConfig(filename="UnileverDailyLog.log", filemode='w')
logger = logging.getLogger("Unilever")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("UnileverDailyLog.log")
logger.addHandler(file_handler)

total_done = 0
total_error = 0

app = FastAPI()
class Item(BaseModel):
    outlet: dict
    job: list

async def on_startup():
    global planogram_data
    global predefined_data
    try:
        # response = requests.get("https://ml.hedigital.net/api/v1/planned-qty")
        response = requests.get("https://coffee.hedigital.net/api/v1/planned-qty")
        print("#"*100)
        response.raise_for_status()
        data = response.json()
        planogram_data = data.get("data", [])
        logger.info(f"The initial data pulled from the DB : {planogram_data}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error making GET request during startup: {str(e)}")
    finally:
        for i in planogram_data:
            slab = i["slab"]
            all_sku = {}
            for item in i.get("sku", []):
                items = {item["name"]:item["qty"]}
                all_sku.update(items)
            predefined_data.update({slab:all_sku})
        print("Slab and SKU details:", predefined_data)
        ublImageProcessingAPI.ublFunc.cleanup()

app.add_event_handler("startup", on_startup)

class ublFuncAPI:
    def __init__(self):
        self.ublFunc = ublFuncAI()

    async def process_planogram(self, planogram, predefined_data):
        try:
            for details in planogram:
                store = details.get("slab", "")
                selfTalker = details.get("name", "")
                img = details.get("image", {}).get("original", "")
                if store and img:
                    result = await self.ublFunc.start_detection(predefined_data, store, details, img, selfTalker)
                    details.update(result)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_planogram: {str(e)}")
        finally:
            self.ublFunc.cleanup()

    async def rebuild_data(self, data):
        rebuilt_data = {}
        for entry in data:
            for product, quantity in entry.items():
                if product in rebuilt_data:
                    rebuilt_data[product] += quantity
                else:
                    rebuilt_data[product] = quantity
        return await self.user_data_mtsos(rebuilt_data)
    
    async def user_data_mtsos(self,data):
        result = []
        for key,value in data.items():
            result.append({"name":key,"detectedQty":value,"size":mtsos_size_demo[key] if key in mtsos_size_demo else ""})
        return result



    async def process_box(self, box):
        try:
            for details in box:
                category = details.get("category", "")
                img = details.get("image", {}).get("original", "")
                if category and img:
                    result = await self.ublFunc.SOS_start_detection(category, details, img)
                    details.update(result)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_box: {str(e)}")
        finally:
            self.ublFunc.cleanup()


    # async def process_categories(self, categories):
    #     try:
    #         for details in categories:
    #             category = details.get("category", "")
    #             shelf = details.get("shelf", [])
    #             all_result = {}
    #             for item in shelf:
    #                 img = item.get("image", {}).get("original","")
    #                 print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX : ",img)
    #                 if category and img:
    #                     result = await self.ublFunc.mtsos_start_detection(category,details,img)
    #                     for sku,count in result.items():
    #                         if sku in all_result:
    #                             all_result.update({sku:all_result[sku]+count})
    #                         else:
    #                             all_result.update({sku:count})
    #                     details.update(all_result)
    #     except requests.exceptions.RequestException as e:
    #         raise HTTPException(status_code=500, detail=f"Error process_box: {str(e)}")
    #     finally:
    #         self.ublFunc.cleanup()
    async def process_categories(self, categories):
        try:
            for details in categories:
                category = details.get("category", "")
                shelf = details.get("shelf", [])
                # print(shelf[0])
                all_result = []
                for item in shelf:
                    for key,value in item.items():
                        if key=="image":
                            img = value.get("original","")
                            if category and img:
                                # Pass 'category' argument to mtsos_start_detection
                                result = await self.ublFunc.mtsos_start_detection(category, img, value)
                                for sku,count in result.items():
                                    if sku in all_result:
                                        # data = {"name":sku,"detectedQty":all_result[sku]+count}
                                        all_result.append({sku:all_result[sku]+count})
                                    else:
                                        # data = {"name":sku,"detectedQty":count}
                                        all_result.append({sku:count})
                details.update({"sku":await self.rebuild_data(all_result)})  # Update 'details' dictionary with the results
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_categories: {str(e)}")
        finally:
            self.ublFunc.cleanup()



    async def process_store(self, item, predefined_data):
        try:
            name = item.get("name", "")
            if name in ("DA", "QPDS"):
                await self.process_planogram(item.get("planogram", []), predefined_data)
            elif name == "SOS":
                await self.process_box(item.get("box", []))
            elif name == "MTSOS":
                await self.process_categories(item.get("categories", []))
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_store: {str(e)}")
        finally:
            self.ublFunc.cleanup()

    async def process_items(self, items: Union[Item, List[Item]]):
        try:
            if isinstance(items, list):
                return await asyncio.gather(*(self.process_item(item) for item in items))
            else:
                return await self.process_item(items)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_items: {str(e)}")
        finally:
            self.ublFunc.cleanup()

    async def process_item(self, item: Item):
        try:
            await self.processBody(item.job)
            return dict(item)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_item: {str(e)}")
        finally:
            self.ublFunc.cleanup()


    async def processBody(self, post_body):
        try:
            tasks = [asyncio.create_task(self.process_store(item, predefined_data)) for item in post_body]
            await asyncio.gather(*tasks)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error processBody: {str(e)}")
        finally:
            self.ublFunc.cleanup()
def get_bd_time():
    bd_timezone = pytz.timezone("Asia/Dhaka")
    time_now = datetime.now(bd_timezone)
    current_time = time_now.strftime("%I:%M:%S %p")
    return current_time

ublImageProcessingAPI = ublFuncAPI()

planogram_data = None
predefined_data = {}

@app.get("/status")
async def status():
    return {"message": "AI Server is running"}

@app.post("/nlp")
async def create_items(items: Union[Item, List[Item]]):
    try:
        results = await ublImageProcessingAPI.process_items(items)
        return results
    except Exception as e:
        global total_error
        total_error += 1
        logger.info(f"Time: {get_bd_time()}, Failed: {total_error}, Payload: {items}")
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
    finally:
        global total_done
        total_done += 1
        logger.info(f"Time: {get_bd_time()}, Successful: {total_done}, Payload: {items}")
        print("-"*100)
        print(f"Daily Execution Count : {total_done}")
        print(f"Time : {get_bd_time()}")
        ublImageProcessingAPI.ublFunc.cleanup()

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=5656)
    finally:
        ublImageProcessingAPI.ublFunc.cleanup()
