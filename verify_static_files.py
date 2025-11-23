#!/usr/bin/env python3
"""
Static Files Verification Script for KB Helper
Checks that all CSS files exist and templates are properly configured.
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_mark(condition):
    return f"{GREEN}✓{RESET}" if condition else f"{RED}✗{RESET}"

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}KB Helper - Static Files Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    base_dir = Path(__file__).parent
    issues = []

    # 1. Check CSS files exist
    print(f"{YELLOW}[1] Checking CSS Files...{RESET}")
    css_files = [
        'analyzer/static/analyzer/css/base.css',
        'analyzer/static/analyzer/css/index.css',
        'analyzer/static/analyzer/css/analysis.css',
        'analyzer/static/analyzer/css/duplicates.css',
    ]

    for css_file in css_files:
        file_path = base_dir / css_file
        exists = file_path.exists()
        print(f"  {check_mark(exists)} {css_file}")
        if not exists:
            issues.append(f"Missing file: {css_file}")

    # 2. Check templates have {% load static %}
    print(f"\n{YELLOW}[2] Checking Template Configuration...{RESET}")
    templates = [
        'analyzer/templates/analyzer/base.html',
        'analyzer/templates/analyzer/index.html',
        'analyzer/templates/analyzer/stale_content.html',
        'analyzer/templates/analyzer/low_engagement.html',
        'analyzer/templates/analyzer/duplicates.html',
    ]

    for template in templates:
        template_path = base_dir / template
        if template_path.exists():
            content = template_path.read_text()
            has_load_static = '{% load static %}' in content
            has_static_link = "{% static 'analyzer/css/" in content or template == 'analyzer/templates/analyzer/base.html'

            status = has_load_static and (has_static_link or template == 'analyzer/templates/analyzer/base.html')
            print(f"  {check_mark(status)} {template}")

            if not has_load_static:
                issues.append(f"{template}: Missing {{% load static %}}")
            elif not has_static_link and template != 'analyzer/templates/analyzer/base.html':
                issues.append(f"{template}: No CSS link with {{% static %}}")
        else:
            print(f"  {check_mark(False)} {template} (not found)")
            issues.append(f"Template not found: {template}")

    # 3. Check base.html links CSS files
    print(f"\n{YELLOW}[3] Checking base.html CSS Links...{RESET}")
    base_html = base_dir / 'analyzer/templates/analyzer/base.html'
    if base_html.exists():
        content = base_html.read_text()
        has_base_css = "{% static 'analyzer/css/base.css' %}" in content
        print(f"  {check_mark(has_base_css)} Links to base.css")
        if not has_base_css:
            issues.append("base.html: Missing link to base.css")
    else:
        print(f"  {check_mark(False)} base.html not found")
        issues.append("base.html not found")

    # 4. Check for old inline styles (should be removed)
    print(f"\n{YELLOW}[4] Checking for Old Inline Styles...{RESET}")
    templates_to_check = [
        'analyzer/templates/analyzer/stale_content.html',
        'analyzer/templates/analyzer/low_engagement.html',
    ]

    clean_count = 0
    for template in templates_to_check:
        template_path = base_dir / template
        if template_path.exists():
            content = template_path.read_text()
            # Check if still using .chip class with white-text
            has_old_style = 'class="chip' in content and 'white-text' in content
            clean = not has_old_style
            clean_count += clean
            print(f"  {check_mark(clean)} {template} {'(clean)' if clean else '(old chip styling found)'}")
            if has_old_style:
                issues.append(f"{template}: Still using old chip styling")

    # 5. Check settings.py configuration
    print(f"\n{YELLOW}[5] Checking Django Settings...{RESET}")
    settings_path = base_dir / 'kb_portal/settings.py'
    if settings_path.exists():
        content = settings_path.read_text()
        has_static_url = "STATIC_URL" in content
        has_static_root = "STATIC_ROOT" in content

        print(f"  {check_mark(has_static_url)} STATIC_URL configured")
        print(f"  {check_mark(has_static_root)} STATIC_ROOT configured")

        if not has_static_url:
            issues.append("settings.py: STATIC_URL not configured")
        if not has_static_root:
            issues.append("settings.py: STATIC_ROOT not configured")
    else:
        print(f"  {check_mark(False)} settings.py not found")
        issues.append("settings.py not found")

    # 6. Check CSS file content
    print(f"\n{YELLOW}[6] Verifying CSS Content...{RESET}")
    base_css = base_dir / 'analyzer/static/analyzer/css/base.css'
    if base_css.exists():
        content = base_css.read_text()
        has_variables = ':root {' in content and '--primary-' in content
        has_card_styles = '.card {' in content
        has_shadows = '--shadow-' in content

        print(f"  {check_mark(has_variables)} CSS variables defined")
        print(f"  {check_mark(has_card_styles)} Card styles present")
        print(f"  {check_mark(has_shadows)} Shadow variables defined")

        if not has_variables:
            issues.append("base.css: Missing CSS variables")
        if not has_card_styles:
            issues.append("base.css: Missing card styles")
        if not has_shadows:
            issues.append("base.css: Missing shadow variables")

    analysis_css = base_dir / 'analyzer/static/analyzer/css/analysis.css'
    if analysis_css.exists():
        content = analysis_css.read_text()
        has_stat_cards = '.stat-card' in content
        has_clean_data = 'Table Data - Clean' in content or '.data-value' in content

        print(f"  {check_mark(has_stat_cards)} Statistics card styles present")
        print(f"  {check_mark(has_clean_data)} Clean table data styles present")

        if not has_stat_cards:
            issues.append("analysis.css: Missing stat-card styles")
        if not has_clean_data:
            issues.append("analysis.css: Missing clean table data styles")

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    if not issues:
        print(f"{GREEN}✓ All checks passed! Static files are properly configured.{RESET}")
        print(f"\n{YELLOW}Next steps:{RESET}")
        print("  1. Run: python manage.py runserver")
        print("  2. Visit: http://127.0.0.1:8000")
        print("  3. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)")
        print("  4. Verify modern styling on all pages")
    else:
        print(f"{RED}✗ Found {len(issues)} issue(s):{RESET}\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print(f"\n{YELLOW}Please fix the issues above and run this script again.{RESET}")
        sys.exit(1)

    print(f"{BLUE}{'='*60}{RESET}\n")

if __name__ == '__main__':
    main()
