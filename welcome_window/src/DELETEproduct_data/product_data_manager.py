import os
import csv
from collections import defaultdict
from .prefix_to_website_name import get_website_name_for_prefix, MANUAL_ADDITIONS

class ProductDataManager:
    def __init__(self, search_dir):
        self.products = []
        self.sku_index = {}
        self.prefix_index = defaultdict(list)
        self.load_all(search_dir)

    def load_all(self, search_dir):
        for fname in os.listdir(search_dir):
            if fname.lower().endswith('.csv'):
                with open(os.path.join(search_dir, fname), newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sku = row.get('Legacy SKU', '') or row.get('SKU', '')
                        variant = row.get('Variant', '') or row.get('Variant', '')
                        prefix = variant[:6] if variant and len(variant) >= 6 else ''
                        mapped_website_name = get_website_name_for_prefix(prefix)
                        manual = MANUAL_ADDITIONS.get(prefix, {})
                        enriched_row = dict(row)
                        enriched_row['Prefix'] = prefix
                        enriched_row['Mapped Website Name'] = mapped_website_name
                        enriched_row['has_battery'] = manual.get('has_battery')
                        enriched_row['manual_notes'] = manual.get('notes', '')
                        self.products.append(enriched_row)
                        if sku:
                            self.sku_index[sku] = enriched_row
                        if prefix:
                            self.prefix_index[prefix].append(enriched_row)

    def search_by_any_field(self, query):
        query = query.lower()
        return [row for row in self.products if any(query in str(v).lower() for v in row.values())]

    def get_by_sku(self, sku):
        return self.sku_index.get(sku)

    def get_by_variant_prefix(self, prefix):
        return self.prefix_index.get(prefix, [])

    def enrich_label_record(self, label_record):
        # Assume label_record contains at least 'sku'
        sku = label_record.get('sku') or label_record.get('SKU') or label_record.get('Legacy SKU')
        product_info = self.get_by_sku(sku) if sku else None
        prefix = product_info['Prefix'] if product_info else None
        mapped_website_name = product_info['Mapped Website Name'] if product_info else None
        has_battery = product_info['has_battery'] if product_info else None
        manual_notes = product_info['manual_notes'] if product_info else ''
        enriched = dict(label_record)
        enriched['product_info'] = product_info
        enriched['variant_prefix'] = prefix
        enriched['mapped_website_name'] = mapped_website_name
        enriched['has_battery'] = has_battery
        enriched['manual_notes'] = manual_notes
        return enriched
