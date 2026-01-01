# FileUploaderNew Test Checklist

## Pre-Test Verification ✅

- ✅ Component is imported in `app/pillars/content/page.tsx`
- ✅ No linter errors
- ✅ ContentAPIManager is properly exported
- ✅ All imports are correct

## Test Scenarios

### 1. Basic File Upload (Structured Data)
- [ ] Navigate to Content Pillar page
- [ ] Select "Structured Data" file type
- [ ] Upload a CSV or Excel file
- [ ] Verify:
  - File appears in dropzone
  - Upload button is enabled
  - Upload succeeds
  - Success message appears
  - File appears in FileDashboard
  - Pillar states are updated (data, parsing)

### 2. PDF/Document Upload
- [ ] Select "PDF Document" file type
- [ ] Upload a PDF or DOCX file
- [ ] Verify:
  - Upload succeeds
  - File appears in FileDashboard
  - File also appears in operations pillar (if PDF)

### 3. Mainframe/Binary Upload (Copybook Required)
- [ ] Select "Mainframe/Binary" file type
- [ ] Verify copybook file input appears
- [ ] Try to upload without copybook:
  - [ ] Upload button should be disabled
  - [ ] Error message should appear
- [ ] Upload copybook file (.cpy, .cbl, or .txt)
- [ ] Upload main binary file
- [ ] Verify:
  - Both files are uploaded
  - Success message appears
  - File appears in FileDashboard

### 4. SOP/Workflow Upload
- [ ] Select "SOP/Workflow" file type
- [ ] Upload a workflow file (.docx, .pdf, .bpmn, .txt, or .json)
- [ ] Verify:
  - Upload succeeds
  - File appears in FileDashboard
  - File also appears in operations pillar

### 5. Error Handling
- [ ] Try to upload without selecting file type:
  - [ ] Dropzone should be disabled
  - [ ] Upload button should not appear
- [ ] Try to upload wrong file type:
  - [ ] Should show validation error
- [ ] Test with invalid/network error:
  - [ ] Error message should appear
  - [ ] onUploadError callback should fire (if provided)

### 6. Semantic Test IDs
- [ ] Verify test IDs are present:
  - [ ] `data-testid="content-pillar-file-upload-area"`
  - [ ] `data-testid="file-type-selector"`
  - [ ] `data-testid="file-upload-dropzone"`
  - [ ] `data-testid="select-files-to-upload"`
  - [ ] `data-testid="select-copybook-file"` (for Binary files)
  - [ ] `data-testid="complete-file-upload"`

### 7. Callback Props
- [ ] Test with `onFileUploaded` callback:
  - [ ] Callback should fire with file ID after successful upload
- [ ] Test with `onUploadError` callback:
  - [ ] Callback should fire with error message on failure

### 8. State Management
- [ ] Verify pillar states are updated:
  - [ ] `data` pillar state has new file
  - [ ] `parsing` pillar state has new file
  - [ ] `operations` pillar state has file (for SOP/Workflow and PDF)

### 9. UI/UX
- [ ] Verify visual feedback:
  - [ ] Drag active state (blue border)
  - [ ] File selected state (green border)
  - [ ] Uploading state (spinner, disabled button)
  - [ ] Success state (green message)
  - [ ] Error state (red message)
  - [ ] Processing status display

### 10. Authentication
- [ ] Test without authentication:
  - [ ] Should show "Authentication Required" message
  - [ ] Upload should be disabled

## API Integration Verification

### Check Browser Console
- [ ] No console errors
- [ ] API calls are made to `/api/content-pillar/upload-file`
- [ ] Request includes:
  - [ ] File in FormData
  - [ ] Copybook file (if provided)
  - [ ] Session token in headers

### Check Network Tab
- [ ] POST request to `/api/content-pillar/upload-file`
- [ ] Status code: 200 (success) or appropriate error code
- [ ] Response includes file metadata

## Known Issues to Watch For

1. **FileType enum conversion**: Make sure Select component handles FileType enum correctly
2. **Session token**: Verify `guideSessionToken` is available
3. **Pillar state updates**: Check that `setPillarState` is working correctly
4. **Copybook file**: Verify it's sent correctly in FormData

## Quick Test Commands

```bash
# Start frontend (if not running)
cd symphainy_source/symphainy-frontend
npm run dev

# Check for TypeScript errors
npm run type-check

# Check for lint errors
npm run lint
```

## Expected Behavior

1. **File Type Selection**: Dropdown shows all 5 file types with descriptions
2. **File Drop**: Drag & drop or click to select file
3. **Copybook (Binary only)**: Copybook input appears for Mainframe/Binary files
4. **Upload**: Button uploads file via semantic API
5. **Success**: File appears in dashboard, states updated, success message shown
6. **Reset**: Form resets after 3 seconds

## Success Criteria

✅ All test scenarios pass
✅ No console errors
✅ Semantic API calls work correctly
✅ Pillar states update correctly
✅ Semantic test IDs are present
✅ Callbacks fire correctly
✅ UI/UX is smooth and responsive

---

## Next Steps After Testing

If all tests pass:
1. ✅ FileUploaderNew approach is validated
2. → Apply same pattern to FileDashboardNew
3. → Apply same pattern to ParsePreviewNew
4. → Handle MetadataExtractor
5. → Rename components
6. → Archive old versions

If issues found:
1. Document issues
2. Fix FileUploaderNew
3. Re-test
4. Then proceed with other components





