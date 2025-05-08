import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
THEGRAPH_API_KEY = os.getenv("THEGRAPH_API_KEY")

# Subgraph endpoint with configurable API key
SUBGRAPH_URL = (
    f"https://gateway.thegraph.com/api/{THEGRAPH_API_KEY}/subgraphs/id/"
    "GFvGfWBX47RNnvgwL6SjAAf2mrqrPxF91eA53F4eNegW"
)

# GraphQL client setup
def get_client():
    transport = RequestsHTTPTransport(url=SUBGRAPH_URL)
    return Client(transport=transport, fetch_schema_from_transport=False)

# Fetch positions function with updated query to get ticks and liquidity
def query_positions(pool_address):
    client = get_client()
    query = gql("""
    query GetPositions($pool: String!) {
      positions(
        first: 1000
        where: {pool: $pool, liquidity_gt: "0"}
      ) {
        id
        owner
        liquidity
        tickLower {
          tickIdx
          price1
          price0
        }
        tickUpper {
          tickIdx
          price1
          price0
        }
        token0 {
          symbol
          decimals
        }
        token1 {
          symbol
          decimals
        }
        pool {
          tick
          liquidity
          token0Price
          token1Price
          token0 {
            symbol
            decimals
          }
          token1 {
            symbol
            decimals
          }
        }
      }
    }
    """)
    response = client.execute(query, variable_values={"pool": pool_address.lower()})
    return response["positions"]
