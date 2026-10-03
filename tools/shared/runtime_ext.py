

# ---------------------------------------------------------------------------
# LEVEL 2 EXTENSION (backwards compatible with Level 1's _pfb_run).
# Adds: top-level `await` (for pyodide.http.pyfetch), matplotlib plots shown
# as images, and plot colours that match the page's light/dark theme.
# Level 1 can switch to this version unchanged when the code is shared.
# ---------------------------------------------------------------------------
import ast
import base64
import inspect
import os
import warnings

os.environ.setdefault("MPLBACKEND", "Agg")   # draw plots in memory, never in a window

_pfb_theme = "light"   # set by the page before every run: "light" or "dark"

# Validated categorical palette (first three slots are colour-blind safe as a set).
_PFB_PLOT_STYLE = {
    "light": {"surface": "#fcfcfb", "text": "#0b0b0b", "muted": "#52514e", "grid": "#e4e3df",
              "colors": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]},
    "dark": {"surface": "#1a1a19", "text": "#ffffff", "muted": "#c3c2b7", "grid": "#383835",
             "colors": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]},
}


def _pfb_plot_setup(code):
    """Reset matplotlib to the page's style before each run (only if the code uses it)."""
    if "matplotlib" not in code:
        return
    import matplotlib
    from cycler import cycler
    style = _PFB_PLOT_STYLE.get(_pfb_theme, _PFB_PLOT_STYLE["light"])
    matplotlib.rcdefaults()
    matplotlib.rcParams.update({
        "figure.figsize": (6.4, 4.0), "figure.dpi": 100, "font.size": 11,
        "figure.facecolor": style["surface"], "axes.facecolor": style["surface"],
        "savefig.facecolor": style["surface"], "text.color": style["text"],
        "axes.labelcolor": style["text"], "axes.titlecolor": style["text"],
        "axes.edgecolor": style["muted"], "xtick.color": style["muted"], "ytick.color": style["muted"],
        "xtick.labelcolor": style["text"], "ytick.labelcolor": style["text"],
        "grid.color": style["grid"], "axes.prop_cycle": cycler(color=style["colors"]),
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "lines.linewidth": 2, "lines.markersize": 7,
        "patch.force_edgecolor": True, "patch.edgecolor": style["surface"], "patch.linewidth": 1,
    })
    import matplotlib.pyplot as plt
    plt.close("all")


def _pfb_alt_text(fig):
    """Build a short description of a figure from its titles and axis labels."""
    descriptions = []
    for ax in fig.axes:
        if ax.containers:
            kind = "Bar chart or histogram"
        elif ax.collections:
            kind = "Scatter plot"
        elif ax.get_lines():
            kind = "Line plot"
        else:
            kind = "Plot"
        bits = [kind]
        if ax.get_title():
            bits.append(f"titled '{ax.get_title()}'")
        if ax.get_xlabel():
            bits.append(f"x-axis: {ax.get_xlabel()}")
        if ax.get_ylabel():
            bits.append(f"y-axis: {ax.get_ylabel()}")
        descriptions.append(", ".join(bits))
    if fig._suptitle is not None and fig._suptitle.get_text():
        descriptions.insert(0, f"Figure titled '{fig._suptitle.get_text()}'")
    return ". ".join(descriptions) or "A plot with no title or axis labels"


def _pfb_collect_plots():
    """Turn every open matplotlib figure into a PNG (as text), then close them all."""
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is None:
        return []
    images = []
    try:
        for number in plt.get_fignums():
            fig = plt.figure(number)
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=110, bbox_inches="tight")
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            images.append({"src": "data:image/png;base64," + encoded, "alt": _pfb_alt_text(fig)})
    finally:
        plt.close("all")
    return images


def _pfb_forget_local_modules():
    """Make `import mymodule` re-read .py files from the page's folder on every run."""
    here = os.getcwd()
    if here not in sys.path:
        sys.path.insert(0, here)
    for name, module in list(sys.modules.items()):
        path = getattr(module, "__file__", None) or ""
        if path.startswith(here + os.sep):
            del sys.modules[name]


async def _pfb_exec(source, filename, namespace):
    """Like exec(), but also allows `await` at the top level of the code."""
    compiled = compile(source, filename, "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    result = eval(compiled, namespace)
    if inspect.iscoroutine(result):
        await result


async def _pfb_run(code, tests=None):
    result = {"output": "", "error": None, "check": None, "images": []}
    buffer = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buffer
    namespace = {"__name__": "__main__"}
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*non-interactive.*")   # plt.show() in memory
            try:
                _pfb_forget_local_modules()
                _pfb_plot_setup(code + "\n" + (tests if isinstance(tests, str) else ""))
                await _pfb_exec(code, _USER_FILE, namespace)
            except SystemExit:
                pass
            except BaseException as exc:
                result["error"] = _pfb_describe(exc, code)
            result["output"] = buffer.getvalue()
            if isinstance(tests, str) and result["error"] is None:
                namespace["_output"] = result["output"]
                namespace["_source"] = code
                sys.stdout = sys.stderr = io.StringIO()   # hide anything printed while testing
                try:
                    await _pfb_exec(tests, "<check>", namespace)
                    result["check"] = {"passed": True}
                except AssertionError as exc:
                    result["check"] = {"passed": False, "message": str(exc)}
                except BaseException as exc:
                    result["check"] = {"passed": False, "error": _pfb_describe(exc, code)}
            try:
                result["images"] = _pfb_collect_plots()
            except BaseException as exc:
                if result["error"] is None:
                    result["error"] = _pfb_describe(exc, code)
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    return json.dumps(result)
