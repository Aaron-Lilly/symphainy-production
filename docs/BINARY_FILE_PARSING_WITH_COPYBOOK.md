# Binary File Parsing with Copybook - UI Enhancement

## Overview

This document describes the enhancement to the file parsing flow to support selecting a copybook file when parsing binary files.

## Problem

Previously, the file parsing UI only allowed selecting one file (either the .bin or .cpy file) from a dropdown. When parsing a binary file (.bin), the backend requires a copybook file (.cpy) to define the structure, but there was no way to select both files in the UI.

**Error Message:**
```
"Parsing Failed
Copybook required. Provide 'copybook' (string or bytes) in options."
```

## Solution

### Frontend Changes

1. **FileDashboard Component** (`app/pillars/content/components/FileDashboard.tsx`):
   - Added state management for parse dialog:
     - `parseDialogOpen`: Controls modal visibility
     - `fileToParse`: Stores the file being parsed
     - `selectedCopybookFileId`: Stores the selected copybook file ID
   
   - Added `isBinaryFile()` helper function to detect binary files:
     - Checks file extensions: `.bin`, `.dat`, `.ebcdic`, `.mainframe`, `.cobol`
   
   - Updated `handleParseClick()`:
     - Opens a modal dialog when clicking "Parse" button
     - Initializes state for file and copybook selection
   
   - Updated `handleParseFile()`:
     - Now accepts optional `copybookFileId` parameter
     - Passes `copybookFileId` to `ContentAPIManager.processFile()`
   - Reloads files after successful parsing to update status

2. **Parse File Modal**:
   - Shows file information (name, type, size)
   - Displays copybook file selector for binary files
   - Validates that copybook is selected for binary files
   - Provides Cancel and Parse buttons

### Backend Integration

The backend already supports `copybook_file_id` parameter:
- **API Endpoint**: `POST /api/v1/content-pillar/process-file/{fileId}`
- **Request Body**: 
  ```json
  {
    "copybook_file_id": "uuid-of-copybook-file",
    "processing_options": {}
  }
  ```
- **ContentAPIManager**: Already accepts `copybookFileId` parameter and sends it in the request

## User Flow

1. User clicks "Parse" button on a file
2. Modal dialog opens showing:
   - File to parse (name, type, size)
   - Copybook file selector (if binary file or if user wants to select one)
3. For binary files:
   - Copybook selector is required (marked with red asterisk)
   - User must select a copybook file before parsing
4. User clicks "Parse File" button
5. Frontend sends request with:
   - `file_id`: The file to parse
   - `copybook_file_id`: The selected copybook file (if provided)
6. Backend processes the file using the copybook
7. Success/error toast notification is shown
8. File list is refreshed to show updated status

## File Detection

Binary files are detected by extension:
- `.bin`
- `.dat`
- `.ebcdic`
- `.mainframe`
- `.cobol`

## UI Components Used

- **FileSelector**: Reusable component for selecting files
  - Filters by status (Uploaded)
  - Shows file name, type, and size
  - Placeholder: "Select a copybook file (.cpy, .cob, .cbl)"

- **Modal Dialog**: Custom modal using Card component
  - Overlay with backdrop
  - Centered on screen
  - Responsive design

## Testing

1. Upload a binary file (.bin) and a copybook file (.cpy)
2. Click "Parse" on the binary file
3. Modal should open showing:
   - Binary file information
   - Copybook selector (required)
4. Select a copybook file
5. Click "Parse File"
6. Verify:
   - Request includes `copybook_file_id`
   - Parsing succeeds
   - File status updates to "Parsed"

## Error Handling

- **Missing Copybook for Binary File**: 
  - Toast error: "Copybook required. Please select a copybook file to parse this binary file."
  - Parse button is disabled until copybook is selected

- **Parsing Failure**:
  - Toast error with backend error message
  - File remains in "Uploaded" status

## Future Enhancements

1. **Auto-detect Copybook**: 
   - Automatically suggest copybook files based on naming conventions
   - Match binary file name with copybook file name

2. **Copybook Validation**:
   - Validate copybook file format before parsing
   - Show preview of copybook structure

3. **Multiple Copybooks**:
   - Support selecting multiple copybooks for complex files
   - Allow copybook chaining/imports

4. **Copybook Library**:
   - Maintain a library of common copybooks
   - Allow users to save frequently used copybooks

## Files Modified

- `symphainy-frontend/app/pillars/content/components/FileDashboard.tsx`
  - Added parse dialog state management
  - Added binary file detection
  - Added copybook file selection UI
  - Updated parse file handler to pass copybook_file_id

## Backend Compatibility

The backend already supports this flow:
- `ContentOrchestrator.process_file()` accepts `copybook_file_id`
- `FrontendGatewayService.handle_process_file_request()` extracts `copybook_file_id` from request
- Copybook file content is retrieved from storage and passed to parser

No backend changes were required for this enhancement.






