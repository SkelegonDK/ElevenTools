# Migration Notes: Session-Based File Management

## Overview

This change introduces session-based file organization, moving from shared directories to per-session isolation. This ensures privacy in multi-user deployments and adds download functionality.

## What Changed

### Before
- All files stored in shared directories: `outputs/single/` and `outputs/bulk/`
- Files visible to all users in cloud deployments
- No download functionality
- No automatic cleanup

### After
- Files stored in session-specific directories: `outputs/{session_id}/single/` and `outputs/{session_id}/bulk/`
- Each user session has isolated file storage
- Download buttons for individual files and bulk ZIP downloads
- Automatic cleanup of old session directories (default: 24 hours)

## Migration Steps

### For New Deployments
No action required - session-based storage is automatic.

### For Existing Deployments

1. **Backup Existing Files** (Recommended)
   ```bash
   # Backup existing outputs directory
   cp -r outputs outputs_backup_$(date +%Y%m%d)
   ```

2. **Verify Old Files**
   - Check `outputs/single/` and `outputs/bulk/` for any important files
   - Download or move important files before cleanup

3. **Deploy New Version**
   - Deploy the updated code
   - New files will automatically use session-based storage

4. **Optional: Cleanup Old Directories**
   ```bash
   # After verifying no important files remain
   rm -rf outputs/single outputs/bulk
   ```

## Configuration

### Session Timeout

The default session timeout is 24 hours. To customize:

**Environment Variable:**
```bash
export SESSION_TIMEOUT_HOURS=48  # 48 hours instead of 24
```

**In Code:**
```python
from utils.session_manager import cleanup_old_sessions
cleanup_old_sessions(max_age_hours=48)  # Custom timeout
```

## Behavior Changes

### File Access
- **Before**: All users could see all files in File Explorer
- **After**: Users only see files from their own session

### File Persistence
- **Before**: Files persisted until manually deleted
- **After**: Files are automatically cleaned up after session timeout (default: 24 hours)

### Download
- **Before**: No download functionality (files only accessible via File Explorer)
- **After**: Download buttons available for individual files and bulk ZIP downloads

## Troubleshooting

### Files Not Showing in File Explorer
- Verify you're viewing files from your current session
- Check that session ID hasn't changed (browser refresh may create new session)
- Ensure files were generated after the update

### Missing Old Files
- Old files in `outputs/single/` and `outputs/bulk/` are not automatically migrated
- Access them directly from the filesystem if needed
- Consider backing up important files before cleanup

### Cleanup Not Working
- Check application logs for cleanup operation messages
- Verify `outputs/` directory permissions
- Ensure cleanup is being called on app startup

## Rollback

If you need to rollback to the previous file organization:

1. Restore previous code version
2. Files in session directories will remain but won't be accessible
3. Restore from backup if needed: `cp -r outputs_backup_YYYYMMDD/* outputs/`

## Support

For issues or questions about this migration, please:
1. Check application logs for error messages
2. Review the session management code in `utils/session_manager.py`
3. Open an issue in the repository with details

