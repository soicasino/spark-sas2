"""
Meters Router - Handle meter reading operations for slot machine
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import Optional

from models.requests import MeterRequest, MeterType
from models.responses import MetersResponse, BalanceResponse, ErrorResponse
from sas_web_service import SASWebService

router = APIRouter(prefix="/api/meters", tags=["Meters"])

# Dependency to get the SAS web service instance
async def get_sas_service() -> SASWebService:
    """Dependency to get SAS service instance"""
    from main import sas_service
    return sas_service


@router.get("/all", response_model=MetersResponse)
async def get_all_meters(
    meter_type: MeterType = Query(MeterType.BASIC, description="Type of meters to retrieve"),
    game_id: Optional[int] = Query(None, description="Game ID for game-specific meters"),
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Get meter readings from the slot machine
    
    - **meter_type**: Type of meters to retrieve (basic, extended, all, bill, game)
    - **game_id**: Required when meter_type is 'game'
    """
    try:
        start_time = datetime.now()
        
        # Validate game_id requirement
        if meter_type == MeterType.GAME and game_id is None:
            raise HTTPException(
                status_code=400,
                detail="game_id is required when meter_type is 'game'"
            )
        
        # Execute meters command
        parameters = {"meter_type": meter_type.value}
        if game_id is not None:
            parameters["game_id"] = game_id
            
        result = await sas_service.execute_command_async(
            "get_meters", 
            parameters=parameters,
            timeout=15.0  # Meters can take a while
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MetersResponse(
                success=True,
                message=f"Meters ({meter_type.value}) retrieved successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        elif result["status"] == "timeout":
            raise HTTPException(
                status_code=408,
                detail="Meter request timed out - slot machine may not be responding"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get meters: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Meters error: {str(e)}"
        )


@router.post("/request", response_model=MetersResponse)
async def request_meters(
    request: MeterRequest,
    sas_service: SASWebService = Depends(get_sas_service)
):
    """
    Request meter readings using POST with request body
    
    This endpoint accepts a JSON body with meter request parameters
    """
    try:
        start_time = datetime.now()
        
        # Validate game_id requirement
        if request.meter_type == MeterType.GAME and request.game_id is None:
            raise HTTPException(
                status_code=400,
                detail="game_id is required when meter_type is 'game'"
            )
        
        # Execute meters command
        parameters = {"meter_type": request.meter_type.value}
        if request.game_id is not None:
            parameters["game_id"] = request.game_id
            
        result = await sas_service.execute_command_async(
            "get_meters",
            parameters=parameters,
            timeout=15.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MetersResponse(
                success=True,
                message=f"Meters ({request.meter_type.value}) retrieved successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        elif result["status"] == "timeout":
            raise HTTPException(
                status_code=408,
                detail="Meter request timed out - slot machine may not be responding"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get meters: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Meters error: {str(e)}"
        )


@router.get("/basic", response_model=MetersResponse)
async def get_basic_meters(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Get basic meter readings (turnover, win, games played, current credits)
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async(
            "get_meters",
            parameters={"meter_type": "basic"},
            timeout=15.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MetersResponse(
                success=True,
                message="Basic meters retrieved successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get basic meters: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Basic meters error: {str(e)}"
        )


@router.get("/extended", response_model=MetersResponse)
async def get_extended_meters(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Get extended meter readings (includes additional meters like AFT, bonus, etc.)
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async(
            "get_meters",
            parameters={"meter_type": "extended"},
            timeout=15.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return MetersResponse(
                success=True,
                message="Extended meters retrieved successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get extended meters: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extended meters error: {str(e)}"
        )


@router.get("/balance", response_model=BalanceResponse) 
async def get_balance(sas_service: SASWebService = Depends(get_sas_service)):
    """
    Get current balance information (cashable, restricted, nonrestricted amounts)
    """
    try:
        start_time = datetime.now()
        
        result = await sas_service.execute_command_async(
            "get_balance",
            timeout=10.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result["status"] == "completed":
            return BalanceResponse(
                success=True,
                message="Balance retrieved successfully",
                execution_time_ms=execution_time,
                data=result["result"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get balance: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Balance error: {str(e)}"
        ) 