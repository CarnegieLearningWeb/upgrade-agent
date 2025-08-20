import aiohttp
import asyncio
import json
from typing import List, Dict, Any, Optional
from enum import Enum
from src.api.auth import auth_manager
from src.models.api_types import (
    APIResponse, HealthCheckResponse, ContextMetadata, ContextMetadataItem,
    ExperimentName, Experiment, ExperimentCreateRequest,
    ExperimentStateUpdate, InitRequest, InitResponse,
    AssignRequest, AssignResponse, MarkRequest, MarkResponse, AssignmentResult
)
from src.config import config


class AuthType(Enum):
    NONE = "none"
    BEARER = "bearer"
    USER_ID = "user_id"


class UpGradeAPIError(Exception):
    def __init__(self, message: str, status_code: int = None, response_data: Any = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class UpGradeAPI:
    def __init__(self):
        self.base_url = config.UPGRADE_API_URL
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.retry_attempts = 3
        self.retry_delay = 1
    
    async def _build_headers(self, auth_type: AuthType, user_id: Optional[str] = None) -> Dict[str, str]:
        """Build appropriate headers based on auth type."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if auth_type == AuthType.BEARER:
            token = await auth_manager.get_access_token()
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == AuthType.USER_ID:
            if user_id:
                headers["User-Id"] = user_id
        # AuthType.NONE adds no additional headers
        
        return headers
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        auth_type: AuthType = AuthType.BEARER,
        user_id: Optional[str] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> APIResponse:
        """Unified request method handling all auth types with retry logic."""
        url = f"{self.base_url}{endpoint}"
        headers = await self._build_headers(auth_type, user_id)
        
        for attempt in range(self.retry_attempts):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                        params=params
                    ) as response:
                        response_text = await response.text()
                        
                        if response.status >= 500:
                            if attempt < self.retry_attempts - 1:
                                await asyncio.sleep(self.retry_delay * (attempt + 1))
                                continue
                            raise UpGradeAPIError(
                                f"Server error: {response_text}",
                                status_code=response.status,
                                response_data=response_text
                            )
                        
                        try:
                            response_data = json.loads(response_text) if response_text else None
                        except json.JSONDecodeError:
                            response_data = response_text
                        
                        if response.status >= 400:
                            error_msg = response_data.get("message", response_text) if isinstance(response_data, dict) else response_text
                            raise UpGradeAPIError(
                                f"API error: {error_msg}",
                                status_code=response.status,
                                response_data=response_data
                            )
                        
                        return APIResponse(
                            success=True,
                            data=response_data,
                            status_code=response.status
                        )
                        
            except aiohttp.ClientError as e:
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise UpGradeAPIError(f"Request failed: {str(e)}")
            except UpGradeAPIError:
                raise
            except Exception as e:
                raise UpGradeAPIError(f"Unexpected error: {str(e)}")
        
        raise UpGradeAPIError(f"Failed after {self.retry_attempts} attempts")
    
    # System Information Endpoints
    
    async def health_check(self) -> HealthCheckResponse:
        response = await self._make_request("GET", "/", auth_type=AuthType.NONE)
        return HealthCheckResponse(**response.data)
    
    async def get_context_metadata(self) -> ContextMetadata:
        response = await self._make_request("GET", "/experiments/contextMetaData")
        return ContextMetadata(**response.data)
    
    # Experiment Management Endpoints
    
    async def get_experiment_names(self) -> List[ExperimentName]:
        response = await self._make_request("GET", "/experiments/names")
        return [ExperimentName(**exp) for exp in response.data]
    
    async def get_all_experiments(self) -> List[Experiment]:
        response = await self._make_request("GET", "/experiments")
        return [Experiment(**exp) for exp in response.data]
    
    async def get_experiment_by_id(self, experiment_id: str) -> Experiment:
        response = await self._make_request("GET", f"/experiments/single/{experiment_id}")
        return Experiment(**response.data)
    
    async def create_experiment(self, experiment: ExperimentCreateRequest) -> Experiment:
        response = await self._make_request(
            "POST", 
            "/experiments",
            data=experiment.model_dump(exclude_none=True)
        )
        return Experiment(**response.data)
    
    async def update_experiment(self, experiment_id: str, experiment: ExperimentCreateRequest) -> Experiment:
        response = await self._make_request(
            "PUT",
            f"/experiments/{experiment_id}",
            data=experiment.model_dump(exclude_none=True)
        )
        return Experiment(**response.data)
    
    async def update_experiment_state(self, state_update: ExperimentStateUpdate) -> Experiment:
        response = await self._make_request(
            "POST",
            "/experiments/state",
            data=state_update.model_dump(exclude_none=True)
        )
        return Experiment(**response.data)
    
    async def delete_experiment(self, experiment_id: str) -> APIResponse:
        return await self._make_request("DELETE", f"/experiments/{experiment_id}")
    
    # User Simulation & Testing Endpoints
    
    async def init_user(self, user_id: str, init_request: InitRequest) -> InitResponse:
        response = await self._make_request(
            "POST",
            "/v6/init",
            auth_type=AuthType.USER_ID,
            user_id=user_id,
            data=init_request.model_dump(exclude_none=True)
        )
        return InitResponse(**response.data)
    
    async def assign_condition(self, user_id: str, context: str) -> AssignResponse:
        assign_request = AssignRequest(context=context)
        response = await self._make_request(
            "POST",
            "/v6/assign",
            auth_type=AuthType.USER_ID,
            user_id=user_id,
            data=assign_request.model_dump(exclude_none=True)
        )
        # Response is directly an array of AssignmentResult  
        return [AssignmentResult(**item) for item in response.data] if response.data else []
    
    async def mark_decision_point(self, user_id: str, mark_request: MarkRequest) -> MarkResponse:
        response = await self._make_request(
            "POST",
            "/v6/mark",
            auth_type=AuthType.USER_ID,
            user_id=user_id,
            data=mark_request.model_dump(exclude_none=True)
        )
        return MarkResponse(**response.data)


# Create singleton instance
upgrade_api = UpGradeAPI()