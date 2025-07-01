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
            
            # Step 1: Get all properties for the customer using pagination to avoid timeouts
            # The customerId is already in the headers, so the API should filter automatically
            all_properties = []
            page_index = 1  # PMS API uses 1-based page indexing
            page_size = 100  # Smaller page size to prevent timeouts
            total_count = 0
            
            while True:
                try:
                    logger.info(f"Fetching properties page {page_index} (size: {page_size})")
                    properties_response = await self.api_client.get("/api/Property/GetAll", params={
                        "PageIndex": page_index,
                        "PageSize": page_size,
                        "Status": None if include_inactive else True  # True = active only, None = all
                    })
                    
                    if not properties_response or "items" not in properties_response:
                        break
                    
                    page_items = properties_response.get("items", [])
                    total_count = properties_response.get("totalCount", 0)
                    
                    if not page_items:
                        break
                    
                    all_properties.extend(page_items)
                    logger.info(f"Retrieved {len(page_items)} properties, total so far: {len(all_properties)}")
                    
                    # Check if we've fetched all properties
                    if len(all_properties) >= total_count or len(page_items) < page_size:
                        break
                    
                    page_index += 1
                    
                except Exception as e:
                    logger.error(f"Error fetching properties page {page_index}: {e}")
                    # Continue with what we have so far
                    break
            
            if not all_properties:
                return [TextContent(
                    type="text",
                    text="No properties found for this customer."
                )]
            
            properties = all_properties
            logger.info(f"Successfully fetched {len(properties)} out of {total_count} total properties")
            
            # Step 2: Build context information
            context_parts = [
                f"Customer Property Context\n",
                f"You have {total_count} properties in total.\n",
                f"{len([p for p in properties if p.get('status', False)])} properties are active.\n",
                f"{len([p for p in properties if not p.get('status', False)])} properties are inactive.\n\n"
            ]
            
            # Step 3: Get detailed information for each property
            for idx, property_summary in enumerate(properties, 1):
                property_id = property_summary.get("id")
                property_name = property_summary.get("name", "Unknown")
                property_status = "Active" if property_summary.get("status", False) else "Inactive"
                
                context_parts.append(f"\nProperty number {idx} is called {property_name}.\n")
                context_parts.append(f"This property is currently {property_status.lower()}.\n")
                context_parts.append(f"Property ID is {property_id}.\n")
                
                # Add internal name if different from display name
                internal_name = property_summary.get("internalName")
                if internal_name and internal_name != property_name:
                    context_parts.append(f"It is also known internally as {internal_name}.\n")
                
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
                            region = property_detail.get("region", "")
                            apt = property_detail.get("apt", "")
                            
                            if any([street, city, state, address]):
                                location_parts = []
                                if apt:
                                    location_parts.append(f"Apt {apt}")
                                location_parts.extend(filter(None, [address, street, city, state, zip_code, country]))
                                if region:
                                    location_parts.append(f"Region: {region}")
                                full_address = ', '.join(location_parts)
                                context_parts.append(f"The property is located at {full_address}.\n")
                            
                            # Capacity and Accommodation info
                            max_occupancy = property_detail.get("maxOccupancy")
                            max_adults = property_detail.get("maxAdults")
                            bedrooms = property_detail.get("bedrooms")
                            bathrooms = property_detail.get("bathrooms")
                            beds = property_detail.get("beds")
                            
                            if max_occupancy:
                                context_parts.append(f"The property can accommodate up to {max_occupancy} guests.\n")
                            if max_adults:
                                context_parts.append(f"Maximum {max_adults} adults allowed.\n")
                            if bedrooms:
                                context_parts.append(f"The property has {int(bedrooms)} bedrooms.\n")
                            if bathrooms:
                                context_parts.append(f"There are {bathrooms} bathrooms.\n")
                            if beds:
                                context_parts.append(f"The property has {int(beds)} beds.\n")
                            
                            # Property type and details
                            property_type = property_detail.get("typeCode")
                            if property_type:
                                context_parts.append(f"This is a {property_type}.\n")
                            
                            # Additional property details
                            classification = property_detail.get("classification")
                            if classification:
                                context_parts.append(f"Classification: {classification}\n")
                            
                            area_sqft = property_detail.get("areaSquareFeet")
                            if area_sqft:
                                context_parts.append(f"Area: {area_sqft} sq ft\n")
                            
                            min_occupancy = property_detail.get("minOccupancy")
                            if min_occupancy:
                                context_parts.append(f"Min Occupancy: {min_occupancy} guests\n")
                            
                            max_pets = property_detail.get("maxPets")
                            if max_pets is not None:
                                context_parts.append(f"Max Pets: {max_pets}\n")
                            
                            num_units = property_detail.get("numberOfUnits")
                            if num_units:
                                context_parts.append(f"Number of Units: {num_units}\n")
                            
                            # Check-in/Check-out times
                            check_in_from = property_detail.get("checkInFrom")
                            check_in_until = property_detail.get("checkInUntil")
                            check_out_from = property_detail.get("checkOutFrom")
                            check_out_until = property_detail.get("checkOutUntil")
                            
                            if check_in_from or check_in_until:
                                check_in_time = f"{check_in_from}" + (f"-{check_in_until}" if check_in_until != check_in_from else "")
                                context_parts.append(f"Check in time is {check_in_time}.\n")
                            if check_out_from or check_out_until:
                                check_out_time = f"{check_out_from}" + (f"-{check_out_until}" if check_out_until != check_out_from else "")
                                context_parts.append(f"Check out time is {check_out_time}.\n")
                            
                            # WiFi and Access Codes
                            wifi_network = property_detail.get("wifiNetwork")
                            wifi_password = property_detail.get("wifiPassword")
                            door_code = property_detail.get("doorCode")
                            lock_code = property_detail.get("lockCode")
                            
                            if wifi_network:
                                context_parts.append(f"The WiFi network name is {wifi_network}.\n")
                            if wifi_password:
                                context_parts.append(f"The WiFi password is {wifi_password}.\n")
                            if door_code:
                                context_parts.append(f"The door access code is {door_code}.\n")
                            if lock_code:
                                context_parts.append(f"The lock code is {lock_code}.\n")
                            
                            # Property Manager
                            property_manager = property_detail.get("propertyManager")
                            if property_manager:
                                context_parts.append(f"The property is managed by {property_manager}.\n")
                            
                            # Pricing Settings
                            pricing_settings = property_detail.get("pricingSettings")
                            if pricing_settings:
                                currency = pricing_settings.get("currency", "EUR")
                                base_price = pricing_settings.get("basePrice")
                                weekend_base_price = pricing_settings.get("weekendBasePrice")
                                cleaning_fee = pricing_settings.get("cleaningFee")
                                security_deposit = pricing_settings.get("securityDepositFee")
                                pet_fee = pricing_settings.get("petFee")
                                extra_person_fee = pricing_settings.get("extraPersonFee")
                                monthly_factor = pricing_settings.get("monthlyPriceFactor")
                                weekly_factor = pricing_settings.get("weeklyPriceFactor")
                                guests_included = pricing_settings.get("guestsIncludedInRegularFee")
                                weekend_days = pricing_settings.get("weekendDays")
                                
                                context_parts.append(f"\nHere is the pricing information.\n")
                                if base_price is not None:
                                    context_parts.append(f"The base price is {base_price} {currency} per night.\n")
                                if weekend_base_price and weekend_base_price > 0:
                                    context_parts.append(f"The weekend price is {weekend_base_price} {currency} per night.\n")
                                if weekend_days:
                                    context_parts.append(f"Weekend Days: {weekend_days}\n")
                                if cleaning_fee:
                                    context_parts.append(f"Cleaning Fee: {currency} {cleaning_fee}\n")
                                if security_deposit:
                                    context_parts.append(f"Security Deposit: {currency} {security_deposit}\n")
                                if pet_fee:
                                    context_parts.append(f"Pet Fee: {currency} {pet_fee}\n")
                                if extra_person_fee:
                                    context_parts.append(f"Extra Person Fee: {currency} {extra_person_fee}\n")
                                if guests_included is not None:
                                    context_parts.append(f"Guests Included in Base Price: {guests_included}\n")
                                if monthly_factor and monthly_factor != 1.0:
                                    context_parts.append(f"Monthly Discount: {(1 - monthly_factor) * 100:.0f}%\n")
                                if weekly_factor and weekly_factor != 1.0:
                                    context_parts.append(f"Weekly Discount: {(1 - weekly_factor) * 100:.0f}%\n")
                            
                            # Additional Fees and Taxes
                            fees = property_detail.get("fees", [])
                            if fees:
                                context_parts.append(f"\nAdditional Fees:\n")
                                for fee in fees:
                                    fee_name = fee.get("name", "Unknown Fee")
                                    fee_amount = fee.get("amount", 0)
                                    fee_type = fee.get("type", "")
                                    context_parts.append(f"  - {fee_name}: {currency} {fee_amount} ({fee_type})\n")
                            
                            taxes = property_detail.get("taxes", [])
                            if taxes:
                                context_parts.append(f"\nTaxes:\n")
                                for tax in taxes:
                                    tax_name = tax.get("name", "Unknown Tax")
                                    tax_rate = tax.get("rate", 0)
                                    context_parts.append(f"  {tax_name} is {tax_rate} percent.\n")
                            
                            # Amenities with full details
                            amenities = property_detail.get("amenities", [])
                            if amenities:
                                context_parts.append(f"\nThis property has {len(amenities)} amenities.\n")
                                
                                # Group amenities by category
                                amenity_categories = {}
                                for amenity in amenities:
                                    if isinstance(amenity, dict) and not amenity.get("isDeleted", False):
                                        type_code = amenity.get("typeCode", "OTHER")
                                        attributes = amenity.get("attributes", "")
                                        instruction = amenity.get("instruction", "")
                                        is_present = amenity.get("isPresent")
                                        
                                        # Determine category based on type code
                                        if "KITCHEN" in type_code or "REFRIGERATOR" in type_code or "OVEN" in type_code or "MICROWAVE" in type_code:
                                            category = "Kitchen"
                                        elif "BATHROOM" in type_code or "TUB" in type_code or "SHOWER" in type_code or "BIDET" in type_code:
                                            category = "Bathroom"
                                        elif "BEDROOM" in type_code or "BED" in type_code or "LINENS" in type_code:
                                            category = "Bedroom"
                                        elif "SAFETY" in type_code or "DETECTOR" in type_code or "EXTINGUISHER" in type_code or "FIRST_AID" in type_code:
                                            category = "Safety"
                                        elif "CHILD" in type_code or "BABY" in type_code or "INFANT" in type_code:
                                            category = "Family"
                                        elif "PARKING" in type_code or "GARAGE" in type_code:
                                            category = "Parking"
                                        elif "POOL" in type_code or "BEACH" in type_code or "WATERFRONT" in type_code:
                                            category = "Water Features"
                                        elif "INTERNET" in type_code or "WIFI" in type_code or "WIRELESS" in type_code:
                                            category = "Internet"
                                        elif "TV" in type_code or "CABLE" in type_code or "SOUND" in type_code or "VIDEO" in type_code:
                                            category = "Entertainment"
                                        elif "AIR_CONDITIONING" in type_code or "HEATING" in type_code or "FAN" in type_code:
                                            category = "Climate Control"
                                        elif "OUTDOOR" in type_code or "GARDEN" in type_code or "BALCONY" in type_code or "PATIO" in type_code:
                                            category = "Outdoor"
                                        else:
                                            category = "Other"
                                        
                                        if category not in amenity_categories:
                                            amenity_categories[category] = []
                                        
                                        amenity_info = attributes
                                        if instruction:
                                            amenity_info += f" (Note: {instruction})"
                                        if is_present is False:
                                            amenity_info += " [NOT PRESENT]"
                                        
                                        amenity_categories[category].append(amenity_info)
                                
                                # Display amenities by category
                                for category in sorted(amenity_categories.keys()):
                                    context_parts.append(f"  In the {category} category, there are {len(amenity_categories[category])} items.\n")
                                    for amenity in amenity_categories[category]:  # Show ALL amenities
                                        context_parts.append(f"    {amenity}\n")
                            
                            # License info
                            license_code = property_detail.get("licenseCode")
                            license_date = property_detail.get("licenseDate")
                            if license_code:
                                context_parts.append(f"License code is {license_code}")
                                if license_date:
                                    context_parts.append(f" issued on {license_date}")
                                context_parts.append("\n")
                            
                            # Currency info
                            base_currency = property_detail.get("baseCurrency")
                            if base_currency:
                                context_parts.append(f"The base currency is {base_currency}.\n")
                            
                            # Coordinates
                            lat = property_detail.get("latitude")
                            lon = property_detail.get("longitude")
                            if lat and lon:
                                context_parts.append(f"The property is located at latitude {lat} and longitude {lon}.\n")
                            
                            # Time Zone
                            time_zone = property_detail.get("timeZone")
                            if time_zone:
                                context_parts.append(f"The property is in the {time_zone} time zone.\n")
                            
                            # Description (showing FULL descriptions for voice agent context)
                            descriptions = property_detail.get("descriptions", [])
                            if descriptions:
                                context_parts.append(f"\nThe property has {len(descriptions)} descriptions.\n")
                                for desc_idx, desc in enumerate(descriptions, 1):
                                    if isinstance(desc, dict) and desc.get("text"):
                                        description_text = desc["text"]
                                        desc_type = desc.get("typeCode", "Unknown")
                                        desc_lang = desc.get("language", "Default")
                                        context_parts.append(f"  Description {desc_idx} (Type: {desc_type}, Language: {desc_lang}):\n")
                                        context_parts.append(f"  {description_text}\n\n")
                            
                            # Images count only (details removed per user request)
                            images = property_detail.get("images", [])
                            if images:
                                context_parts.append(f"\nTotal Images Available: {len(images)}\n")
                            
                            # Integrations (OTA connections)
                            integrations = property_detail.get("integrations", [])
                            if integrations:
                                context_parts.append(f"\nOTA Integrations:\n")
                                for integration in integrations:
                                    source = integration.get("source", "Unknown")
                                    ota_id = integration.get("otaId", "")
                                    ota_url = integration.get("otaUrl", "")
                                    if ota_id:
                                        context_parts.append(f"  - {source.title()}: ID {ota_id}\n")
                                    if ota_url:
                                        context_parts.append(f"    URL: {ota_url}\n")
                            
                            # Knowledge Base Status
                            knowledge_percentage = property_detail.get("knowledgePercentage")
                            knowledge_conflict = property_detail.get("knowledgeConflict")
                            knowledge_last_sync = property_detail.get("knowledgeLastSync")
                            conversation_rag = property_detail.get("conversationRagStatus")
                            document_rag = property_detail.get("documentRagStatus")
                            kb_rag_status = property_detail.get("knowledgeBaseRagStatus")
                            
                            if any([knowledge_percentage is not None, knowledge_conflict is not None, knowledge_last_sync]):
                                context_parts.append(f"\nKnowledge Base Status:\n")
                                if knowledge_percentage is not None:
                                    context_parts.append(f"  Completion: {knowledge_percentage}%\n")
                                if knowledge_conflict is not None:
                                    context_parts.append(f"  Conflicts: {knowledge_conflict}\n")
                                if knowledge_last_sync:
                                    context_parts.append(f"  Last Sync: {knowledge_last_sync}\n")
                                if conversation_rag is not None:
                                    context_parts.append(f"  Conversation RAG Status: {conversation_rag}\n")
                                if document_rag is not None:
                                    context_parts.append(f"  Document RAG Status: {document_rag}\n")
                                if kb_rag_status is not None:
                                    context_parts.append(f"  KB RAG Status: {'Active' if kb_rag_status else 'Inactive'}\n")
                            
                            # Channel and Listing Information
                            channel_code = property_detail.get("channelCode")
                            listing_id = property_detail.get("listingId")
                            customer_channel_id = property_detail.get("customerChannelId")
                            is_channel = property_detail.get("isChannel")
                            
                            if any([channel_code, listing_id, customer_channel_id, is_channel is not None]):
                                context_parts.append(f"\nChannel Information:\n")
                                if channel_code:
                                    context_parts.append(f"  Channel Code: {channel_code}\n")
                                if listing_id:
                                    context_parts.append(f"  Listing ID: {listing_id}\n")
                                if customer_channel_id:
                                    context_parts.append(f"  Customer Channel ID: {customer_channel_id}\n")
                                if is_channel is not None:
                                    context_parts.append(f"  Is Channel: {'Yes' if is_channel else 'No'}\n")
                            
                            # Booking Settings
                            booking_settings = property_detail.get("bookingSettings")
                            if booking_settings:
                                context_parts.append(f"\nBooking Settings:\n")
                                for key, value in booking_settings.items():
                                    if value is not None:
                                        context_parts.append(f"  {key}: {value}\n")
                            
                            # Nearest Places
                            nearest_places = property_detail.get("nearestPlaces")
                            if nearest_places:
                                context_parts.append(f"\nNearby Attractions:\n")
                                for place in nearest_places:
                                    place_name = place.get("name", "Unknown")
                                    distance = place.get("distance", "")
                                    context_parts.append(f"  - {place_name}: {distance}\n")
                            
                            # Custom Fields
                            custom_fields = property_detail.get("customFields", [])
                            if custom_fields:
                                context_parts.append(f"\nCustom Fields:\n")
                                for field in custom_fields:
                                    field_name = field.get("name", "Unknown Field")
                                    field_value = field.get("value", "")
                                    context_parts.append(f"  {field_name}: {field_value}\n")
                            
                            # Tags
                            tags = property_detail.get("tags", [])
                            if tags:
                                tag_names = [tag.get("name", "") for tag in tags if tag.get("name")]
                                if tag_names:
                                    context_parts.append(f"\nTags: {', '.join(tag_names)}\n")
                            
                            # Files
                            files = property_detail.get("files", [])
                            if files:
                                context_parts.append(f"\nAdditional Files ({len(files)} total):\n")
                                for file in files:
                                    file_name = file.get("name", "Unknown")
                                    file_type = file.get("type", "")
                                    file_url = file.get("url", "")
                                    file_size = file.get("size", "")
                                    context_parts.append(f"  - {file_name}")
                                    if file_type:
                                        context_parts.append(f" (Type: {file_type})")
                                    if file_size:
                                        context_parts.append(f" [Size: {file_size}]")
                                    context_parts.append("\n")
                                    if file_url:
                                        context_parts.append(f"    URL: {file_url}\n")
                            
                            # Sub-rooms
                            sub_rooms = property_detail.get("subRooms", [])
                            if sub_rooms:
                                context_parts.append(f"\nSub-rooms/Units ({len(sub_rooms)} total):\n")
                                for room in sub_rooms:  # Show ALL sub-rooms
                                    room_name = room.get("name", "Unnamed Room")
                                    room_type = room.get("type", "")
                                    room_id = room.get("id", "")
                                    room_desc = room.get("description", "")
                                    context_parts.append(f"  - {room_name}")
                                    if room_type:
                                        context_parts.append(f" (Type: {room_type})")
                                    if room_id:
                                        context_parts.append(f" [ID: {room_id}]")
                                    context_parts.append("\n")
                                    if room_desc:
                                        context_parts.append(f"    Description: {room_desc}\n")
                                
                    except Exception as e:
                        logger.warning(f"Could not fetch details for property {property_id}: {e}")
                
                context_parts.append("\n")
            
            # Step 4: Add comprehensive summary statistics
            context_parts.append("\n" + "=" * 50 + "\n")
            context_parts.append("SUMMARY & STATISTICS\n")
            context_parts.append("=" * 50 + "\n")
            
            context_parts.append(f"Total Properties: {total_count}\n")
            
            active_count = len([p for p in properties if p.get('status', False)])
            inactive_count = total_count - active_count
            context_parts.append(f"Status Breakdown:\n")
            context_parts.append(f"  - Active: {active_count} properties\n")
            context_parts.append(f"  - Inactive: {inactive_count} properties\n")
            
            # Property types summary
            property_types = {}
            for prop in properties:
                prop_type = prop.get('typeCode', 'Unknown')
                property_types[prop_type] = property_types.get(prop_type, 0) + 1
            
            if property_types:
                context_parts.append(f"\nProperty Types:\n")
                for ptype, count in property_types.items():
                    context_parts.append(f"  - {ptype}: {count}\n")
            
            # Location summary
            cities = {}
            for prop in properties:
                city = prop.get('city', 'Unknown')
                if city:
                    cities[city] = cities.get(city, 0) + 1
            
            if cities:
                context_parts.append(f"\nLocations:\n")
                for city, count in cities.items():
                    context_parts.append(f"  - {city}: {count} properties\n")
            
            # Capacity summary
            total_max_occupancy = sum(p.get('maxOccupancy', 0) for p in properties if p.get('maxOccupancy'))
            total_bedrooms = sum(p.get('bedrooms', 0) for p in properties if p.get('bedrooms'))
            
            if total_max_occupancy > 0:
                context_parts.append(f"\nTotal Capacity:\n")
                context_parts.append(f"  - Combined Max Occupancy: {total_max_occupancy} guests\n")
                context_parts.append(f"  - Total Bedrooms: {total_bedrooms}\n")
            
            # Integration summary
            integrations_count = {}
            for prop in properties:
                for integration in prop.get('integrations', []):
                    source = integration.get('source', 'unknown')
                    integrations_count[source] = integrations_count.get(source, 0) + 1
            
            if integrations_count:
                context_parts.append(f"\nOTA Integrations:\n")
                for source, count in integrations_count.items():
                    context_parts.append(f"  - {source.title()}: {count} properties\n")
            
            # Knowledge base summary
            kb_complete = len([p for p in properties if p.get('knowledgePercentage', 0) >= 80])
            kb_partial = len([p for p in properties if 0 < p.get('knowledgePercentage', 0) < 80])
            kb_empty = len([p for p in properties if p.get('knowledgePercentage', 0) == 0])
            
            context_parts.append(f"\nKnowledge Base Completion:\n")
            context_parts.append(f"  - Complete (80%+): {kb_complete} properties\n")
            context_parts.append(f"  - Partial (1-79%): {kb_partial} properties\n")
            context_parts.append(f"  - Empty (0%): {kb_empty} properties\n")
            
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