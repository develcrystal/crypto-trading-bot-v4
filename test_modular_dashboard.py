#!/usr/bin/env python3
"""
🚀 MODULAR DASHBOARD TEST SCRIPT
Überprüft alle modularen Komponenten und Abhängigkeiten
"""

import sys
import os
from pathlib import Path
import importlib.util

def test_module_imports():
    """Test all modular component imports"""
    
    print("🚀 TESTING MODULAR DASHBOARD COMPONENTS")
    print("=" * 50)
    
    # Base path
    base_path = Path(__file__).parent
    sys.path.append(str(base_path))
    
    # Test imports
    test_results = {}
    
    modules_to_test = [
        ("ui.components.layout_manager", "Layout Manager"),
        ("ui.components.data_manager", "Data Manager"),
        ("ui.widgets.price_widget", "Price Widget"),
        ("ui.widgets.order_book", "Order Book Widget"),
        ("ui.widgets.portfolio_monitor", "Portfolio Monitor"),
        ("ui.widgets.trading_controls", "Trading Controls"),
        ("ui.advanced_chart", "Smart Money Chart"),
        ("core.api_client", "API Client")
    ]
    
    for module_name, display_name in modules_to_test:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                module = importlib.import_module(module_name)
                test_results[display_name] = "✅ SUCCESS"
                print(f"✅ {display_name}: Import successful")
            else:
                test_results[display_name] = "❌ NOT FOUND"
                print(f"❌ {display_name}: Module not found")
        except Exception as e:
            test_results[display_name] = f"❌ ERROR: {str(e)}"
            print(f"❌ {display_name}: Import error - {str(e)}")
    
    return test_results

def check_file_structure():
    """Check if all required files exist"""
    
    print("\n📁 CHECKING FILE STRUCTURE")
    print("=" * 30)
    
    base_path = Path(__file__).parent
    
    required_files = [
        "ui/__init__.py",
        "ui/components/__init__.py", 
        "ui/components/layout_manager.py",
        "ui/components/data_manager.py",
        "ui/widgets/__init__.py",
        "ui/widgets/price_widget.py",
        "ui/widgets/order_book.py",
        "ui/widgets/portfolio_monitor.py",
        "ui/widgets/trading_controls.py",
        "ui/advanced_chart.py",
        "ui/main_dashboard.py",
        "core/api_client.py",
        "launch_modular_dashboard.py"
    ]
    
    file_results = {}
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            file_results[file_path] = "✅ EXISTS"
            print(f"✅ {file_path}")
        else:
            file_results[file_path] = "❌ MISSING"
            print(f"❌ {file_path} - MISSING!")
    
    return file_results

def test_streamlit_compatibility():
    """Test Streamlit imports"""
    
    print("\n🎨 TESTING STREAMLIT COMPATIBILITY")
    print("=" * 35)
    
    try:
        import streamlit as st
        print("✅ Streamlit: Available")
        
        import plotly.graph_objects as go
        print("✅ Plotly: Available")
        
        import pandas as pd
        print("✅ Pandas: Available")
        
        import numpy as np
        print("✅ NumPy: Available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def generate_test_report(import_results, file_results, streamlit_ok):
    """Generate comprehensive test report"""
    
    print("\n📊 TEST REPORT SUMMARY")
    print("=" * 30)
    
    # Import results
    successful_imports = sum(1 for result in import_results.values() if "SUCCESS" in result)
    total_imports = len(import_results)
    
    print(f"📦 Module Imports: {successful_imports}/{total_imports} successful")
    
    # File structure
    existing_files = sum(1 for result in file_results.values() if "EXISTS" in result)
    total_files = len(file_results)
    
    print(f"📁 File Structure: {existing_files}/{total_files} files present")
    
    # Dependencies
    deps_status = "✅ Ready" if streamlit_ok else "❌ Missing dependencies"
    print(f"🎨 Dependencies: {deps_status}")
    
    # Overall status
    overall_ready = (successful_imports == total_imports and 
                    existing_files == total_files and 
                    streamlit_ok)
    
    print(f"\n🎯 OVERALL STATUS: {'✅ READY TO LAUNCH' if overall_ready else '❌ NEEDS ATTENTION'}")
    
    if overall_ready:
        print("\n🚀 READY TO LAUNCH MODULAR DASHBOARD!")
        print("Run: python launch_modular_dashboard.py")
    else:
        print("\n🔧 ISSUES TO RESOLVE:")
        if successful_imports < total_imports:
            print("   - Fix module import errors")
        if existing_files < total_files:
            print("   - Create missing files")
        if not streamlit_ok:
            print("   - Install missing dependencies")
    
    return overall_ready

def main():
    """Run all tests"""
    
    # Test imports
    import_results = test_module_imports()
    
    # Check file structure
    file_results = check_file_structure()
    
    # Test Streamlit
    streamlit_ok = test_streamlit_compatibility()
    
    # Generate report
    ready = generate_test_report(import_results, file_results, streamlit_ok)
    
    return ready

if __name__ == "__main__":
    main()
