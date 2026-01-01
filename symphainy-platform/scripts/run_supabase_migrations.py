#!/usr/bin/env python3
"""
Supabase Migration Runner - Idiot-Proof Edition

Safely runs SQL migrations against Supabase database.
Uses direct PostgreSQL connection for reliable SQL execution.

Usage:
    python3 scripts/run_supabase_migrations.py [--dry-run] [--migration N]

Options:
    --dry-run: Show what would be executed without running
    --migration N: Run only migration N (001, 002, etc.)
    --skip-confirm: Skip confirmation prompt (useful for automation)
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Try different import paths
    try:
        from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
        from utilities.configuration.environment_loader import EnvironmentLoader
    except ImportError:
        # Alternative import path
        from symphainy_platform.utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
        from symphainy_platform.utilities.configuration.environment_loader import EnvironmentLoader
except ImportError as e:
    print(f"⚠️  Could not import configuration utilities: {e}")
    print("   Will use environment variables directly")
    UnifiedConfigurationManager = None
    EnvironmentLoader = None


class SupabaseMigrationRunner:
    """Run Supabase migrations safely using direct PostgreSQL connection."""
    
    def __init__(self, dry_run: bool = False):
        """Initialize migration runner."""
        self.dry_run = dry_run
        
        # Load Supabase credentials from environment
        if EnvironmentLoader:
            try:
                self.config_manager = UnifiedConfigurationManager()
                self.env_loader = EnvironmentLoader(self.config_manager)
                self.supabase_url = self.env_loader.get_secret("SUPABASE_URL")
                self.supabase_service_key = self.env_loader.get_secret("SUPABASE_SERVICE_KEY")
            except Exception as e:
                print(f"⚠️  Could not load from config manager: {e}")
                print("   Falling back to environment variables")
                self.supabase_url = None
                self.supabase_service_key = None
        else:
            self.supabase_url = None
            self.supabase_service_key = None
        
        # Fallback to environment variables
        if not self.supabase_url:
            self.supabase_url = os.getenv("SUPABASE_URL")
        if not self.supabase_service_key:
            self.supabase_service_key = (
                os.getenv("SUPABASE_SERVICE_KEY") or 
                os.getenv("SUPABASE_SECRET_KEY") or
                os.getenv("SUPABASE_KEY")
            )
        
        # Try loading from .env.secrets file
        if not self.supabase_url or not self.supabase_service_key:
            try:
                from dotenv import load_dotenv
                secrets_file = project_root / ".env.secrets"
                if secrets_file.exists():
                    load_dotenv(secrets_file)
                    if not self.supabase_url:
                        self.supabase_url = os.getenv("SUPABASE_URL")
                    if not self.supabase_service_key:
                        self.supabase_service_key = (
                            os.getenv("SUPABASE_SERVICE_KEY") or 
                            os.getenv("SUPABASE_SECRET_KEY") or
                            os.getenv("SUPABASE_KEY")
                        )
            except ImportError:
                pass
        
        if not self.supabase_url or not self.supabase_service_key:
            print("❌ Missing Supabase credentials")
            print("   Required: SUPABASE_URL, SUPABASE_SERVICE_KEY")
            print("   Set in environment or .env.secrets file")
            sys.exit(1)
        
        # Extract project reference from URL
        # Format: https://<project-ref>.supabase.co
        try:
            self.project_ref = self.supabase_url.split("//")[1].split(".")[0]
        except:
            print("❌ Could not extract project reference from SUPABASE_URL")
            sys.exit(1)
        
        # Migration directory
        self.migration_dir = project_root / "foundations" / "public_works_foundation" / "sql" / "migrations"
        
        if not self.migration_dir.exists():
            print(f"❌ Migration directory not found: {self.migration_dir}")
            sys.exit(1)
        
        # Database connection string (will be constructed)
        self.db_url = None
        self._setup_database_connection()
    
    def _setup_database_connection(self):
        """Setup database connection string."""
        # Try to get from environment first
        self.db_url = os.getenv("DATABASE_URL")
        
        if self.db_url:
            print("✅ Found DATABASE_URL in environment")
            return
        
        # Try to construct from Supabase URL
        # We need the direct database connection string
        # Format: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
        
        # Get database password from environment or secrets
        db_password = None
        if hasattr(self, 'env_loader') and self.env_loader:
            try:
                db_password = self.env_loader.get_secret("SUPABASE_DB_PASSWORD")
            except:
                pass
        if not db_password:
            db_password = os.getenv("SUPABASE_DB_PASSWORD")
        
        if db_password:
            self.db_url = f"postgresql://postgres.{self.project_ref}:{db_password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
            print("✅ Constructed DATABASE_URL from credentials")
        else:
            print("⚠️  DATABASE_URL not found")
            print("   Options:")
            print("   1. Set DATABASE_URL environment variable")
            print("   2. Set SUPABASE_DB_PASSWORD in .env.secrets")
            print("   3. Get connection string from Supabase Dashboard:")
            print(f"      Settings → Database → Connection string → URI")
    
    def get_migration_files(self) -> List[Path]:
        """Get migration files in order."""
        migrations = sorted(self.migration_dir.glob("*.sql"))
        return migrations
    
    def read_migration_file(self, file_path: Path) -> str:
        """Read migration file content."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Failed to read {file_path}: {e}")
            raise
    
    def execute_sql_via_psycopg2(self, sql: str, description: str) -> bool:
        """Execute SQL via psycopg2 (Python PostgreSQL adapter - most reliable)."""
        if not self.db_url:
            print(f"   ❌ Cannot execute: DATABASE_URL not available")
            return False
        
        if self.dry_run:
            print(f"   [DRY RUN] Would execute: {description}")
            print(f"   SQL preview: {sql[:200]}...")
            return True
        
        try:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # Parse connection string
            conn = psycopg2.connect(self.db_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            
            # Execute SQL (split by semicolon for multiple statements)
            statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
            
            for statement in statements:
                if statement:
                    cursor.execute(statement)
            
            cursor.close()
            conn.close()
            
            print(f"   ✅ {description}")
            return True
            
        except ImportError:
            print(f"   ⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
            return False
        except Exception as e:
            print(f"   ❌ psycopg2 execution failed: {e}")
            return False
    
    def execute_sql_via_psql(self, sql: str, description: str) -> bool:
        """Execute SQL via psql (command-line tool)."""
        if not self.db_url:
            print(f"   ❌ Cannot execute: DATABASE_URL not available")
            return False
        
        if self.dry_run:
            print(f"   [DRY RUN] Would execute: {description}")
            print(f"   SQL preview: {sql[:200]}...")
            return True
        
        try:
            # Use psql to execute SQL
            # -c flag executes command and exits
            result = subprocess.run(
                ["psql", self.db_url, "-c", sql],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"   ✅ {description}")
                if result.stdout.strip():
                    # Show first few lines of output
                    output_lines = result.stdout.strip().split('\n')[:3]
                    for line in output_lines:
                        if line.strip():
                            print(f"      {line}")
                return True
            else:
                print(f"   ❌ {description}")
                print(f"      Error: {result.stderr[:200]}")
                return False
                
        except FileNotFoundError:
            print(f"   ⚠️  psql not found. Install PostgreSQL client:")
            print(f"      Ubuntu/Debian: sudo apt-get install postgresql-client")
            print(f"      macOS: brew install postgresql")
            return False
        except subprocess.TimeoutExpired:
            print(f"   ❌ Execution timed out: {description}")
            return False
        except Exception as e:
            print(f"   ❌ psql execution failed: {e}")
            return False
    
    def execute_sql_via_supabase_cli(self, sql_file: Path) -> bool:
        """Execute SQL via Supabase CLI (alternative method)."""
        if self.dry_run:
            print(f"   [DRY RUN] Would execute via Supabase CLI: {sql_file.name}")
            return True
        
        try:
            # Check if Supabase CLI is available
            result = subprocess.run(
                ["supabase", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"   ⚠️  Supabase CLI not found")
                return False
            
            # Execute SQL file via Supabase CLI
            # Note: This requires the project to be linked
            result = subprocess.run(
                ["supabase", "db", "execute", "--file", str(sql_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"   ✅ Executed via Supabase CLI: {sql_file.name}")
                return True
            else:
                print(f"   ❌ Supabase CLI execution failed: {result.stderr[:200]}")
                return False
                
        except FileNotFoundError:
            print(f"   ⚠️  Supabase CLI not found")
            return False
        except Exception as e:
            print(f"   ❌ Supabase CLI execution failed: {e}")
            return False
    
    def run_migration(self, migration_file: Path) -> bool:
        """Run a single migration file."""
        migration_name = migration_file.name
        print(f"\n📄 Running migration: {migration_name}")
        
        try:
            sql = self.read_migration_file(migration_file)
            
            if not sql.strip():
                print(f"⚠️  Migration file is empty: {migration_name}")
                return True
            
            # Try psycopg2 first (most reliable Python method)
            if self.db_url:
                print(f"   Using psycopg2 connection...")
                success = self.execute_sql_via_psycopg2(sql, migration_name)
                if success:
                    return True
                else:
                    print(f"   ⚠️  psycopg2 failed, trying psql...")
            
            # Try psql as fallback
            if self.db_url:
                print(f"   Using psql connection...")
                success = self.execute_sql_via_psql(sql, migration_name)
                if success:
                    return True
                else:
                    print(f"   ⚠️  psql failed, trying Supabase CLI...")
            
            # Fallback to Supabase CLI
            success = self.execute_sql_via_supabase_cli(migration_file)
            if success:
                return True
            
            # If both fail, provide instructions
            print(f"\n❌ Could not execute migration automatically")
            print(f"   Migration file: {migration_file}")
            print(f"\n   Manual options:")
            print(f"   1. Copy SQL to Supabase Dashboard → SQL Editor")
            print(f"   2. Use psql: psql <DATABASE_URL> -f {migration_file}")
            print(f"   3. Use Supabase CLI: supabase db execute --file {migration_file}")
            
            return False
            
        except Exception as e:
            print(f"❌ Error running migration {migration_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_migrations(self, specific_migration: Optional[str] = None, skip_confirm: bool = False) -> bool:
        """Run all migrations or a specific one."""
        migrations = self.get_migration_files()
        
        if not migrations:
            print("⚠️  No migration files found")
            return True
        
        print(f"📦 Found {len(migrations)} migration file(s):")
        for m in migrations:
            print(f"   - {m.name}")
        
        if specific_migration:
            # Run only specific migration
            migrations = [m for m in migrations if specific_migration in m.name]
            if not migrations:
                print(f"❌ Migration {specific_migration} not found")
                return False
            print(f"\n🎯 Running only: {migrations[0].name}")
        
        print(f"\n{'🔍 [DRY RUN MODE]' if self.dry_run else '🚀 [EXECUTION MODE]'}")
        print(f"   Will run {len(migrations)} migration(s)")
        
        if not self.dry_run and not skip_confirm:
            print(f"\n⚠️  This will modify your Supabase database.")
            print(f"   Project: {self.project_ref}")
            print(f"   URL: {self.supabase_url}")
            response = input("\n   Continue? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Migration cancelled")
                return False
        
        success_count = 0
        failed_migrations = []
        
        for migration in migrations:
            if self.run_migration(migration):
                success_count += 1
            else:
                failed_migrations.append(migration.name)
                print(f"\n❌ Migration failed: {migration.name}")
                if not skip_confirm:
                    response = input("   Continue with next migration? (yes/no): ")
                    if response.lower() != 'yes':
                        print("   Stopping migration process")
                        break
        
        print(f"\n{'='*60}")
        if success_count == len(migrations):
            print(f"✅ Successfully ran {success_count}/{len(migrations)} migration(s)")
        else:
            print(f"⚠️  Completed {success_count}/{len(migrations)} migration(s)")
            if failed_migrations:
                print(f"   Failed: {', '.join(failed_migrations)}")
                print(f"   Review errors above and fix before retrying")
        
        return success_count == len(migrations)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Supabase migrations safely",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (see what would happen)
  python3 scripts/run_supabase_migrations.py --dry-run
  
  # Run all migrations
  python3 scripts/run_supabase_migrations.py
  
  # Run specific migration
  python3 scripts/run_supabase_migrations.py --migration 001
  
  # Run without confirmation (for automation)
  python3 scripts/run_supabase_migrations.py --skip-confirm
        """
    )
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be executed without running")
    parser.add_argument("--migration", type=str, 
                       help="Run only specific migration (e.g., '001')")
    parser.add_argument("--skip-confirm", action="store_true",
                       help="Skip confirmation prompt (useful for automation)")
    
    args = parser.parse_args()
    
    print("="*60)
    print("Supabase Migration Runner")
    print("="*60)
    
    runner = SupabaseMigrationRunner(dry_run=args.dry_run)
    success = runner.run_all_migrations(
        specific_migration=args.migration,
        skip_confirm=args.skip_confirm
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
