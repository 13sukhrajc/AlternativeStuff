import ast
import json
from pprint import pprint

from ai.substitutes import generate_substitutes
from pipeline.enhancer import enhance_substitutes

def run(query):
    # Step 1: Generate original product + substitute titles
    base_data = generate_substitutes(query)

    # Step 2: Enhance substitutes with ASIN + affiliate links
    final_output = enhance_substitutes(base_data)

    print(final_output)


if __name__ == "__main__":
    # run("ps5 slim")
    data = "{'original_product': {'title': 'ps5 slim', 'asin': 'B0FRSZT2H5', 'price': 399, 'affiliate_link': 'https://www.amazon.com/dp/B0FRSZT2H5/?tag=buybuzz02b-20'}, 'substitutes': [{'title': 'PlayStation 5', 'asin': 'B0FRGTYSL5', 'price': 549, 'affiliate_link': 'https://www.amazon.com/dp/B0FRGTYSL5/?tag=buybuzz02b-20'}, {'title': 'PlayStation 5 Digital Edition', 'asin': 'B0FRSZT2H5', 'price': 399, 'affiliate_link': 'https://www.amazon.com/dp/B0FRSZT2H5/?tag=buybuzz02b-20'}, {'title': 'Xbox Series S', 'asin': 'B0D932YWSZ', 'price': 392.73, 'affiliate_link': 'https://www.amazon.com/dp/B0D932YWSZ/?tag=buybuzz02b-20'}, {'title': 'Nintendo Switch', 'asin': 'B0BFJWCYTL', 'price': 324.64, 'affiliate_link': 'https://www.amazon.com/dp/B0BFJWCYTL/?tag=buybuzz02b-20'}, {'title': 'Xbox Series X', 'asin': 'B08H75RTZ8', 'price': 574.99, 'affiliate_link': 'https://www.amazon.com/dp/B08H75RTZ8/?tag=buybuzz02b-20'}]}"

    data_dict = ast.literal_eval(data)
    cheapest = min(data_dict["substitutes"], key=lambda x: x["price"])
    print(cheapest["affiliate_link"])