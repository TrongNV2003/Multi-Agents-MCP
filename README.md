# Multi-Agents with MCP SSE server
This repo introduce a Multi-Agents system in the field of consultant for sales product, with MCP SSE server include functions for create orders if users want to buy a products and retrieve products from MongoDB, powered by CrewAI.

The system contains 3 main agents:
- **Consultant Agent**: Analyze customer requirements, advise on products, create final feedback
- **Inventory Agent**: Check product stock status and pricing from DB
- **Order Agent**: Process order creation when customer has demand

## Features
- Analyze customer requests using AI to identify products and purchase intentions
- Automated order processing with detailed information
- Get information of products from db (Mongodb)
- Integrated Function Calling to save orders
- Scalable and sequential processing pipeline
- Include calling tools for flexible if you want to use function calling instead of MCP SSE server

## System Architecture
1. **CrewAI Pipeline**: Coordinate workflow between agents
2. **Specialized agents**: Consultant, stock staff, order staff

## Usage
Start MCP SSE server:
```python
python mcp_server.py
```

Running Agents:
```python
python main.py
```

## Future plans
- Applying MCP (Model Context Protocol) for flexible plug-and-play external tools and APIs. (Done)
- Applying A2A (Agent to Agent Protocol) for Agents able to interact with each other.
- Build UI for users easy to interact with Multi Agents.