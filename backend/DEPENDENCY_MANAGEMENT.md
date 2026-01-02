# Dependency Management Guide

## Version Pinning Strategy

This project uses a **pinned version strategy** for production dependencies and **compatible version ranges** for test dependencies.

### Production Dependencies (`requirements.txt`)

All production dependencies are **pinned to specific versions** to ensure reproducible builds:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
bcrypt==3.2.2
```

**Rationale:**
- Ensures consistent behavior across environments
- Prevents unexpected breaking changes
- Makes deployments predictable

### Test Dependencies (`requirements-test.txt`)

Test dependencies use **compatible version ranges** with upper bounds to prevent incompatibilities:

```txt
pytest>=7.4.0
httpx>=0.24.0,<0.28.0  # Upper bound prevents TestClient issues
bcrypt==3.2.2          # Must match requirements.txt
```

**Rationale:**
- Allows minor version updates for bug fixes
- Upper bounds prevent breaking changes
- Critical dependencies (like bcrypt) must match production

## Key Compatibility Notes

### httpx and TestClient
- **Issue:** httpx 0.28+ breaks TestClient compatibility with starlette
- **Solution:** Pin to `httpx>=0.24.0,<0.28.0`
- **Status:** Will be resolved when starlette updates

### bcrypt and passlib
- **Issue:** bcrypt 4.0+ has API changes incompatible with passlib
- **Solution:** Pin to `bcrypt==3.2.2` in both files
- **Status:** Stable, no immediate need to upgrade

### SQLAlchemy 2.0
- **Status:** Using SQLAlchemy 2.0 style (`declarative_base` from `sqlalchemy.orm`)
- **Migration:** Complete

### Pydantic V2
- **Status:** Using `ConfigDict` instead of class-based `Config`
- **Migration:** Complete

## Updating Dependencies

### Process

1. **Test Updates Locally:**
   ```bash
   pip install --upgrade <package>
   pytest tests/ -v
   ```

2. **Update requirements.txt:**
   - Pin to the tested version
   - Update requirements-test.txt if needed

3. **Run Full Test Suite:**
   ```bash
   make test-all
   ```

4. **Document Breaking Changes:**
   - Update this file
   - Update CHANGELOG.md if applicable

### Security Updates

For security patches:
1. Update immediately
2. Test thoroughly
3. Deploy as hotfix if critical

## Version Compatibility Matrix

| Package | Production | Test | Notes |
|---------|-----------|------|-------|
| fastapi | 0.104.1 | >=0.104.0 | Stable |
| httpx | - | >=0.24.0,<0.28.0 | Test only |
| bcrypt | 3.2.2 | 3.2.2 | Must match |
| sqlalchemy | 2.0.23 | >=2.0.0 | Using 2.0 style |
| pydantic | 2.5.0 | >=2.5.0 | Using ConfigDict |

## Future Considerations

1. **Consider Poetry or pip-tools** for better dependency resolution
2. **Automated dependency updates** via Dependabot
3. **Regular security audits** via `pip-audit` or similar

