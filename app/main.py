from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import sys
from io import StringIO
import contextlib

import subprocess
from fastapi.responses import HTMLResponse

app = FastAPI()


class CodeInput(BaseModel):
    code: str

class CommandInput(BaseModel):
    command: str



@app.post("/execute")
async def execute_code(code_input: CodeInput):
    try:
        output_buffer = StringIO()
        
        with contextlib.redirect_stdout(output_buffer):
            exec(code_input.code)
            
        output = output_buffer.getvalue()
        
        return {
            "status": "success",
            "output": output,
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "output": None,
                "error": str(e)
            }
        )




@app.post("/run-command/")
async def run_command(command_input: CommandInput):
    try:
        result = subprocess.run(command_input.command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)
        
        return {"output": result.stdout}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@app.get("/execute-page", response_class=HTMLResponse)
async def execute_page():
    with open("app/execute_code.html", "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/run-command-page", response_class=HTMLResponse)
async def run_command_page():
    with open("app/run_command.html", "r") as file:
        return HTMLResponse(content=file.read())