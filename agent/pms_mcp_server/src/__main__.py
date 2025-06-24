"""
Entry point for running the PMS MCP Server as a module
"""

import os
import sys

# Check if we should run HTTP server (for LiveKit integration)
if os.getenv("MCP_MODE", "http").lower() == "http":
    from .http_server import main
    main()
else:
    # Run stdio server (for Claude Desktop, etc.)
    from .server import main
    import asyncio
    asyncio.run(main())