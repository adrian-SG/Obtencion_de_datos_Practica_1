from scrapy.loader import ItemLoader

class PracticaItemLoader(ItemLoader):

    def __init__(self, item=None, selector=None, response=None, parent=None, copy_from=None, **context):

        super().__init__(item=item, selector=selector, response=response, parent=parent, **context)

        if copy_from is not None:
            for field_name, value in copy_from.load_item().items():
                super()._add_value(field_name, value)