#!/usr/bin/env python3
"""
Debug Observer - See what UI elements are detected.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from AppKit import NSWorkspace
import Quartz

def get_frontmost_app():
    """Get the frontmost application."""
    workspace = NSWorkspace.sharedWorkspace()
    active_app = workspace.frontmostApplication()
    return active_app.localizedName()

def get_ui_elements(app_ref):
    """Get all UI elements from an application."""
    elements = []
    
    try:
        # Get all windows
        windows = app_ref.windows()
        if not windows:
            return elements
        
        # Get first window
        window = windows[0]
        
        # Get all children recursively
        def traverse(element, depth=0):
            try:
                role = element.role()
                title = element.title() if hasattr(element, 'title') else None
                value = element.value() if hasattr(element, 'value') else None
                
                indent = "  " * depth
                print(f"{indent}Role: {role}")
                if title:
                    print(f"{indent}  Title: {title}")
                if value:
                    print(f"{indent}  Value: {value}")
                
                elements.append({
                    'role': role,
                    'title': title,
                    'value': value,
                    'depth': depth
                })
                
                # Traverse children
                children = element.children()
                if children:
                    for child in children:
                        traverse(child, depth + 1)
            except Exception as e:
                print(f"{indent}Error: {e}")
        
        traverse(window)
        
    except Exception as e:
        print(f"Error getting UI elements: {e}")
    
    return elements

def main():
    """Main debug function."""
    print("="*60)
    print("Sentry-AI Observer Debug")
    print("="*60)
    
    print("\nWaiting 5 seconds...")
    print("Open a dialog (e.g., TextEdit > Cmd+W > Save dialog)")
    print()
    
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("\nCapturing UI elements...\n")
    
    # Get frontmost app
    app_name = get_frontmost_app()
    print(f"Frontmost app: {app_name}\n")
    
    # Get accessibility reference
    try:
        # Get running applications
        running_apps = NSWorkspace.sharedWorkspace().runningApplications()
        target_app = None
        
        for app in running_apps:
            if app.localizedName() == app_name:
                target_app = app
                break
        
        if not target_app:
            print(f"Could not find app: {app_name}")
            return
        
        # Get accessibility reference
        pid = target_app.processIdentifier()
        app_ref = Quartz.AXUIElementCreateApplication(pid)
        
        # Get UI elements
        elements = get_ui_elements(app_ref)
        
        print("\n" + "="*60)
        print(f"Total elements found: {len(elements)}")
        print("="*60)
        
        # Count by role
        roles = {}
        for elem in elements:
            role = elem['role']
            roles[role] = roles.get(role, 0) + 1
        
        print("\nElements by role:")
        for role, count in sorted(roles.items()):
            print(f"  {role}: {count}")
        
        # Find buttons
        buttons = [e for e in elements if 'Button' in str(e['role'])]
        print(f"\nButtons found: {len(buttons)}")
        for btn in buttons:
            print(f"  - {btn['title']} (role: {btn['role']})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDebug interrupted")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
