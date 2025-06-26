import httpx
from typing import Dict, Any, Optional, List, Union
import os
from urllib.parse import urljoin
import base64

class PMSAPIClient:
    def __init__(self, base_url: str = "https://pms.botel.ai", api_key: Optional[str] = None, customer_id: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key or os.getenv("PMS_API_KEY")
        self.customer_id = customer_id or os.getenv("PMS_CUSTOMER_ID", "ae0c85c5-7fa7-4e09-8a94-0df5da38e72e")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=60.0
        )
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "customerId": self.customer_id
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        
        # Handle 204 No Content responses
        if response.status_code == 204:
            return {}
            
        return response.json()
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if files:
            response = await self.client.post(endpoint, files=files, data=data)
        else:
            response = await self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    
    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.put(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        response = await self.client.delete(endpoint)
        response.raise_for_status()
        try:
            return response.json()
        except:
            return {"status": "success"}
    
    async def close(self):
        await self.client.aclose()
    
    # Channel endpoints
    async def get_channels(self) -> Dict[str, Any]:
        return await self.get("/api/Channel/Get")
    
    # Customer endpoints
    async def get_customer(self, **kwargs) -> Dict[str, Any]:
        """Get customer by Id, ChannelId, CustomerId, or StripeAccountId"""
        return await self.get("/api/Customer/Get", params=kwargs)
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Customer/Add", customer_data)
    
    async def update_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Customer/Update", customer_data)
    
    async def delete_customer(self, customer_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/Customer/Delete?id={customer_id}")
    
    async def get_customer_custom_fields(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetCustomFields", params={"customerId": customer_id})
    
    async def add_customer_custom_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Customer/AddCustomFields", data)
    
    async def get_customer_custom_channel(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetCustomChannel", params={"customerId": customer_id})
    
    async def get_customer_users(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetUsers", params={"customerId": customer_id})
    
    async def add_customer_channel(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Customer/AddCustomerChannel", data)
    
    async def add_customer_subscription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Customer/AddSubscription", data)
    
    async def update_customer_subscription(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Customer/UpdateSubscription", data)
    
    async def get_customer_subscription(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetSubscription", params={"customerId": customer_id})
    
    async def add_subscription_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Customer/AddSubscriptionPayment", data)
    
    async def get_user_properties(self, user_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetUserProperties", params={"userId": user_id})
    
    async def get_channel_properties(self, customer_id: int, channel_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetChannelProperties", params={"customerId": customer_id, "channelId": channel_id})
    
    async def update_customer_channel(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Customer/CustomerChannelUpdate", data)
    
    async def get_all_customer_channels(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetAllCustomerChannel", params={"customerId": customer_id})
    
    async def get_customer_upsell(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetCustomerUpsell", params={"customerId": customer_id})
    
    async def get_customers_by_channel_type(self, channel_type: int) -> Dict[str, Any]:
        return await self.get("/api/Customer/GetCustomersByChannelType", params={"channelType": channel_type})
    
    # CustomerContacts endpoints
    async def get_customer_contact(self, contact_id: int) -> Dict[str, Any]:
        return await self.get("/api/CustomerContacts/Get", params={"id": contact_id})
    
    async def create_customer_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/CustomerContacts/Add", contact_data)
    
    async def update_customer_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/CustomerContacts/Update", contact_data)
    
    async def delete_customer_contact(self, contact_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/CustomerContacts/Delete?id={contact_id}")
    
    async def search_customer_contacts(self, customer_id: int, page_index: int = 0, page_size: int = 10) -> Dict[str, Any]:
        return await self.get("/api/CustomerContacts/Search", params={
            "customerId": customer_id,
            "pageIndex": page_index,
            "pageSize": page_size
        })
    
    # CustomerDepartment endpoints
    async def get_customer_department(self, department_id: int) -> Dict[str, Any]:
        return await self.get("/api/CustomerDepartment/Get", params={"id": department_id})
    
    async def create_customer_department(self, department_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/CustomerDepartment/Add", department_data)
    
    async def update_customer_department(self, department_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/CustomerDepartment/Update", department_data)
    
    async def delete_customer_department(self, department_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/CustomerDepartment/Delete?id={department_id}")
    
    async def get_all_customer_departments(self) -> Dict[str, Any]:
        return await self.get("/api/CustomerDepartment/GetAll")
    
    async def get_departments_by_customer(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/CustomerDepartment/GetByCustomer", params={"customerId": customer_id})
    
    async def add_user_to_department(self, department_id: int, user_id: int) -> Dict[str, Any]:
        return await self.post("/api/CustomerDepartment/AddUser", {"departmentId": department_id, "userId": user_id})
    
    async def remove_user_from_department(self, department_id: int, user_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/CustomerDepartment/RemoveUser?departmentId={department_id}&userId={user_id}")
    
    # Property endpoints
    async def get_properties(self, customer_id: int, page_index: int = 0, page_size: int = 10) -> Dict[str, Any]:
        return await self.get("/api/Property/Get", params={
            "customerId": customer_id,
            "pageIndex": page_index,
            "pageSize": page_size
        })
    
    async def get_property(self, property_id: int) -> Dict[str, Any]:
        return await self.get("/api/Property/GetById", params={"id": property_id})
    
    async def get_property_by_id(self, property_id: int) -> Dict[str, Any]:
        return await self.get("/api/Property/Get", params={"id": property_id})
    
    async def create_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Property/Add", property_data)
    
    async def update_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Property/Update", property_data)
    
    async def delete_property(self, property_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/Property/Delete?id={property_id}")
    
    async def search_properties(self, **params) -> Dict[str, Any]:
        return await self.get("/api/Property/Search", params=params)
    
    async def get_property_availability(self, property_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
        return await self.get("/api/Property/GetAvailability", params={
            "propertyId": property_id,
            "startDate": start_date,
            "endDate": end_date
        })
    
    async def get_property_files(self, property_id: int, file_type: Optional[str] = None) -> Dict[str, Any]:
        params = {"propertyId": property_id}
        if file_type:
            params["fileType"] = file_type
        return await self.get("/api/Property/GetFiles", params=params)
    
    # Reservation endpoints
    async def get_reservations(self, **params) -> Dict[str, Any]:
        return await self.get("/api/Reservation/Get", params=params)
    
    async def get_reservation(self, reservation_id: int) -> Dict[str, Any]:
        return await self.get("/api/Reservation/GetById", params={"id": reservation_id})
    
    async def create_reservation(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Reservation/Add", reservation_data)
    
    async def update_reservation(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Reservation/Update", reservation_data)
    
    async def cancel_reservation(self, reservation_id: int) -> Dict[str, Any]:
        return await self.post(f"/api/Reservation/Cancel", {"reservationId": reservation_id})
    
    async def search_gap_reservations(self, reservation_id: int) -> Dict[str, Any]:
        return await self.get("/api/Reservation/SearchGapReservationsById", params={"id": reservation_id})
    
    async def approve_reservation(self, reservation_id: int, approved: bool, note: Optional[str] = None) -> Dict[str, Any]:
        data = {"reservationId": reservation_id, "approved": approved}
        if note:
            data["note"] = note
        return await self.post("/api/Reservation/Approval", data)
    
    async def add_reservation(self, reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Reservation/AddReservation", reservation_data)
    
    # Message endpoints
    async def get_messages(self, **params) -> Dict[str, Any]:
        return await self.get("/api/Message/Get", params=params)
    
    async def send_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Message/Send", message_data)
    
    async def get_message_history(self, customer_id: int, page_index: int = 0, page_size: int = 10) -> Dict[str, Any]:
        return await self.get("/api/Message/GetHistory", params={
            "customerId": customer_id,
            "pageIndex": page_index,
            "pageSize": page_size
        })
    
    # AI/CoPilot endpoints
    async def process_ai_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Message/CoPilotMessage", message_data)
    
    async def generate_ai_response(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Message/GenerateResponse", prompt_data)
    
    # Task endpoints
    async def get_tasks(self, **params) -> Dict[str, Any]:
        return await self.get("/api/Task/Get", params=params)
    
    async def get_task(self, task_id: int) -> Dict[str, Any]:
        return await self.get("/api/Task/GetById", params={"id": task_id})
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Task/Add", task_data)
    
    async def insert_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Task/Insert", task_data)
    
    async def update_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Task/Update", task_data)
    
    async def delete_task(self, task_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/Task/Delete?id={task_id}")
    
    async def complete_task(self, task_id: int) -> Dict[str, Any]:
        return await self.post("/api/Task/Complete", {"taskId": task_id})
    
    async def upload_task_image_base64(self, task_id: int, base64_image: str, filename: str) -> Dict[str, Any]:
        return await self.post("/api/Task/UploadBase64", {
            "taskId": task_id,
            "base64Image": base64_image,
            "filename": filename
        })
    
    # Review endpoints
    async def get_reviews(self, **params) -> Dict[str, Any]:
        return await self.get("/api/Review/Get", params=params)
    
    async def create_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Review/Add", review_data)
    
    async def respond_to_review(self, review_id: int, response: str) -> Dict[str, Any]:
        return await self.post("/api/Review/Respond", {"reviewId": review_id, "response": response})
    
    # User endpoints
    async def get_users(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/User/Get", params={"customerId": customer_id})
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        return await self.get("/api/User/GetById", params={"id": user_id})
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/User/Add", user_data)
    
    async def update_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/User/Update", user_data)
    
    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/User/Delete?id={user_id}")
    
    # Role endpoints
    async def get_roles(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Role/Get", params={"customerId": customer_id})
    
    async def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Role/Add", role_data)
    
    async def update_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Role/Update", role_data)
    
    async def delete_role(self, role_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/Role/Delete?id={role_id}")
    
    async def assign_role_to_user(self, user_id: int, role_id: int) -> Dict[str, Any]:
        return await self.post("/api/Role/AssignToUser", {"userId": user_id, "roleId": role_id})
    
    # Tag endpoints
    async def get_tags(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Tag/Get", params={"customerId": customer_id})
    
    async def create_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Tag/Add", tag_data)
    
    async def update_tag(self, tag_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Tag/Update", tag_data)
    
    async def delete_tag(self, tag_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/Tag/Delete?id={tag_id}")
    
    # RatePlan endpoints
    async def get_rate_plans(self, property_id: int) -> Dict[str, Any]:
        return await self.get("/api/RatePlan/Get", params={"propertyId": property_id})
    
    async def create_rate_plan(self, rate_plan_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/RatePlan/Add", rate_plan_data)
    
    async def update_rate_plan(self, rate_plan_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/RatePlan/Update", rate_plan_data)
    
    async def delete_rate_plan(self, rate_plan_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/RatePlan/Delete?id={rate_plan_id}")
    
    async def check_rate_plan_availability(self, property_id: int, start_date: str, end_date: str, guest_count: int) -> Dict[str, Any]:
        return await self.get("/api/RatePlan/CheckAvailability", params={
            "propertyId": property_id,
            "startDate": start_date,
            "endDate": end_date,
            "guestCount": guest_count
        })
    
    async def search_rate_plans(self, start_date: str, end_date: str, guest_count: int, **params) -> Dict[str, Any]:
        search_params = {
            "startDate": start_date,
            "endDate": end_date,
            "guestCount": guest_count
        }
        search_params.update(params)
        return await self.get("/api/RatePlan/Search", params=search_params)
    
    # KnowledgeBase endpoints
    async def get_knowledge_base(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/KnowledgeBase/Get", params={"customerId": customer_id})
    
    async def create_knowledge_base_entry(self, kb_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/KnowledgeBase/Add", kb_data)
    
    async def update_knowledge_base_entry(self, kb_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/KnowledgeBase/Update", kb_data)
    
    async def delete_knowledge_base_entry(self, kb_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/KnowledgeBase/Delete?id={kb_id}")
    
    async def generate_knowledge_base_from_url(self, url: str, customer_id: int) -> Dict[str, Any]:
        return await self.post("/api/KnowledgeBase/GenerateFromUrl", {"url": url, "customerId": customer_id})
    
    async def add_or_update_knowledge_base_message(self, kb_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/KnowledgeBase/AddOrUpdateMessage", kb_data)
    
    async def generate_botel_knowledge_base(self, customer_id: int) -> Dict[str, Any]:
        return await self.post("/api/KnowledgeBase/GenerateBotel", {"customerId": customer_id})
    
    # File endpoints
    async def upload_file_base64(self, file_data: str, filename: str, customer_id: int) -> Dict[str, Any]:
        return await self.post("/api/File/UploadBase64", {
            "fileData": file_data,
            "filename": filename,
            "customerId": customer_id
        })
    
    async def upload_file_multipart(self, file_path: str, customer_id: int) -> Dict[str, Any]:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            return await self.post("/api/File/UploadMultipart", data={"customerId": customer_id}, files=files)
    
    # Settings endpoints
    async def get_settings(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/Settings/Get", params={"customerId": customer_id})
    
    async def update_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Settings/Update", settings_data)
    
    # Permission endpoints
    async def get_permissions(self, role_id: int) -> Dict[str, Any]:
        return await self.get("/api/Permission/Get", params={"roleId": role_id})
    
    async def update_permissions(self, permission_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/Permission/Update", permission_data)
    
    # Stripe endpoints
    async def create_stripe_checkout_session(self, checkout_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/Stripe/CreateCheckoutSession", checkout_data)
    
    async def get_stripe_payment_status(self, session_id: str) -> Dict[str, Any]:
        return await self.get("/api/Stripe/GetPaymentStatus", params={"sessionId": session_id})
    
    # SavedMessageTemplates endpoints
    async def get_saved_message_templates(self, customer_id: int) -> Dict[str, Any]:
        return await self.get("/api/SavedMessageTemplates/Get", params={"customerId": customer_id})
    
    async def insert_saved_message_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/SavedMessageTemplates/Insert", template_data)
    
    async def update_saved_message_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.put("/api/SavedMessageTemplates/Update", template_data)
    
    async def delete_saved_message_template(self, template_id: int) -> Dict[str, Any]:
        return await self.delete(f"/api/SavedMessageTemplates/Delete?id={template_id}")
    
    # Cross-API complex operations
    async def get_customer_full_profile(self, customer_id: int) -> Dict[str, Any]:
        """Get complete customer profile including all related data"""
        customer = await self.get_customer(Id=customer_id)
        contacts = await self.search_customer_contacts(customer_id)
        departments = await self.get_departments_by_customer(customer_id)
        channels = await self.get_all_customer_channels(customer_id)
        subscription = await self.get_customer_subscription(customer_id)
        custom_fields = await self.get_customer_custom_fields(customer_id)
        
        return {
            "customer": customer,
            "contacts": contacts,
            "departments": departments,
            "channels": channels,
            "subscription": subscription,
            "customFields": custom_fields
        }
    
    async def get_property_full_details(self, property_id: int) -> Dict[str, Any]:
        """Get complete property details including rate plans and availability"""
        property_data = await self.get_property(property_id)
        rate_plans = await self.get_rate_plans(property_id)
        
        return {
            "property": property_data,
            "ratePlans": rate_plans
        }
    
    async def get_reservation_complete_info(self, reservation_id: int) -> Dict[str, Any]:
        """Get complete reservation information including property and customer details"""
        reservation = await self.get_reservation(reservation_id)
        
        if reservation.get("propertyId"):
            property_data = await self.get_property(reservation["propertyId"])
        else:
            property_data = None
            
        if reservation.get("customerId"):
            customer_data = await self.get_customer(Id=reservation["customerId"])
        else:
            customer_data = None
        
        return {
            "reservation": reservation,
            "property": property_data,
            "customer": customer_data
        }