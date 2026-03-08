import json

def extract_products_from_file(input_file, output_file):
    try:
        # Read raw text from file
        with open(input_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Parse JSON string
        data = json.loads(raw_text)

        if "products" not in data or not isinstance(data["products"], list):
            raise ValueError("Invalid format: 'products' array not found.")

        simplified = []

        for product in data["products"]:
            merchant = product.get("merchants", [{}])[0]

            simplified.append({
                "title": product.get("title"),
                "tier": product.get("tier"),
                "affiliate_link": merchant.get("affiliate_link"),
                "price": merchant.get("price")
            })

        # Write cleaned JSON to output file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(simplified, f, indent=2)

        print(f"Filtered data saved to {output_file}")

    except Exception as e:
        print("Error:", e)


# 🔹 Run it
extract_products_from_file("output.json", "cleanOutput.json")