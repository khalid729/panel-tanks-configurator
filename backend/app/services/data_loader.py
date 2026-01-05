"""
Data Loader Service - Loads data from JSON files
"""
import json
from pathlib import Path
from functools import lru_cache
from typing import Optional
from app.core.config import settings


class DataLoader:
    """Loads and caches data from JSON files"""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self._prices_cache: dict = {}
        self._weights_cache: dict = {}
        self._panel_config_cache: dict = {}
        self._input_options_cache: dict = {}

    def _load_json(self, filename: str) -> dict | list:
        """Load JSON file"""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @lru_cache(maxsize=1)
    def get_input_options(self) -> dict:
        """Get input options"""
        return self._load_json("input_options.json")

    @lru_cache(maxsize=1)
    def get_panel_config(self) -> dict:
        """Get panel configuration"""
        return self._load_json("panel_config.json")

    def get_prices(self) -> dict[str, dict]:
        """Get prices dictionary keyed by part_no"""
        if not self._prices_cache:
            prices_data = self._load_json("prices_complete.json")
            for item in prices_data:
                data = item.get("data", {})
                part_no = data.get("B", "")
                if part_no and part_no != "#N/A":
                    self._prices_cache[part_no] = {
                        "part_no": part_no,
                        "name_kr": data.get("C", ""),
                        "price_usd": float(data.get("D", 0)) if data.get("D") else 0,
                        "spec": data.get("E", ""),
                        "name_en": data.get("F", ""),
                    }
        return self._prices_cache

    def get_weights(self) -> dict[str, float]:
        """Get weights dictionary keyed by part_no"""
        if not self._weights_cache:
            weights_data = self._load_json("weights_complete.json")
            for item in weights_data:
                data = item.get("data", {})
                part_no = data.get("A", "")
                weight = data.get("B", 0)
                if part_no and weight:
                    # Handle duplicates by keeping the first non-zero value
                    if part_no not in self._weights_cache or self._weights_cache[part_no] == 0:
                        self._weights_cache[part_no] = float(weight)
        return self._weights_cache

    def get_price(self, part_no: str) -> float:
        """Get price for a specific part"""
        prices = self.get_prices()
        part_data = prices.get(part_no, {})
        return part_data.get("price_usd", 0)

    def get_weight(self, part_no: str) -> float:
        """Get weight for a specific part"""
        weights = self.get_weights()
        return weights.get(part_no, 0)

    def get_part_info(self, part_no: str) -> dict:
        """Get complete part information"""
        prices = self.get_prices()
        weights = self.get_weights()

        part_data = prices.get(part_no, {})
        return {
            "part_no": part_no,
            "name": part_data.get("name_en", part_data.get("name_kr", "")),
            "price_usd": part_data.get("price_usd", 0),
            "weight_kg": weights.get(part_no, 0),
            "spec": part_data.get("spec", "")
        }


# Singleton instance
@lru_cache(maxsize=1)
def get_data_loader() -> DataLoader:
    """Get singleton DataLoader instance"""
    return DataLoader()
