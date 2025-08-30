from typing import List
from uuid import UUID
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import (
    ProductIn,
    ProductOut,
    ProductUpdate,
    ProductUpdateOut,
)
from store.core.exceptions import NotFoundException, BaseException

class ProductUsecase:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient = db_client.get()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        product_model = ProductModel(**body.model_dump())
        doc = product_model.model_dump()
        doc["created_at"] = datetime.utcnow()

        try:
            await self.collection.insert_one(doc)
        except DuplicateKeyError:
            raise BaseException(
                message="Já existe um produto com esse identificador ou chave única."
            )

        return ProductOut(**doc)

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return ProductOut(**result)

    async def query(
        self,
        price_min: float | None = None,
        price_max: float | None = None,
    ) -> List[ProductOut]:
        # Monta filtro dinâmico de preço
        price_filter: dict = {}
        if price_min is not None:
            price_filter["$gt"] = price_min
        if price_max is not None:
            price_filter["$lt"] = price_max

        query_filter: dict = {}
        if price_filter:
            query_filter["price"] = price_filter

        cursor = self.collection.find(query_filter)
        return [ProductOut(**item) async for item in cursor]

    async def update(
        self, id: UUID, body: ProductUpdate
    ) -> ProductUpdateOut:
        # Prepara dados de atualização
        updates = body.model_dump(exclude_none=True)
        # Garante updated_at
        updates["updated_at"] = updates.get("updated_at", datetime.utcnow())

        result = await self.collection.find_one_and_update(
            {"id": id},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        return ProductUpdateOut(**result)

    async def delete(self, id: UUID) -> bool:
        result = await self.collection.delete_one({"id": id})
        if result.deleted_count == 0:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return True


product_usecase = ProductUsecase()


product_usecase = ProductUsecase()
