
-- Disable auto indexing before doing bulk insertions / deletions

-- Deleting previous entries of loader script
delete from DB.DBA.load_list;

--      <folder with data>  <pattern>    <default graph if no graph file specified>
ld_dir ('/scratch/clariah-sdh/converters/src/hisco_converter/rdf', '*.ttl', 'http://data.socialhistory.org/vocab/hisco/');

rdf_loader_run();

-- See if we have any errors
-- select * from DB.DBA.load_list where ll_state <> 2;


-- re-enable auto-indexing once finished with bulk operations
