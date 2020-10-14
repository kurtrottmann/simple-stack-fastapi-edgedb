from typing import Any
from uuid import UUID

from edgedb import AsyncIOConnection
from fastapi import APIRouter, Depends, HTTPException

from app import auth, crud, db, schemas

router = APIRouter()


@router.get("/", response_model=schemas.PaginatedItems)
async def read_items(
    con: AsyncIOConnection = Depends(db.get_con),
    filtering: schemas.ItemFilterParams = Depends(),
    commons: schemas.CommonQueryParams = Depends(),
    current_user: schemas.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Retrieve items.
    """
    if not current_user.is_superuser:
        filtering.owner__id = current_user.id
    items = await crud.item.get_multi(
        con,
        filtering=filtering.dict_exclude_unset(),
        ordering=commons.ordering,
        offset=commons.offset,
        limit=commons.limit,
    )
    return items


@router.post("/", response_model=schemas.Item, status_code=201)
async def create_item(
    *,
    con: AsyncIOConnection = Depends(db.get_con),
    item_in: schemas.ItemCreate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    item = await crud.item.create(con, obj_in=item_in, owner_id=current_user.id)
    return item


@router.put("/{item_id}", response_model=schemas.Item)
async def update_item(
    *,
    con: AsyncIOConnection = Depends(db.get_con),
    item_id: UUID,
    item_in: schemas.ItemUpdate,
    current_user: schemas.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    item = await crud.item.get(con, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner.id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = await crud.item.update(con, id=item_id, obj_in=item_in)
    return item


@router.get("/{item_id}", response_model=schemas.Item)
async def read_item(
    *,
    con: AsyncIOConnection = Depends(db.get_con),
    item_id: UUID,
    current_user: schemas.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Get item by id.
    """
    item = await crud.item.get(con, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner.id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.delete("/{item_id}", response_model=schemas.Item)
async def delete_item(
    *,
    con: AsyncIOConnection = Depends(db.get_con),
    item_id: UUID,
    current_user: schemas.User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    item = await crud.item.get(con, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner.id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = await crud.item.remove(con, id=item_id)
    return item
