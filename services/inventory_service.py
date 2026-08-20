"""Inventory service module for managing inventory movements."""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import (
    User,
    Product,
    Department,
    CurrentInventory,
    InventoryMovement,
    Status,
)
from schemas import InventoryMovementValidation, ProductValidation, DepartmentValidation


def department_creation(
    department_validation: DepartmentValidation, login_confirmation: int, db: Session
):
    """Allow a administrator to create a department"""
    my_number_validation_administrator = (
        db.query(User).filter(User.my_number == login_confirmation).first()
    )
    if not my_number_validation_administrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if (
        my_number_validation_administrator.role_user != Status.ADMINISTRATOR
        or my_number_validation_administrator.is_active is False
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: only administrator can create department on plataform",
        )

    user = db.query(User).filter(User.id == department_validation.users_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.role_user != Status.MANAGER or user.is_active is False:
        raise HTTPException(
            status_code=400,
            detail="Only managers can be assigned to a department.",
        )

    new_department = Department(
        users_id=department_validation.users_id,
        department_title=department_validation.department_title,
    )
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return {"message": "Department created successfully."}


def product_creation(
    product_validation: ProductValidation, login_confirmation: int, db: Session
):
    """Allow a manager to create a product"""
    my_number_validation_manager = (
        db.query(User).filter(User.my_number == login_confirmation).first()
    )
    if not my_number_validation_manager:
        raise HTTPException(status_code=404, detail="manager not found")
    if (
        my_number_validation_manager.role_user != Status.MANAGER
        or my_number_validation_manager.is_active is False
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: only manager can create product on plataform",
        )

    new_product = Product(
        product_name=product_validation.product_name,
        base_price=product_validation.base_price,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product created successfully."}


def inventory_movement_creation(
    inventory_movement_validation: InventoryMovementValidation,
    login_confirmation: int,
    db: Session,
):
    """Allow a manager to move products in/out of inventory"""
    my_number_validation_manager = (
        db.query(User).filter(User.my_number == login_confirmation).first()
    )
    if not my_number_validation_manager:
        raise HTTPException(status_code=404, detail="manager not found")
    if (
        my_number_validation_manager.role_user != Status.MANAGER
        or my_number_validation_manager.is_active is False
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied: only manager can move products in/out of inventory",
        )

    product = (
        db.query(Product)
        .filter(Product.id == inventory_movement_validation.product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    department = (
        db.query(Department)
        .filter(Department.id == inventory_movement_validation.departments_id)
        .first()
    )
    if not department:
        raise HTTPException(status_code=404, detail="Department not found.")

    if inventory_movement_validation.movement_type not in ["IN", "OUT"]:
        raise HTTPException(
            status_code=400, detail="Invalid movement type. Must be 'IN' or 'OUT'."
        )

    inventory_record = (
        db.query(CurrentInventory)
        .filter(
            CurrentInventory.product_id == inventory_movement_validation.product_id,
            CurrentInventory.departments_id
            == inventory_movement_validation.departments_id,
        )
        .first()
    )

    if inventory_movement_validation.movement_type == "IN":
        if inventory_record:

            inventory_record.product_in_stock += inventory_movement_validation.quantity
        else:

            inventory_record = CurrentInventory(
                product_id=inventory_movement_validation.product_id,
                departments_id=inventory_movement_validation.departments_id,
                product_in_stock=inventory_movement_validation.quantity,
                product_to_come=0,
            )
            db.add(inventory_record)
            db.flush()

    elif inventory_movement_validation.movement_type == "OUT":
        if not inventory_record:
            raise HTTPException(
                status_code=404,
                detail="Inventory record not found. Cannot remove non-existent stock.",
            )
        if inventory_record.product_in_stock < inventory_movement_validation.quantity:
            raise HTTPException(
                status_code=400, detail="Insufficient stock for the requested movement."
            )

        inventory_record.product_in_stock -= inventory_movement_validation.quantity

    new_movement = InventoryMovement(
        current_inventory_id=inventory_record.id,
        movement_type=inventory_movement_validation.movement_type,
        quantity=inventory_movement_validation.quantity,
        unit_price_at_transaction=product.base_price,
    )
    db.add(new_movement)

    db.commit()
    db.refresh(inventory_record)

    return {
        "message": f"Inventory movement '{inventory_movement_validation.movement_type}' for product '{product.product_name}' processed successfully."
    }
