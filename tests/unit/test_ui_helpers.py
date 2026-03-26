from src.ui_helpers import app_css


def test_app_css_uses_carbon_and_slate_theme_tokens() -> None:
    css = app_css()

    assert "--bg: #0F171A;" in css
    assert "--panel: #162028;" in css
    assert "--accent: #3B82F6;" in css
    assert "max-width: 1600px;" in css
    assert "height: clamp(400px, calc(100vh - 16rem), 900px);" in css


def test_app_css_styles_sidebar_for_dark_theme_contrast() -> None:
    css = app_css()

    assert '[data-testid="stSidebar"]' in css
    assert '[data-testid="stSidebarNav"] a' in css
    assert '[data-testid="stSidebarNavLink"][aria-current="page"]' in css


def test_app_css_styles_default_buttons_for_dark_theme_contrast() -> None:
    css = app_css()

    assert '[data-testid="stButton"] button' in css
    assert "background: var(--panel)" in css
    assert "color: var(--ink)" in css


def test_app_css_styles_expander_for_dark_theme_contrast() -> None:
    css = app_css()

    assert '[data-testid="stExpander"] details' in css
    assert '[data-testid="stExpander"] summary' in css
