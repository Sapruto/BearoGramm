from typing import Any, Optional, List, Tuple
from pydantic import BaseModel, Field

from ...types.base.base_message_data import BaseMessageData
from ...types.message_registry import MessageRegistry, get_message_registry

from src.core.logger import get_logger

logger = get_logger(__name__)

class ProcessDataResponse(BaseModel):
    success: bool = Field(...)
    processed_data: List[BaseMessageData] = Field(default_factory=list)
    error_message: Optional[str] = Field(default=None)

class DataProcessor:
    def __init__(self, message_registry: Optional[MessageRegistry] = None):
        self.message_registry = message_registry or get_message_registry()

    async def save_data(self, typing_to_data: List[Tuple[str, Any]]) -> ProcessDataResponse:
        processed = []

        for data_type, raw_data in typing_to_data:
            data_service = self.message_registry.get_data_service(data_type)
            if not data_service:
                return ProcessDataResponse(
                    success=False,
                    error_message=f"Unknown data type: {data_type}"
                )

            try:
                result_data = await data_service.save_data(raw_data)
                processed.append(result_data)

            except Exception as e:
                return ProcessDataResponse(
                    success=False,
                    error_message=f"Error creating {data_type}: {str(e)}"
                )

        return ProcessDataResponse(
            success=True,
            processed_data=processed
        )

    async def delete_data(self, processed_data: List[BaseMessageData]) -> None:
        for data in processed_data:
            data_service = self.message_registry.get_data_service(data.data_type)
            if not data_service:
                continue

            try:
                success = data_service.delete_data(data)
                if not success:
                    logger.error("Error in unprocess data")

            except Exception as e:
                logger.error(f"Error in unprocess_data: {e}")

    async def update_data(self, old_message_data: List[BaseMessageData], new_typing_to_data: List[Tuple[str, Any]]) -> ProcessDataResponse:
        old_data_copy = [data.model_copy(deep=True) for data in old_message_data]

        old_indices_by_type = {}
        for idx, data in enumerate(old_message_data):
            data_type = data.data_type
            if data_type not in old_indices_by_type:
                old_indices_by_type[data_type] = []
            old_indices_by_type[data_type].append(idx)

        new_data_by_type = {}
        for data_type, raw_data in new_typing_to_data:
            new_data_by_type[data_type] = raw_data

        result_data = list(old_message_data)
        processed_new_items = []
        rollback_needed = False
        error_message = None

        try:
            for data_type, raw_data in new_data_by_type.items():
                data_service = self.message_registry.get_data_service(data_type)
                if not data_service:
                    raise ValueError(f"Unknown data type: {data_type}")

                old_indices = old_indices_by_type.get(data_type, [])
                for idx in sorted(old_indices, reverse=True):
                    old_item = result_data[idx]
                    try:
                        success = await data_service.delete_data(old_item)
                        if not success:
                            logger.warning(f"Failed to unprocess {data_type}")
                    except Exception as e:
                        logger.error(f"Error unprocessing: {e}")
                    result_data.pop(idx)

                try:
                    new_item = await data_service.save_data(raw_data)
                    processed_new_items.append(new_item)
                    result_data.append(new_item)
                except Exception as e:
                    error_message = f"Error processing {data_type}: {str(e)}"
                    rollback_needed = True
                    break

            if not rollback_needed:
                return ProcessDataResponse(
                    success=True,
                    processed_data=result_data
                )
            else:
                raise ValueError(error_message)

        except Exception as e:
            logger.error(f"Reprocess failed: {e}")

            for new_item in processed_new_items:
                try:
                    data_service = self.message_registry.get_data_service(new_item.data_type)
                    if data_service:
                        await data_service.delete_data(new_item)
                except Exception as rollback_error:
                    logger.error(f"Rollback error: {rollback_error}")

            return ProcessDataResponse(
                success=False,
                processed_data=old_data_copy,
                error_message=str(e)
            )
