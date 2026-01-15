# Development Journal

> Short notes on problems, fixes, and lessons learned.

---

## 2026-01-13
**Problem:** 
Accidentally deleted a database table. After that, migrations started failing because existing migration files were out of sync with the database.

**Why:**
I renamed a model directly, which caused Django to expect a table that no longer matched the existing schema. The migration history and actual database state became inconsistent.

**Fix:**  
Deleted existing migration files, cleared the corresponding entries from the `django_migrations` table in the database, and then re-created and applied migrations again from the beginning.

**Lesson:**  
Renaming models can break migration history. Always handle model renames carefully and understand how Django migrations track schema changes before modifying or deleting tables.

## 2026-01-14
Created seperate regn pages for traveller and operator