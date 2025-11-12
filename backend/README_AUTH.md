# Authentication & Default Users

## Development Default Users

For development and testing, default users can be automatically created on server startup.

### Enable Seed Users

Set environment variable:
```bash
export ENABLE_DEV_SEED=true
```

Or in `.env` file:
```
ENABLE_DEV_SEED=true
```

### Default Credentials

**Admin User:**
- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`
- Role: `admin`

**Analyst User:**
- Username: `analyst`
- Email: `analyst@example.com`
- Password: `analyst123`
- Role: `analyst`

### Customize Default Users

Set environment variables:
```bash
DEV_ADMIN_USERNAME=myadmin
DEV_ADMIN_EMAIL=myadmin@example.com
DEV_ADMIN_PASSWORD=mypassword
DEV_ANALYST_USERNAME=myanalyst
DEV_ANALYST_EMAIL=myanalyst@example.com
DEV_ANALYST_PASSWORD=mypassword
```

### Security Notes

⚠️ **IMPORTANT:**
- Seed users are **ONLY** created in non-production environments
- Never set `ENABLE_DEV_SEED=true` in production
- Default passwords are weak - change them in production
- Seed script checks `ENV` variable and skips if `production`

### Manual Seed

Run seed script manually:
```bash
cd backend
python -m src.app.core.seed
```

### Production

For production:
1. **DO NOT** enable `ENABLE_DEV_SEED`
2. Create users through the registration endpoint or admin panel
3. Use strong, unique passwords
4. Consider using environment-specific user management

