from typing import Annotated,Literal,Optional
import joblib
from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from pydantic import BaseModel,Field
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data(year):
    try:
        return joblib.load(f"model_year_{year}.pkl")
    except FileNotFoundError:
        raise HTTPException(status_code=400,detail="File not found error")

class Student(BaseModel):
    Gender: Literal['Male', 'Female', 'Other']
    CGPA100: Annotated[float, Field(..., gt=0, lt=5, strict=True)]
    CGPA200: Optional[Annotated[float, Field(gt=0, lt=5, strict=True)]] = None
    CGPA300: Optional[Annotated[float, Field(gt=0, lt=5, strict=True)]] = None
    attendance: Annotated[float, Field(..., gt=0, lt=100, strict=True)]
    study_hours: Annotated[float, Field(..., gt=0, lt=12, strict=True)]


def cal_sgpa(year,data):
    if year==2:
        return data['CGPA100']
    elif year==3:
        return (data['CGPA100']+data['CGPA200'])/2
    elif year==4:
        return (data['CGPA100']+data['CGPA200']+data['CGPA300'])/3

def suggestions(sgpa):
    if sgpa<1.5 :
        return "INCREASE STUDY TIME AND ATTENDANCE YOU ARE AT HIGH RISK"
    elif 1.5 < sgpa < 3.5:
        return "YOU ARE DOING OK BUT NEED MORE FOCUS YOU ARE AT LOW RISK"
    else:
        return "YOU ARE DOING WELL NO RISK"


@app.post('/predict')
def predict(year:int , user_data : Student):
    if year not in [2,3,4]:
        raise HTTPException(status_code=400,detail="Year not valid Enter year between 2 and 4")
    model=load_data(year)
    data=user_data.model_dump()
    sgpa=cal_sgpa(year,data)
    try:
        prediction = model.predict(pd.DataFrame([data]))[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=200,content={'predicted_cgpa':float(prediction),
     "current_sgpa":float(sgpa),
     "suggestion" : suggestions(sgpa)})