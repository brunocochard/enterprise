def preposition(source = False, target = False) :
        if source: return "Source."
        elif target: return "Target."
        else: return ""

class Query(object):

    def __init__(self,table):
        self.select_attributes = []
        self.where_attributes = []
        self.orderby_attributes = []

        self.select_query = ""
        self.table_query = table
        self.where_query = ""
        self.orderby_query = ""
        self.query_mode = ""

    def build(self):
        return self.select_query + self.table_query + self.where_query + self.orderby_query

    def select(self,attribute):
        if len(self.select_attributes): self.select_query += ", "

        self.select_query += "[" + attribute + "]"
        self.select_attributes.append(attribute)

    def where(self,attribute, op, value, clause = "AND", source = False, target = False):
        if len(self.where_attributes): self.where_query += " " + clause + " "
        if value.find('@') == -1: value = "'" + value + "'"

        self.where_query += preposition(source, target) + "[" + attribute + "] " + op  + " " + value
        self.where_attributes.append(attribute)

    def orderby(self,attribute, by = 'desc', source = False, target = False):
        if len(self.orderby_attributes): self.orderby_query += ", "

        self.orderby_query += preposition(source, target) + "[" + attribute + "] " + by + ""
        self.orderby_attributes.append(attribute)

    def mode(self, type = "recursive", match = ""):
        """
            mode can be MustContain,  Recursive
            match can be none or ReturnMatchingChildren
        """
        self.query_mode += "mode(" + type + ", " + match + ")"

    def __repr__(self):
        return ("Select " + self.select_query +
                " From " + self.table_query +
                " Where " + self.where_query +
                " " + self.query_mode +
                " Order by " + self.orderby_query)
