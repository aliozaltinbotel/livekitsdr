from typing import Dict, Any, List
from mcp.types import Tool, TextContent
from .api_client import PMSAPIClient
import json
import logging

logger = logging.getLogger(__name__)


class PMSTools:
    def __init__(self, api_client: PMSAPIClient):
        self.api_client = api_client
    
    def get_available_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            Tool(
                name="get_customer_properties_context",
                description="Fetch all properties for the customer and their detailed information to provide context to the LLM",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_inactive": {
                            "type": "boolean",
                            "description": "Include inactive properties (default: false)",
                            "default": False
                        }
                    }
                }
            ),
            Tool(
                name="check_property_availability_and_pricing",
                description="Check property availability and calculate pricing for specific dates and guest count",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "property_id": {
                            "type": "string",
                            "description": "The property ID to check"
                        },
                        "check_in_date": {
                            "type": "string",
                            "description": "Check-in date in YYYY-MM-DD format"
                        },
                        "check_out_date": {
                            "type": "string",
                            "description": "Check-out date in YYYY-MM-DD format"
                        },
                        "guest_count": {
                            "type": "integer",
                            "description": "Number of guests",
                            "minimum": 1
                        },
                        "include_pets": {
                            "type": "boolean",
                            "description": "Whether pets will be included (default: false)",
                            "default": False
                        }
                    },
                    "required": ["property_id", "check_in_date", "check_out_date", "guest_count"]
                }
            )
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a tool by name"""
        
        if name == "get_customer_properties_context":
            return await self._get_customer_properties_context(arguments)
        elif name == "check_property_availability_and_pricing":
            return await self._check_property_availability_and_pricing(arguments)
        
        raise ValueError(f"Unknown tool: {name}")
    
    async def _get_customer_properties_context(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Fetch all properties for the customer and provide detailed context
        """
        try:
            include_inactive = arguments.get("include_inactive", False)
            
            # Step 1: Get all properties for the customer using the GetAll endpoint
            # The customerId is already in the headers, so the API should filter automatically
            properties_response = await self.api_client.get("/api/Property/GetAll", params={
                "PageSize": 100,  # Get up to 100 properties
                "Status": None if include_inactive else True  # True = active only, None = all
            })
            
            if not properties_response or "items" not in properties_response:
                return [TextContent(
                    type="text",
                    text="No properties found for this customer."
                )]
            
            properties = properties_response.get("items", [])
            total_count = properties_response.get("totalCount", 0)
            
            # Step 2: Build context information
            context_parts = [
                f"Customer Property Context\n",
                f"Total Properties: {total_count}\n",
                f"Active Properties: {len([p for p in properties if p.get('status', False)])}\n\n"
            ]
            
            # Step 3: Get detailed information for each property
            for idx, property_summary in enumerate(properties, 1):
                property_id = property_summary.get("id")
                property_name = property_summary.get("name", "Unknown")
                property_status = "Active" if property_summary.get("status", False) else "Inactive"
                
                context_parts.append(f"Property {idx}: {property_name}\n")
                context_parts.append(f"Status: {property_status}\n")
                context_parts.append(f"ID: {property_id}\n")
                
                # Try to get more details for active properties
                if property_id and property_status == "Active":
                    try:
                        # Get full property details
                        property_detail = await self.api_client.get("/api/Property/Get", params={
                            "Id": property_id
                        })
                        
                        # Extract key information
                        if property_detail:
                            # Basic Location info
                            street = property_detail.get("street", "")
                            city = property_detail.get("city", "")
                            state = property_detail.get("state", "")
                            country = property_detail.get("countryCode", "")
                            address = property_detail.get("address", "")
                            zip_code = property_detail.get("zipCode", "")
                            
                            if any([street, city, state]):
                                full_address = ', '.join(filter(None, [address, street, city, state, zip_code, country]))
                                context_parts.append(f"Location: {full_address}\n")
                            
                            # Capacity and Accommodation info
                            max_occupancy = property_detail.get("maxOccupancy")
                            max_adults = property_detail.get("maxAdults")
                            bedrooms = property_detail.get("bedrooms")
                            bathrooms = property_detail.get("bathrooms")
                            beds = property_detail.get("beds")
                            
                            if max_occupancy:
                                context_parts.append(f"Max Occupancy: {max_occupancy} guests\n")
                            if max_adults:
                                context_parts.append(f"Max Adults: {max_adults}\n")
                            if bedrooms:
                                context_parts.append(f"Bedrooms: {bedrooms}\n")
                            if bathrooms:
                                context_parts.append(f"Bathrooms: {bathrooms}\n")
                            if beds:
                                context_parts.append(f"Beds: {beds}\n")
                            
                            # Property type and details
                            property_type = property_detail.get("typeCode")
                            if property_type:
                                context_parts.append(f"Type: {property_type}\n")
                            
                            # Check-in/Check-out times
                            check_in_from = property_detail.get("checkInFrom")
                            check_in_until = property_detail.get("checkInUntil")
                            check_out_from = property_detail.get("checkOutFrom")
                            check_out_until = property_detail.get("checkOutUntil")
                            
                            if check_in_from or check_in_until:
                                check_in_time = f"{check_in_from}" + (f"-{check_in_until}" if check_in_until != check_in_from else "")
                                context_parts.append(f"Check-in Time: {check_in_time}\n")
                            if check_out_from or check_out_until:
                                check_out_time = f"{check_out_from}" + (f"-{check_out_until}" if check_out_until != check_out_from else "")
                                context_parts.append(f"Check-out Time: {check_out_time}\n")
                            
                            # WiFi and Access Codes
                            wifi_network = property_detail.get("wifiNetwork")
                            wifi_password = property_detail.get("wifiPassword")
                            door_code = property_detail.get("doorCode")
                            lock_code = property_detail.get("lockCode")
                            
                            if wifi_network:
                                context_parts.append(f"WiFi Network: {wifi_network}\n")
                            if wifi_password:
                                context_parts.append(f"WiFi Password: {wifi_password}\n")
                            if door_code:
                                context_parts.append(f"Door Code: {door_code}\n")
                            if lock_code:
                                context_parts.append(f"Lock Code: {lock_code}\n")
                            
                            # Property Manager
                            property_manager = property_detail.get("propertyManager")
                            if property_manager:
                                context_parts.append(f"Property Manager: {property_manager}\n")
                            
                            # Pricing Settings
                            pricing_settings = property_detail.get("pricingSettings")
                            if pricing_settings:
                                base_price = pricing_settings.get("basePrice")
                                currency = pricing_settings.get("currency")
                                cleaning_fee = pricing_settings.get("cleaningFee")
                                security_deposit = pricing_settings.get("securityDepositFee")
                                pet_fee = pricing_settings.get("petFee")
                                extra_person_fee = pricing_settings.get("extraPersonFee")
                                
                                if base_price and currency:
                                    context_parts.append(f"Base Price: {currency} {base_price}/night\n")
                                if cleaning_fee:
                                    context_parts.append(f"Cleaning Fee: {currency} {cleaning_fee}\n")
                                if security_deposit:
                                    context_parts.append(f"Security Deposit: {currency} {security_deposit}\n")
                                if pet_fee:
                                    context_parts.append(f"Pet Fee: {currency} {pet_fee}\n")
                                if extra_person_fee:
                                    context_parts.append(f"Extra Person Fee: {currency} {extra_person_fee}\n")
                            
                            # Amenities
                            amenities = property_detail.get("amenities", [])
                            if amenities:
                                amenity_names = []
                                for amenity in amenities[:20]:  # Limit to first 20 amenities
                                    if isinstance(amenity, dict):
                                        amenity_name = amenity.get("attributes") or amenity.get("typeCode", "")
                                        if amenity_name:
                                            amenity_names.append(amenity_name)
                                
                                if amenity_names:
                                    context_parts.append(f"Amenities: {', '.join(amenity_names)}\n")
                                    if len(amenities) > 20:
                                        context_parts.append(f"  (and {len(amenities) - 20} more amenities)\n")
                            
                            # License info
                            license_code = property_detail.get("licenseCode")
                            if license_code:
                                context_parts.append(f"License: {license_code}\n")
                            
                            # Coordinates
                            lat = property_detail.get("latitude")
                            lon = property_detail.get("longitude")
                            if lat and lon:
                                context_parts.append(f"Coordinates: {lat}, {lon}\n")
                            
                            # Time Zone
                            time_zone = property_detail.get("timeZone")
                            if time_zone:
                                context_parts.append(f"Time Zone: {time_zone}\n")
                            
                            # Description (now showing full description for voice agent context)
                            descriptions = property_detail.get("descriptions", [])
                            if descriptions:
                                for desc in descriptions:
                                    if isinstance(desc, dict) and desc.get("text"):
                                        description_text = desc["text"]
                                        # Show first 500 chars of description
                                        desc_preview = description_text[:500] + "..." if len(description_text) > 500 else description_text
                                        context_parts.append(f"Description: {desc_preview}\n")
                                        break
                            
                            # Images count
                            images = property_detail.get("images", [])
                            if images:
                                context_parts.append(f"Images Available: {len(images)} photos\n")
                                
                    except Exception as e:
                        logger.warning(f"Could not fetch details for property {property_id}: {e}")
                
                context_parts.append("\n")
            
            # Step 4: Add summary statistics
            context_parts.append("Summary\n")
            context_parts.append(f"This customer has {total_count} properties in the system.\n")
            
            active_count = len([p for p in properties if p.get('status', False)])
            if active_count > 0:
                context_parts.append(f"{active_count} properties are currently active and available for bookings.\n")
            
            inactive_count = total_count - active_count
            if inactive_count > 0:
                context_parts.append(f"{inactive_count} properties are inactive.\n")
            
            # Join all parts into final context
            context_text = "".join(context_parts)
            
            return [TextContent(
                type="text",
                text=context_text
            )]
            
        except Exception as e:
            logger.error(f"Error in get_customer_properties_context: {e}")
            return [TextContent(
                type="text",
                text=f"Error fetching property context: {str(e)}"
            )]
    
    async def _check_property_availability_and_pricing(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Check property availability and calculate pricing for specific dates
        """
        try:
            from datetime import datetime
            
            # Extract arguments
            property_id = arguments.get("property_id")
            check_in_date = arguments.get("check_in_date")
            check_out_date = arguments.get("check_out_date")
            guest_count = arguments.get("guest_count", 1)
            include_pets = arguments.get("include_pets", False)
            
            # Validate dates
            try:
                check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
                
                if check_out <= check_in:
                    return [TextContent(
                        type="text",
                        text="Error: Check-out date must be after check-in date."
                    )]
                
                nights = (check_out - check_in).days
                
            except ValueError:
                return [TextContent(
                    type="text",
                    text="Error: Invalid date format. Please use YYYY-MM-DD format."
                )]
            
            # Step 1: Get property details including pricing
            property_detail = await self.api_client.get("/api/Property/Get", params={
                "Id": property_id
            })
            
            if not property_detail:
                return [TextContent(
                    type="text",
                    text=f"Property {property_id} not found."
                )]
            
            property_name = property_detail.get("name", "Unknown Property")
            max_occupancy = property_detail.get("maxOccupancy", 0)
            property_status = property_detail.get("status", False)
            
            # Check if property is active
            if not property_status:
                return [TextContent(
                    type="text",
                    text=f"Availability Check\n\nProperty: {property_name}\nStatus: This property is currently inactive and not available for bookings."
                )]
            
            # Check guest count
            if guest_count > max_occupancy:
                return [TextContent(
                    type="text",
                    text=f"Availability Check\n\nProperty: {property_name}\nError: This property has a maximum occupancy of {max_occupancy} guests. You requested {guest_count} guests."
                )]
            
            # Step 2: Check for existing reservations (basic availability)
            try:
                reservations_response = await self.api_client.get("/api/Reservation/Get", params={
                    "propertyId": property_id,
                    "pageSize": 1000  # Get many to check dates
                })
            except Exception as e:
                # If we get a 204 or other error, assume no reservations
                logger.debug(f"No reservations found or error checking: {e}")
                reservations_response = None
            
            is_available = True
            conflicting_dates = []
            
            if reservations_response and isinstance(reservations_response, dict) and "items" in reservations_response:
                reservations = reservations_response.get("items", [])
                
                for reservation in reservations:
                    # Skip cancelled reservations
                    if reservation.get("status") in ["Cancelled", "Declined"]:
                        continue
                    
                    res_checkin = reservation.get("checkIn")
                    res_checkout = reservation.get("checkOut")
                    
                    if res_checkin and res_checkout:
                        try:
                            res_in = datetime.strptime(res_checkin.split("T")[0], "%Y-%m-%d")
                            res_out = datetime.strptime(res_checkout.split("T")[0], "%Y-%m-%d")
                            
                            # Check for date overlap
                            if not (check_out <= res_in or check_in >= res_out):
                                is_available = False
                                conflicting_dates.append(f"{res_in.strftime('%Y-%m-%d')} to {res_out.strftime('%Y-%m-%d')}")
                        except:
                            continue
            
            # Step 3: Calculate pricing
            pricing_settings = property_detail.get("pricingSettings", {})
            base_price = pricing_settings.get("basePrice", 0)
            currency = pricing_settings.get("currency", "EUR")
            cleaning_fee = pricing_settings.get("cleaningFee", 0)
            security_deposit = pricing_settings.get("securityDepositFee", 0)
            pet_fee = pricing_settings.get("petFee", 0) if include_pets else 0
            extra_person_fee = pricing_settings.get("extraPersonFee", 0)
            guests_included = pricing_settings.get("guestsIncludedInRegularFee", 0)
            
            # Calculate accommodation cost
            accommodation_total = base_price * nights
            
            # Calculate extra person fees
            extra_persons = max(0, guest_count - guests_included) if guests_included > 0 else 0
            extra_person_total = extra_persons * extra_person_fee * nights
            
            # Calculate total
            subtotal = accommodation_total + extra_person_total
            total_cost = subtotal + cleaning_fee + pet_fee
            
            # Build response
            response_parts = [
                f"Availability and Pricing Check\n",
                f"\nProperty: {property_name}\n",
                f"Dates: {check_in_date} to {check_out_date} ({nights} nights)\n",
                f"Guests: {guest_count}\n"
            ]
            
            if include_pets:
                response_parts.append("Pets: Yes\n")
            
            response_parts.append("\nAvailability\n")
            
            if is_available:
                response_parts.append("Available - These dates are available for booking.\n")
            else:
                response_parts.append("Not Available - These dates conflict with existing bookings:\n")
                for conflict in conflicting_dates:
                    response_parts.append(f"   {conflict}\n")
            
            response_parts.append("\nPricing Breakdown\n")
            response_parts.append(f"Accommodation: {currency} {accommodation_total:,.2f} ({currency} {base_price}/night × {nights} nights)\n")
            
            if extra_person_total > 0:
                response_parts.append(f"Extra Person Fee: {currency} {extra_person_total:,.2f} ({extra_persons} extra persons × {currency} {extra_person_fee}/night × {nights} nights)\n")
            
            if cleaning_fee > 0:
                response_parts.append(f"Cleaning Fee: {currency} {cleaning_fee:,.2f}\n")
            
            if pet_fee > 0:
                response_parts.append(f"Pet Fee: {currency} {pet_fee:,.2f}\n")
            
            response_parts.append(f"\nTotal: {currency} {total_cost:,.2f}\n")
            
            if security_deposit and security_deposit > 0:
                response_parts.append(f"\nNote: A security deposit of {currency} {security_deposit:,.2f} may be required.\n")
            
            # Add booking instructions if available
            if is_available:
                response_parts.append("\nNext Steps\n")
                response_parts.append("This property is available for your requested dates. ")
                response_parts.append("To proceed with the booking, please confirm your details and we can help you complete the reservation.\\n")
            
            return [TextContent(
                type="text",
                text="".join(response_parts)
            )]
            
        except Exception as e:
            logger.error(f"Error in check_property_availability_and_pricing: {e}")
            return [TextContent(
                type="text",
                text=f"Error checking availability and pricing: {str(e)}"
            )]