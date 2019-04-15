from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from catalog.db.setup import Base, Category, Item
from catalog.config import SQL_COMMAND

engine = create_engine(SQL_COMMAND)
Base.metadata.bind = engine
DBSessionMaker = sessionmaker(bind=engine)


def get_session():
    return DBSessionMaker()


def add_category(data, commit=True, session=None):
    if session is None:
        session = get_session()
    required = dict()
    required["name"] = data.get("name")
    print("CREATING:\tcategory\n\tinput_data:\t{}".format(data))
    if any([requirement is None for requirement in required.values()]):
        print('required info not provided: {}'.format(required.keys()))
    else:
        category = Category()
        category.name = data['name']
        session.add(category)
        if commit is True:
            session.commit()


def get_all_categories(session=None):
    if session is None:
        session = get_session()
    return session.query(Category)


def get_category_and_items(data, session=None):
    if session is None:
        session = get_session()
    required = dict()
    required['category_id'] = data.get('category_id')
    if any([requirement is None for requirement in required.values()]):
        print('required info not provided: {}'.format(required.keys()))
    else:
        categories = get_categories_where(required, session=session)
        for category in categories:  # should be only one entry!
            category_items = get_category_items(category, session=session)
            return category, category_items


def get_category_items(category, session=None):
    if session is None:
        session = get_session()
    print("GETTING:\t{}.category_items".format(category))
    return session.query(Item).filter(Item.Category == category)


def get_categories_where(data, session=None):
    if session is None:
        session = get_session()
    print("GETTING:\tcategory:\n\twith criteria:{}".format(data))
    # Filter By Criteria:
    criteria = dict()
    criteria["name"] = data.get("name")
    criteria["category_id"] = data.get("category_id")
    if any([criterion is None for criterion in criteria.items()]):
        for key, value in criteria.items():
            if key == "name" and value is not None:
                return session.query(Category).filter(Category.name == criteria["name"])
            elif key == "category_id" and value is not None:
                return session.query(Category).filter(Category.id == criteria["category_id"])
    else:
        return session.query(Category).filter(Category.id == criteria["category_id"],
                                              Category.name == criteria["name"])


def update_category(data, commit=True, session=None):
    if session is None:
        session = get_session()
    # Requirements:
    required = dict()
    required["category_id"] = data.get("category_id")
    # Update Information:
    update = dict()
    update["name"] = data.get("name")
    print("UPDATING:\tcategory\n\tinput_data:\t{}".format(data))
    if any([requirement is None for requirement in required.values()]):
        print('required info not provided: {}'.format(required.keys()))
    else:
        categories = get_categories_where(required, session=session)
        for category in categories:
            category.name = update["name"]
        if commit is True:
            session.commit()


def delete_category(category, commit=False, session=None):
    if session is None:
        session = get_session()
    print("DELETING:\tcategory:\t:\t{}".format(category))
    category_items = get_category_items(category)
    for category_item in category_items:
        print('\tDELETE:\tcategory_item:\t{}'.format(category_item))
        session.delete(category_item)
    print('\tDELETE:\tcategory:\t{}'.format(category))
    session.delete(category)
    if commit is True:
        session.commit()


def delete_categories_where(data, commit=True, session=None):
    if session is None:
        session = get_session()
    categories = get_categories_where(data, session=session)
    for category in categories:
        delete_category(category, session=session)
    if commit is True:
        session.commit()


def add_item(data, commit=True, session=None):
    if session is None:
        session = get_session()
    required = dict()
    required["name"] = data.get("name")
    required["category_id"] = data.get("category_id")
    optional = dict()
    optional["description"] = data.get("description")
    print("CREATING:\titem\n\tinput_data:\t{}".format(data))
    if any([requirement is None for requirement in required.values()]):
        print('required info not provided: {}'.format(required.keys()))
    else:
        item = Item()
        item.name = required['name']
        item.category_id = required['category_id']
        if optional['description'] is not None:
            item.description = optional['description']
        session.add(item)
        if commit is True:
            session.commit()


def get_all_items():
def get_item():
    def get_item_where():


def update_item():


def delete_item():