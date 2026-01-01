# FileUploaderNew Quick Test Guide

## Quick Start

1. **Start the frontend** (if not already running):
   ```bash
   cd symphainy_source/symphainy-frontend
   npm run dev
   ```

2. **Start the backend** (if not already running):
   ```bash
   cd symphainy_source/symphainy-platform
   # Your backend startup command
   ```

3. **Navigate to Content Pillar**:
   - Open browser to `http://localhost:3000/pillars/content` (or your frontend URL)
   - You should see the FileUploaderNew component

## Quick Smoke Test (5 minutes)

### Test 1: Basic Upload
1. Select "Structured Data" from file type dropdown
2. Click or drag a CSV/Excel file
3. Click "Upload File"
4. **Expected**: Success message, file appears in dashboard

### Test 2: Copybook Support
1. Select "Mainframe/Binary" from file type dropdown
2. **Expected**: Copybook file input appears
3. Select a copybook file (.cpy, .cbl, or .txt)
4. Select a binary file (.bin or .dat)
5. Click "Upload File"
6. **Expected**: Both files upload successfully

### Test 3: Error Handling
1. Select "Mainframe/Binary"
2. Select binary file but NOT copybook
3. **Expected**: Upload button disabled, error message

## Browser DevTools Checks

### Console Tab
- ✅ No red errors
- ✅ Check for API calls to `/api/content-pillar/upload-file`
- ✅ Check for any warnings

### Network Tab
1. Filter by "upload-file"
2. Upload a file
3. **Check Request**:
   - Method: POST
   - URL: `/api/content-pillar/upload-file`
   - Headers: Should include `X-Session-Token`
   - Body: FormData with file
4. **Check Response**:
   - Status: 200 (or appropriate)
   - Response body: Should have file metadata

### Elements Tab
- Inspect upload area
- Verify `data-testid="content-pillar-file-upload-area"` is present
- Verify `data-testid="select-files-to-upload"` is present
- Verify `data-testid="complete-file-upload"` is present

## Common Issues & Fixes

### Issue: "ContentAPIManager is not a constructor"
**Fix**: Check import path - should be:
```typescript
import { ContentAPIManager } from '@/shared/managers/ContentAPIManager';
```

### Issue: "Cannot read property 'guideSessionToken' of undefined"
**Fix**: Make sure `useGlobalSession()` is available and session is initialized

### Issue: Select dropdown not working
**Fix**: FileType enum needs to be converted to string:
```typescript
value={option.type.toString()}
```

### Issue: Upload fails with 401/403
**Fix**: Check session token is being passed correctly

### Issue: File not appearing in dashboard
**Fix**: Check pillar state updates are working:
- `setPillarState('data', ...)`
- `setPillarState('parsing', ...)`

## What to Look For

### ✅ Success Indicators
- File uploads successfully
- Success toast message appears
- File appears in FileDashboard
- No console errors
- Semantic test IDs are present
- Processing status shows
- Form resets after 3 seconds

### ❌ Failure Indicators
- Console errors
- Upload button doesn't work
- No API call made
- API call fails (check Network tab)
- File doesn't appear in dashboard
- Error message doesn't appear

## Test Results Template

```
Date: ___________
Tester: ___________

### Test 1: Basic Upload
- [ ] Pass
- [ ] Fail (Notes: ___________)

### Test 2: Copybook Support
- [ ] Pass
- [ ] Fail (Notes: ___________)

### Test 3: Error Handling
- [ ] Pass
- [ ] Fail (Notes: ___________)

### Console Errors
- [ ] None
- [ ] Errors found: ___________

### Network Calls
- [ ] API calls working
- [ ] Issues: ___________

### Semantic Test IDs
- [ ] All present
- [ ] Missing: ___________

### Overall Status
- [ ] ✅ Ready to proceed
- [ ] ⚠️ Issues found (need fixes)
- [ ] ❌ Blocking issues

Notes:
___________
```

## Next Steps

If all tests pass ✅:
- Proceed with completing FileDashboardNew
- Apply same pattern to other components

If issues found ⚠️:
- Document issues in this file
- Fix FileUploaderNew
- Re-test
- Then proceed





