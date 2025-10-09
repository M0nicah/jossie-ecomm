#!/usr/bin/env python3
"""
Django Development Optimization Script

This script helps optimize your Django development environment for faster startup times.
Run this periodically to maintain good performance.

Usage: python optimize_dev.py
"""

import os
import sqlite3
import subprocess
import time
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f" {text}")
    print("=" * 50)

def remove_ds_store_files():
    """Remove macOS .DS_Store files that can slow down file operations"""
    print_header("Removing .DS_Store files")
    
    ds_store_files = []
    for root, dirs, files in os.walk('.'):
        if '.DS_Store' in files:
            ds_store_path = os.path.join(root, '.DS_Store')
            ds_store_files.append(ds_store_path)
    
    if ds_store_files:
        for file_path in ds_store_files:
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            except OSError as e:
                print(f"❌ Failed to remove {file_path}: {e}")
        print(f"📊 Total .DS_Store files removed: {len(ds_store_files)}")
    else:
        print("✅ No .DS_Store files found")

def optimize_sqlite_database():
    """Optimize SQLite database performance"""
    print_header("Optimizing SQLite Database")
    
    db_path = 'db.sqlite3'
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return
    
    print(f"📊 Database size before: {os.path.getsize(db_path) / 1024:.1f} KB")
    
    try:
        # Test connection speed before optimization
        start_time = time.time()
        conn = sqlite3.connect(db_path)
        conn.close()
        connection_time_before = time.time() - start_time
        
        # Run VACUUM to defragment and optimize
        start_time = time.time()
        conn = sqlite3.connect(db_path)
        conn.execute('VACUUM;')
        conn.execute('ANALYZE;')  # Update query planner statistics
        conn.close()
        vacuum_time = time.time() - start_time
        
        # Test connection speed after optimization
        start_time = time.time()
        conn = sqlite3.connect(db_path)
        conn.close()
        connection_time_after = time.time() - start_time
        
        print(f"✅ Database optimized in {vacuum_time:.2f}s")
        print(f"📊 Database size after: {os.path.getsize(db_path) / 1024:.1f} KB")
        print(f"⚡ Connection time before: {connection_time_before:.3f}s")
        print(f"⚡ Connection time after: {connection_time_after:.3f}s")
        
        if connection_time_before > connection_time_after:
            improvement = ((connection_time_before - connection_time_after) / connection_time_before) * 100
            print(f"🚀 Connection speed improved by {improvement:.1f}%")
        
    except sqlite3.Error as e:
        print(f"❌ Database optimization failed: {e}")

def check_staticfiles_issues():
    """Check for static files performance issues"""
    print_header("Checking Static Files")
    
    staticfiles_dir = Path('staticfiles')
    static_dir = Path('static')
    
    if staticfiles_dir.exists():
        file_count = sum(1 for _ in staticfiles_dir.rglob('*') if _.is_file())
        print(f"📊 Staticfiles directory contains {file_count} files")
        
        if file_count > 1000:
            print("⚠️  Warning: Large number of static files may slow startup")
            print("   Consider running 'python manage.py collectstatic --clear' periodically")
    
    if static_dir.exists():
        file_count = sum(1 for _ in static_dir.rglob('*') if _.is_file())
        print(f"📊 Static directory contains {file_count} files")

def check_media_files():
    """Check media files directory"""
    print_header("Checking Media Files")
    
    media_dir = Path('media')
    if media_dir.exists():
        file_count = sum(1 for _ in media_dir.rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in media_dir.rglob('*') if f.is_file())
        print(f"📊 Media directory contains {file_count} files")
        print(f"📊 Total size: {total_size / (1024*1024):.1f} MB")
        
        if file_count > 500:
            print("⚠️  Warning: Large number of media files")
            print("   Consider using cloud storage (Cloudinary) for production")
    else:
        print("✅ No local media directory found")

def check_python_cache():
    """Clean Python bytecode cache files"""
    print_header("Checking Python Cache")
    
    pycache_dirs = []
    pyc_files = []
    
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    
    total_items = len(pycache_dirs) + len(pyc_files)
    if total_items > 0:
        print(f"📊 Found {len(pycache_dirs)} __pycache__ directories and {len(pyc_files)} .pyc files")
        print("💡 Tip: Run 'find . -name \"*.pyc\" -delete' and 'find . -name \"__pycache__\" -type d -exec rm -rf {} +' to clean")
    else:
        print("✅ Python cache is clean")

def test_startup_speed():
    """Test Django startup speed"""
    print_header("Testing Django Startup Speed")
    
    try:
        start_time = time.time()
        result = subprocess.run(['python3', 'manage.py', 'check'], 
                              capture_output=True, text=True, timeout=30)
        end_time = time.time()
        
        startup_time = end_time - start_time
        print(f"⚡ Django startup time: {startup_time:.2f}s")
        
        if startup_time < 1.0:
            print("🚀 Excellent startup time!")
        elif startup_time < 3.0:
            print("✅ Good startup time")
        elif startup_time < 10.0:
            print("⚠️  Moderate startup time - consider optimizations")
        else:
            print("❌ Slow startup time - optimization needed")
        
        if result.returncode != 0:
            print("❌ Django check failed:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Django startup test timed out (>30s)")
    except Exception as e:
        print(f"❌ Error testing startup: {e}")

def show_optimization_tips():
    """Show additional optimization tips"""
    print_header("Optimization Tips")
    
    tips = [
        "🔧 Use DEBUG=False in production for better performance",
        "🔧 Consider using Redis for caching instead of local memory",
        "🔧 Enable database connection pooling for high-traffic sites",
        "🔧 Use a CDN for static files in production",
        "🔧 Regular database maintenance (VACUUM, ANALYZE)",
        "🔧 Monitor and limit the number of installed apps",
        "🔧 Use select_related() and prefetch_related() in queries",
        "🔧 Consider using django-debug-toolbar for query optimization"
    ]
    
    for tip in tips:
        print(tip)

def main():
    """Run all optimization tasks"""
    print("🚀 Django Development Optimization Tool")
    print("This script will optimize your Django development environment")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run optimization tasks
    remove_ds_store_files()
    optimize_sqlite_database()
    check_staticfiles_issues()
    check_media_files()
    check_python_cache()
    test_startup_speed()
    show_optimization_tips()
    
    print("\n🎉 Optimization complete!")
    print("Run this script periodically to maintain good performance.")

if __name__ == '__main__':
    main()