"""
Automated Comprehensive Verification Suite for Theme Switcher (Light, Dark, System)
in Internship FAQ Assistant.
"""

import sys
import unittest
import requests
import re
import db

BASE_URL = "http://127.0.0.1:5000"


class TestThemeImplementation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure server is reachable
        try:
            r = requests.get(f"{BASE_URL}/", timeout=5)
            assert r.status_code == 200
        except Exception as e:
            print(f"Error: Flask server not reachable at {BASE_URL}: {e}")
            sys.exit(1)

    def test_01_index_html_anti_fouc_and_switchers(self):
        """Verify index.html contains Anti-FOUC script, topbar, sidebar, and appearance pane."""
        r = requests.get(f"{BASE_URL}/")
        self.assertEqual(r.status_code, 200)
        html = r.text

        # 1. Anti-FOUC script before style.css
        self.assertIn("Instant Anti-FOUC Theme Resolution Script", html)
        self.assertIn("localStorage.getItem(\"internbot_theme\")", html)
        self.assertIn("document.documentElement.setAttribute(\"data-theme\", resolved)", html)

        # 2. Topbar theme switcher with light, dark, system
        self.assertIn('id="topbar-theme-switcher"', html)
        self.assertIn('data-theme-val="light"', html)
        self.assertIn('data-theme-val="dark"', html)
        self.assertIn('data-theme-val="system"', html)
        self.assertIn('☀️', html)
        self.assertIn('🌙', html)
        self.assertIn('💻', html)

        # 3. Sidebar theme switcher in sidebar-footer
        self.assertIn('class="sidebar-theme-bar"', html)
        self.assertIn('id="sidebar-theme-pill"', html)
        self.assertIn('id="sidebar-theme-current-text"', html)

        # 4. Settings Appearance tab and section
        self.assertIn('data-section="appearance"', html)
        self.assertIn('id="pane-appearance"', html)
        self.assertIn('data-theme-choice="light"', html)
        self.assertIn('data-theme-choice="dark"', html)
        self.assertIn('data-theme-choice="system"', html)
        self.assertIn('id="save-appearance-btn"', html)
        self.assertIn('id="theme-save-toast"', html)
        self.assertIn('class="theme-card-preview light-preview"', html)
        self.assertIn('class="theme-card-preview dark-preview"', html)
        self.assertIn('class="theme-card-preview split-preview"', html)

        print("PASS: test_01_index_html_anti_fouc_and_switchers")

    def test_02_css_theme_variables_and_palettes(self):
        """Verify style.css includes exact requested variables for Light and Dark themes."""
        r = requests.get(f"{BASE_URL}/static/style.css")
        self.assertEqual(r.status_code, 200)
        css = r.text

        # 1. Light Theme Variables
        self.assertIn('[data-theme="light"]', css)
        self.assertIn('--bg-primary: #ffffff;', css)
        self.assertIn('--bg-secondary: #f8fafc;', css)
        self.assertIn('--bg-sidebar: #ffffff;', css)
        self.assertIn('--bg-card: #ffffff;', css)
        self.assertIn('--text-primary: #1f2937;', css)
        self.assertIn('--text-secondary: #64748b;', css)
        self.assertIn('--border-color: #e2e8f0;', css)
        self.assertIn('--input-bg: #ffffff;', css)

        # 2. Dark Theme Variables - exact user requested palette
        self.assertIn('[data-theme="dark"]', css)
        self.assertIn('--bg-primary: #212121;', css)
        self.assertIn('--bg-secondary: #2a2a2a;', css)
        self.assertIn('--bg-sidebar: #171717;', css)
        self.assertIn('--bg-card: #2a2a2a;', css)
        self.assertIn('--text-primary: #f5f5f5;', css)
        self.assertIn('--text-secondary: #b3b3b3;', css)
        self.assertIn('--border-color: #404040;', css)
        self.assertIn('--input-bg: #303030;', css)

        # 3. Theme Switcher components
        self.assertIn('.theme-switcher-pill', css)
        self.assertIn('.sidebar-theme-bar', css)
        self.assertIn('.appearance-status-banner', css)
        self.assertIn('.theme-cards-grid', css)
        self.assertIn('.theme-option-card', css)
        self.assertIn('.light-preview', css)
        self.assertIn('.dark-preview', css)
        self.assertIn('.split-preview', css)

        print("PASS: test_02_css_theme_variables_and_palettes")

    def test_03_js_theme_controller(self):
        """Verify script.js includes setTheme, syncThemeUI, initThemeManager, and OS listener."""
        r = requests.get(f"{BASE_URL}/static/script.js")
        self.assertEqual(r.status_code, 200)
        js = r.text

        self.assertIn("function resolveActiveTheme(preference)", js)
        self.assertIn("function setTheme(preference, saveToServer = false)", js)
        self.assertIn("function syncThemeUI(preference, active)", js)
        self.assertIn("function initThemeManager()", js)
        self.assertIn("prefers-color-scheme: dark", js)
        self.assertIn("initThemeManager();", js)

        print("PASS: test_03_js_theme_controller")

    def test_04_backend_settings_api_theme_persistence(self):
        """Verify /api/settings saves and returns theme correctly for authenticated and guest users."""
        session = requests.Session()

        # 1. Sign in with demo account
        auth_res = session.post(f"{BASE_URL}/api/auth/google", json={"email": "student_demo@gmail.com", "name": "Demo Student"})
        self.assertEqual(auth_res.status_code, 200)
        auth_data = auth_res.json()
        self.assertTrue(auth_data.get("success"))
        user_id = auth_data["user"]["id"]

        # 2. Save dark theme
        save_res = session.post(f"{BASE_URL}/api/settings", json={"theme": "dark"})
        self.assertEqual(save_res.status_code, 200)
        save_data = save_res.json()
        self.assertTrue(save_data.get("success"))
        self.assertEqual(save_data["settings"]["theme"], "dark")

        # 3. Retrieve settings
        get_res = session.get(f"{BASE_URL}/api/settings")
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.json()
        self.assertTrue(get_data.get("logged_in"))
        self.assertEqual(get_data["settings"]["theme"], "dark")

        # 4. Check SQLite database record directly
        db_settings = db.get_user_settings(user_id)
        self.assertEqual(db_settings["theme"], "dark")

        # 5. Switch to system theme
        save_sys = session.post(f"{BASE_URL}/api/settings", json={"theme": "system"})
        self.assertEqual(save_sys.status_code, 200)
        self.assertEqual(save_sys.json()["settings"]["theme"], "system")
        self.assertEqual(db.get_user_settings(user_id)["theme"], "system")

        # 6. Guest user persistence test (not logged in)
        guest_session = requests.Session()
        guest_save = guest_session.post(f"{BASE_URL}/api/settings", json={"theme": "light"})
        self.assertEqual(guest_save.status_code, 200)
        self.assertFalse(guest_save.json().get("logged_in"))
        self.assertEqual(guest_save.json()["settings"]["theme"], "light")

        print("PASS: test_04_backend_settings_api_theme_persistence")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestThemeImplementation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\nALL THEME IMPLEMENTATION TESTS PASSED (4/4)! 100% SUCCESS.")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED.")
        sys.exit(1)
