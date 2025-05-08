# prefix_to_website_name.py

# Auto-generated mapping from variant prefix to most common website name/product line.
# You can manually add or override entries in the MANUAL_ADDITIONS section below.

PREFIX_TO_WEBSITE_NAME = {
    "100316": "Disco A",
    "100119": "The Original Large",
    "100128": "The Original Medium",
    "100027": "The Original Carry-On",
    "100017": "The Original Bigger Carry-On",
    "100242": "The Travel Wellness Kit",
    "100018": "The Original Bigger Carry-On",
    "100028": "The Original Carry-On",
    "100300": "Charm A",
    "100206": "The Insider Packing Cubes (Set of 4)",
    "100043": "Everywhere Bag",
    "100405": "The Luggage Tag (Part)",
    "100709": "Luggage Tag",
    "100634": "Bigger Carry-On 2.0",
    "100207": "The Insider Packing Cubes (Set of 4)",
    "100100": "Kit - Trolley",
    "100633": "Carry-On 2.0",
    "100635": "Medium 2.0",
    "100637": "Large 2.0",
    "100638": "Trunk",
    "100091": "The Kids' Carry-On",
    "100567": "PC20LuggageTag",
    "100115": "The Large Toiletry Bag",
    "100465": "The Luggage Tag and Charm Duo",
    "100019": "The Bigger Carry-On Flex",
    "100118": "The Large Flex",
    "100281": "The Everywhere Zip Backpack",
    "100003": "The Backpack",
    "100029": "The Carry-On Flex",
    "100121": "The Medium Flex",
    "100533": "The Bigger Carry-On 2.0",
    "100664": "Carry-On Flex",
    "100665": "Bigger Carry-On Flex",
    "100666": "Medium Flex",
    "100667": "Large Flex",
    # ... (add more as needed from your output)
}

# --- MANUAL ADDITIONS & SPECIAL CASES ---
# You can add or override mappings here, or add extra metadata.
# For example, to note which carry-ons have batteries, or add new product lines.

MANUAL_ADDITIONS = {
    # Example: Add a special note for battery-carrying variants
    "100027": {
        "website_name": "The Original Carry-On",
        "has_battery": None,  # Set to True/False if known, or leave as None for manual review
        "notes": "Some variants have batteries; verify individually."
    },
    # Example: Add a new mapping or override
    "100XXX": {
        "website_name": "Special Product",
        "has_battery": True,
        "notes": "Manual addition."
    },
    # Add more manual entries as needed
}

def get_website_name_for_prefix(prefix):
    # Check manual additions first
    if prefix in MANUAL_ADDITIONS:
        return MANUAL_ADDITIONS[prefix]["website_name"]
    return PREFIX_TO_WEBSITE_NAME.get(prefix)

# Example usage:
# print(get_website_name_for_prefix("100027"))
