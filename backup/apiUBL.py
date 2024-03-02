import asyncio
import requests
from typing import List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mainUBL import ublFuncAI
from datetime import datetime
from aiohttp import ClientSession
from io import BytesIO
import pytz
import logging

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

    async def process_box(self, box):
        try:
            for details in box:
                category = details.get("category", "")
                img = details.get("image", {}).get("original", "")
                if category and img:
                    result = await self.ublFunc.SOSstart_detection(category, details, img)
                    details.update(result)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_box: {str(e)}")
        finally:
            self.ublFunc.cleanup()


    async def process_categories(self, categories):
        try:
            for details in categories:
                category = details.get("category", "")
                image_quality = details.get("image",{})
                img = details.get("image", {}).get("original", "")
                mtsos_final_result = {}
                if category and img:
                    result = await self.ublFunc.MTSOSstart_detection(img,category)
                    for sku,count in result["detection_data"].items():
                        if sku not in mtsos_final_result:
                            mtsos_final_result.update({sku:count})
                        elif sku in mtsos_final_result:
                            mtsos_final_result.update({sku:mtsos_final_result[sku]+count})
                details.update(mtsos_final_result)
                image_quality.update({"quality":result["quality"]})
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error process_planogram: {str(e)}")
        finally:
            self.ublFunc.cleanup()

    async def process_store(self, item, predefined_data):
        try:
            name = item.get("name", "")
            if name in ("DA", "QPDS"):
                await self.process_planogram(item.get("planogram", []), predefined_data)
            elif name == "SOS":
                await self.process_box(item.get("box", []))
            # elif name == "MTSOS":
            #     await self.process_categories(item.get("categories", []))
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
