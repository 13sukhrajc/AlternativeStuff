import ast
import asyncio
import json

from ai.substitutes import generate_substitutes
from pipeline.enhancer_async import enhance_substitutes_async

def run(query):
    base_data = generate_substitutes(query)
    final_output = asyncio.run(enhance_substitutes_async(base_data))
    print(final_output)

if __name__ == "__main__":
    # run("Chocolate whey protein")
    data = ast.literal_eval("{'original_product': {'title': 'Chocolate whey protein', 'asin': 'B0CQ3RJQX1', 'price': 29.98, 'affiliate_link': 'https://www.amazon.com/dp/B0CQ3RJQX1/?tag=buybuzz02b-20'}, 'substitutes': [{'title': 'Milk Chocolate Plant-Based Protein', 'asin': 'B0F7BCY1J5', 'price': 29.94, 'affiliate_link': 'https://www.amazon.com/dp/B0F7BCY1J5/?tag=buybuzz02b-20'}, {'title': 'Double Chocolate Fudge Whey Protein Powder', 'asin': 'B002DYIZH6', 'price': 36.52, 'affiliate_link': 'https://www.amazon.com/dp/B002DYIZH6/?tag=buybuzz02b-20'}, {'title': 'Peanut Butter Chocolate Whey Protein', 'asin': 'B006E54GJG', 'price': 35.96, 'affiliate_link': 'https://www.amazon.com/dp/B006E54GJG/?tag=buybuzz02b-20'}, {'title': 'Strawberry Chocolate Whey Protein Powder', 'asin': 'B000GIURIQ', 'price': 42, 'affiliate_link': 'https://www.amazon.com/dp/B000GIURIQ/?tag=buybuzz02b-20'}, {'title': 'Peanut Butter Fudge Whey Protein', 'asin': 'B000FRXJ6A', 'price': 16.01, 'affiliate_link': 'https://www.amazon.com/dp/B000FRXJ6A/?tag=buybuzz02b-20'}]}")
    print(json.dumps(data, indent=4))