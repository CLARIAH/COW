## List of Virtuoso scripts for loading / maintenance
## From https://github.com/dbpedia/dbpedia-docs


* `auto_indexing_disable.sql` disables auto indexing of Virtuoso to make loading faster
* `auto_indexing_enable.sql` enables auto indexing of Virtuoso. This is used for functions like `bif:contains`
* `clear_graph.sql` clears the contents of a graph (need to set the graph)
* `create_graph_groups.sql` Creates a virtual graph as a view of multiple graphs
* `fct_plugin_reindex.sql` indexes the database to make the FCT plugin work better
* `init_dbpedia_vad_plugin.sql` Used to setup the basic configuration for the dbpedia_vad plugin
* `load_data.sql` loads the contents of a folder to the db
* `load_manually_rdf_file.sql` inserts a single RDF/XML file to the db
* `virtuoso-run-isql.sh` Open an ISQL interface (need to adapt username, password isql port)
* `virtuoso-run-script.sh` add a SQL script as an argument to this file and VOS will execute it (need to adapt username, password isql port)
