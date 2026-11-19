
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"]
)

index_name = os.environ["PINECONE_INDEX_NAME"]

print("Available indexes:")

for index in pc.list_indexes():
    print(index.name)

index = pc.Index(index_name)

stats = index.describe_index_stats()

print("\nIndex statistics:")
print("Dimension:", stats.dimension)
print("Total vectors:", stats.total_vector_count)
