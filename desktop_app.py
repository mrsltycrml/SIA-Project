import sys
import os
from pathlib import Path
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
try:
    from PyQt5 import QtWebEngineWidgets
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

# Try to import VLC for better IPTV stream playback
try:
    import vlc
    HAS_VLC = True
except ImportError:
    HAS_VLC = False
    vlc = None

# Ensure project root is on sys.path so we can import the existing modules
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules import music, videos, games, database, auth  # type: ignore

# Initialize database on startup
database.init_db()


# -------------------------- Shared UI helpers --------------------------- #

def create_dark_palette():
    """Return a dark QPalette similar to Spotify / Netflix."""
    palette = QtGui.QPalette()
    base = QtGui.QColor(18, 18, 18)
    alt = QtGui.QColor(24, 24, 24)
    text = QtGui.QColor(235, 235, 235)
    accent = QtGui.QColor(30, 215, 96)  # Spotify green

    palette.setColor(QtGui.QPalette.Window, base)
    palette.setColor(QtGui.QPalette.WindowText, text)
    palette.setColor(QtGui.QPalette.Base, alt)
    palette.setColor(QtGui.QPalette.AlternateBase, base)
    palette.setColor(QtGui.QPalette.Text, text)
    palette.setColor(QtGui.QPalette.Button, alt)
    palette.setColor(QtGui.QPalette.ButtonText, text)
    palette.setColor(QtGui.QPalette.Highlight, accent)
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    return palette


def load_pixmap_from_url(url: str, size=None) -> QtGui.QPixmap:
    """Best-effort image loading helper (used for album art / posters)."""
    if not url:
        return QtGui.QPixmap()
    try:
        import requests

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        pix = QtGui.QPixmap()
        pix.loadFromData(resp.content)
        if size is not None and not pix.isNull():
            # Scale maintaining aspect ratio, centered
            pix = pix.scaled(size.width(), size.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        return pix
    except Exception as e:
        print(f"Failed to load image from {url}: {e}")
        return QtGui.QPixmap()


# -------------------------- Auth windows --------------------------- #

class AuthWindow(QtWidgets.QWidget):
    """Modern minimalistic login / signup window."""

    authenticated = QtCore.pyqtSignal(str)  # email

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIA - Login")
        self.setFixedSize(600, 700)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 20)

        card = QtWidgets.QFrame()
        card.setGraphicsEffect(shadow)
        card.setObjectName("authCard")

        self.stack = QtWidgets.QStackedWidget()
        self.login_page = self._build_login_page()
        self.signup_page = self._build_signup_page()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.addWidget(self.stack)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card, alignment=QtCore.Qt.AlignCenter)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #0f0f0f;
                color: #f5f5f5;
                font-family: Segoe UI, Roboto, Arial;
            }
            QFrame#authCard {
                background-color: #181818;
                border-radius: 24px;
                min-width: 500px;
                min-height: 600px;
            }
            QLineEdit {
                background-color: #202020;
                border: 1px solid #333;
                border-radius: 14px;
                padding: 14px 18px;
                color: #f5f5f5;
                font-size: 15px;
                selection-background-color: #1ed760;
            }
            QLineEdit:focus {
                border-color: #1ed760;
            }
            QPushButton {
                border-radius: 18px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 15px;
            }
            QPushButton#primaryBtn {
                background-color: #1ed760;
                color: #000;
            }
            QPushButton#primaryBtn:hover {
                background-color: #1fdf64;
            }
            QPushButton#ghostBtn {
                background-color: transparent;
                color: #a0a0a0;
            }
            QPushButton#ghostBtn:hover {
                color: #ffffff;
            }
            QLabel#titleLabel {
                font-size: 32px;
                font-weight: 700;
                padding: 8px 0;
            }
            QLabel#subtitleLabel {
                color: #aaaaaa;
                font-size: 14px;
                padding: 4px 0;
            }
            """
        )

    # --- page builders --- #

    def _build_login_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        v.setSpacing(20)
        v.setContentsMargins(0, 20, 0, 20)

        title = QtWidgets.QLabel("Welcome back")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        subtitle = QtWidgets.QLabel("Log in to continue to your dashboard.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        self.login_email = QtWidgets.QLineEdit()
        self.login_email.setPlaceholderText("Email")
        self.login_password = QtWidgets.QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QtWidgets.QLineEdit.Password)

        login_btn = QtWidgets.QPushButton("Log in")
        login_btn.setObjectName("primaryBtn")
        login_btn.clicked.connect(self.handle_login)

        switch_btn = QtWidgets.QPushButton("New here? Create an account")
        switch_btn.setObjectName("ghostBtn")
        switch_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        v.addStretch(1)
        v.addWidget(title)
        v.addWidget(subtitle)
        v.addSpacing(32)
        v.addWidget(self.login_email)
        v.addWidget(self.login_password)
        v.addSpacing(20)
        v.addWidget(login_btn)
        v.addSpacing(16)
        v.addWidget(switch_btn, alignment=QtCore.Qt.AlignCenter)
        v.addStretch(1)
        return w

    def _build_signup_page(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        v.setSpacing(20)
        v.setContentsMargins(0, 20, 0, 20)

        title = QtWidgets.QLabel("Create account")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignCenter)
        subtitle = QtWidgets.QLabel("One account for music, videos and games.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        self.signup_email = QtWidgets.QLineEdit()
        self.signup_email.setPlaceholderText("Email")
        self.signup_password = QtWidgets.QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QtWidgets.QLineEdit.Password)

        signup_btn = QtWidgets.QPushButton("Sign up")
        signup_btn.setObjectName("primaryBtn")
        signup_btn.clicked.connect(self.handle_signup)

        switch_btn = QtWidgets.QPushButton("Already have an account? Log in")
        switch_btn.setObjectName("ghostBtn")
        switch_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        v.addStretch(1)
        v.addWidget(title)
        v.addWidget(subtitle)
        v.addSpacing(32)
        v.addWidget(self.signup_email)
        v.addWidget(self.signup_password)
        v.addSpacing(20)
        v.addWidget(signup_btn)
        v.addSpacing(16)
        v.addWidget(switch_btn, alignment=QtCore.Qt.AlignCenter)
        v.addStretch(1)
        return w

    # --- handlers --- #

    def handle_signup(self):
        email = self.signup_email.text().strip().lower()
        password = self.signup_password.text()
        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Signup", "Please fill in all fields.")
            return
        
        # Check if user already exists in database
        existing_user = database.get_user_by_email(email)
        if existing_user:
            QtWidgets.QMessageBox.warning(self, "Signup", "User already exists.")
            return
        
        try:
            # Hash password using bcrypt
            password_hash = auth.hash_password(password)
            password_hash_str = password_hash.decode('utf-8')
            
            # Create user in database
            user = database.create_user(email, password_hash_str)
            if user:
                QtWidgets.QMessageBox.information(self, "Signup", "Account created. You can log in now.")
                self.stack.setCurrentIndex(0)  # Switch to login page
            else:
                QtWidgets.QMessageBox.warning(self, "Signup", "Error creating account. Please try again.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Signup", f"Error creating account: {str(e)}")

    def handle_login(self):
        email = self.login_email.text().strip().lower()
        password = self.login_password.text()
        
        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Login", "Please fill in all fields.")
            return
        
        # Query database for user
        user = database.get_user_by_email(email)
        
        if not user:
            QtWidgets.QMessageBox.warning(self, "Login", "Invalid email or password.")
            return
        
        # Verify password against stored hash
        if not auth.verify_password(password, user["password_hash"]):
            QtWidgets.QMessageBox.warning(self, "Login", "Invalid email or password.")
            return
        
        self.authenticated.emit(email)


# -------------------------- Main window + pages --------------------------- #

class MusicPage(QtWidgets.QWidget):
    """Spotify-like page with full media controls, navigation, and large display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #121212;")
        
        # Audio player for preview playback
        self.player = QtMultimedia.QMediaPlayer(self)
        self.current_track = None
        self.track_list = []  # Store all tracks for navigation
        self.current_index = -1
        
        # Connect player signals
        self.player.positionChanged.connect(self.update_progress)
        self.player.durationChanged.connect(self.update_duration)
        self.player.stateChanged.connect(self.update_play_button)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title at top left (same style as Videos)
        title_row = QtWidgets.QHBoxLayout()
        title_row.setContentsMargins(32, 32, 32, 16)
        title = QtWidgets.QLabel("🎵 SIA Music")
        title.setStyleSheet("font-size: 36px; font-weight: 700; color: #ffffff;")
        title_row.addWidget(title)
        title_row.addStretch()
        main_layout.addLayout(title_row)
        
        # Main content area (no sidebar)
        self.content_stack = QtWidgets.QStackedWidget()
        self.search_page = self._create_search_page()
        self.library_page = self._create_library_page()
        self.playlists_page = self._create_playlists_page()
        self.content_stack.addWidget(self.search_page)
        self.content_stack.addWidget(self.library_page)
        self.content_stack.addWidget(self.playlists_page)
        main_layout.addWidget(self.content_stack, 1)
        
        # Bottom player bar (fixed height)
        self.player_bar = self._create_player_bar()
        main_layout.addWidget(self.player_bar)
        
        # Set initial view
        self.content_stack.setCurrentIndex(0)
    
    def _create_nav_sidebar(self) -> QtWidgets.QWidget:
        """Create left navigation sidebar."""
        sidebar = QtWidgets.QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
            QPushButton {
                background-color: transparent;
                color: #b3b3b3;
                border-radius: 8px;
                padding: 12px 20px;
                text-align: left;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #282828;
            }
            QPushButton#navActive {
                color: #ffffff;
                background-color: #1ed760;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)
        
        # Logo/Brand
        brand = QtWidgets.QLabel("🎵 SIA Music")
        brand.setStyleSheet("font-size: 24px; font-weight: 700; color: #ffffff; padding: 20px 0;")
        layout.addWidget(brand)
        
        # Navigation buttons
        self.nav_search = QtWidgets.QPushButton("🔍 Search")
        self.nav_library = QtWidgets.QPushButton("📚 Your Library")
        self.nav_playlists = QtWidgets.QPushButton("📋 Playlists")
        
        self.nav_search.clicked.connect(lambda: self._switch_view(0))
        self.nav_library.clicked.connect(lambda: self._switch_view(1))
        self.nav_playlists.clicked.connect(lambda: self._switch_view(2))
        
        layout.addWidget(self.nav_search)
        layout.addWidget(self.nav_library)
        layout.addWidget(self.nav_playlists)
        layout.addStretch()
        
        return sidebar
    
    def _switch_view(self, index: int):
        """Switch between navigation views."""
        self.content_stack.setCurrentIndex(index)
        # Update active button
        for i, btn in enumerate([self.nav_search, self.nav_library, self.nav_playlists]):
            btn.setObjectName("navActive" if i == index else "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    def _create_search_page(self) -> QtWidgets.QWidget:
        """Create search page."""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: #121212;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Search bar
        search_container = QtWidgets.QHBoxLayout()
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("What do you want to listen to?")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border-radius: 24px;
                padding: 14px 24px;
                font-size: 16px;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #1ed760;
            }
        """)
        self.search_edit.returnPressed.connect(self.perform_search)
        search_btn = QtWidgets.QPushButton("Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1ed760;
                color: #000000;
                border-radius: 24px;
                padding: 14px 32px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #1fdf64;
            }
        """)
        search_btn.clicked.connect(self.perform_search)
        search_container.addWidget(self.search_edit, 1)
        search_container.addWidget(search_btn)
        layout.addLayout(search_container)
        
        # Results list
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.track_list_widget = QtWidgets.QListWidget()
        self.track_list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
                min-height: 80px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(30, 215, 96, 0.2);
            }
        """)
        self.track_list_widget.itemDoubleClicked.connect(self.play_selected_track)
        self.track_list_widget.itemClicked.connect(self._on_track_selected)
        scroll_area.setWidget(self.track_list_widget)
        layout.addWidget(scroll_area, 1)
        
        return page
    
    def _create_library_page(self) -> QtWidgets.QWidget:
        """Create library page."""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: #121212;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        title = QtWidgets.QLabel("Your Library")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #ffffff;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("Your recently played tracks will appear here.")
        info.setStyleSheet("font-size: 18px; color: #b3b3b3; padding: 40px;")
        info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info, 1)
        
        return page
    
    def _create_playlists_page(self) -> QtWidgets.QWidget:
        """Create playlists page."""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: #121212;")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        title = QtWidgets.QLabel("Playlists")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #ffffff;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("Create and manage your playlists here.")
        info.setStyleSheet("font-size: 18px; color: #b3b3b3; padding: 40px;")
        info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info, 1)
        
        return page
    
    def _create_player_bar(self) -> QtWidgets.QWidget:
        """Create bottom player bar with controls."""
        bar = QtWidgets.QWidget()
        bar.setFixedHeight(100)
        bar.setStyleSheet("""
            QWidget {
                background-color: #181818;
                border-top: 1px solid #282828;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(bar)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)
        
        # Left: Track info with album art
        track_info_layout = QtWidgets.QHBoxLayout()
        track_info_layout.setSpacing(12)
        
        self.album_art_label = QtWidgets.QLabel()
        self.album_art_label.setFixedSize(64, 64)
        self.album_art_label.setStyleSheet("background-color: #282828; border-radius: 4px;")
        self.album_art_label.setScaledContents(True)
        track_info_layout.addWidget(self.album_art_label)
        
        track_text_layout = QtWidgets.QVBoxLayout()
        track_text_layout.setSpacing(4)
        self.track_title_label = QtWidgets.QLabel("Not playing")
        self.track_title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff;")
        self.track_artist_label = QtWidgets.QLabel("")
        self.track_artist_label.setStyleSheet("font-size: 12px; color: #b3b3b3;")
        track_text_layout.addWidget(self.track_title_label)
        track_text_layout.addWidget(self.track_artist_label)
        track_info_layout.addLayout(track_text_layout)
        
        layout.addLayout(track_info_layout, 0)
        
        # Center: Media controls
        controls_layout = QtWidgets.QVBoxLayout()
        controls_layout.setSpacing(8)
        
        # Progress bar
        progress_layout = QtWidgets.QHBoxLayout()
        self.time_label = QtWidgets.QLabel("0:00")
        self.time_label.setStyleSheet("font-size: 11px; color: #b3b3b3; min-width: 40px;")
        self.progress_bar = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.progress_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #535353;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #1ed760;
            }
            QSlider::sub-page:horizontal {
                background-color: #b3b3b3;
            }
        """)
        self.progress_bar.sliderPressed.connect(self._on_progress_pressed)
        self.progress_bar.sliderReleased.connect(self._on_progress_released)
        self.progress_bar.valueChanged.connect(self._on_progress_changed)
        self.duration_label = QtWidgets.QLabel("0:00")
        self.duration_label.setStyleSheet("font-size: 11px; color: #b3b3b3; min-width: 40px;")
        progress_layout.addWidget(self.time_label)
        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.duration_label)
        controls_layout.addLayout(progress_layout)
        
        # Control buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(16)
        
        self.prev_btn = QtWidgets.QPushButton("⏮")
        self.prev_btn.setFixedSize(48, 48)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b3b3b3;
                border: none;
                font-size: 28px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        self.prev_btn.clicked.connect(self.play_previous)
        
        self.play_pause_btn = QtWidgets.QPushButton("▶")
        self.play_pause_btn.setFixedSize(64, 64)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: none;
                border-radius: 32px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #1ed760;
                transform: scale(1.1);
            }
        """)
        self.play_pause_btn.setEnabled(False)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        
        self.next_btn = QtWidgets.QPushButton("⏭")
        self.next_btn.setFixedSize(48, 48)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b3b3b3;
                border: none;
                font-size: 28px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        self.next_btn.clicked.connect(self.play_next)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.prev_btn)
        buttons_layout.addWidget(self.play_pause_btn)
        buttons_layout.addWidget(self.next_btn)
        buttons_layout.addStretch()
        
        controls_layout.addLayout(buttons_layout)
        layout.addLayout(controls_layout, 1)
        
        # Right: Volume control
        volume_layout = QtWidgets.QHBoxLayout()
        volume_layout.setSpacing(8)
        volume_icon = QtWidgets.QLabel("🔊")
        volume_icon.setStyleSheet("font-size: 16px;")
        volume_layout.addWidget(volume_icon)
        
        # Volume slider
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)  # Default volume
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #535353;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #1ed760;
            }
            QSlider::sub-page:horizontal {
                background-color: #b3b3b3;
            }
        """)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout, 0)
        
        return bar

    def perform_search(self):
        query = self.search_edit.text().strip()
        self.track_list_widget.clear()
        self.track_list.clear()
        if not query:
            return
        
        tracks = music.search_tracks(query)
        self.track_list = tracks
        
        for t in tracks:
            # Create custom item widget for better display
            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout(item_widget)
            item_layout.setContentsMargins(12, 8, 12, 8)
            item_layout.setSpacing(16)
            
            # Album art
            art_label = QtWidgets.QLabel()
            art_label.setFixedSize(64, 64)
            art_label.setStyleSheet("background-color: #282828; border-radius: 4px;")
            art_label.setScaledContents(True)
            pix = load_pixmap_from_url(t.get("image", ""), QtCore.QSize(64, 64))
            if not pix.isNull():
                art_label.setPixmap(pix)
            item_layout.addWidget(art_label)
            
            # Track info
            info_layout = QtWidgets.QVBoxLayout()
            info_layout.setSpacing(4)
            title_label = QtWidgets.QLabel(t.get("name", "Unknown"))
            title_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")
            artist_label = QtWidgets.QLabel(f"{t.get('artists', 'Unknown')} • {t.get('album', 'Unknown')}")
            artist_label.setStyleSheet("font-size: 14px; color: #b3b3b3;")
            info_layout.addWidget(title_label)
            info_layout.addWidget(artist_label)
            item_layout.addLayout(info_layout, 1)
            
            # Duration placeholder
            duration_label = QtWidgets.QLabel("30s")
            duration_label.setStyleSheet("font-size: 14px; color: #b3b3b3;")
            item_layout.addWidget(duration_label)
            
            # Create list item
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            item.setData(QtCore.Qt.UserRole, t)
            self.track_list_widget.addItem(item)
            self.track_list_widget.setItemWidget(item, item_widget)
        
        if self.track_list_widget.count() > 0:
            self.play_pause_btn.setEnabled(True)
    
    def _on_track_selected(self, item):
        """Handle track selection."""
        pass
    
    def _get_selected_track(self):
        item = self.track_list_widget.currentItem()
        if not item:
            return None
        return item.data(QtCore.Qt.UserRole) or None
    
    def play_selected_track(self, _item=None):
        track = self._get_selected_track()
        if not track:
            # Try to play first track if none selected
            if self.track_list_widget.count() > 0:
                self.track_list_widget.setCurrentRow(0)
                track = self._get_selected_track()
            else:
                return
        
        if not track:
            return
        
        url = track.get("preview_url")
        if not url:
            QtWidgets.QMessageBox.information(self, "Playback", "No preview available for this track.")
            return
        
        # Update current track and index
        self.current_track = track
        self.current_index = self.track_list_widget.currentRow()
        
        # Update UI
        self.track_title_label.setText(track.get("name", "Unknown"))
        self.track_artist_label.setText(track.get("artists", "Unknown"))
        
        # Load album art
        pix = load_pixmap_from_url(track.get("image", ""), QtCore.QSize(64, 64))
        if not pix.isNull():
            self.album_art_label.setPixmap(pix)
        else:
            self.album_art_label.clear()
            self.album_art_label.setText("🎵")
            self.album_art_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Play track
        media = QtMultimedia.QMediaContent(QtCore.QUrl(url))
        self.player.setMedia(media)
        self.player.play()
    
    def toggle_play_pause(self):
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
        elif self.player.state() in (QtMultimedia.QMediaPlayer.PausedState, QtMultimedia.QMediaPlayer.StoppedState):
            if self.current_track is None:
                self.play_selected_track()
            else:
                self.player.play()
    
    def play_next(self):
        if self.track_list_widget.count() == 0:
            return
        if self.current_index < self.track_list_widget.count() - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.track_list_widget.setCurrentRow(self.current_index)
        self.play_selected_track()
    
    def play_previous(self):
        if self.track_list_widget.count() == 0:
            return
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = self.track_list_widget.count() - 1
        self.track_list_widget.setCurrentRow(self.current_index)
        self.play_selected_track()
    
    def update_play_button(self, state):
        """Update play/pause button based on player state."""
        if state == QtMultimedia.QMediaPlayer.PlayingState:
            self.play_pause_btn.setText("⏸")
        else:
            self.play_pause_btn.setText("▶")
    
    def update_progress(self, position):
        """Update progress bar and time label."""
        if not self.progress_bar.isSliderDown():
            self.progress_bar.setValue(position)
        self.time_label.setText(self._format_time(position))
    
    def update_duration(self, duration):
        """Update duration label."""
        self.progress_bar.setMaximum(duration)
        self.duration_label.setText(self._format_time(duration))
    
    def _format_time(self, milliseconds):
        """Format milliseconds to MM:SS."""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def _on_progress_pressed(self):
        """Handle progress bar press."""
        pass
    
    def _on_progress_released(self):
        """Handle progress bar release - seek to position."""
        position = self.progress_bar.value()
        self.player.setPosition(position)
    
    def _on_progress_changed(self, value):
        """Handle progress bar value change."""
        if self.progress_bar.isSliderDown():
            self.time_label.setText(self._format_time(value))
    
    def _on_volume_changed(self, value):
        """Handle volume slider change."""
        # Convert 0-100 to 0.0-1.0 for QMediaPlayer
        volume = value / 100.0
        self.player.setVolume(int(volume * 100))  # QMediaPlayer uses 0-100


class VideosPage(QtWidgets.QWidget):
    """Netflix-style grid of posters with embedded video player."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Stacked widget to switch between grid and player
        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Grid view page
        self.grid_page = QtWidgets.QWidget()
        grid_layout = QtWidgets.QVBoxLayout(self.grid_page)
        grid_layout.setContentsMargins(32, 32, 32, 32)
        grid_layout.setSpacing(24)

        # Header with larger title
        title_row = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("📺 SIA Channels")
        title.setStyleSheet("font-size: 36px; font-weight: 700; color: #ffffff;")
        title_row.addWidget(title)
        title_row.addStretch(1)
        grid_layout.addLayout(title_row)
        
        # Search and filter row
        filter_row = QtWidgets.QHBoxLayout()
        filter_row.setSpacing(12)
        
        # Search bar
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search channels by name...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 16px;
                color: #ffffff;
                min-width: 300px;
            }
            QLineEdit:focus {
                border-color: #1ed760;
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        self.search_edit.returnPressed.connect(self.refresh_grid)
        
        # Country filter
        country_label = QtWidgets.QLabel("Country:")
        country_label.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 0 8px;")
        self.country_combo = QtWidgets.QComboBox()
        self.country_combo.addItem("All Countries", "")
        self.country_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 14px;
                color: #ffffff;
                min-width: 180px;
            }
            QComboBox:hover {
                border-color: #1ed760;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #ffffff;
                selection-background-color: #1ed760;
                border-radius: 8px;
            }
        """)
        self.country_combo.currentIndexChanged.connect(self.refresh_grid)
        
        # Category filter
        category_label = QtWidgets.QLabel("Category:")
        category_label.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 0 8px;")
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItem("All Categories", "")
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 14px;
                color: #ffffff;
                min-width: 180px;
            }
            QComboBox:hover {
                border-color: #1ed760;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #ffffff;
                selection-background-color: #1ed760;
                border-radius: 8px;
            }
        """)
        self.category_combo.currentIndexChanged.connect(self.refresh_grid)
        
        # Search button
        search_btn = QtWidgets.QPushButton("🔍 Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1ed760;
                color: #000000;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1fdf64;
            }
        """)
        search_btn.clicked.connect(self.refresh_grid)
        
        filter_row.addWidget(self.search_edit)
        filter_row.addWidget(country_label)
        filter_row.addWidget(self.country_combo)
        filter_row.addWidget(category_label)
        filter_row.addWidget(self.category_combo)
        filter_row.addWidget(search_btn)
        filter_row.addStretch()
        grid_layout.addLayout(filter_row)
        
        # Load filter options in background
        self._load_filter_options()

        # Status label
        self.status_label = QtWidgets.QLabel("Loading channels...")
        self.status_label.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 8px 0;")
        grid_layout.addWidget(self.status_label)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.grid_widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(20)
        scroll_area.setWidget(self.grid_widget)
        grid_layout.addWidget(scroll_area, 1)

        self.stack.addWidget(self.grid_page)
        
        # Video player page
        self.player_page = self._create_player_page()
        self.stack.addWidget(self.player_page)
        
        self.current_movie = None
        self.all_channels = []  # Store all channels for discovery
        # Load channels on startup (empty query shows all)
        try:
            self.refresh_grid()
        except Exception as e:
            print(f"[VideosPage] Error loading channels on startup: {e}")
            self.status_label.setText("Error loading channels. Please try again.")
    
    def _load_filter_options(self):
        """Load country and category options for filters."""
        try:
            # Load countries
            countries = videos.get_available_countries()
            for country in countries:  # Show all countries
                display_text = f"{country['name']} ({country['code']})"
                self.country_combo.addItem(display_text, country['code'])
            
            # Load categories
            categories = videos.get_available_categories()
            for category in categories:
                self.category_combo.addItem(category.capitalize(), category.lower())
        except Exception as e:
            print(f"[VideosPage] Failed to load filter options: {e}")

    def refresh_grid(self):
        # Clear old widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        query = self.search_edit.text().strip()
        country = self.country_combo.currentData()
        category = self.category_combo.currentData()
        
        # Build status message
        status_parts = ["Loading channels"]
        if query:
            status_parts.append(f"matching '{query}'")
        if country:
            country_name = self.country_combo.currentText().split(" (")[0]
            status_parts.append(f"in {country_name}")
        if category:
            status_parts.append(f"category: {category}")
        self.status_label.setText(" ".join(status_parts) + "...")
        
        # Load more channels for better display (increase max_results)
        movie_list = videos.search_videos(
            query=query,
            max_results=50,
            country=country if country else None,
            category=category if category else None
        )
        self.all_channels = movie_list

        if not movie_list:
            # Show message if no results
            no_results = QtWidgets.QLabel(
                "No channels found.\n\n"
                "Try searching for a different term or leave search empty to see all channels."
            )
            no_results.setAlignment(QtCore.Qt.AlignCenter)
            no_results.setStyleSheet("""
                color: #b3b3b3;
                font-size: 18px;
                padding: 60px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            """)
            self.grid_layout.addWidget(no_results, 0, 0, 1, 4)
            if query:
                self.status_label.setText(f"No channels found matching '{query}'")
            else:
                self.status_label.setText("No channels found")
            return

        # Use 4 columns for larger display
        cols = 4
        for idx, movie in enumerate(movie_list):
            r, c = divmod(idx, cols)
            card = self._create_movie_card(movie)
            self.grid_layout.addWidget(card, r, c)
        
        # Add stretch to make grid fill available space symmetrically
        for i in range(cols):
            self.grid_layout.setColumnStretch(i, 1)
        
        # Update status
        channel_text = "channel" if len(movie_list) == 1 else "channels"
        if query:
            self.status_label.setText(f"Showing {len(movie_list)} {channel_text} matching '{query}'")
        else:
            self.status_label.setText(f"Showing {len(movie_list)} {channel_text}")

    def _create_player_page(self) -> QtWidgets.QWidget:
        """Create the video player page with navigation and discovery elements."""
        page = QtWidgets.QWidget()
        page.setStyleSheet("background-color: #0a0a0a;")
        main_layout = QtWidgets.QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top navigation bar
        nav_bar = QtWidgets.QWidget()
        nav_bar.setFixedHeight(70)
        nav_bar.setStyleSheet("background-color: rgba(0, 0, 0, 0.8);")
        nav_layout = QtWidgets.QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(24, 16, 24, 16)
        
        back_btn = QtWidgets.QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        back_btn.clicked.connect(self.show_grid)
        nav_layout.addWidget(back_btn)
        
        # Channel info in nav bar
        self.channel_title_label = QtWidgets.QLabel("")
        self.channel_title_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #ffffff; padding: 0 20px;")
        nav_layout.addWidget(self.channel_title_label)
        
        nav_layout.addStretch()
        
        # Fullscreen button
        self.fullscreen_btn = QtWidgets.QPushButton("⛶ Fullscreen")
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        nav_layout.addWidget(self.fullscreen_btn)
        self.is_fullscreen = False
        
        main_layout.addWidget(nav_bar)
        
        # Video player container
        self.player_container = QtWidgets.QWidget()
        self.player_layout = QtWidgets.QVBoxLayout(self.player_container)
        self.player_layout.setContentsMargins(0, 0, 0, 0)
        self.player_layout.setSpacing(0)
        
        # Initialize VLC if available (preferred for IPTV streams)
        self.vlc_instance = None
        self.vlc_media_player = None
        self.vlc_widget = None
        self.use_vlc = False
        
        if HAS_VLC:
            try:
                # Create VLC instance
                self.vlc_instance = vlc.Instance([
                    '--intf', 'dummy',
                    '--quiet',
                    '--no-xlib',
                    '--live-caching=1000',
                    '--network-caching=1000'
                ])
                self.vlc_media_player = self.vlc_instance.media_player_new()
                
                # Create widget for VLC video output
                self.vlc_widget = QtWidgets.QFrame()
                self.vlc_widget.setStyleSheet("background-color: #000000;")
                
                # Set VLC output to the widget (platform-specific)
                if sys.platform == "win32":
                    self.vlc_media_player.set_hwnd(int(self.vlc_widget.winId()))
                elif sys.platform == "linux":
                    self.vlc_media_player.set_xwindow(self.vlc_widget.winId())
                elif sys.platform == "darwin":
                    self.vlc_media_player.set_nsobject(int(self.vlc_widget.winId()))
                
                self.use_vlc = True
                print("[VideosPage] VLC player initialized successfully")
            except Exception as e:
                print(f"[VideosPage] VLC initialization failed: {e}, falling back to QWebEngineView")
                self.use_vlc = False
        
        # Fallback to QWebEngineView if VLC not available
        if not self.use_vlc:
            if HAS_WEBENGINE:
                self.video_player = QtWebEngineWidgets.QWebEngineView()
                self.video_player.setStyleSheet("background-color: #000000;")
                # Enable JavaScript and other features
                settings = self.video_player.settings()
                settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptEnabled, True)
                settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
                settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            else:
                self.video_player = QtWidgets.QLabel("No video player available.\nPlease install python-vlc or PyQtWebEngine.")
                self.video_player.setAlignment(QtCore.Qt.AlignCenter)
                self.video_player.setStyleSheet("background-color: #000000; color: #ffffff; font-size: 18px; padding: 60px;")
        
        # Add appropriate widget to layout
        if self.use_vlc and self.vlc_widget:
            self.player_layout.addWidget(self.vlc_widget, 1)
        else:
            self.player_layout.addWidget(self.video_player, 1)
        
        main_layout.addWidget(self.player_container, 3)  # Give player 3x space
        
        # Bottom section with channel info and related channels (single scroll)
        bottom_scroll = QtWidgets.QScrollArea()
        bottom_scroll.setWidgetResizable(True)
        bottom_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        bottom_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        bottom_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #121212;
            }
        """)
        
        bottom_section = QtWidgets.QWidget()
        bottom_section.setStyleSheet("background-color: #121212;")
        bottom_layout = QtWidgets.QVBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(32, 24, 32, 24)
        bottom_layout.setSpacing(20)
        
        # Channel details
        details_widget = QtWidgets.QWidget()
        details_layout = QtWidgets.QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(12)
        
        self.channel_name_label = QtWidgets.QLabel("")
        self.channel_name_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #ffffff;")
        details_layout.addWidget(self.channel_name_label)
        
        self.channel_desc_label = QtWidgets.QLabel("")
        self.channel_desc_label.setStyleSheet("font-size: 16px; color: #b3b3b3;")
        self.channel_desc_label.setWordWrap(True)
        details_layout.addWidget(self.channel_desc_label)
        
        bottom_layout.addWidget(details_widget)
        
        # Related/More channels section
        related_label = QtWidgets.QLabel("More Channels")
        related_label.setStyleSheet("font-size: 22px; font-weight: 600; color: #ffffff; padding: 8px 0;")
        bottom_layout.addWidget(related_label)
        
        # Horizontal scrollable related channels (no nested scroll)
        self.related_widget = QtWidgets.QWidget()
        self.related_layout = QtWidgets.QHBoxLayout(self.related_widget)
        self.related_layout.setContentsMargins(0, 0, 0, 0)
        self.related_layout.setSpacing(16)
        
        # Use QScrollArea only for horizontal scrolling of related channels
        related_scroll = QtWidgets.QScrollArea()
        related_scroll.setWidgetResizable(True)
        related_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        related_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        related_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        related_scroll.setWidget(self.related_widget)
        related_scroll.setFixedHeight(200)  # Fixed height to prevent vertical scroll (adjusted for logos)
        
        bottom_layout.addWidget(related_scroll)
        bottom_scroll.setWidget(bottom_section)
        main_layout.addWidget(bottom_scroll, 1)  # Give bottom section 1x space
        
        # Store references for fullscreen functionality (after bottom_scroll is created)
        self.nav_bar = nav_bar
        self.bottom_scroll = bottom_scroll
        self.player_page = page
        self.fullscreen_window = None
        
        return page
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode for the video player only."""
        if not self.is_fullscreen:
            # Enter fullscreen - create a separate fullscreen window
            self.is_fullscreen = True
            self.fullscreen_btn.setText("⛶ Exit Fullscreen")
            
            # Create fullscreen window
            self.fullscreen_window = QtWidgets.QWidget()
            self.fullscreen_window.setWindowFlags(
                QtCore.Qt.Window | 
                QtCore.Qt.FramelessWindowHint | 
                QtCore.Qt.WindowStaysOnTopHint
            )
            self.fullscreen_window.setStyleSheet("background-color: #000000;")
            
            # Get the video player widget
            if self.use_vlc and self.vlc_widget:
                video_widget = self.vlc_widget
            else:
                if not hasattr(self, 'video_player'):
                    # Fallback if video_player doesn't exist
                    self.is_fullscreen = False
                    return
                video_widget = self.video_player
            
            # Remove widget from current layout properly
            self.player_layout.removeWidget(video_widget)
            video_widget.setParent(None)
            
            # Create layout for fullscreen window
            fullscreen_layout = QtWidgets.QVBoxLayout(self.fullscreen_window)
            fullscreen_layout.setContentsMargins(0, 0, 0, 0)
            fullscreen_layout.addWidget(video_widget)
            
            # Add exit button overlay
            exit_btn = QtWidgets.QPushButton("✕ Exit Fullscreen", self.fullscreen_window)
            exit_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.7);
                    color: #ffffff;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.9);
                }
            """)
            exit_btn.clicked.connect(self.toggle_fullscreen)
            exit_btn.setGeometry(20, 20, 180, 40)  # Position in top-left
            
            # Show fullscreen window
            self.fullscreen_window.showFullScreen()
            
            # Reconnect VLC if using VLC
            if self.use_vlc and self.vlc_media_player:
                if sys.platform == "win32":
                    self.vlc_media_player.set_hwnd(int(video_widget.winId()))
                elif sys.platform == "linux":
                    self.vlc_media_player.set_xwindow(video_widget.winId())
                elif sys.platform == "darwin":
                    self.vlc_media_player.set_nsobject(int(video_widget.winId()))
        else:
            # Exit fullscreen - restore widget to original location
            self.is_fullscreen = False
            self.fullscreen_btn.setText("⛶ Fullscreen")
            
            if self.fullscreen_window:
                # Get the video widget back
                if self.use_vlc and self.vlc_widget:
                    video_widget = self.vlc_widget
                else:
                    if not hasattr(self, 'video_player'):
                        return
                    video_widget = self.video_player
                
                # Remove from fullscreen window layout
                fullscreen_layout = self.fullscreen_window.layout()
                if fullscreen_layout:
                    fullscreen_layout.removeWidget(video_widget)
                video_widget.setParent(None)
                
                # Add back to player container
                self.player_layout.addWidget(video_widget, 1)
                
                # Reconnect VLC if using VLC
                if self.use_vlc and self.vlc_media_player:
                    if sys.platform == "win32":
                        self.vlc_media_player.set_hwnd(int(video_widget.winId()))
                    elif sys.platform == "linux":
                        self.vlc_media_player.set_xwindow(video_widget.winId())
                    elif sys.platform == "darwin":
                        self.vlc_media_player.set_nsobject(int(video_widget.winId()))
                
                # Close and destroy fullscreen window
                self.fullscreen_window.close()
                self.fullscreen_window.deleteLater()
                self.fullscreen_window = None
    
    def show_grid(self):
        """Switch back to grid view."""
        # Exit fullscreen if active
        if self.is_fullscreen:
            self.toggle_fullscreen()
        # Stop VLC playback if active
        if self.use_vlc and self.vlc_media_player:
            try:
                self.vlc_media_player.stop()
            except:
                pass
        self.stack.setCurrentIndex(0)
    
    def show_player(self, movie: dict):
        """Switch to player view and load the IPTV channel stream."""
        self.current_movie = movie
        self.stack.setCurrentIndex(1)
        
        # Update channel info in UI
        channel_title = movie.get("title", "Unknown Channel")
        channel_desc = movie.get("description", "TV Channel")
        
        self.channel_title_label.setText(channel_title)
        self.channel_name_label.setText(channel_title)
        self.channel_desc_label.setText(channel_desc)
        
        # Load related channels
        self._load_related_channels(movie)
        
        # Get stream URL (IPTV channels use direct stream URLs)
        stream_url = movie.get("stream_url") or movie.get("embed_url", "")
        
        if not stream_url:
            print(f"[VideosPage] No stream URL found in channel: {movie}")
            return
        
        # Use VLC if available (better for IPTV streams)
        if self.use_vlc and self.vlc_media_player:
            try:
                # Stop any currently playing media
                self.vlc_media_player.stop()
                
                # Create VLC media from URL
                media = self.vlc_instance.media_new(stream_url)
                self.vlc_media_player.set_media(media)
                
                # Play the stream
                self.vlc_media_player.play()
                print(f"[VideosPage] Loading IPTV channel with VLC: {channel_title} - {stream_url}")
            except Exception as e:
                print(f"[VideosPage] VLC playback failed: {e}, falling back to QWebEngineView")
                self._play_with_webengine(stream_url, channel_title)
        else:
            # Fallback to QWebEngineView
            self._play_with_webengine(stream_url, channel_title)
    
    def _play_with_webengine(self, stream_url: str, channel_title: str):
        """Play video using QWebEngineView as fallback."""
        if HAS_WEBENGINE and hasattr(self, 'video_player') and isinstance(self.video_player, QtWebEngineWidgets.QWebEngineView):
            # Create HTML5 video player for IPTV streams
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        background-color: #000000;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        overflow: hidden;
                    }}
                    video {{
                        width: 100%;
                        height: 100%;
                        max-width: 100%;
                        max-height: 100%;
                        object-fit: contain;
                    }}
                </style>
            </head>
            <body>
                <video controls autoplay muted>
                    <source src="{stream_url}" type="video/mp4">
                    <source src="{stream_url}" type="application/x-mpegURL">
                    <source src="{stream_url}" type="application/vnd.apple.mpegurl">
                    Your browser does not support the video tag.
                </video>
            </body>
            </html>
            """
            
            # Load HTML content with the video player
            self.video_player.setHtml(html_content)
            print(f"[VideosPage] Loading IPTV channel with QWebEngineView: {channel_title} - {stream_url}")
        else:
            print("[VideosPage] QWebEngineView not available or not properly initialized")
    
    def _load_related_channels(self, current_channel: dict):
        """Load related channels for discovery."""
        # Clear existing related channels
        while self.related_layout.count():
            item = self.related_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        
        # Get current channel country/language for related channels
        current_country = current_channel.get("description", "").lower()
        
        # Show up to 10 related channels (excluding current)
        related_count = 0
        for channel in self.all_channels:
            if related_count >= 10:
                break
            if channel.get("id") == current_channel.get("id"):
                continue
            
            # Create smaller card for related channels
            card = self._create_related_channel_card(channel)
            self.related_layout.addWidget(card)
            related_count += 1
        
        self.related_layout.addStretch()

    def _create_movie_card(self, movie: dict) -> QtWidgets.QWidget:
        """Create a large channel card for the grid view."""
        card_widget = QtWidgets.QWidget()
        card_widget.setCursor(QtCore.Qt.PointingHandCursor)
        card_widget.setStyleSheet(
            """
            QWidget {
                background-color: transparent;
                border-radius: 12px;
            }
            QWidget:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            """
        )
        v = QtWidgets.QVBoxLayout(card_widget)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(16)

        # Container for poster with play button overlay - MUCH LARGER
        poster_container = QtWidgets.QWidget()
        poster_container.setFixedSize(380, 570)  # Increased from 280x420
        poster_container.setStyleSheet("background-color: #1a1a1a; border-radius: 10px;")
        
        # Make entire container clickable
        def play_movie():
            self.show_player(movie)
        poster_container.mousePressEvent = lambda e: play_movie()
        
        # Use a stacked layout approach for overlay
        container_layout = QtWidgets.QVBoxLayout(poster_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Larger poster size
        poster = QtWidgets.QLabel()
        poster.setFixedSize(380, 570)
        poster.setAlignment(QtCore.Qt.AlignCenter)
        poster.setStyleSheet("background-color: #1a1a1a; border-radius: 10px;")
        
        # Load and scale image properly maintaining aspect ratio
        pix = load_pixmap_from_url(movie.get("thumbnail", ""), poster.size())
        if pix.isNull():
            # Create placeholder with TV icon
            pix = QtGui.QPixmap(poster.size())
            pix.fill(QtGui.QColor(40, 40, 40))
            painter = QtGui.QPainter(pix)
            painter.setPen(QtGui.QColor(100, 100, 100))
            painter.setFont(QtGui.QFont("Arial", 18))
            painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, "📺\nNo Logo")
            painter.end()
        else:
            # Center the scaled image on a background
            scaled_pix = QtGui.QPixmap(poster.size())
            scaled_pix.fill(QtGui.QColor(20, 20, 20))
            painter = QtGui.QPainter(scaled_pix)
            x = (scaled_pix.width() - pix.width()) // 2
            y = (scaled_pix.height() - pix.height()) // 2
            painter.drawPixmap(x, y, pix)
            painter.end()
            pix = scaled_pix
        
        poster.setPixmap(pix)
        poster.setScaledContents(False)
        
        # Larger play button overlay
        play_btn = QtWidgets.QPushButton("▶", poster_container)
        play_btn.setFixedSize(90, 90)  # Increased from 70x70
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 215, 96, 0.9);
                color: #000000;
                border-radius: 45px;
                font-size: 36px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(30, 215, 96, 1.0);
                transform: scale(1.1);
            }
        """)
        play_btn.clicked.connect(play_movie)
        # Center the play button
        play_btn.move(145, 240)  # (380-90)/2, (570-90)/2
        play_btn.raise_()
        play_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        container_layout.addWidget(poster)

        # Larger title with description
        title_lbl = QtWidgets.QLabel(movie.get("title", ""))
        title_lbl.setWordWrap(True)
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 600; color: #ffffff; padding: 8px;")
        
        desc_lbl = QtWidgets.QLabel(movie.get("description", ""))
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(QtCore.Qt.AlignCenter)
        desc_lbl.setStyleSheet("font-size: 14px; color: #b3b3b3; padding: 4px;")

        v.addWidget(poster_container, alignment=QtCore.Qt.AlignCenter)
        v.addWidget(title_lbl)
        v.addWidget(desc_lbl)
        v.addStretch()
        
        return card_widget
    
    def _create_related_channel_card(self, channel: dict) -> QtWidgets.QWidget:
        """Create a smaller channel card for the related channels section with logo."""
        card_widget = QtWidgets.QWidget()
        card_widget.setCursor(QtCore.Qt.PointingHandCursor)
        card_widget.setStyleSheet(
            """
            QWidget {
                background-color: transparent;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            """
        )
        v = QtWidgets.QVBoxLayout(card_widget)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(8)
        
        def play_channel():
            self.show_player(channel)
        card_widget.mousePressEvent = lambda e: play_channel()

        # Container for channel logo/image
        logo_container = QtWidgets.QWidget()
        logo_container.setFixedSize(180, 120)
        logo_container.setStyleSheet("background-color: #1a1a1a; border-radius: 8px;")
        
        container_layout = QtWidgets.QVBoxLayout(logo_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(180, 120)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_label.setStyleSheet("background-color: #1a1a1a; border-radius: 8px;")
        
        # Load channel logo/thumbnail
        thumbnail_url = channel.get("thumbnail", "") or channel.get("logo", "")
        if thumbnail_url:
            pix = load_pixmap_from_url(thumbnail_url, QtCore.QSize(180, 120))
            if not pix.isNull():
                # Scale maintaining aspect ratio
                scaled_pix = QtGui.QPixmap(180, 120)
                scaled_pix.fill(QtGui.QColor(26, 26, 26))
                painter = QtGui.QPainter(scaled_pix)
                x = (scaled_pix.width() - pix.width()) // 2
                y = (scaled_pix.height() - pix.height()) // 2
                painter.drawPixmap(x, y, pix)
                painter.end()
                logo_label.setPixmap(scaled_pix)
            else:
                # Placeholder
                pix = QtGui.QPixmap(180, 120)
                pix.fill(QtGui.QColor(40, 40, 40))
                painter = QtGui.QPainter(pix)
                painter.setPen(QtGui.QColor(100, 100, 100))
                painter.setFont(QtGui.QFont("Arial", 10))
                painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, "📺")
                painter.end()
                logo_label.setPixmap(pix)
        else:
            # Placeholder
            pix = QtGui.QPixmap(180, 120)
            pix.fill(QtGui.QColor(40, 40, 40))
            painter = QtGui.QPainter(pix)
            painter.setPen(QtGui.QColor(100, 100, 100))
            painter.setFont(QtGui.QFont("Arial", 10))
            painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, "📺")
            painter.end()
            logo_label.setPixmap(pix)
        
        logo_label.setScaledContents(False)
        container_layout.addWidget(logo_label)

        # Channel name
        title_lbl = QtWidgets.QLabel(channel.get("title", ""))
        title_lbl.setWordWrap(True)
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #ffffff; padding: 4px;")

        v.addWidget(logo_container, alignment=QtCore.Qt.AlignCenter)
        v.addWidget(title_lbl)
        
        return card_widget


class GamesPage(QtWidgets.QWidget):
    """Friv-style grid of colorful tiles with embedded game player."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Stacked widget to switch between grid and game
        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Grid view page
        self.grid_page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.grid_page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title_row = QtWidgets.QHBoxLayout()
        title_row.setContentsMargins(32, 32, 32, 16)
        title = QtWidgets.QLabel("🎮 SIA Games")
        title.setStyleSheet("font-size: 36px; font-weight: 700; color: #ffffff;")
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        self.grid_widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        scroll_area.setWidget(self.grid_widget)
        layout.addWidget(scroll_area)

        self.stack.addWidget(self.grid_page)
        
        # Game player page
        self.game_page = self._create_game_page()
        self.stack.addWidget(self.game_page)
        
        self.current_game = None
        self.populate_games()
    
    def _create_game_page(self) -> QtWidgets.QWidget:
        """Create the game player page with back button."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with back button
        header = QtWidgets.QHBoxLayout()
        header.setContentsMargins(16, 16, 16, 8)
        back_btn = QtWidgets.QPushButton("← Back to Games")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        back_btn.clicked.connect(self.show_grid)
        header.addWidget(back_btn)
        header.addStretch()
        layout.addLayout(header)
        
        # Game player
        if HAS_WEBENGINE:
            self.game_player = QtWebEngineWidgets.QWebEngineView()
            self.game_player.setStyleSheet("background-color: #000000;")
        else:
            self.game_player = QtWidgets.QLabel("QWebEngineWidgets not available.\nPlease install PyQtWebEngine.")
            self.game_player.setAlignment(QtCore.Qt.AlignCenter)
            self.game_player.setStyleSheet("background-color: #000000; color: #ffffff; font-size: 16px; padding: 40px;")
        
        layout.addWidget(self.game_player, 1)
        
        return page
    
    def show_grid(self):
        """Switch back to grid view."""
        self.stack.setCurrentIndex(0)
    
    def show_game(self, game_path: Path, game_title: str):
        """Switch to game view and load the game."""
        self.current_game = game_path
        self.stack.setCurrentIndex(1)
        
        if HAS_WEBENGINE:
            url = QtCore.QUrl.fromLocalFile(str(game_path.resolve()))
            self.game_player.load(url)

    def populate_games(self):
        games_list = games.list_games()
        
        # Filter out sample_game
        games_list = [g for g in games_list if g.get("slug", "").lower() != "sample_game"]

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        # Use 3 columns for larger games (instead of 4)
        cols = 3
        palette = [
            "#ff7675",
            "#74b9ff",
            "#ffeaa7",
            "#55efc4",
            "#fd79a8",
            "#fdcb6e",
            "#00cec9",
        ]

        for idx, g in enumerate(games_list):
            r, c = divmod(idx, cols)
            card = self._create_game_card(g, palette[idx % len(palette)])
            self.grid_layout.addWidget(card, r, c)
        
        # Add column stretches for better layout
        for i in range(cols):
            self.grid_layout.setColumnStretch(i, 1)

    def _create_game_card(self, game: dict, color: str) -> QtWidgets.QWidget:
        """Create a portrait card for a game with image support."""
        card_widget = QtWidgets.QWidget()
        card_widget.setCursor(QtCore.Qt.PointingHandCursor)
        card_widget.setStyleSheet(
            """
            QWidget {
                background-color: transparent;
                border-radius: 20px;
            }
            QWidget:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            """
        )
        v = QtWidgets.QVBoxLayout(card_widget)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(12)

        # Container for game image
        image_container = QtWidgets.QWidget()
        image_container.setFixedSize(280, 400)  # Portrait aspect ratio
        image_container.setStyleSheet(f"background-color: {color}; border-radius: 20px;")
        
        def play_game():
            self.open_game(game)
        image_container.mousePressEvent = lambda e: play_game()
        
        container_layout = QtWidgets.QVBoxLayout(image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Game image (if available, otherwise use colored background)
        game_image = QtWidgets.QLabel()
        game_image.setFixedSize(280, 400)
        game_image.setAlignment(QtCore.Qt.AlignCenter)
        game_image.setStyleSheet(f"background-color: {color}; border-radius: 20px;")
        
        # Try to load image from game data or use placeholder
        image_url = game.get("image", "") or game.get("thumbnail", "")
        if image_url:
            pix = load_pixmap_from_url(image_url, QtCore.QSize(280, 400))
            if not pix.isNull():
                # Scale maintaining aspect ratio
                scaled_pix = QtGui.QPixmap(280, 400)
                scaled_pix.fill(QtGui.QColor(color))
                painter = QtGui.QPainter(scaled_pix)
                x = (scaled_pix.width() - pix.width()) // 2
                y = (scaled_pix.height() - pix.height()) // 2
                painter.drawPixmap(x, y, pix)
                painter.end()
                game_image.setPixmap(scaled_pix)
            else:
                # Placeholder with game icon
                pix = QtGui.QPixmap(280, 400)
                pix.fill(QtGui.QColor(color))
                painter = QtGui.QPainter(pix)
                painter.setPen(QtGui.QColor("#000000"))
                painter.setFont(QtGui.QFont("Arial", 24))
                painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, "🎮")
                painter.end()
                game_image.setPixmap(pix)
        else:
            # Placeholder with game icon
            pix = QtGui.QPixmap(280, 400)
            pix.fill(QtGui.QColor(color))
            painter = QtGui.QPainter(pix)
            painter.setPen(QtGui.QColor("#000000"))
            painter.setFont(QtGui.QFont("Arial", 24))
            painter.drawText(pix.rect(), QtCore.Qt.AlignCenter, "🎮")
            painter.end()
            game_image.setPixmap(pix)
        
        game_image.setScaledContents(False)
        container_layout.addWidget(game_image)

        # Game title
        title_lbl = QtWidgets.QLabel(game.get("title", "Game"))
        title_lbl.setWordWrap(True)
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 600; color: #ffffff; padding: 8px;")

        v.addWidget(image_container, alignment=QtCore.Qt.AlignCenter)
        v.addWidget(title_lbl)
        v.addStretch()
        
        return card_widget

    def open_game(self, game: dict):
        rel_path = game.get("path", "").lstrip("/")
        if not rel_path:
            QtWidgets.QMessageBox.warning(self, "Error", "Game path not found.")
            return
        
        game_file = PROJECT_ROOT / rel_path
        if not game_file.exists():
            QtWidgets.QMessageBox.warning(self, "Error", f"Game file not found: {game_file}")
            return
        
        # Show game in the same page
        self.show_game(game_file, game.get("title", "Game"))


class MainWindow(QtWidgets.QMainWindow):
    """Main desktop shell with sidebar navigation."""

    def __init__(self, user_email: str):
        super().__init__()
        self.user_email = user_email
        self.setWindowTitle(f"SIA - {user_email}")
        # Larger default size for better UI display
        self.resize(1400, 900)
        # Allow window to be maximized
        self.setWindowState(QtCore.Qt.WindowMaximized)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            """
            QFrame {
                background-color: #000000;
            }
            QPushButton {
                background-color: transparent;
                color: #b3b3b3;
                border-radius: 14px;
                padding: 12px 20px;
                text-align: left;
                font-size: 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #282828;
            }
            QPushButton#navActive {
                color: #ffffff;
                background-color: #1ed760;
            }
            QLabel#brandLabel {
                font-size: 22px;
                font-weight: 700;
            }
            QPushButton#logoutBtn {
                background-color: #e74c3c;
                color: #ffffff;
                border-radius: 14px;
                padding: 12px 20px;
                font-size: 18px;
                font-weight: 600;
                margin-top: 20px;
            }
            QPushButton#logoutBtn:hover {
                background-color: #c0392b;
            }
            """
        )
        side_layout = QtWidgets.QVBoxLayout(sidebar)
        side_layout.setContentsMargins(16, 16, 16, 16)
        side_layout.setSpacing(10)

        brand = QtWidgets.QLabel("SIA Hub")
        brand.setObjectName("brandLabel")
        side_layout.addWidget(brand)
        side_layout.addSpacing(10)

        self.btn_music = QtWidgets.QPushButton("Music")
        self.btn_videos = QtWidgets.QPushButton("Videos")
        self.btn_games = QtWidgets.QPushButton("Games")
        side_layout.addWidget(self.btn_music)
        side_layout.addWidget(self.btn_videos)
        side_layout.addWidget(self.btn_games)
        side_layout.addStretch(1)

        logout_btn = QtWidgets.QPushButton("Log out")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.close)
        side_layout.addWidget(logout_btn)

        # Pages
        self.pages = QtWidgets.QStackedWidget()
        self.music_page = MusicPage()
        self.videos_page = VideosPage()
        self.games_page = GamesPage(parent=self)  # Pass parent so games can open windows
        self.pages.addWidget(self.music_page)
        self.pages.addWidget(self.videos_page)
        self.pages.addWidget(self.games_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages, 1)

        self.btn_music.clicked.connect(lambda: self.set_page(0))
        self.btn_videos.clicked.connect(lambda: self.set_page(1))
        self.btn_games.clicked.connect(lambda: self.set_page(2))
        self.set_page(0)

    def set_page(self, idx: int):
        self.pages.setCurrentIndex(idx)
        for i, btn in enumerate([self.btn_music, self.btn_videos, self.btn_games]):
            btn.setObjectName("navActive" if i == idx else "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(create_dark_palette())

    auth = AuthWindow()

    def on_auth(email: str):
        try:
            auth.hide()  # Hide first before creating main window
            main_win = MainWindow(email)
            main_win.show()
            main_win.raise_()  # Bring to front
            main_win.activateWindow()  # Activate window
            auth.close()
        except Exception as e:
            print(f"[main] Error creating main window: {e}")
            import traceback
            traceback.print_exc()
            QtWidgets.QMessageBox.critical(auth, "Error", f"Failed to start application: {str(e)}")
            auth.show()  # Show auth window again if error

    auth.authenticated.connect(on_auth)
    # Show login / signup in fullscreen for an immersive modern experience
    auth.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


