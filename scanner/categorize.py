"""Dead simple keyword categorisation. A trained classifier would be overkill
for the ~15 shops I actually go to."""

CATEGORIES = {
    "groceries": ["carrefour", "monoprix", "lidl", "auchan", "franprix",
                  "leclerc", "intermarche", "casino", "aldi", "biocoop"],
    "restaurants": ["mcdonald", "burger", "kebab", "pizza", "sushi",
                    "restaurant", "brasserie", "tacos", "kfc", "subway"],
    "transport": ["sncf", "ratp", "navigo", "uber", "bolt", "blablacar",
                  "total energies", "essence"],
    "pharmacy": ["pharmacie", "parapharmacie"],
    "shopping": ["fnac", "zara", "uniqlo", "decathlon", "ikea", "action",
                 "amazon"],
    "coffee": ["starbucks", "columbus", "cafe", "café", "coffee"],
}


def categorize(merchant):
    m = merchant.lower()
    for category, keywords in CATEGORIES.items():
        if any(k in m for k in keywords):
            return category
    return "other"
