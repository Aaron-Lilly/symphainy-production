# Uploading Clean Test Files

## Option 1: Upload via UI (Recommended)
1. Go to Content Pillar in the UI
2. Upload `scenario3_annuity_data_clean.bin` as the data file
3. Upload `scenario3_copybook_clean.cpy` as the copybook

## Option 2: Upload via Script (Local Machine)
If you want to upload from your local machine:

1. Get your authentication token:
   - Open browser DevTools (F12) -> Network tab
   - Make any API request
   - Copy the `Authorization` header value (the token part after "Bearer ")

2. Run the upload script:
   ```bash
   cd /path/to/symphainy_source/scripts
   python3 upload_clean_files_local.py --token YOUR_TOKEN
   ```

## Files Location
- Data file: `scripts/clean_test_files/scenario3_annuity_data_clean.bin`
- Copybook: `scripts/clean_test_files/scenario3_copybook_clean.cpy`

## What's Different
- **Data file**: No header comments, starts directly with "POL001", 81-byte records
- **Copybook**: Only the data record structure (POLICYHOLDER-RECORD), no metadata tables
