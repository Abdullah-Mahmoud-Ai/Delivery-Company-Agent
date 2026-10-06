import json
from datetime import date
from pathlib import Path
from typing import Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field


API_KEY = "demo-shipping-key"
DATA_DIR = Path(__file__).parent / "data"

ShipmentStatus = Literal[
    "delivered",
    "in_transit",
    "delayed",
    "returned",
    "cancelled",
]


app = FastAPI(
    title="Shipping API Mock Server",
    description=(
        "Mock API for a delivery company used in the Pydantic AI course. "
        "It provides shipment, payment, return, branch performance, and management operations."
    ),
    version="2.0.0",
    openapi_tags=[
        {
            "name": "System",
            "description": "Health check and server status.",
        },
        {
            "name": "Shipments",
            "description": "Read, create, update, reschedule, cancel, and track shipments.",
        },
        {
            "name": "Returns",
            "description": "Returned shipment records and return reasons.",
        },
        {
            "name": "Payments",
            "description": "Payment records and financial summaries.",
        },
        {
            "name": "Branches",
            "description": "Branch data and operational performance.",
        },
        {
            "name": "Management",
            "description": "High-level operational overview for management.",
        },
    ],
)


# ---------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# ---------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------

class CreateShipmentRequest(BaseModel):
    customer_id: str = Field(
        examples=["CUST-1001"],
        description="Customer ID.",
    )
    customer_name: str = Field(
        examples=["Ahmed Ali"],
        description="Customer full name.",
    )
    branch_id: str = Field(
        examples=["BR-001"],
        description="Branch ID responsible for the shipment.",
    )
    branch_name: str = Field(
        examples=["Riyadh"],
        description="Branch name responsible for the shipment.",
    )
    origin_city: str = Field(
        examples=["Riyadh"],
        description="Shipment origin city.",
    )
    destination_city: str = Field(
        examples=["Jeddah"],
        description="Shipment destination city.",
    )
    expected_delivery: date = Field(
        examples=["2026-07-25"],
        description="Expected delivery date in YYYY-MM-DD format.",
    )
    amount: float = Field(
        gt=0,
        examples=[150.0],
        description="Shipment amount.",
    )
    weight_kg: float = Field(
        gt=0,
        examples=[4.5],
        description="Shipment weight in kilograms.",
    )


class UpdateShipmentRequest(BaseModel):
    customer_name: Optional[str] = Field(
        default=None,
        examples=["Ahmed Mohammed"],
        description="Updated customer name.",
    )
    destination_city: Optional[str] = Field(
        default=None,
        examples=["Dammam"],
        description="Updated destination city.",
    )
    expected_delivery: Optional[date] = Field(
        default=None,
        examples=["2026-07-28"],
        description="Updated expected delivery date.",
    )
    amount: Optional[float] = Field(
        default=None,
        gt=0,
        examples=[180.0],
        description="Updated shipment amount.",
    )
    weight_kg: Optional[float] = Field(
        default=None,
        gt=0,
        examples=[6.2],
        description="Updated shipment weight in kilograms.",
    )


class ChangeShipmentStatusRequest(BaseModel):
    status: ShipmentStatus = Field(
        examples=["delayed"],
        description="New shipment status.",
    )


class RescheduleShipmentRequest(BaseModel):
    expected_delivery: date = Field(
        examples=["2026-07-30"],
        description="New expected delivery date.",
    )


class CancelShipmentRequest(BaseModel):
    reason: str = Field(
        min_length=3,
        examples=["Customer refused to receive the shipment"],
        description="Clear reason for cancelling the shipment.",
    )


# ---------------------------------------------------------------------
# Data Helpers
# ---------------------------------------------------------------------

def load_json(filename: str):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Data file not found: {filename}",
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(filename: str, data):
    file_path = DATA_DIR / filename

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_shipments_data():
    return load_json("shipments.json")


def get_branches_data():
    return load_json("branches.json")


def get_payments_data():
    return load_json("payments.json")


def get_returns_data():
    return load_json("returns.json")


def generate_shipment_id(shipments: list[dict]) -> str:
    numbers = [
        int(shipment["shipment_id"].replace("SHP-", ""))
        for shipment in shipments
        if shipment.get("shipment_id", "").startswith("SHP-")
    ]

    next_number = max(numbers, default=1000) + 1
    return f"SHP-{next_number}"


def find_shipment_or_404(shipments: list[dict], shipment_id: str) -> dict:
    for shipment in shipments:
        if shipment["shipment_id"] == shipment_id:
            return shipment

    raise HTTPException(status_code=404, detail="Shipment not found")


# ---------------------------------------------------------------------
# System
# ---------------------------------------------------------------------

@app.get(
    "/health",
    tags=["System"],
    summary="Check API health",
)
def health_check():
    return {
        "status": "ok",
        "message": "Shipping API Mock Server is running",
    }


# ---------------------------------------------------------------------
# Shipments - Read
# ---------------------------------------------------------------------

@app.get(
    "/shipments",
    tags=["Shipments"],
    summary="Get shipments",
    description="Returns shipments with optional filters by status and branch name.",
    dependencies=[Depends(verify_api_key)],
)
def get_shipments(
    status: Optional[ShipmentStatus] = Query(
        default=None,
        description="Filter shipments by status.",
    ),
    branch_name: Optional[str] = Query(
        default=None,
        description="Filter shipments by branch name.",
    ),
):
    shipments = get_shipments_data()

    if status:
        shipments = [
            shipment for shipment in shipments
            if shipment["status"].lower() == status.lower()
        ]

    if branch_name:
        shipments = [
            shipment for shipment in shipments
            if shipment["branch_name"].lower() == branch_name.lower()
        ]

    return {
        "count": len(shipments),
        "shipments": shipments,
    }


@app.get(
    "/shipments/delayed",
    tags=["Shipments"],
    summary="Get delayed shipments",
    description="Returns all shipments with delayed status.",
    dependencies=[Depends(verify_api_key)],
)
def get_delayed_shipments():
    shipments = get_shipments_data()

    delayed_shipments = [
        shipment for shipment in shipments
        if shipment["status"] == "delayed"
    ]

    return {
        "count": len(delayed_shipments),
        "shipments": delayed_shipments,
    }


@app.get(
    "/shipments/returned",
    tags=["Shipments"],
    summary="Get returned shipments",
    description="Returns returned shipment records.",
    dependencies=[Depends(verify_api_key)],
)
def get_returned_shipments():
    returns = get_returns_data()

    return {
        "count": len(returns),
        "returned_shipments": returns,
    }


@app.get(
    "/shipments/{shipment_id}",
    tags=["Shipments"],
    summary="Get shipment by ID",
    description="Returns details for a specific shipment.",
    dependencies=[Depends(verify_api_key)],
)
def get_shipment_by_id(shipment_id: str):
    shipments = get_shipments_data()
    return find_shipment_or_404(shipments, shipment_id)


# ---------------------------------------------------------------------
# Shipments - Write Operations
# ---------------------------------------------------------------------

@app.post(
    "/shipments",
    tags=["Shipments"],
    summary="Create a new shipment",
    description="Creates a new shipment and stores it in shipments.json.",
    dependencies=[Depends(verify_api_key)],
)
def create_shipment(payload: CreateShipmentRequest):
    shipments = get_shipments_data()

    new_shipment = {
        "shipment_id": generate_shipment_id(shipments),
        "customer_id": payload.customer_id,
        "customer_name": payload.customer_name,
        "branch_id": payload.branch_id,
        "branch_name": payload.branch_name,
        "origin_city": payload.origin_city,
        "destination_city": payload.destination_city,
        "status": "in_transit",
        "created_at": date.today().isoformat(),
        "expected_delivery": payload.expected_delivery.isoformat(),
        "delivered_at": None,
        "amount": payload.amount,
        "weight_kg": payload.weight_kg,
    }

    shipments.append(new_shipment)
    save_json("shipments.json", shipments)

    return {
        "message": "Shipment created successfully",
        "shipment": new_shipment,
    }


@app.patch(
    "/shipments/{shipment_id}",
    tags=["Shipments"],
    summary="Update shipment details",
    description="Updates editable shipment fields such as customer name, destination, amount, weight, or expected delivery date.",
    dependencies=[Depends(verify_api_key)],
)
def update_shipment(shipment_id: str, payload: UpdateShipmentRequest):
    shipments = get_shipments_data()
    shipment = find_shipment_or_404(shipments, shipment_id)

    updates = payload.model_dump(exclude_none=True)

    if "expected_delivery" in updates:
        updates["expected_delivery"] = updates["expected_delivery"].isoformat()

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No update fields were provided",
        )

    shipment.update(updates)
    save_json("shipments.json", shipments)

    return {
        "message": "Shipment updated successfully",
        "updated_fields": list(updates.keys()),
        "shipment": shipment,
    }


@app.patch(
    "/shipments/{shipment_id}/status",
    tags=["Shipments"],
    summary="Change shipment status",
    description="Changes the shipment status to delivered, in_transit, delayed, returned, or cancelled.",
    dependencies=[Depends(verify_api_key)],
)
def change_shipment_status(
    shipment_id: str,
    payload: ChangeShipmentStatusRequest,
):
    shipments = get_shipments_data()
    shipment = find_shipment_or_404(shipments, shipment_id)

    shipment["status"] = payload.status

    if payload.status == "delivered":
        shipment["delivered_at"] = date.today().isoformat()

    if payload.status != "cancelled":
        shipment.pop("cancellation_reason", None)
        shipment.pop("cancelled_at", None)

    save_json("shipments.json", shipments)

    return {
        "message": "Shipment status changed successfully",
        "shipment": shipment,
    }


@app.patch(
    "/shipments/{shipment_id}/schedule",
    tags=["Shipments"],
    summary="Reschedule shipment delivery",
    description="Updates the expected delivery date for a shipment.",
    dependencies=[Depends(verify_api_key)],
)
def reschedule_shipment(
    shipment_id: str,
    payload: RescheduleShipmentRequest,
):
    shipments = get_shipments_data()
    shipment = find_shipment_or_404(shipments, shipment_id)

    old_expected_delivery = shipment.get("expected_delivery")
    shipment["expected_delivery"] = payload.expected_delivery.isoformat()

    save_json("shipments.json", shipments)

    return {
        "message": "Shipment rescheduled successfully",
        "old_expected_delivery": old_expected_delivery,
        "new_expected_delivery": shipment["expected_delivery"],
        "shipment": shipment,
    }


@app.patch(
    "/shipments/{shipment_id}/cancel",
    tags=["Shipments"],
    summary="Cancel shipment with reason",
    description="Soft-cancels a shipment by changing its status to cancelled and storing a cancellation reason.",
    dependencies=[Depends(verify_api_key)],
)
def cancel_shipment(
    shipment_id: str,
    payload: CancelShipmentRequest,
):
    shipments = get_shipments_data()
    shipment = find_shipment_or_404(shipments, shipment_id)

    if shipment["status"] == "delivered":
        raise HTTPException(
            status_code=400,
            detail="Delivered shipments cannot be cancelled",
        )

    shipment["status"] = "cancelled"
    shipment["cancellation_reason"] = payload.reason
    shipment["cancelled_at"] = date.today().isoformat()

    save_json("shipments.json", shipments)

    return {
        "message": "Shipment cancelled successfully",
        "shipment": shipment,
    }


# ---------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------

@app.get(
    "/returns",
    tags=["Returns"],
    summary="Get returns",
    description="Returns all shipment return records.",
    dependencies=[Depends(verify_api_key)],
)
def get_returns():
    returns = get_returns_data()

    return {
        "count": len(returns),
        "returns": returns,
    }


# ---------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------

@app.get(
    "/branches",
    tags=["Branches"],
    summary="Get branches",
    description="Returns all delivery company branches.",
    dependencies=[Depends(verify_api_key)],
)
def get_branches():
    branches = get_branches_data()

    return {
        "count": len(branches),
        "branches": branches,
    }


@app.get(
    "/branches/performance",
    tags=["Branches"],
    summary="Get branches performance",
    description="Returns operational performance metrics for all branches.",
    dependencies=[Depends(verify_api_key)],
)
def get_branches_performance():
    branches = get_branches_data()
    shipments = get_shipments_data()
    payments = get_payments_data()
    returns = get_returns_data()

    performance = []

    for branch in branches:
        branch_id = branch["branch_id"]

        branch_shipments = [
            shipment for shipment in shipments
            if shipment["branch_id"] == branch_id
        ]

        branch_payments = [
            payment for payment in payments
            if payment["branch_id"] == branch_id
        ]

        branch_returns = [
            item for item in returns
            if item["branch_id"] == branch_id
        ]

        delivered_count = sum(
            1 for shipment in branch_shipments
            if shipment["status"] == "delivered"
        )

        delayed_count = sum(
            1 for shipment in branch_shipments
            if shipment["status"] == "delayed"
        )

        cancelled_count = sum(
            1 for shipment in branch_shipments
            if shipment["status"] == "cancelled"
        )

        returned_count = len(branch_returns)

        paid_revenue = sum(
            payment["amount"] for payment in branch_payments
            if payment["status"] == "paid"
        )

        performance.append(
            {
                "branch_id": branch_id,
                "branch_name": branch["name"],
                "city": branch["city"],
                "total_shipments": len(branch_shipments),
                "delivered_shipments": delivered_count,
                "delayed_shipments": delayed_count,
                "returned_shipments": returned_count,
                "cancelled_shipments": cancelled_count,
                "paid_revenue": round(paid_revenue, 2),
            }
        )

    return {
        "count": len(performance),
        "branches_performance": performance,
    }


# ---------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------

@app.get(
    "/payments",
    tags=["Payments"],
    summary="Get payments",
    description="Returns payment records with optional filters by status and branch name.",
    dependencies=[Depends(verify_api_key)],
)
def get_payments(
    status: Optional[str] = Query(
        default=None,
        description="Filter payments by status.",
    ),
    branch_name: Optional[str] = Query(
        default=None,
        description="Filter payments by branch name.",
    ),
):
    payments = get_payments_data()

    if status:
        payments = [
            payment for payment in payments
            if payment["status"].lower() == status.lower()
        ]

    if branch_name:
        payments = [
            payment for payment in payments
            if payment["branch_name"].lower() == branch_name.lower()
        ]

    return {
        "count": len(payments),
        "payments": payments,
    }


@app.get(
    "/payments/summary",
    tags=["Payments"],
    summary="Get payments summary",
    description="Returns paid, pending, and refunded payment totals.",
    dependencies=[Depends(verify_api_key)],
)
def get_payments_summary():
    payments = get_payments_data()

    total_paid = sum(
        payment["amount"] for payment in payments
        if payment["status"] == "paid"
    )

    total_pending = sum(
        payment["amount"] for payment in payments
        if payment["status"] == "pending"
    )

    total_refunded = sum(
        payment["amount"] for payment in payments
        if payment["status"] == "refunded"
    )

    return {
        "total_payments": len(payments),
        "paid_amount": round(total_paid, 2),
        "pending_amount": round(total_pending, 2),
        "refunded_amount": round(total_refunded, 2),
    }


# ---------------------------------------------------------------------
# Management
# ---------------------------------------------------------------------

@app.get(
    "/management/overview",
    tags=["Management"],
    summary="Get management overview",
    description="Returns a high-level operational summary for management.",
    dependencies=[Depends(verify_api_key)],
)
def get_management_overview():
    shipments = get_shipments_data()
    payments = get_payments_data()
    returns = get_returns_data()

    total_shipments = len(shipments)

    delayed_count = sum(
        1 for shipment in shipments
        if shipment["status"] == "delayed"
    )

    delivered_count = sum(
        1 for shipment in shipments
        if shipment["status"] == "delivered"
    )

    in_transit_count = sum(
        1 for shipment in shipments
        if shipment["status"] == "in_transit"
    )

    cancelled_count = sum(
        1 for shipment in shipments
        if shipment["status"] == "cancelled"
    )

    returned_count = len(returns)

    paid_revenue = sum(
        payment["amount"] for payment in payments
        if payment["status"] == "paid"
    )

    pending_revenue = sum(
        payment["amount"] for payment in payments
        if payment["status"] == "pending"
    )

    return {
        "total_shipments": total_shipments,
        "delivered_shipments": delivered_count,
        "in_transit_shipments": in_transit_count,
        "delayed_shipments": delayed_count,
        "returned_shipments": returned_count,
        "cancelled_shipments": cancelled_count,
        "paid_revenue": round(paid_revenue, 2),
        "pending_revenue": round(pending_revenue, 2),
    }