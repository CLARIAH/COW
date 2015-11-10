
-- Disable auto indexing before doing bulk insertions / deletions

-- Deleting previous entries of loader script
delete from DB.DBA.load_list;

-- see http://www.openlinksw.com/dataspace/dav/wiki/Main/VirtBulkRDFLoader
select 'Loading data...';
--      <folder with data>  <pattern>    <default graph if no graph file specified>
ld_dir ('/scratch/clariah-sdh/rdf/napp', '*.ttl', 'http://data.socialhistory.org/vocab/napp/');

rdf_loader_run();

-- See if we have any errors
select * from DB.DBA.load_list where ll_state <> 2;


-- re-enable auto-indexing once finished with bulk operations
