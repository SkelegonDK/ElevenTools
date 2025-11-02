"""UI tests for sidebar font consistency debugging."""

import pytest
from playwright.sync_api import Page, expect


class TestSidebarFontConsistency:
    """Test suite for debugging sidebar font consistency issues."""

    def test_sidebar_font_before_button_press(self, configured_page: Page, streamlit_server: str):
        """Capture sidebar font before any button interaction."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for fonts to load
        
        # Get sidebar element
        sidebar = configured_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        # Capture computed font-family of sidebar
        sidebar_font_before = configured_page.evaluate("""
            () => {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) return null;
                const style = window.getComputedStyle(sidebar);
                return {
                    fontFamily: style.fontFamily,
                    fontWeight: style.fontWeight,
                    fontSize: style.fontSize
                };
            }
        """)
        
        print(f"\n[DEBUG] Sidebar font BEFORE button press:")
        print(f"  Font Family: {sidebar_font_before['fontFamily']}")
        print(f"  Font Weight: {sidebar_font_before['fontWeight']}")
        print(f"  Font Size: {sidebar_font_before['fontSize']}")
        
        # Store for comparison
        configured_page._sidebar_font_before = sidebar_font_before
        
        assert sidebar_font_before is not None, "Sidebar font should be accessible"

    def test_sidebar_font_after_button_press(self, configured_page: Page, streamlit_server: str):
        """Capture sidebar font after button interaction."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)  # Wait for fonts to load
        
        # Get sidebar element and capture initial font
        sidebar = configured_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        initial_font = configured_page.evaluate("""
            () => {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) return null;
                const style = window.getComputedStyle(sidebar);
                return {
                    fontFamily: style.fontFamily,
                    fontWeight: style.fontWeight,
                    fontSize: style.fontSize
                };
            }
        """)
        
        print(f"\n[DEBUG] Sidebar font BEFORE button press:")
        print(f"  Font Family: {initial_font['fontFamily']}")
        print(f"  Font Weight: {initial_font['fontWeight']}")
        
        # Find and click a button - prefer expander toggles as they're safe to click
        expander_button = configured_page.locator('[data-testid="stExpander"] button').first
        
        if expander_button.count() > 0:
            try:
                expander_button.click(timeout=5000)
            except Exception:
                # Try force click if normal click fails
                expander_button.click(force=True, timeout=2000)
        else:
            # Fallback: try to find Generate Audio button or other action buttons
            action_buttons = configured_page.locator('button:not([data-testid="stBaseButton-header"])')
            if action_buttons.count() > 0:
                try:
                    action_buttons.first.click(timeout=5000)
                except Exception:
                    action_buttons.first.click(force=True, timeout=2000)
        
        # Wait for Streamlit rerun to complete
        # Wait for loading indicators to disappear
        try:
            loading_overlay = configured_page.locator('[data-testid="stAppSpinner"]')
            if loading_overlay.count() > 0:
                loading_overlay.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass
        
        configured_page.wait_for_load_state("networkidle", timeout=5000)
        configured_page.wait_for_timeout(1000)  # Additional wait for font reload
        
        # Capture font after button press
        font_after = configured_page.evaluate("""
            () => {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) return null;
                const style = window.getComputedStyle(sidebar);
                return {
                    fontFamily: style.fontFamily,
                    fontWeight: style.fontWeight,
                    fontSize: style.fontSize
                };
            }
        """)
        
        print(f"\n[DEBUG] Sidebar font AFTER button press:")
        print(f"  Font Family: {font_after['fontFamily']}")
        print(f"  Font Weight: {font_after['fontWeight']}")
        print(f"  Font Size: {font_after['fontSize']}")
        
        # Compare fonts
        if initial_font and font_after:
            font_changed = (
                initial_font['fontFamily'] != font_after['fontFamily'] or
                initial_font['fontWeight'] != font_after['fontWeight']
            )
            
            if font_changed:
                print(f"\n[WARNING] Font changed after button press!")
                print(f"  Before: {initial_font['fontFamily']} / {initial_font['fontWeight']}")
                print(f"  After: {font_after['fontFamily']} / {font_after['fontWeight']}")
            else:
                print(f"\n[OK] Font remained consistent")
        
        assert font_after is not None, "Sidebar font should be accessible after button press"

    def _wait_for_streamlit_ready(self, page: Page, timeout: int = 5000):
        """Wait for Streamlit to finish loading/rerunning."""
        # Wait for loading indicators to disappear
        try:
            # Check for Streamlit's loading spinner/overlay
            loading_overlay = page.locator('[data-testid="stAppSpinner"]')
            if loading_overlay.count() > 0:
                loading_overlay.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass  # No loading overlay found, that's fine
        
        # Wait for network to be idle
        page.wait_for_load_state("networkidle", timeout=timeout)
        # Additional wait for fonts to stabilize
        page.wait_for_timeout(1000)

    def test_sidebar_font_multiple_interactions(self, configured_page: Page, streamlit_server: str):
        """Test sidebar font consistency across multiple button presses."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)
        
        sidebar = configured_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        
        fonts_captured = []
        
        # Capture initial font
        initial_font = configured_page.evaluate("""
            () => {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) return null;
                const style = window.getComputedStyle(sidebar);
                return {
                    fontFamily: style.fontFamily,
                    fontWeight: style.fontWeight
                };
            }
        """)
        fonts_captured.append(("Initial", initial_font))
        
        # Perform multiple interactions
        for i in range(3):
            # Wait for Streamlit to be ready before each interaction
            self._wait_for_streamlit_ready(configured_page)
            
            # Find buttons, excluding header/navigation buttons
            # Target buttons in the main content area or specific action buttons
            action_buttons = configured_page.locator('button:not([data-testid="stBaseButton-header"])')
            
            # Try to find specific action buttons first (like expander toggles)
            expander_buttons = configured_page.locator('[data-testid="stExpander"] button')
            
            button_to_click = None
            if expander_buttons.count() > 0:
                # Use expander toggle buttons as they're safe to click multiple times
                button_to_click = expander_buttons.first
            elif action_buttons.count() > 0:
                # Fall back to any non-header button
                button_to_click = action_buttons.first
            
            if button_to_click and button_to_click.count() > 0:
                try:
                    # Try normal click first
                    button_to_click.click(timeout=5000)
                except Exception:
                    # If normal click fails, try force click
                    try:
                        button_to_click.click(force=True, timeout=2000)
                    except Exception:
                        # If both fail, skip this interaction
                        print(f"\n[WARNING] Could not click button for interaction {i+1}, skipping")
                        continue
                
                # Wait for Streamlit rerun to complete
                self._wait_for_streamlit_ready(configured_page)
                
                # Capture font after each interaction
                font = configured_page.evaluate("""
                    () => {
                        const sidebar = document.querySelector('[data-testid="stSidebar"]');
                        if (!sidebar) return null;
                        const style = window.getComputedStyle(sidebar);
                        return {
                            fontFamily: style.fontFamily,
                            fontWeight: style.fontWeight
                        };
                    }
                """)
                fonts_captured.append((f"After interaction {i+1}", font))
            else:
                print(f"\n[WARNING] No clickable button found for interaction {i+1}, skipping")
                break
        
        # Print all captured fonts
        print(f"\n[DEBUG] Font consistency across {len(fonts_captured)} interactions:")
        for label, font in fonts_captured:
            if font:
                print(f"  {label}: {font['fontFamily']} / {font['fontWeight']}")
        
        # Verify consistency (need at least 2 samples)
        if len(fonts_captured) > 1:
            reference_font = fonts_captured[0][1]
            for label, font in fonts_captured[1:]:
                if font and reference_font:
                    assert font['fontFamily'] == reference_font['fontFamily'], \
                        f"Font family changed: {label} has {font['fontFamily']} instead of {reference_font['fontFamily']}"
                    assert font['fontWeight'] == reference_font['fontWeight'], \
                        f"Font weight changed: {label} has {font['fontWeight']} instead of {reference_font['fontWeight']}"
        else:
            pytest.skip("Not enough interactions completed to verify consistency")

    def test_sidebar_font_across_pages(self, configured_page: Page, streamlit_server: str):
        """Test sidebar font consistency when navigating between pages."""
        configured_page.goto(streamlit_server)
        configured_page.wait_for_load_state("networkidle")
        configured_page.wait_for_timeout(2000)
        
        # Capture font on main page
        main_page_font = configured_page.evaluate("""
            () => {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) return null;
                const style = window.getComputedStyle(sidebar);
                return {
                    fontFamily: style.fontFamily,
                    fontWeight: style.fontWeight
                };
            }
        """)
        
        print(f"\n[DEBUG] Main page sidebar font:")
        print(f"  Font Family: {main_page_font['fontFamily']}")
        print(f"  Font Weight: {main_page_font['fontWeight']}")
        
        # Navigate to Bulk Generation page
        bulk_link = configured_page.get_by_role("link", name="Bulk Generation", exact=False)
        if bulk_link.count() > 0:
            bulk_link.click()
            configured_page.wait_for_load_state("networkidle")
            configured_page.wait_for_timeout(2000)
            
            bulk_page_font = configured_page.evaluate("""
                () => {
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (!sidebar) return null;
                    const style = window.getComputedStyle(sidebar);
                    return {
                        fontFamily: style.fontFamily,
                        fontWeight: style.fontWeight
                    };
                }
            """)
            
            print(f"\n[DEBUG] Bulk Generation page sidebar font:")
            print(f"  Font Family: {bulk_page_font['fontFamily']}")
            print(f"  Font Weight: {bulk_page_font['fontWeight']}")
            
            # Compare fonts
            if main_page_font and bulk_page_font:
                assert main_page_font['fontFamily'] == bulk_page_font['fontFamily'], \
                    f"Font family differs between pages: main={main_page_font['fontFamily']}, bulk={bulk_page_font['fontFamily']}"
                assert main_page_font['fontWeight'] == bulk_page_font['fontWeight'], \
                    f"Font weight differs between pages: main={main_page_font['fontWeight']}, bulk={bulk_page_font['fontWeight']}"

