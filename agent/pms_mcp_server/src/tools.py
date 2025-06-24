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
            )
        ]
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute a tool by name"""
        
        if name == "get_customer_properties_context":
            return await self._get_customer_properties_context(arguments)
        
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
                f"# Customer Property Context\n",
                f"Total Properties: {total_count}\n",
                f"Active Properties: {len([p for p in properties if p.get('status', False)])}\n\n"
            ]
            
            # Step 3: Get detailed information for each property
            for idx, property_summary in enumerate(properties, 1):
                property_id = property_summary.get("id")
                property_name = property_summary.get("name", "Unknown")
                property_status = "Active" if property_summary.get("status", False) else "Inactive"
                
                context_parts.append(f"## Property {idx}: {property_name}\n")
                context_parts.append(f"- **Status**: {property_status}\n")
                context_parts.append(f"- **ID**: {property_id}\n")
                
                # Try to get more details for active properties
                if property_id and property_status == "Active":
                    try:
                        # Get full property details
                        property_detail = await self.api_client.get("/api/Property/Get", params={
                            "Id": property_id
                        })
                        
                        # Extract key information
                        if property_detail:
                            # Location info
                            street = property_detail.get("street", "")
                            city = property_detail.get("city", "")
                            state = property_detail.get("state", "")
                            country = property_detail.get("countryCode", "")
                            
                            if any([street, city, state]):
                                context_parts.append(f"- **Location**: {', '.join(filter(None, [street, city, state, country]))}\n")
                            
                            # Capacity info
                            max_occupancy = property_detail.get("maxOccupancy")
                            max_adults = property_detail.get("maxAdults")
                            if max_occupancy:
                                context_parts.append(f"- **Max Occupancy**: {max_occupancy} guests\n")
                            if max_adults:
                                context_parts.append(f"- **Max Adults**: {max_adults}\n")
                            
                            # Property type
                            property_type = property_detail.get("typeCode")
                            if property_type:
                                context_parts.append(f"- **Type**: {property_type}\n")
                            
                            # License info
                            license_code = property_detail.get("licenseCode")
                            if license_code:
                                context_parts.append(f"- **License**: {license_code}\n")
                            
                            # Coordinates
                            lat = property_detail.get("latitude")
                            lon = property_detail.get("longitude")
                            if lat and lon:
                                context_parts.append(f"- **Coordinates**: {lat}, {lon}\n")
                            
                            # Description
                            description = property_detail.get("description")
                            if description:
                                # Truncate long descriptions
                                desc_preview = description[:200] + "..." if len(description) > 200 else description
                                context_parts.append(f"- **Description**: {desc_preview}\n")
                                
                    except Exception as e:
                        logger.warning(f"Could not fetch details for property {property_id}: {e}")
                
                context_parts.append("\n")
            
            # Step 4: Add summary statistics
            context_parts.append("## Summary\n")
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