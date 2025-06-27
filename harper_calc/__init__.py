diff --git a//dev/null b/harper_calc/__init__.py
index 0000000000000000000000000000000000000000..303a43ae6c06cdd0a815c85701030ad7d1a364e0 100644
--- a//dev/null
+++ b/harper_calc/__init__.py
@@ -0,0 +1,9 @@
+__all__ = [
+    "calculate_annual_load",
+    "calculate_runoff_volume",
+    "CalculatorApp",
+]
+__version__ = "0.1.0"
+
+from .calculator import calculate_annual_load, calculate_runoff_volume
+from .gui import CalculatorApp
