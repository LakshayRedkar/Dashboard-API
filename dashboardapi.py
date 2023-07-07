from fastapi import FastAPI, Query
import databases
import sqlalchemy
from datetime import datetime,date
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

# CORS configuration
origins = [
    "https://www.example.com",  # Replace with your website URL
    "http://localhost:8000",    # Allow localhost for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Database connection 
DATABASE_URL = "postgresql://postgres:lakshay@localhost/lakshay"

database = databases.Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup():
    await database.connect()
    metadata.create_all(bind=engine)




@app.get("/data")
async def get_ward_data(from_date: date = Query(None),
                         to_date: date = Query(None),
                         show_data: str = Query(None)):
    table_name = ""
    metadata.reflect(bind=engine)
    print(metadata.tables.keys())
    if show_data:
        if show_data == "ward":
            table_name = "wards_data"
        elif show_data == "prabhag":
            table_name = "prabhags_data"
        elif show_data == "region":
            table_name = "regions_data"
        elif show_data == "building":
            table_name = "buildings_data"

    # if not table_name:
    #     return {"error": "Invalid show_data value"}

    specific_table = metadata.tables.get(table_name)
    # if not specific_table:
    #     return {"error": "Table not found"}

    query = specific_table.select()

    if from_date and to_date:
        query = query.where(specific_table.c.date.between(from_date, to_date))

    compiled = query.compile(compile_kwargs={"literal_binds": True})
    print(compiled)
    results = await database.fetch_all(query)
    return results

# @app.get("/get-student/{student_id}")
# def get_student(student_id:int = Path(description="Please provide id",gt=0,lt=5)):
#     return students[student_id]

# @app.get("/get-by-name/{student_id}")
# def get_student(*,student_id:int,name: Optional[str] =None, test :int):
#     for student_id in students:
#         if students[student_id]["name"]==name:
#             return students[student_id]
#     return {"Data":"Not Found"}




# server configuration 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)