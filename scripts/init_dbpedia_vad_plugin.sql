--# The following are used to setup the vad plugin in DBpedia Live

select 'Settings registry values...';
registry_set('dbp_decode_iri','off');
registry_set('dbp_domain','http://dbpedia.org');
registry_set('dbp_graph', 'http://dbpedia.org');
registry_set('dbp_lang', 'en');
registry_set('dbp_DynamicLocal', 'off');
registry_set('dbp_category', 'Category');
registry_set('dbp_template', 'Template');
registry_set('dbp_imprint', 'http://dbpedia.org/Imprint');
registry_set('dbp_website', 'http://dbpedia.org');
registry_set('dbp_lhost', ':8870');
registry_set('dbp_vhost', 'dbpedia.org');

