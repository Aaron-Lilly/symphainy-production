# Parsed File Storage Analysis and Fix

## Current State vs. What Should Happen

### What Should Happen (Architecture)

1. **Three Separate Tables for Lineage:**
   - `project_files` - Original uploaded files (status="uploaded") AND parsed files (status="parsed")
   - `parsed_data_files` - Metadata for parsed files, linking back to original via `file_id`
   - `embedding_files` - Metadata for embeddings, linking back to parsed files via `parsed_file_id` and original via `file_id`

2. **File Storage:**
   - Original files: Binary in GCS + metadata in `project_files`
   - Parsed files: Binary in GCS + metadata in BOTH `project_files` (status="parsed") AND `parsed_data_files`
   - Embeddings: Documents in ArangoDB + metadata in `embedding_files`

3. **UI Tracking:**
   - Track by `ui_name` (not UUID) as per user requirement
   - Dashboard displays files from `project_files` table
   - Parsed files have `ui_name` like "parsed_{original_name}"

4. **Lineage:**
   - `parsed_data_files.file_id` → links to original `project_files.uuid`
   - `parsed_data_files.metadata.project_file_uuid` → links to parsed file's `project_files.uuid`
   - `embedding_files.parsed_file_id` → links to `parsed_data_files.parsed_file_id`
   - `embedding_files.file_id` → links to original `project_files.uuid`

5. **Delete Cascade:**
   - Delete from `project_files` should cascade to:
     - `parsed_data_files` (via `file_id` foreign key or manual cleanup)
     - `embedding_files` (via `file_id` foreign key or manual cleanup)
   - Delete parsed file from `project_files` should also delete from `parsed_data_files`

### What Was Actually Happening (Before Fix)

1. **Problem 1: Duplicate Entries**
   - `store_parsed_file()` was calling `create_file()` which created entries in `project_files` with status="parsed"
   - BUT it was also creating entries in `parsed_data_files`
   - This caused:
     - Statistics showing 98 files (counting both tables incorrectly)
     - Dashboard showing duplicate entries
     - Confusion about which table to query

2. **Problem 2: Missing Content**
   - `get_parsed_file()` was trying to retrieve from `project_files` but the file wasn't there
   - OR it was trying to retrieve from GCS but the path was wrong
   - Result: "Parsed file has no content" error

3. **Problem 3: Incorrect Statistics**
   - Statistics were counting:
     - Uploaded files from `project_files` with status="uploaded" ✓
     - Parsed files from `parsed_data_files` ✓
     - BUT also counting parsed files from `project_files` with status="parsed" (duplicates)

4. **Problem 4: Delete Not Working**
   - Delete feature deletes from `project_files` only
   - Doesn't cascade to `parsed_data_files` or `embedding_files`
   - Leaves orphaned records

### What We Fixed

1. **Fixed `store_parsed_file()`:**
   - Now stores parsed file binary in GCS ✓
   - Creates entry in `project_files` with status="parsed" (for dashboard/delete) ✓
   - Creates entry in `parsed_data_files` with `file_id` linking to original (for lineage) ✓
   - Stores `project_file_uuid` in `parsed_data_files.metadata` (for delete cascade) ✓
   - Stores `user_id` and `ui_name` in `parsed_data_files.metadata` (for queries) ✓

2. **Fixed `get_parsed_file()`:**
   - First tries to get from `project_files` entry (faster) ✓
   - Falls back to GCS if not found ✓
   - Returns file_content correctly ✓

3. **Fixed `list_parsed_files()`:**
   - Queries `parsed_data_files` table ✓
   - Filters by `metadata->user_id` (since user_id is in metadata JSONB) ✓

4. **Fixed Statistics:**
   - Counts uploaded files from `project_files` with status="uploaded" (excluding parsed files) ✓
   - Counts parsed files from `parsed_data_files` table ✓
   - Counts embedded files from `embedding_files` table ✓

### What Still Needs to Be Done

1. **Cleanup Duplicate Entries:**
   - Old parsed files in `project_files` that don't have corresponding entries in `parsed_data_files`
   - Or entries in `parsed_data_files` that don't have corresponding entries in `project_files`
   - Need to identify and clean up orphaned records

2. **Delete Cascade:**
   - When deleting a file from `project_files`, need to:
     - Delete from `parsed_data_files` (via `file_id` or `metadata->project_file_uuid`)
     - Delete from `embedding_files` (via `file_id` or `parsed_file_id`)
   - Currently delete only soft-deletes from `project_files`

3. **Dashboard Status Display:**
   - Dashboard should show parsed files with status="parsed" (not "uploaded")
   - Currently dashboard might be showing old entries with incorrect status

4. **Schema Enhancement (Optional):**
   - Consider adding `user_id` and `ui_name` columns to `parsed_data_files` table (currently in metadata JSONB)
   - This would improve query performance

## Cleanup Script Needed

We need a script to:
1. Identify orphaned parsed files in `project_files` (status="parsed" but no corresponding entry in `parsed_data_files`)
2. Identify orphaned parsed files in `parsed_data_files` (no corresponding entry in `project_files`)
3. Clean up duplicate entries
4. Fix incorrect status values

## Testing Checklist

- [ ] Upload a file → should create entry in `project_files` with status="uploaded"
- [ ] Parse a file → should create entries in BOTH `project_files` (status="parsed") AND `parsed_data_files`
- [ ] Dashboard should show 8 files (6 uploaded + 2 parsed)
- [ ] Statistics should show correct counts
- [ ] Delete parsed file → should delete from both `project_files` AND `parsed_data_files`
- [ ] Delete original file → should cascade delete parsed files and embeddings
- [ ] Embedding creation should work (no "no content" error)


