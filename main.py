import ast
import asyncio
import json

from ai.substitutes import generate_substitutes
from pipeline.enhancer_async import enhance_substitutes_async

def run(query):
    base_data = generate_substitutes(query)
    final_output = asyncio.run(enhance_substitutes_async(base_data, domain="amazon.com"))
    print(json.dumps(final_output, indent=4))

if __name__ == "__main__":
    run("https://www.amazon.ca/ATTACK-SHARK-DPI-PAW3950-Lightweight-Programmable/dp/B0FMRZF662/ref=mp_s_a_1_4?crid=RES6WJFE76JS&dib=eyJ2IjoiMSJ9.meKhyuvopfcp4jyuweJh45gmts6_Jr1HdIu3uX1GNGVyX4tGOaK4t3gRgHL13iw6PfH3v-I6CeK5OT_7bxORW371bYDMXL0A4R3VTS6ulX2AO02E4OQahhUmKrQF26tCMWXRE1WYnHRDV03NMGMf-ss5gdYFtlNwJvfzL6Td4Afj445QuhCTKIBcvO-rZqJfLDjRfybhTSDv-wqZbYk-SA.1bhSwpoiQRI2NRjNV0Kwg8kipjQGvXnJmDyGPv_uPKA&dib_tag=se&keywords=final+mouse&qid=1772066936&sprefix=final+mouse%2Caps%2C142&sr=8-4")
