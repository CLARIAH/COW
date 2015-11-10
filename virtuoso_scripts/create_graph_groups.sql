--# See here for more details http://docs.openlinksw.com/virtuoso/rdfgraphsecurity.html

--# this is the master (virtual) graph group
DB.DBA.RDF_GRAPH_GROUP_CREATE ('http://dbpedia.org',1);

--# the following groups are defined as subgroup of the master
DB.DBA.RDF_GRAPH_GROUP_INS ('http://dbpedia.org','http://live.dbpedia.org');
DB.DBA.RDF_GRAPH_GROUP_INS ('http://dbpedia.org','http://static.dbpedia.org');
DB.DBA.RDF_GRAPH_GROUP_INS ('http://dbpedia.org','http://dbpedia.org/ontology');
DB.DBA.RDF_GRAPH_GROUP_INS ('http://dbpedia.org','http://dbpedia.org/ontology/meta');
