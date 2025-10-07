from azure.storage.blob import BlobServiceClient, ContainerClient
import pandas as pd
import io
import json
import os
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


class AzuriteFunction:
    """
    Process nutritional data from Azurite Blob Storage and store results in simulated NoSQL
    """

    def __init__(self):
        # Azurite default connection string
        self.connect_str = (
            "DefaultEndpointsProtocol=http;"
            "AccountName=devstoreaccount1;"
            "AccountKey=Eby8vdM02xNOcqFlErCHM36Zo8Czu8xF3h4/gZfy6OM+Kj6Pu/zJFNJxd7GE3aEw==;"
            "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
        )
        self.container_name = "datasets"
        self.blob_name = "AllDiets.csv"
        self.nosql_dir = "simulated_nosql"

    def setup_nosql_directory(self):
        """Create directory for simulated NoSQL storage"""
        if not os.path.exists(self.nosql_dir):
            os.makedirs(self.nosql_dir)
            print(f"✓ Created directory: {self.nosql_dir}")

    def test_azurite_connection(self):
        """Test connection to Azurite"""
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connect_str
            )
            # List containers to verify connection
            containers = list(blob_service_client.list_containers())
            print(f"✓ Successfully connected to Azurite")
            print(f"✓ Found {len(containers)} container(s)")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Azurite: {str(e)}")
            print("\nMake sure Azurite is running:")
            print(
                "  - Docker: docker run -p 10000:10000 mcr.microsoft.com/azure-storage/azurite azurite-blob --blobHost 0.0.0.0"
            )
            print(
                "  - NPM: azurite --silent --location azurite --debug azurite/debug.log"
            )
            return False

    def upload_csv_to_azurite(self, local_csv_path):
        """Upload CSV file to Azurite for testing"""
        try:
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connect_str
            )

            # Create container if it doesn't exist
            try:
                container_client = blob_service_client.create_container(
                    self.container_name
                )
                print(f"✓ Created container: {self.container_name}")
            except Exception:
                container_client = blob_service_client.get_container_client(
                    self.container_name
                )
                print(f"✓ Using existing container: {self.container_name}")

            # Upload the CSV file
            blob_client = container_client.get_blob_client(self.blob_name)

            with open(local_csv_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            print(f"✓ Uploaded {local_csv_path} to Azurite as {self.blob_name}")
            return True

        except Exception as e:
            print(f"✗ Failed to upload CSV: {str(e)}")
            return False

    def read_csv_from_azurite(self):
        """Read CSV file from Azurite Blob Storage"""
        try:
            print("\n" + "=" * 60)
            print("READING DATA FROM AZURITE BLOB STORAGE")
            print("=" * 60)

            blob_service_client = BlobServiceClient.from_connection_string(
                self.connect_str
            )
            container_client = blob_service_client.get_container_client(
                self.container_name
            )
            blob_client = container_client.get_blob_client(self.blob_name)

            # Download blob content
            print(f"📥 Downloading blob: {self.blob_name}")
            stream = blob_client.download_blob().readall()

            # Load into pandas DataFrame
            df = pd.read_csv(io.BytesIO(stream))
            print(f"✓ Successfully loaded {len(df)} records")
            print(f"✓ Columns: {list(df.columns)}")
            print(f"✓ Diet types: {df['Diet_type'].unique().tolist()}")

            return df

        except Exception as e:
            print(f"✗ Error reading from Azurite: {str(e)}")
            return None

    def calculate_averages(self, df):
        """Calculate average macronutrients per diet type"""
        print("\n" + "=" * 60)
        print("CALCULATING AVERAGE MACRONUTRIENTS")
        print("=" * 60)

        # Calculate averages
        avg_macros = df.groupby("Diet_type")[
            ["Protein(g)", "Carbs(g)", "Fat(g)"]
        ].mean()

        print("\nAverage Macronutrients by Diet Type:")
        print(avg_macros.round(2))

        return avg_macros

    def store_in_nosql(self, avg_macros, df):
        """Store results in simulated NoSQL database (JSON files)"""
        print("\n" + "=" * 60)
        print("STORING RESULTS IN SIMULATED NOSQL DATABASE")
        print("=" * 60)

        self.setup_nosql_directory()

        # 1. Store average macronutrients
        results = avg_macros.reset_index().to_dict(orient="records")
        results_file = os.path.join(self.nosql_dir, "avg_macronutrients.json")

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved: {results_file}")

        # 2. Store detailed statistics per diet type
        detailed_stats = {}
        for diet_type in df["Diet_type"].unique():
            diet_data = df[df["Diet_type"] == diet_type]
            detailed_stats[diet_type] = {
                "count": len(diet_data),
                "avg_protein": float(diet_data["Protein(g)"].mean()),
                "avg_carbs": float(diet_data["Carbs(g)"].mean()),
                "avg_fat": float(diet_data["Fat(g)"].mean()),
                "max_protein": float(diet_data["Protein(g)"].max()),
                "min_protein": float(diet_data["Protein(g)"].min()),
                "top_cuisines": diet_data["Cuisine_type"]
                .value_counts()
                .head(3)
                .to_dict(),
            }

        stats_file = os.path.join(self.nosql_dir, "detailed_statistics.json")
        with open(stats_file, "w") as f:
            json.dump(detailed_stats, f, indent=2)
        print(f"✓ Saved: {stats_file}")

        # 3. Store metadata
        metadata = {
            "processed_at": datetime.now().isoformat(),
            "total_records": len(df),
            "diet_types": df["Diet_type"].unique().tolist(),
            "cuisine_types": df["Cuisine_type"].unique().tolist(),
            "source_blob": self.blob_name,
            "source_container": self.container_name,
        }

        metadata_file = os.path.join(self.nosql_dir, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Saved: {metadata_file}")

        # 4. Create a document-style NoSQL structure
        documents = []
        for _, row in avg_macros.iterrows():
            diet_type = row.name
            diet_data = df[df["Diet_type"] == diet_type]

            document = {
                "_id": diet_type.lower().replace(" ", "_"),
                "diet_type": diet_type,
                "macronutrients": {
                    "protein_g": float(row["Protein(g)"]),
                    "carbs_g": float(row["Carbs(g)"]),
                    "fat_g": float(row["Fat(g)"]),
                },
                "recipe_count": len(diet_data),
                "cuisines": diet_data["Cuisine_type"].value_counts().head(5).to_dict(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            documents.append(document)

        documents_file = os.path.join(self.nosql_dir, "diet_documents.json")
        with open(documents_file, "w") as f:
            json.dump(documents, f, indent=2)
        print(f"✓ Saved: {documents_file}")

        return results

    def query_nosql(self, diet_type=None):
        """Query the simulated NoSQL database"""
        print("\n" + "=" * 60)
        print("QUERYING SIMULATED NOSQL DATABASE")
        print("=" * 60)

        documents_file = os.path.join(self.nosql_dir, "diet_documents.json")

        try:
            with open(documents_file, "r") as f:
                documents = json.load(f)

            if diet_type:
                # Filter by diet type
                result = [
                    doc
                    for doc in documents
                    if doc["diet_type"].lower() == diet_type.lower()
                ]
                print(f"\nQuery: diet_type = '{diet_type}'")
                print(json.dumps(result, indent=2))
            else:
                # Return all
                print(f"\nAll documents ({len(documents)} total):")
                for doc in documents:
                    print(f"\n{doc['diet_type']}:")
                    print(f"  Protein: {doc['macronutrients']['protein_g']:.2f}g")
                    print(f"  Carbs: {doc['macronutrients']['carbs_g']:.2f}g")
                    print(f"  Fat: {doc['macronutrients']['fat_g']:.2f}g")

            return documents

        except FileNotFoundError:
            print("✗ NoSQL database not found. Run process_data() first.")
            return None

    def process_data(self, local_csv_path=None):
        """Main processing function"""
        print("\n" + "=" * 60)
        print("AZURITE NUTRITIONAL DATA PROCESSOR")
        print("=" * 60)

        # Test Azurite connection
        if not self.test_azurite_connection():
            return "Failed: Azurite is not running or not accessible"

        # Upload CSV if provided
        if local_csv_path and os.path.exists(local_csv_path):
            if not self.upload_csv_to_azurite(local_csv_path):
                return "Failed: Could not upload CSV to Azurite"

        # Read CSV from Azurite
        df = self.read_csv_from_azurite()
        if df is None:
            return "Failed: Could not read data from Azurite"

        # Calculate averages
        avg_macros = self.calculate_averages(df)

        # Store in NoSQL
        results = self.store_in_nosql(avg_macros, df)

        print("\n" + "=" * 60)
        print("✓ DATA PROCESSING COMPLETE")
        print("=" * 60)
        print(f"\nResults stored in '{self.nosql_dir}/' directory:")
        print("  - avg_macronutrients.json")
        print("  - detailed_statistics.json")
        print("  - diet_documents.json")
        print("  - metadata.json")

        return "Data processed and stored successfully"


def main():
    """Main execution function"""
    processor = AzuriteFunction()

    # Option 1: Upload local CSV and process
    # Uncomment and provide your CSV path
    local_csv = "AllDiets.csv"  # Update this path!

    if os.path.exists(local_csv):
        result = processor.process_data(local_csv_path=local_csv)
    else:
        # Option 2: Process existing blob in Azurite
        result = processor.process_data()

    print(f"\n{result}")

    # Demo: Query the NoSQL database
    processor.query_nosql()

    # Demo: Query specific diet type
    print("\n" + "-" * 60)
    processor.query_nosql(diet_type="paleo")


main()
