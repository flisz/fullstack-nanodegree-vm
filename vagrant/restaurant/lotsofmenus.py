from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query

from config import SQL_COMMAND
from database_setup import Restaurant, Base, MenuItem

engine = create_engine(SQL_COMMAND)
#Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DB = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, "you can
# revert all of them back to the last commit by calling
# session.rollback()    

def do_session():
    restaurants = get_restaurants()
    try:
        session = DB()
        load_restaurants(restaurants,session)    
        get_restaurants_from_db(session)
    finally:
        print("restaurants loaded!")


def load_restaurants(restaurants,session):   
    for restaurant in restaurants:        
        restaurant_object = Restaurant(name=restaurant.get("name"))
        print("adding restaurant: {}".format(restaurant_object.name))
        add_to_db(restaurant_object,session)
        menu_items = restaurant.get("menu_items")
        for menu_item in menu_items:
            menu_item_object = get_menu_item_object(menu_item,restaurant_object)
            add_to_db(menu_item_object,session)
    

def get_restaurants_from_db(session):
    print("getting restaurants")
    restaurant_objects = session.query(Restaurant)
    for count, restaurant_object in enumerate(restaurant_objects):
        print("#:\tRESTAURANT NAME:")
        print('{}\t{}'.format(count,restaurant_object.name))
        get_restaurant_menu_from_db(session,restaurant_object)


def get_restaurant_menu_from_db(session,restaurant_object):
    menu_item_objects = session.query(MenuItem).filter(MenuItem.restaurant == restaurant_object)
    print("\t\t#:\tMENU:")
    for count, menu_item_object in enumerate(menu_item_objects):
        print('\t\t{}\t{}'.format(count,menu_item_object.name))


def add_to_db(this,session):
    session.add(this)
    session.commit()


def get_menu_item_object(menu_item,restaurant_object):
    menu_item_object = MenuItem(
        name=menu_item.get("name"),
        description=menu_item.get("description"),
        price=menu_item.get("price"),
        course=menu_item.get("course"),
        restaurant=restaurant_object
        )
    print("adding menu_item: {}".format(menu_item_object.name))
    return menu_item_object


def get_restaurants():
    restaurants = [{
    "name": "Urban Burger", 
    "menu_items": [{
        "name": "Veggie Burger", 
        "description": "Juicy grilled veggie patty with tomato mayo and lettuce",
        "price": "$7.50", 
        "course": "Entree"
        },{
        "name": "French Fries",
        "description": "with garlic and parmesan",
        "price": "$2.99",
        "course": "Appetizer"
        },{
        "name": "Chicken Burger",
        "description": "Juicy grilled chicken patty with tomato mayo and lettuce",
        "price": "$5.50",
        "course": "Entree"
        },{
        "name": "Chocolate Cake",
        "description": "fresh baked and served with ice cream",
        "price": "$3.99",
        "course": "Dessert"
        },{
        "name": "Sirloin Burger",
        "description": "Made with grade A beef",
        "price": "$7.99",
        "course": "Entree"
        },{
        "name": "Root Beer",
        "description": "16oz of refreshing goodness",
        "price": "$1.99",
        "course": "Beverage"
        },{
        "name": "Iced Tea",
        "description": "with Lemon",
        "price": "$.99",
        "course": "Beverage"
        },{
        "name": "Grilled Cheese Sandwich",
        "description": "On texas toast with American Cheese",
        "price": "$3.49",
        "course": "Entree"
        },{
        "name": "Veggie Burger",
        "description": "Made with freshest of ingredients and home grown spices",
        "price": "$5.99",
        "course": "Entree"
        }]
    },{
    "name": "Super Stir Fry",
    "menu_items": [{
        "name": "Chicken Stir Fry",
        "description": "With your choice of noodles vegetables and sauces",
        "price": "$7.99",
        "course": "Entree"
        },{
        "name": "Peking Duck",
        "description": "A famous duck dish from Beijing[1] that has been prepared since the imperial era. The meat is prized for its thin, crisp skin, with authentic versions of the dish serving mostly the skin and little meat, sliced in front of the diners by the cook",
        "price": "$25",
        "course": "Entree"
        },{
        "name": "Spicy Tuna Roll",
        "description": "Seared rare ahi, avocado, edamame, cucumber with wasabi soy sauce",
        "price": "15",
        "course": "Entree"
        },{
        "name": "Nepali Momo ",
        "description": "Steamed dumplings made with vegetables, spices and meat.",
        "price": "12",
        "course": "Entree"
        },{
        "name": "Beef Noodle Soup",
        "description": "A Chinese noodle soup made of stewed or red braised beef, beef broth, vegetables and Chinese noodles.",
        "price": "14",
        "course": "Entree"
        },{
        "name": "Ramen",
        "description": "a Japanese noodle soup dish. It consists of Chinese-style wheat noodles served in a meat- or (occasionally) fish-based broth, often flavored with soy sauce or miso, and uses toppings such as sliced pork, dried seaweed, kamaboko, and green onions.",
        "price": "12",
        "course": "Entree"
        }]
    },{
    "name": "Panda Garden",
    "menu_items": [{
        "name": "Pho",
        "description": "a Vietnamese noodle soup consisting of broth, linguine-shaped rice noodles called banh pho, a few herbs, and meat.",
        "price": "$8.99",
        "course": "Entree"
        },{
        "name": "Chinese Dumplings",
        "description": "a common Chinese dumpling which generally consists of minced meat and finely chopped vegetables wrapped into a piece of dough skin. The skin can be either thin and elastic or thicker.",
        "price": "$6.99",
        "course": "Appetizer"
        },{
        "name": "Gyoza",
        "description": "The most prominent differences between Japanese-style gyoza and Chinese-style jiaozi are the rich garlic flavor, the light seasoning of Japanese gyoza with salt and soy sauce, and the fact that gyoza wrappers are much thinner",
        "price": "$9.95",
        "course": "Entree"
        },{
        "name": "Stinky Tofu",
        "description": "Taiwanese dish, deep fried fermented tofu served with pickled cabbage.",
        "price": "$6.99",
        "course": "Entree"
        },{
        "name": "Veggie Burger",
        "description": "Juicy grilled veggie patty with tomato mayo and lettuce",
        "price": "$9.50",
        "course": "Entree"
        }]
    },{
    "name": "Thyme for That Vegetarian Cuisine",
    "menu_items": [{
        "name": "Tres Leches Cake",
        "description": "Rich, luscious sponge cake soaked in sweet milk and topped with vanilla bean whipped cream and strawberries.",
        "price": "$2.99",
        "course": "Dessert"
        },{
        "name": "Mushroom risotto",
        "description": "Portabello mushrooms in a creamy risotto",
        "price": "$5.99",
        "course": "Entree"
        },{
        "name": "Honey Boba Shaved Snow",
        "description": "Milk snow layered with honey boba, jasmine tea jelly, grass jelly, caramel, cream, and freshly made mochi",
        "price": "$4.50",
        "course": "Dessert"
        },{
        "name": "Cauliflower Manchurian",
        "description": "Golden fried cauliflower florets in a midly spiced soya,garlic sauce cooked with fresh cilantro, celery, chilies,ginger & green onions",
        "price": "$6.95",
        "course": "Appetizer"
        },{
        "name": "Aloo Gobi Burrito",
        "description": "Vegan goodness. Burrito filled with rice, garbanzo beans, curry sauce, potatoes (aloo), fried cauliflower (gobi) and chutney. Nom Nom",
        "price": "$7.95",
        "course": "Entree"
        },{
        "name": "Veggie Burger",
        "description": "Juicy grilled veggie patty with tomato mayo and lettuce",
        "price": "$6.80",
        "course": "Entree"
        }]
    },{
    "name": "Tony\'s Bistro ",
    "menu_items": [{
        "name": "Shellfish Tower",
        "description": "Lobster, shrimp, sea snails, crawfish, stacked into a delicious tower",
        "price": "$13.95",
        "course": "Entree"
        },{
        "name": "Chicken and Rice",
        "description": "Chicken... and rice",
        "price": "$4.95",
        "course": "Entree"
        },{
        "name": "Mom's Spaghetti",
        "description": "Spaghetti with some incredible tomato sauce made by mom",
        "price": "$6.95",
        "course": "Entree"
        },{
        "name": "Choc Full O\' Mint (Smitten\'s Fresh Mint Chip ice cream)",
        "description": "Milk, cream, salt, ..., Liquid nitrogen magic",
        "price": "$3.95",
        "course": "Dessert"
        },{
        "name": "Tonkatsu Ramen",
        "description": "Noodles in a delicious pork-based broth with a soft-boiled egg",
        "price": "$7.95",
        "course": "Entree"
        }]
    },{
    "name": "Andala\'s",
    "menu_items": [{
        "name": "Lamb Curry",
        "description": "Slow cook that thang in a pool of tomatoes, onions and alllll those tasty Indian spices. Mmmm.",
        "price": "$9.95",
        "course": "Entree"
        },{
        "name": "Chicken Marsala",
        "description": "Chicken cooked in Marsala wine sauce with mushrooms",
        "price": "$7.95",
        "course": "Entree"
        },{
        "name": "Potstickers",
        "description": "Delicious chicken and veggies encapsulated in fried dough.",
        "price": "$6.50",
        "course": "Appetizer"
        },{
        "name": "Nigiri Sampler",
        "description": "Maguro, Sake, Hamachi, Unagi, Uni, TORO!",
        "price": "$6.75",
        "course": "Appetizer"
        },{
        "name": "Veggie Burger",
        "description": "Juicy grilled veggie patty with tomato mayo and lettuce",
        "price": "$7.00",
        "course": "Entree"
        }]
    },{
    "name": "Auntie Ann\'s Diner ",
    "menu_items": [{
        "name": "Chicken Fried Steak",
        "description": "Fresh battered sirloin steak fried and smothered with cream gravy",
        "price": "$8.99",
        "course": "Entree"
        },{
        "name": "Boysenberry Sorbet",
        "description": "An unsettlingly huge amount of ripe berries turned into frozen (and seedless) awesomeness",
        "price": "$2.99",
        "course": "Dessert"
        },{
        "name": "Broiled salmon",
        "description": "Salmon fillet marinated with fresh herbs and broiled hot & fast",
        "price": "$10.95",
        "course": "Entree"
        },{
        "name": "Morels on toast (seasonal)",
        "description": "Wild morel mushrooms fried in butter, served on herbed toast slices",
        "price": "$7.50",
        "course": "Appetizer"
        },{
        "name": "Tandoori Chicken",
        "description": "Chicken marinated in yoghurt and seasoned with a spicy mix(chilli, tamarind among others) and slow cooked on burning charcoal.",
        "price": "$8.95",
        "course": "Entree"
        },{
        "name": "Veggie Burger",
        "description": "Juicy grilled veggie patty with tomato mayo and lettuce",
        "price": "$9.50",
        "course": "Entree"
        },{
        "name": "Spinach Ice Cream",
        "description": "vanilla ice cream made with organic spinach leaves",
        "price": "$1.99",
        "course": "Dessert"
        }]
    },{
    "name": "Cocina Y Amor ",
    "menu_items": [{
        "name": "Super Burrito Al Pastor",
        "description": "Marinated Pork, Rice, Beans, Avocado, Cilantro, Salsa, Tortilla",
        "price": "$5.95",
        "course": "Entree"
        },{
        "name": "Cachapa",
        "description": "Golden brown, corn-based Venezuelan pancake; usually stuffed with queso telita or queso de mano, and possibly lechon. ",
        "price": "$7.99",
        "course": "Entree"
        }]
    },{
    "name": "State Bird Provisions",
    "menu_items": [{
        "name": "Chantrelle Toast",
        "description": "Crispy Toast with Sesame Seeds slathered with buttery chantrelle mushrooms",
        "price": "$5.95",
        "course": "Appetizer"
        },{
        "name": "Guanciale Chawanmushi",
        "description": "Japanese egg custard served hot with spicey Italian Pork Jowl (guanciale)",
        "price": "$6.95",
        "course": "Dessert"
        },{
        "name": "Lemon Curd Ice Cream Sandwich",
        "description": "Lemon Curd Ice Cream Sandwich on a chocolate macaron with cardamom meringue and cashews",
        "price": "$4.25",
        "course": "Dessert"
        }]
    }]
    return restaurants


if __name__ == "__main__":
    do_session()
