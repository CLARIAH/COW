select 'loading latest dbpedia ontology';
--# See http://docs.openlinksw.com/virtuoso/fn_rdf_load_rdfxml.html
DB.DBA.RDF_LOAD_RDFXML (http_get ('http://mappings.dbpedia.org/server/ontology/dbpedia.owl'), 'http://dbpedia.org', 'http://dbpedia.org/resource/classes#');


--# For big files you should use DB.DBA.RDF_LOAD_RDFXML_MT
--# http://docs.openlinksw.com/virtuoso/fn_rdf_load_rdfxml_mt.html
