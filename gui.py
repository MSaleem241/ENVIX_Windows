import threading
import queue
import os
from tkinter import filedialog
import customtkinter as ctk
from installer import setup_tool, setup_stack
from doctor import run_doctor, quick_check
from tools import TOOLS
from stacks import STACKS
from projects import PROJECTS
from project_setup import create_project




ctk.set_appearance_mode("dark")          
ctk.set_default_color_theme("blue")




BG_MAIN     = "#0f0f11"    
BG_SIDEBAR  = "#141418"    
BG_CARD     = "#1c1c22"    
BG_CARD2    = "#232329"    
ACCENT      = "#4f6ef7"    
ACCENT_DARK = "#3a52c7"    

TXT_PRIMARY   = "#f0f0f5"
TXT_SECONDARY = "#8a8a9a"
TXT_SUCCESS   = "#4ade80"  
TXT_WARN      = "#facc15"  
TXT_ERROR     = "#f87171"  

STATUS_COLORS = {
    "ok":         ("#16a34a", "#dcfce7"),  
    "missing":    ("#dc2626", "#fee2e2"),
    "path_issue": ("#ca8a04", "#fef9c3"),
}


TOOL_META = {
    "node":   {"label": "Node.js",     "desc": "JavaScript runtime",      "icon": "⬡"},
    "python": {"label": "Python 3",    "desc": "Scripting & backend",      "icon": "🐍"},
    "git":    {"label": "Git",         "desc": "Version control",          "icon": "⎇"},
    "vscode": {"label": "VS Code",     "desc": "Code editor",              "icon": "{}"},
    "java":   {"label": "Java 21 JDK", "desc": "Java development kit",     "icon": "☕"},
    "go":     {"label": "Go",          "desc": "Systems & cloud backend",  "icon": "◉"},
    "docker": {"label": "Docker",      "desc": "Container platform",       "icon": "🐳"},
}


PROJECT_META = {
    "web":            {"icon": "🌐", "color": "#4f6ef7"},
    "backend_python": {"icon": "🐍", "color": "#7c3aed"},
    "backend_node":   {"icon": "⬡",  "color": "#16a34a"},
    "fullstack":       {"icon": "⛓",  "color": "#059669"},
    "ai_ml":          {"icon": "🤖", "color": "#ea580c"},
    "data_science":   {"icon": "📊", "color": "#0891b2"},
    "game_dev":       {"icon": "🎮", "color": "#db2777"},
}




def run_in_thread(fn, *args):
    """Run a blocking function in a background thread so the GUI stays responsive."""
    t = threading.Thread(target=fn, args=args, daemon=True)
    t.start()


def run_with_logged_output(log_panel, work_fn):
    """
    Run work_fn() while redirecting any print() it calls into log_panel.

    This is shared by every page that calls into installer.py / project_setup.py
    (Languages, Tools, Presets, Doctor) so the "capture print, restore print"
    pattern only has to be written once instead of copy-pasted on every page.
    """
    import builtins
    original_print = builtins.print

    def patched_print(*args, **kwargs):
        message = " ".join(str(a) for a in args)
        log_panel.log(f"   {message}")

    builtins.print = patched_print
    try:
        work_fn()
    finally:
        
        builtins.print = original_print


class ResponsiveCardGrid(ctk.CTkScrollableFrame):
    """
    A scrollable grid that automatically re-flows its columns based on the
    window's current width, instead of a hardcoded "always 2 columns" grid.

    Why this exists: the old grid used grid_columnconfigure((0, 1), weight=1),
    which always made exactly 2 columns that STRETCH to fill the window —
    on a wide screen that meant 2 huge, oversized cards. This version keeps
    every card at a fixed, comfortable width and simply adds more COLUMNS
    when there's more room, instead of stretching existing cards wider.
    """

    def __init__(self, master, card_width=260, card_pad=8, **kwargs):
        super().__init__(master, fg_color="transparent", label_text="", **kwargs)
        self.card_width = card_width
        self.card_pad = card_pad
        self._cards = []         
        self._current_columns = 1

        
        self.bind("<Configure>", self._on_resize, add="+")

    def add_card(self, card_widget):
        """Register a card to be managed by the responsive grid."""
        self._cards.append(card_widget)
        self._relayout()

    def _on_resize(self, event=None):
        self._relayout()

    def _relayout(self):
        """Recompute how many columns fit, then re-place every card."""
        available_width = self.winfo_width()
        if available_width <= 1:
            return

        column_width = self.card_width + (self.card_pad * 2)
        columns = max(1, available_width // column_width)

        if columns == self._current_columns:
            
            self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
            return  
        self._current_columns = columns

        
        for col in range(columns):
            self.grid_columnconfigure(col, weight=0, uniform="card", minsize=column_width)

        for index, card in enumerate(self._cards):
            row, col = divmod(index, columns)
            card.grid(row=row, column=col, padx=self.card_pad, pady=self.card_pad, sticky="n")

        
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))




class LogPanel(ctk.CTkFrame):
    """
    A scrollable terminal-style output panel.
    Other pages push lines into self.queue; a polling loop renders them.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=12, **kwargs)
        self.queue = queue.Queue()

        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(header, text="Output", font=("", 13, "bold"),
                      text_color=TXT_SECONDARY).pack(side="left")
        ctk.CTkButton(header, text="Clear", width=56, height=24,
                       font=("", 11), fg_color=BG_CARD2, hover_color="#2a2a32",
                       text_color=TXT_SECONDARY, corner_radius=6,
                       command=self.clear).pack(side="right")

    
        self.textbox = ctk.CTkTextbox(
            self, font=("Consolas", 12), wrap="word",
            fg_color=BG_CARD2, text_color="#c0c0d0",
            corner_radius=8
        )
        self.textbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.textbox.configure(state="disabled")

        
        self._poll()

    def log(self, message, color=None):
        """Push a message onto the queue to be rendered on the main thread."""
        self.queue.put((message, color))

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def _poll(self):
        """Check for new messages 20 times/second and render them."""
        try:
            while True:
                msg, color = self.queue.get_nowait()
                self._write(msg)
        except queue.Empty:
            pass
        self.after(50, self._poll)

    def _write(self, message):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")




class StatusBadge(ctk.CTkLabel):
    """A small colored pill showing ok / missing / path_issue."""

    STATUS_TEXT = {"ok": "✓ Installed", "missing": "✗ Missing", "path_issue": "⚠ Broken"}

    def __init__(self, master, status="missing", **kwargs):
        super().__init__(master, font=("", 11), corner_radius=6,
                          padx=8, pady=2, **kwargs)
        self.set(status)

    def set(self, status):
        border_color, bg_color = STATUS_COLORS.get(status, STATUS_COLORS["missing"])
        self.configure(
            text=self.STATUS_TEXT.get(status, "Unknown"),
            fg_color=bg_color,
            text_color=border_color,
        )




class ToolGridPage(ctk.CTkFrame):
    """
    Shows a card for each tool that matches the given category.

    Used for BOTH the Languages tab (category="language") and the Tools tab
    (category="tool") — they're visually and behaviorally identical, just
    filtered to a different subset of TOOLS, so one class serves both
    instead of maintaining two nearly-duplicate page classes.
    """

    CARD_WIDTH = 260   

    def __init__(self, master, log_panel: LogPanel, category, title, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log = log_panel
        self.category = category
        self.title_text = title
        self._badges = {}       
        self._buttons = {}      

        
        self._tool_names = [name for name, data in TOOLS.items()
                             if data.get("category") == category]

        self._build_header()
        self._build_grid()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(hdr, text=self.title_text,
                      font=("", 22, "bold"),
                      text_color=TXT_PRIMARY).pack(side="left")

       
        ctk.CTkButton(
            hdr, text="↺  Refresh Status", width=130, height=32,
            font=("", 12), fg_color=BG_CARD, hover_color=BG_CARD2,
            text_color=TXT_SECONDARY, corner_radius=8,
            command=self._refresh_all
        ).pack(side="right", padx=(0, 4))

    def _build_grid(self):
        
        self.grid = ResponsiveCardGrid(self, card_width=self.CARD_WIDTH)
        self.grid.pack(fill="both", expand=True)

        for name in self._tool_names:
            meta = TOOL_META.get(name, {"label": name, "desc": "", "icon": "•"})
            card = self._build_tool_card(self.grid, name, meta)
            self.grid.add_card(card)

    def _build_tool_card(self, parent, name, meta):
        """Build one tool card. Returns the card widget (caller places it)."""
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14,
                             width=self.CARD_WIDTH)
       
        card.pack_propagate(False)
        card.configure(height=150)

        
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(14, 4))

        ctk.CTkLabel(top, text=meta["icon"],
                      font=("", 18), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(top, text=f"  {meta['label']}",
                      font=("", 13, "bold"),
                      text_color=TXT_PRIMARY).pack(side="left")

        badge = StatusBadge(top, status="missing")
        badge.pack(side="right")
        self._badges[name] = badge

        
        ctk.CTkLabel(card, text=meta["desc"],
                      font=("", 11), text_color=TXT_SECONDARY,
                      anchor="w").pack(fill="x", padx=14, pady=(0, 8))

        btn = ctk.CTkButton(
            card, text="Install", height=30,
            font=("", 12, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            text_color="white", corner_radius=8,
            command=lambda n=name: self._install(n)
        )
        btn.pack(pady=(4, 14), padx=14, fill="x", side="bottom")
        self._buttons[name] = btn

        run_in_thread(self._update_badge, name)
        return card

    def _update_badge(self, name):
        """Run quick_check in a thread and schedule a badge update on main thread."""
        is_ok = quick_check(name)
        status = "ok" if is_ok else "missing"
        self.after(0, lambda: self._badges[name].set(status))

    def _refresh_all(self):
        """Refresh every badge on this page in parallel."""
        for name in self._tool_names:
            run_in_thread(self._update_badge, name)

    def _install(self, name):
        """Kick off installation in a background thread."""
        label = TOOL_META.get(name, {}).get("label", name)
        btn = self._buttons[name]

        btn.configure(state="disabled", text="Installing…")
        self.log.log(f"\n▶  Installing {label}…")

        def do_install():
            run_with_logged_output(self.log, lambda: setup_tool(name))

            self.after(0, lambda: self._update_badge(name))
            self.after(0, lambda: btn.configure(state="normal", text="Install"))
            self.log.log(f"   Done: {label}\n")

        run_in_thread(do_install)



class PresetsPage(ctk.CTkFrame):
    """
    Shows a card for each PROJECT preset (Web Dev, Backend, AI/ML, etc.).

    Clicking "Create Project" on a card:
      1. Opens a folder picker so the user chooses WHERE to create it
      2. Asks for a project folder NAME
      3. Calls project_setup.create_project() in a background thread,
         which installs any needed languages, creates the folder, writes
         starter files, and installs dependencies INSIDE that folder.
    """

    CARD_WIDTH = 280

    def __init__(self, master, log_panel: LogPanel, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log = log_panel
        self._buttons = {}

        self._build_header()
        self._build_cards()

    def _build_header(self):
        ctk.CTkLabel(self, text="Project Presets",
                      font=("", 22, "bold"),
                      text_color=TXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            self,
            text="Pick a starter template — ENVIX creates a project folder "
                 "and sets everything up inside it.",
            font=("", 13), text_color=TXT_SECONDARY, anchor="w", wraplength=600
        ).pack(anchor="w", pady=(0, 20))

    def _build_cards(self):
        
        self.grid = ResponsiveCardGrid(self, card_width=self.CARD_WIDTH)
        self.grid.pack(fill="both", expand=True)

        for name, preset in PROJECTS.items():
            meta = PROJECT_META.get(name, {"icon": "•", "color": ACCENT})
            card = self._build_project_card(self.grid, name, preset, meta)
            self.grid.add_card(card)

    def _build_project_card(self, parent, name, preset, meta):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14,
                             width=self.CARD_WIDTH)
        card.pack_propagate(False)
        card.configure(height=210)

        ctk.CTkFrame(card, fg_color=meta["color"], height=4,
                      corner_radius=0).pack(fill="x", side="top")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=14, pady=12)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=meta["icon"], font=("", 18)).pack(side="left")
        ctk.CTkLabel(top, text=f"  {preset['label']}",
                      font=("", 14, "bold"),
                      text_color=TXT_PRIMARY).pack(side="left")

        ctk.CTkLabel(content, text=preset["desc"],
                      font=("", 11), text_color=TXT_SECONDARY,
                      anchor="w", wraplength=self.CARD_WIDTH - 30,
                      justify="left").pack(fill="x", pady=(6, 8))

        pills_frame = ctk.CTkFrame(content, fg_color="transparent")
        pills_frame.pack(anchor="w", fill="x")
        for lang in preset["languages"]:
            pill_label = TOOL_META.get(lang, {}).get("label", lang)
            ctk.CTkLabel(
                pills_frame, text=pill_label,
                font=("", 10, "bold"),
                fg_color=BG_CARD2, text_color=TXT_SECONDARY,
                corner_radius=4, padx=6, pady=2
            ).pack(side="left", padx=(0, 4), pady=(0, 4))

        btn = ctk.CTkButton(
            card, text="Create Project", height=32,
            font=("", 12, "bold"),
            fg_color=meta["color"], hover_color=ACCENT_DARK,
            text_color="white", corner_radius=8,
            command=lambda n=name: self._start_create_flow(n)
        )
        btn.pack(side="bottom", fill="x", padx=14, pady=(0, 14))
        self._buttons[name] = btn

        return card

    def _start_create_flow(self, preset_name):
        """
        Step 1 of creating a project: ask the user WHERE (a parent folder)
        via the native OS folder picker. tkinter.filedialog works fine
        alongside customtkinter since CTk windows are built on top of Tk.
        """
        parent_folder = filedialog.askdirectory(
            title="Choose where to create your project"
        )
        if not parent_folder:
            return  

        name_dialog = ctk.CTkInputDialog(
            text="Name your project folder:",
            title="New Project"
        )
        project_name = name_dialog.get_input()
        if not project_name:
            return  

        full_path = os.path.join(parent_folder, project_name.strip())
        self._create_project(preset_name, full_path)

    def _create_project(self, preset_name, full_path):
        """Run create_project() in a background thread so the GUI stays responsive."""
        label = PROJECTS[preset_name]["label"]
        btn = self._buttons[preset_name]
        btn.configure(state="disabled", text="Creating…")
        self.log.log(f"\n▶  Creating {label} project at {full_path}…")

        def do_create():
            run_with_logged_output(
                self.log,
                lambda: create_project(preset_name, full_path)
            )
            self.after(0, lambda: btn.configure(state="normal", text="Create Project"))
            self.log.log(f"   {label} project setup complete.\n")

        run_in_thread(do_create)



class DoctorPage(ctk.CTkFrame):
    """
    Runs run_doctor() and displays results per tool:
    status badge, version, and actionable fix suggestion.
    """

    def __init__(self, master, log_panel: LogPanel, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log = log_panel
        self._result_area = None

        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(hdr, text="Doctor",
                      font=("", 22, "bold"),
                      text_color=TXT_PRIMARY).pack(side="left")

        self._scan_btn = ctk.CTkButton(
            hdr, text="▶  Run Scan",
            font=("", 13, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            text_color="white", corner_radius=8,
            width=120, height=36,
            command=self._run_scan
        )
        self._scan_btn.pack(side="right")

    def _build_body(self):
        self._summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._summary_frame.pack(fill="x", pady=(0, 16))

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="")
        self._scroll.pack(fill="both", expand=True)

        self._placeholder = ctk.CTkLabel(
            self._scroll,
            text="Press  ▶ Run Scan  to diagnose your environment.",
            font=("", 14), text_color=TXT_SECONDARY
        )
        self._placeholder.pack(pady=40)

    def _run_scan(self):
        """Launch doctor scan in a background thread."""
        self._scan_btn.configure(state="disabled", text="Scanning…")
        self.log.log("\n▶  Doctor scan running…")

        def do_scan():
            results, summary = run_doctor()
            self.after(0, lambda: self._show_results(results, summary))

        run_in_thread(do_scan)

    def _show_results(self, results, summary):
        for w in self._scroll.winfo_children():
            w.destroy()
        for w in self._summary_frame.winfo_children():
            w.destroy()

        self._build_summary(summary)

        for r in results:
            self._build_result_card(r)

        self._scan_btn.configure(state="normal", text="▶  Run Scan")
        self.log.log(
            f"   Scan complete: {summary['ok']} ok, "
            f"{summary['missing']} missing, {summary['broken']} broken.\n"
        )

    def _build_summary(self, summary):
        """Three metric pills: ok / missing / broken counts."""
        metrics = [
            ("Installed",  summary["ok"],      TXT_SUCCESS),
            ("Missing",    summary["missing"],  TXT_ERROR),
            ("Issues",     summary["broken"],   TXT_WARN),
        ]
        for label, count, color in metrics:
            pill = ctk.CTkFrame(self._summary_frame, fg_color=BG_CARD, corner_radius=10)
            pill.pack(side="left", padx=(0, 10), ipadx=16, ipady=10)
            ctk.CTkLabel(pill, text=str(count),
                          font=("", 28, "bold"), text_color=color).pack()
            ctk.CTkLabel(pill, text=label,
                          font=("", 11), text_color=TXT_SECONDARY).pack()

    def _build_result_card(self, result):
        """Build one result row for a tool."""
        status = result["status"]
        border_color, bg_color = STATUS_COLORS.get(status, STATUS_COLORS["missing"])
        name = result["name"]
        meta = TOOL_META.get(name, {"label": name, "icon": "•"})

        card = ctk.CTkFrame(self._scroll, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="x", pady=5)

        stripe_color = border_color
        ctk.CTkFrame(card, fg_color=stripe_color, width=4,
                      corner_radius=2).pack(side="left", fill="y")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=meta["icon"] + "  " + meta["label"],
                      font=("", 13, "bold"),
                      text_color=TXT_PRIMARY).pack(side="left")
        StatusBadge(top, status=status).pack(side="right")

        note_text = result["version"] if result["version"] else result["note"]
        ctk.CTkLabel(inner, text=note_text,
                      font=("", 11), text_color=TXT_SECONDARY,
                      anchor="w", wraplength=540).pack(fill="x", pady=(4, 0))

        if result["fix"]:
            fix_frame = ctk.CTkFrame(inner, fg_color=BG_CARD2, corner_radius=6)
            fix_frame.pack(fill="x", pady=(8, 0))
            ctk.CTkLabel(fix_frame, text=f"⚡  {result['fix']}",
                          font=("Consolas", 10), text_color=TXT_WARN,
                          anchor="w", wraplength=500).pack(padx=10, pady=6, anchor="w")

            if name in TOOLS and status == "missing":
                ctk.CTkButton(
                    inner, text="Fix Now",
                    font=("", 11), width=80, height=26,
                    fg_color=ACCENT, hover_color=ACCENT_DARK,
                    text_color="white", corner_radius=6,
                    command=lambda n=name: self._fix_tool(n)
                ).pack(anchor="w", pady=(6, 0))

    def _fix_tool(self, name):
        """Trigger install for a missing tool found by the Doctor."""
        label = TOOL_META.get(name, {}).get("label", name)
        self.log.log(f"\n⚡  Doctor: fixing {label}…")

        def do_fix():
            run_with_logged_output(self.log, lambda: setup_tool(name))
            self.log.log(f"   Fix attempt complete. Run scan again to verify.\n")

        run_in_thread(do_fix)



class NavButton(ctk.CTkButton):
    """A sidebar navigation button with active/inactive visual state."""

    def __init__(self, master, text, icon, command, **kwargs):
        super().__init__(
            master,
            text=f" {icon}   {text}",
            anchor="w",
            font=("", 13),
            fg_color="transparent",
            hover_color=BG_CARD,
            text_color=TXT_SECONDARY,
            corner_radius=8,
            height=40,
            command=command,
            **kwargs
        )
        self._active = False

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.configure(fg_color=BG_CARD, text_color=TXT_PRIMARY)
        else:
            self.configure(fg_color="transparent", text_color=TXT_SECONDARY)



class EnvixApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("ENVIX — Dev Environment Manager")
        self.geometry("1180x720")
        self.minsize(900, 600)
        self.configure(fg_color=BG_MAIN)

        self._pages = {}
        self._nav_buttons = {}
        self._active_page = None

        self._build_layout()
        self._show_page("languages")

    def _build_layout(self):
        sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, width=210, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(28, 24))

        ctk.CTkLabel(logo_frame, text="ENVIX",
                      font=("", 22, "bold"),
                      text_color=TXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="Dev Environment Manager",
                      font=("", 10), text_color=TXT_SECONDARY).pack(anchor="w")

        ctk.CTkFrame(sidebar, fg_color=BG_CARD2, height=1).pack(fill="x", padx=16, pady=(0, 16))

        nav_items = [
            ("languages", "Languages", "⬡"),
            ("tools",     "Tools",     "🔧"),
            ("presets",   "Presets",   "⊞"),
            ("doctor",    "Doctor",    "♥"),
        ]
        for page_id, label, icon in nav_items:
            btn = NavButton(
                sidebar, text=label, icon=icon,
                command=lambda p=page_id: self._show_page(p)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_buttons[page_id] = btn

        ctk.CTkLabel(sidebar, text="v1.1.0  •  Windows",
                      font=("", 10), text_color=TXT_SECONDARY).pack(
            side="bottom", pady=16
        )

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        self._content_area = ctk.CTkFrame(right, fg_color="transparent")
        self._content_area.pack(fill="both", expand=True, padx=24, pady=20)

        self._log = LogPanel(right, height=180)
        self._log.pack(fill="x", padx=24, pady=(0, 16))

        self._pages["languages"] = ToolGridPage(
            self._content_area, self._log,
            category="language", title="Languages"
        )
        self._pages["tools"] = ToolGridPage(
            self._content_area, self._log,
            category="tool", title="Tools"
        )
        self._pages["presets"] = PresetsPage(self._content_area, self._log)
        self._pages["doctor"]  = DoctorPage(self._content_area, self._log)

    def _show_page(self, page_id: str):
        """Switch to the given page and update sidebar highlight."""
        if self._active_page:
            self._pages[self._active_page].pack_forget()
            self._nav_buttons[self._active_page].set_active(False)

        self._pages[page_id].pack(fill="both", expand=True)
        self._nav_buttons[page_id].set_active(True)
        self._active_page = page_id



def launch():
    app = EnvixApp()
    app.mainloop()


if __name__ == "__main__":
    launch()
