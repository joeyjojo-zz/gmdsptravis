__author__ = 'jond'

import csv

from rdflib import URIRef, Literal, Namespace, RDF

from gmdspconverters import utils

RECYCLING = Namespace('http://data.gmdsp.org.uk/id/salford/recycling/')
RECYCLING_ONT = Namespace('http://data.gmdsp.org.uk/def/council/recycling/')
RECYCLING_TYPE_ONT = Namespace('http://data.gmdsp.org.uk/def/council/recycling/recycling-type/')

def convert(graph, input_path):

    reader = csv.DictReader(open(input_path, mode='r'))
    for row in reader:
        rc = RECYCLING[utils.idify(row["Location"])]
        graph.add((rc, RDF.type, RECYCLING_ONT["RecyclingSite"]))
        graph.add((rc, utils.RDFS['label'], Literal("Recycling Site at " + row["Location"])))

        address = utils.idify(row["Address"])
        graph.add((rc, utils.VCARD['hasAddress'], RECYCLING["address/"+address]))

        # now add the address VCARD
        vcard = RECYCLING["address/"+address]
        graph.add((vcard, RDF.type, utils.VCARD["Location"]))
        graph.add((vcard, utils.RDFS['label'], Literal("Address of Recycling Site at " + row["Location"])))
        graph.add((vcard, utils.VCARD['street-address'], Literal(row["Address"])))
        graph.add((vcard, utils.VCARD['postal-code'], Literal(row["Postcode"])))
        graph.add((vcard, utils.POST['postcode'], URIRef(utils.convertpostcodeto_osuri(row["Postcode"]))))

        # location information
        graph.add((rc, utils.OS["northing"], Literal(row["Northings"])))
        graph.add((rc, utils.OS["easting"], Literal(row["Eastings"])))
        # add conversion for lat/long
        lat_long = utils.ENtoLL84(float(row["Eastings"]), float(row["Northings"]))
        graph.add((rc, utils.GEO["long"], Literal(lat_long[0])))
        graph.add((rc, utils.GEO["lat"], Literal(lat_long[1])))

        # recycling informationxs
        # maps the CSV header to the recycling facility concept schema
        facility_map = {
            "Cardboard": "cardboard",
            "Paper": "paper",
            "Cartons": "cartons",
            "Shoes": "shoes",
            "Glass": "glass",
            "Textiles": "textiles",
            "Cans": "cans",
            "Plastic Bottles": "plastic",
            "Aerosols": "aerosols",
        }

        for facility in facility_map:
            if row[facility]:
                graph.add((rc, RECYCLING_ONT['recyclingType'], RECYCLING_TYPE_ONT[facility_map[facility]]))
