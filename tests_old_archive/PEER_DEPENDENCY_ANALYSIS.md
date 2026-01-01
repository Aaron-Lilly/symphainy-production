# Peer Dependency Analysis

**Date:** December 2024  
**Status:** ⚠️ Workaround in place (`--legacy-peer-deps`)

---

## 🔍 **Issue Identified**

When running `npm install` without `--legacy-peer-deps`, npm reports:

```
npm error Conflicting peer dependency: @types/react@17.0.90
npm error   peerOptional @types/react@"^16.9.0 || ^17.0.0" from @testing-library/react-hooks@8.0.1
```

---

## 📊 **Root Cause**

1. **@testing-library/react-hooks@8.0.1** requires `@types/react@^16.9.0 || ^17.0.0`
2. **@radix-ui/react-avatar@1.1.10** has optional peer dependency `@types/react@*`
3. **Current React version:** `react@18.2.0` (which uses `@types/react@^18.x`)

The conflict is between:
- `@testing-library/react-hooks` expecting React 16/17 types
- Current codebase using React 18

---

## ✅ **Current Solution**

**Workaround:** Using `--legacy-peer-deps` flag in Dockerfile

```dockerfile
RUN npm ci --legacy-peer-deps && \
```

This allows npm to ignore peer dependency conflicts and proceed with installation.

---

## 🎯 **Recommended Long-term Fix**

### **Option 1: Update Testing Library (Recommended)**
Replace `@testing-library/react-hooks` with React 18 compatible alternatives:

```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",  // React 18 compatible
    "@testing-library/react-hooks": "^8.0.1"  // Remove this
  }
}
```

**Note:** `@testing-library/react-hooks` is deprecated for React 18. Use `@testing-library/react` with `renderHook` instead.

### **Option 2: Pin @types/react Version**
If `@testing-library/react-hooks` is required, pin `@types/react` to v17:

```json
{
  "devDependencies": {
    "@types/react": "^17.0.0",
    "@types/react-dom": "^17.0.0"
  }
}
```

**Warning:** This may cause TypeScript issues with React 18 features.

### **Option 3: Keep Workaround**
If the workaround is working and tests pass, we can keep it. However, this is not ideal for long-term maintenance.

---

## 📋 **Action Items**

- [ ] **Short-term:** Document the workaround in deployment guide
- [ ] **Medium-term:** Migrate tests to use `@testing-library/react` instead of `@testing-library/react-hooks`
- [ ] **Long-term:** Remove `--legacy-peer-deps` after migration

---

## ✅ **Impact Assessment**

**Current Impact:** ⚠️ **LOW**
- Build works with workaround
- Tests pass
- No runtime issues

**Risk if not fixed:** ⚠️ **MEDIUM**
- Future dependency updates may break
- TypeScript type checking may be incomplete
- Harder to maintain

**Priority:** 🟡 **MEDIUM** (not blocking production, but should be addressed)

---

**Last Updated:** December 2024

