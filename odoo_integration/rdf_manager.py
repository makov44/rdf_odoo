from SPARQLWrapper import SPARQLWrapper, JSON


class RdfStore:

    def __init__(self):
        self.sparql = SPARQLWrapper("http://rdf.getdyl.com:8890/sparql")

    def execute(self, query):
        query_result = []
        self.sparql.setQuery(query)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for item in  results["results"]["bindings"]:
            dict_result={}
            for key in item:
                dict_result[key] = item[key]["value"]

            query_result.append(dict_result)

        return query_result
