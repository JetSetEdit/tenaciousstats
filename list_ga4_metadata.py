import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import GetMetadataRequest
import json

# CONFIGURATION
PROPERTY_ID = '368035934'
CREDENTIALS_FILE = 'credentials.json'

# Set credentials if file exists
if os.path.exists(CREDENTIALS_FILE):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDENTIALS_FILE

def list_metadata():
    """Lists all available dimensions and metrics from GA4."""
    try:
        client = BetaAnalyticsDataClient()
        print("Authenticated successfully.\n")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # Get metadata for dimensions and metrics
    request = GetMetadataRequest(
        name=f"properties/{PROPERTY_ID}/metadata"
    )
    
    try:
        metadata = client.get_metadata(request=request)
        
        print("=" * 80)
        print("AVAILABLE DIMENSIONS")
        print("=" * 80)
        print(f"\nTotal Dimensions: {len(metadata.dimensions)}\n")
        
        # Group dimensions by category
        dimensions_by_category = {}
        for dim in metadata.dimensions:
            category = dim.category if dim.category else "Uncategorized"
            if category not in dimensions_by_category:
                dimensions_by_category[category] = []
            dimensions_by_category[category].append({
                'api_name': dim.api_name,
                'ui_name': dim.ui_name,
                'description': dim.description
            })
        
        for category, dims in sorted(dimensions_by_category.items()):
            print(f"\n[{category}]")
            print("-" * 80)
            for dim in sorted(dims, key=lambda x: x['api_name']):
                print(f"  {dim['api_name']:40} | {dim['ui_name']}")
                if dim['description']:
                    print(f"    -> {dim['description'][:70]}")
        
        print("\n" + "=" * 80)
        print("AVAILABLE METRICS")
        print("=" * 80)
        print(f"\nTotal Metrics: {len(metadata.metrics)}\n")
        
        # Group metrics by category
        metrics_by_category = {}
        for metric in metadata.metrics:
            category = metric.category if metric.category else "Uncategorized"
            if category not in metrics_by_category:
                metrics_by_category[category] = []
            metrics_by_category[category].append({
                'api_name': metric.api_name,
                'ui_name': metric.ui_name,
                'description': metric.description,
                'type': metric.type_.name if metric.type_ else 'UNKNOWN'
            })
        
        for category, mets in sorted(metrics_by_category.items()):
            print(f"\n[{category}]")
            print("-" * 80)
            for met in sorted(mets, key=lambda x: x['api_name']):
                type_str = f"[{met['type']}]" if met['type'] else ""
                print(f"  {met['api_name']:40} | {met['ui_name']:30} {type_str}")
                if met['description']:
                    print(f"    -> {met['description'][:70]}")
        
        # Save to JSON file for reference
        output = {
            'dimensions': [
                {
                    'api_name': dim.api_name,
                    'ui_name': dim.ui_name,
                    'description': dim.description,
                    'category': dim.category
                }
                for dim in metadata.dimensions
            ],
            'metrics': [
                {
                    'api_name': metric.api_name,
                    'ui_name': metric.ui_name,
                    'description': metric.description,
                    'category': metric.category,
                    'type': metric.type_.name if metric.type_ else None
                }
                for metric in metadata.metrics
            ]
        }
        
        with open('ga4_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print(f"Metadata saved to: ga4_metadata.json")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    list_metadata()

