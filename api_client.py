import os
from dataclasses import dataclass
from typing import Any

import httpx


class ShippingAPIError(Exception):
    """Raised when the Shipping API request fails."""



@dataclass
class ShippingAPIClient:
    base_url: str
    api_key: str
    timeout: float = 10.0

    @classmethod
    def from_env(cls) -> "ShippingAPIClient":
        return cls(
            base_url=os.getenv("SHIPPING_API_BASE_URL", "http://127.0.0.1:8000"),
            api_key = os.getenv("SHIPPING_API_KEY","demo-shipping-key"),



        )


    def _header(self) -> dict[str,str]:
        return {"X-API-KEY": self.api_key}

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str,Any] | None = None,
        json_data: dict[str,Any] |None = None,
            
    ) -> dict:
        url = f"{self.base_url}{path}"


        try:
            response = httpx.request(

                method= method,
                url=url,
                headers=self._header(),
                params=params,
                json=json_data,
                timeout=self.timeout,


            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as error:
            raise ShippingAPIError(f"API returned {error.response.status_code}: {error.response.text}") from error

        except httpx.RequestError as error:
            raise ShippingAPIError(f"Could not connect to Shipping API: {error}") from error

    def _get(self, path: str, params: dict[str, Any] | None = None,) -> dict:
        return self._request(method="GET", path=path, params=params) 

    def _post(self, path: str, json_data: dict[str, Any]) -> dict:
        return self._request(method="POST", path=path,json_data=json_data)

    def _patch(self, path:str, json_data: dict[str, Any]) -> dict:
        return self._request(method="PATCH", path=path, json_data=json_data)


    # -----------------------------------------------
    # System
    # ----------------------------------------------- 

    def health_check(self) -> dict:
        return self._get("/health")






    def get_shipments(self, status:str | None = None, branch_name: str | None = None ) -> dict:
        params={}

        if status:
            params["status"] = status

        if branch_name:
            params["branch_name"] = branch_name


        return self._get("/shipments", params=params)

    def get_delayed_shipments(self) -> dict:
        return self._get("/shipments/delayed")

    def get_returned_shipments(self) -> dict:
        return self._get("/shipments/returned")

    def get_shipments_by_id(self, shipment_id: str) -> dict:
        return self._get(f"/shipments/{shipment_id}")

    





    def create_shipment(self, shipment_data: dict[str, Any ]) -> dict:
        return self._post(path="/shipments", json_data=shipment_data)


    def update_shipment(self, shipment_id: str, updates: dict[str, Any]) -> dict:
        return self._patch(path=f"/shipments/{shipment_id}", json_data=updates)


    def change_shipment_status(self, shipment_id: str, status: str) -> dict:
        return self._patch(path=f"/shipments/{shipment_id}/status", json_data={"status": status })


    def reschedule_shipment(self, shipment_id: str, expected_deivery: str) -> dict:
        return self._patch(path=f"/shipments/{shipment_id}/schedule", json_data={"expected_delivery": expected_deivery})


    def cancel_shipment(self, shipment_id: str, reason: str) -> dict:
        return self._patch(path=f"/shipments/{shipment_id}/cancel", json_data={"reason": reason})







    def get_returns(self) -> dict:
        return self._get("/returns")






    def get_payments_summary(self) -> dict:
        return self._get("/payments/summary")







    def get_branches_performance(self) -> dict:
        return self._get("/branches/performance")






    def get_management_overview(self) -> dict:
        return self._get("/management/overview")

    
    








    