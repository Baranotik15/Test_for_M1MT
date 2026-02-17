import logging
import pandas as pd
from arcgis.gis import GIS
from arcgis.features import Feature, FeatureLayer

logger = logging.getLogger(__name__)


class ArcGISError(Exception):
    pass


class ArcGISClient:
    """Client for ArcGIS Online services."""

    def __init__(self):
        """Initialize ArcGIS client with anonymous access."""
        try:
            self.gis = GIS()
            logger.info("Connected to ArcGIS (anonymous)")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise ArcGISError(f"Connection failed: {e}") from e

    def get_feature_layer(self, item_id: str, layer_index: int = 0) -> FeatureLayer:
        """Get Feature Layer by item ID."""
        try:
            item = self.gis.content.get(item_id)
            if not item:
                raise ArcGISError(f"Item '{item_id}' not found")

            layer = item.layers[layer_index]
            logger.info(f"Retrieved layer: {layer.properties.name}")
            return layer
        except IndexError:
            raise ArcGISError(f"Layer index {layer_index} not found")
        except Exception as e:
            raise ArcGISError(f"Failed to get layer: {e}") from e

    def print_layer_fields(self, layer: FeatureLayer) -> None:
        """Print layer fields."""
        print("\n" + "=" * 80)
        print(f"LAYER: {layer.properties.name}")
        print("=" * 80)
        for f in layer.properties.fields:
            print(f"  {f.name:20} | {f.type:15} | {f.alias}")
        print("=" * 80 + "\n")


def df_to_features(df: pd.DataFrame, spatial_reference: int = 4326) -> list[Feature]:
    """Convert DataFrame to ArcGIS Features."""
    features = []
    skipped = 0

    for _, row in df.iterrows():
        if pd.isna(row["long"]) or pd.isna(row["lat"]):
            skipped += 1
            continue

        attributes = {
            "date": str(row["Дата"]),
            "region": str(row["Область"]),
            "city": str(row["Місто"]),
            "value_1": int(row["Значення 1"]),
            "value_2": int(row["Значення 2"]),
            "value_3": int(row["Значення 3"]),
            "value_4": int(row["Значення 4"]),
            "value_5": int(row["Значення 5"]),
            "value_6": int(row["Значення 6"]),
            "value_7": int(row["Значення 7"]),
            "value_8": int(row["Значення 8"]),
            "value_9": int(row["Значення 9"]),
            "value_10": int(row["Значення 10"])
        }

        geometry = {
            "x": float(row["long"]),
            "y": float(row["lat"]),
            "spatialReference": {"wkid": spatial_reference}
        }

        features.append(Feature(attributes=attributes, geometry=geometry))

    if skipped:
        logger.warning(f"Skipped {skipped} rows (invalid coordinates)")

    logger.info(f"Created {len(features)} features")
    return features


def upload_features_batch(
    layer: FeatureLayer,
    features: list[Feature],
    batch_size: int = 500,
    show_progress: bool = True
) -> dict[str, int]:
    """Upload features in batches."""
    total = len(features)
    success = failed = 0
    batches = range(0, total, batch_size)

    iterator = batches
    if show_progress:
        try:
            from tqdm import tqdm
            iterator = tqdm(batches, desc="Uploading", unit="batch")
        except ImportError:
            pass

    for i in iterator:
        batch = features[i:i + batch_size]
        try:
            result = layer.edit_features(adds=batch)

            if hasattr(result, 'get') and result.get('addResults'):
                batch_success = sum(1 for r in result['addResults'] if r.get('success'))
                success += batch_success
                failed += len(batch) - batch_success
            else:
                success += len(batch)
        except Exception as e:
            failed += len(batch)
            logger.error(f"Batch failed: {e}")

    logger.info(f"Upload complete: {success}/{total} succeeded")

    if success == 0 and total > 0:
        raise ArcGISError("All batches failed")

    return {"success": success, "failed": failed, "total": total}
