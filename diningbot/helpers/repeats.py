def norm(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


# PER-STATION REPEATS
RISE_AND_DINE = {
    norm("Fresh Cooked Eggs"),
    norm("Scrambled Eggs"),
    norm("Blueberry Danish"),
    norm("Chocolate Chip Buttermilk Muffins"),
    norm("Scones"),
    norm("Plant Based Sausage Patty"),
    norm("Tea Biscuits"),
    norm("Oatmeal"),
    norm("Congee"),
    norm("Maple Syrup"),
}

STACKS = {
    norm("Side of Sliced Tomato"),
    norm("Leaf Lettuce"),
    norm("Sliced Red Onions"),
    norm("Sliced Fresh Cucumbers"),
    norm("Smoked Deli Ham"),
    norm("Deli Roast Beef"),
    norm("Sliced Deli Turkey"),
    norm("Egg Salad Filling no Onion"),
    norm("Tuna Salad Filling"),
    norm("Light Type Mayonnaise"),
    norm("Mustard"),
    norm("Chipotle Aioli"),
    norm("Hummus"),
    norm("Chao Cheese"),
    norm("Mozzarella Cheese Slices"),
    norm("Cheddar Cheese Slices, Mild"),
    norm("Sliced White Bread"),
    norm("Homemade Whole Wheat Bread"),
    norm('Flour Tortilla Wrap, 10"'),
    norm("Sourdough Bread, Pre-Sliced"),
}

LEAF_MARKET = {
    norm("Deluxe Fruit Salad"),
    norm("Chopped Romaine"),
    norm("Diced Tomatoes"),
    norm("Sliced Fresh Cucumbers"),
    norm("Baby Carrots"),
    norm("Diced Fresh Celery"),
    norm("Chopped Broccoli"),
    norm("Fresh Chopped Cauliflower"),
    norm("Sliced Beets"),
    norm("Chopped Hard Cooked Egg"),
    norm("1% Cottage Cheese"),
    norm("Sliced Red Onions"),
    norm("Black Beans"),
    norm("Seasoned Croutons"),
    norm("Sliced Black Olives"),
    norm("Baby Spinach"),
    norm("Salted Sunflower Seeds"),
    norm("Chickpeas"),
    norm("Spring Mix Lettuce"),
    norm("Caesar Salad Dressing"),
    norm("CW Ranch Salad Dressing"),
    norm("Balsamic Salad Dressing"),
}

GRILL_HOUSE = {
    norm("Leaf Lettuce"),
    norm("Side of Sliced Tomato"),
    norm("Cucumber Pickles"),
    norm("Shaved Fresh Red Onions"),
    norm("BBQ Sauce"),
    norm("Sriracha Mayonnaise"),
    norm("Pesto Aioli"),
    norm("Signature Burger Sauce"),
    norm("Kimchi-Style Coleslaw"),
}

# ===========================================
# Hot Plate
TEPPAN_SIGNATURE = {
    norm("jasmine rice"),
    norm("cantonese style chow mein noodles"),
}

FRENCH_TOAST_SIGNATURE = {
    norm("french toast"),
}

PANCAKE_SIGNATURE = {
    norm("pancakes"),
    norm("pancake"),
}

# Fresh Bowl
RICE_BOWL_SIGNATURE = {
    norm("bbq chicken"),
    norm("chili con carne"),
}

MEZZE_BAR_SIGNATURE = {
    norm("tzatziki"),
    norm("hummus"),
}

# Create
RAMEN_BAR_SIGNATURE = {
    norm("ramen noodles"),
    norm("udon noodles"),
}

CURRY_BAR_SIGNATURE = {
    norm("rice pilaf"),
    norm("green curry base"),
    norm("indonesian beef curry"),
    norm("rajma curry"),
}

PASTA_BAR_SIGNATURE = {
    norm("garlic cream cheese sauce"),
    norm("sun-dried tomato sauce"),
}
