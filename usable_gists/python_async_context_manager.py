# Use Case: Custom Async Context Manager
# Purpose: Handles asynchronous session opening, closing, and automatic rollback on failure.
# Key features: __aenter__, __aexit__, and exception propagation parameters.

import asyncio

class AsyncConnectionPoolMock:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.is_connected = False

    async def __aenter__(self):
        # Startup phase
        print(f"Connecting to: {self.connection_string}")
        await asyncio.sleep(0.2)  # Simulate network latency
        self.is_connected = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Teardown phase
        print("Closing database connection pool...")
        await asyncio.sleep(0.1)
        self.is_connected = False
        
        if exc_type is not None:
            # An exception occurred inside the context block
            print(f"Transaction failed with error: {exc_val}. Rolling back.")
            return False  # Propagate the exception to outer scope
        
        print("Transaction committed successfully.")
        return True  # Suppress exception propagation if none occurred

# Usage Example
async def run_context():
    db_url = "postgresql+asyncpg://admin@localhost:5432/dashboard"
    try:
        async with AsyncConnectionPoolMock(db_url) as conn:
            print(f"Pool state active: {conn.is_connected}")
            raise ValueError("Telemetry data corrupt!")
    except ValueError:
        print("Caught exception outside the context block.")

if __name__ == "__main__":
    asyncio.run(run_context())
