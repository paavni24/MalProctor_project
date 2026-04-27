"""
APK Scanner — Extracts features from an APK and runs the trained TUANDROMD model.

Pipeline:
  1. Decompile APK with apktool
  2. Parse AndroidManifest.xml for permissions
  3. Scan smali files for suspicious API calls
  4. Map extracted features to the TUANDROMD 241-column binary vector
  5. Run the saved best_model.pkl and return prediction
"""

import os
import re
import shutil
import subprocess
import pickle
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

# ── Paths ──
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "data", "best_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "data", "scaler.pkl")
TEMP_DIR    = os.path.join(BASE_DIR, "temp_decompiled")
APKTOOL     = os.path.join(BASE_DIR, "bin", "apktool")   # local binary

# ── TUANDROMD Feature Columns ──
# These are the 241 columns from the training dataset (excluding Label).
# Permissions are stored WITHOUT the "android.permission." prefix.
# API calls are stored in smali format like "Ljava/lang/Runtime;->exec".
TUANDROMD_COLUMNS = [
    "ACCESS_ALL_DOWNLOADS", "ACCESS_CACHE_FILESYSTEM", "ACCESS_CHECKIN_PROPERTIES",
    "ACCESS_COARSE_LOCATION", "ACCESS_COARSE_UPDATES", "ACCESS_FINE_LOCATION",
    "ACCESS_LOCATION_EXTRA_COMMANDS", "ACCESS_MOCK_LOCATION", "ACCESS_MTK_MMHW",
    "ACCESS_NETWORK_STATE", "ACCESS_PROVIDER", "ACCESS_SERVICE", "ACCESS_SHARED_DATA",
    "ACCESS_SUPERUSER", "ACCESS_SURFACE_FLINGER", "ACCESS_WIFI_STATE",
    "activityCalled", "ACTIVITY_RECOGNITION", "ACCOUNT_MANAGER", "ADD_VOICEMAIL",
    "ANT", "ANT_ADMIN", "AUTHENTICATE_ACCOUNTS", "AUTORUN_MANAGER_LICENSE_MANAGER",
    "AUTORUN_MANAGER_LICENSE_SERVICE(.autorun)", "BATTERY_STATS", "BILLING",
    "BIND_ACCESSIBILITY_SERVICE", "BIND_APPWIDGET", "BIND_CARRIER_MESSAGING_SERVICE",
    "BIND_DEVICE_ADMIN", "BIND_DREAM_SERVICE", "BIND_GET_INSTALL_REFERRER_SERVICE",
    "BIND_INPUT_METHOD", "BIND_NFC_SERVICE", "BIND_goodwareTIFICATION_LISTENER_SERVICE",
    "BIND_PRINT_SERVICE", "BIND_REMOTEVIEWS", "BIND_TEXT_SERVICE", "BIND_TV_INPUT",
    "BIND_VOICE_INTERACTION", "BIND_VPN_SERVICE", "BIND_WALLPAPER",
    "BLUETOOTH", "BLUETOOTH_ADMIN", "BLUETOOTH_PRIVILEGED", "BODY_SENSORS",
    "BRICK", "BROADCAST_PACKAGE_REMOVED", "BROADCAST_SMS", "BROADCAST_STICKY",
    "BROADCAST_WAP_PUSH", "C2D_MESSAGE", "CALL_PHONE", "CALL_PRIVILEGED",
    "CAMERA", "CAPTURE_AUDIO_OUTPUT", "CAPTURE_SECURE_VIDEO_OUTPUT",
    "CAPTURE_VIDEO_OUTPUT", "CHANGE_COMPONENT_ENABLED_STATE", "CHANGE_CONFIGURATION",
    "CHANGE_DISPLAY_MODE", "CHANGE_NETWORK_STATE", "CHANGE_WIFI_MULTICAST_STATE",
    "CHANGE_WIFI_STATE", "CHECK_LICENSE", "CLEAR_APP_CACHE", "CLEAR_APP_USER_DATA",
    "CONTROL_LOCATION_UPDATES", "DATABASE_INTERFACE_SERVICE", "DELETE_CACHE_FILES",
    "DELETE_PACKAGES", "DEVICE_POWER", "DIAGgoodwareSTIC", "DISABLE_KEYGUARD",
    "DOWNLOAD_SERVICE", "DOWNLOAD_WITHOUT_goodwareTIFICATION", "DUMP",
    "EXPAND_STATUS_BAR", "EXTENSION_PERMISSION", "FACTORY_TEST", "FLASHLIGHT",
    "FORCE_BACK", "FULLSCREEN.FULL", "GET_ACCOUNTS", "GET_PACKAGE_SIZE",
    "GET_TASKS", "GET_TOP_ACTIVITY_INFO", "GLOBAL_SEARCH", "GOOGLE_AUTH",
    "GOOGLE_PHOTOS", "HARDWARE_TEST", "INJECT_EVENTS", "INSTALL_LOCATION_PROVIDER",
    "INSTALL_PACKAGES", "INSTALL_SHORTCUT", "INTERACT_ACROSS_USERS",
    "INTERNAL_SYSTEM_WINDOW", "INTERNET", "JPUSH_MESSAGE",
    "KILL_BACKGROUND_PROCESSES", "LOCATION_HARDWARE", "MANAGE_ACCOUNTS",
    "MANAGE_APP_TOKENS", "MANAGE_DOCUMENTS", "MAPS_RECEIVE", "MASTER_CLEAR",
    "MEDIA_BUTTON", "MEDIA_CONTENT_CONTROL", "MESSAGE", "MODIFY_AUDIO_SETTINGS",
    "MODIFY_PHONE_STATE", "MOUNT_FORMAT_FILESYSTEMS", "MOUNT_UNMOUNT_FILESYSTEMS",
    "NFC", "PERSISTENT_ACTIVITY", "PERMISSION", "PERMISSION_RUN_TASKS", "PLUGIN",
    "PROCESS_OUTGOING_CALLS", "READ", "READ_ATTACHMENT", "READ_AVESTTINGS",
    "READ_CALENDAR", "READ_CALL_LOG", "READ_CONTACTS", "READ_CONTENT_PROVIDER",
    "READ_DATA", "READ_DATABASES", "READ_EXTERNAL_STORAGE", "READ_FRAME_BUFFER",
    "READ_GMAIL", "READ_GSERVICES", "READ_HISTORY_BOOKMARKS", "READ_INPUT_STATE",
    "READ_LOGS", "READ_MESSAGES", "READ_OWNER_DATA", "READ_PHONE_STATE",
    "READ_PROFILE", "READ_SETTINGS", "READ_SMS", "READ_SOCIAL_STREAM",
    "READ_SYNC_SETTINGS", "READ_SYNC_STATS", "READ_USER_DICTIONARY", "READ_VOICEMAIL",
    "REBOOT", "RECEIVE", "RECEIVE_BOOT_COMPLETED", "RECEIVE_MMS",
    "RECEIVE_SIGNED_DATA_RESULT", "RECEIVE_SMS", "RECEIVE_USER_PRESENT",
    "RECEIVE_WAP_PUSH", "RECORD_AUDIO", "REORDER_TASKS", "RESPOND",
    "RESTART_PACKAGES", "REQUEST", "SDCARD_WRITE", "SEND",
    "SEND_RESPOND_VIA_MESSAGE", "SEND_SMS", "SET_ACTIVITY_WATCHER", "SET_ALARM",
    "SET_ALWAYS_FINISH", "SET_ANIMATION_SCALE", "SET_DEBUG_APP", "SET_ORIENTATION",
    "SET_POINTER_SPEED", "SET_PREFERRED_APPLICATIONS", "SET_PROCESS_LIMIT",
    "SET_TIME", "SET_TIME_ZONE", "SET_WALLPAPER", "SET_WALLPAPER_HINTS",
    "SIGNAL_PERSISTENT_PROCESSES", "STATUS_BAR", "STORAGE",
    "SUBSCRIBED_FEEDS_READ", "SUBSCRIBED_FEEDS_WRITE", "SYSTEM_ALERT_WINDOW",
    "TRANSMIT_IR", "UNINSTALL_SHORTCUT", "UPDATE_DEVICE_STATS",
    "USES_POLICY_FORCE_LOCK", "USE_CREDENTIALS", "USE_FINGERPRINT", "USE_SIP",
    "VIBRATE", "WAKE_LOCK", "WRITE", "WRITE_APN_SETTINGS", "WRITE_AVSETTING",
    "WRITE_CALENDAR", "WRITE_CALL_LOG", "WRITE_CONTACTS", "WRITE_DATA",
    "WRITE_DATABASES", "WRITE_EXTERNAL_STORAGE", "WRITE_GSERVICES",
    "WRITE_HISTORY_BOOKMARKS", "WRITE_INTERNAL_STORAGE", "WRITE_MEDIA_STORAGE",
    "WRITE_OWNER_DATA", "WRITE_PROFILE", "WRITE_SECURE_SETTINGS", "WRITE_SETTINGS",
    "WRITE_SMS", "WRITE_SOCIAL_STREAM", "WRITE_SYNC_SETTINGS",
    "WRITE_USER_DICTIONARY", "WRITE_VOICEMAIL",
    # API Calls (27 columns)
    "Ljava/lang/reflect/Method;->invoke",
    "Ljavax/crypto/Cipher;->doFinal",
    "Ljava/lang/Runtime;->exec",
    "Ljava/lang/System;->load",
    "Ldalvik/system/DexClassLoader;->loadClass",
    "Ljava/lang/System;->loadLibrary",
    "Ljava/net/URL;->openConnection",
    "Landroid/hardware/Camera;->open",
    "Landroid/hardware/Camera;->takePicture",
    "Landroid/telephony/SmsManager;->sendMultipartTextMessage",
    "Landroid/telephony/SmsManager;->sendTextMessage",
    "Landroid/media/AudioRecord;->startRecording",
    "Landroid/telephony/TelephonyManager;->getCellLocation",
    "Lcom/google/android/gms/location/LocationClient;->getLastLocation",
    "Landroid/location/LocationManager;->getLastKgoodwarewnLocation",
    "Landroid/telephony/TelephonyManager;->getDeviceId",
    "Landroid/content/pm/PackageManager;->getInstalledApplications",
    "Landroid/content/pm/PackageManager;->getInstalledPackages",
    "Landroid/telephony/TelephonyManager;->getLine1Number",
    "Landroid/telephony/TelephonyManager;->getNetworkOperator",
    "Landroid/telephony/TelephonyManager;->getNetworkOperatorName",
    "Landroid/telephony/TelephonyManager;->getNetworkCountryIso",
    "Landroid/telephony/TelephonyManager;->getSimOperator",
    "Landroid/telephony/TelephonyManager;->getSimOperatorName",
    "Landroid/telephony/TelephonyManager;->getSimCountryIso",
    "Landroid/telephony/TelephonyManager;->getSimSerialNumber",
    "Lorg/apache/http/impl/client/DefaultHttpClient;->execute",
]

# Suspicious features to flag in the UI
SUSPICIOUS_PERMISSIONS = {
    "SEND_SMS", "READ_SMS", "RECEIVE_SMS", "READ_CONTACTS", "CALL_PHONE",
    "READ_CALL_LOG", "CAMERA", "RECORD_AUDIO", "ACCESS_FINE_LOCATION",
    "READ_PHONE_STATE", "INSTALL_PACKAGES", "DELETE_PACKAGES",
    "BIND_DEVICE_ADMIN", "SYSTEM_ALERT_WINDOW", "WRITE_SMS",
    "PROCESS_OUTGOING_CALLS", "READ_LOGS", "DISABLE_KEYGUARD",
    "INTERNET", "ACCESS_SUPERUSER", "RECEIVE_BOOT_COMPLETED",
}

SUSPICIOUS_APIS = {
    "Ljava/lang/Runtime;->exec",
    "Ldalvik/system/DexClassLoader;->loadClass",
    "Ljava/lang/reflect/Method;->invoke",
    "Ljavax/crypto/Cipher;->doFinal",
    "Landroid/telephony/SmsManager;->sendTextMessage",
    "Landroid/telephony/SmsManager;->sendMultipartTextMessage",
    "Landroid/telephony/TelephonyManager;->getDeviceId",
    "Landroid/telephony/TelephonyManager;->getLine1Number",
    "Landroid/media/AudioRecord;->startRecording",
    "Landroid/hardware/Camera;->takePicture",
}


def decompile_apk(apk_path):
    """Decompile APK using apktool. Returns path to decompiled dir or None."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    basename = os.path.splitext(os.path.basename(apk_path))[0]
    output_dir = os.path.join(TEMP_DIR, basename)

    # Clean up previous decompilation
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    try:
        subprocess.run(
            [APKTOOL, "d", apk_path, "-o", output_dir, "-f"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=120,
        )
        return output_dir
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[!] Decompilation failed: {e}")
        return None


def extract_permissions(manifest_path):
    """Extract permission names from AndroidManifest.xml."""
    permissions = set()
    if not os.path.exists(manifest_path):
        return permissions

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        ns = "{http://schemas.android.com/apk/res/android}"

        for perm in root.findall("uses-permission"):
            name = perm.get(f"{ns}name", "")
            # Strip "android.permission." prefix to match TUANDROMD format
            if "." in name:
                name = name.rsplit(".", 1)[-1]
            permissions.add(name)
    except Exception as e:
        print(f"[!] Manifest parse error: {e}")

    return permissions


def extract_api_calls(smali_dir):
    """Scan smali files for API call signatures matching TUANDROMD columns."""
    api_calls = set()
    if not os.path.exists(smali_dir):
        return api_calls

    # Only look for API calls that are in the TUANDROMD feature set
    target_apis = [c for c in TUANDROMD_COLUMNS if c.startswith("L")]
    api_pattern = re.compile(r"invoke-\S+\s+\{[^}]*\},\s*(L[^;]+;->[^\s(]+)")

    for dirpath, _, files in os.walk(smali_dir):
        for fname in files:
            if not fname.endswith(".smali"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for match in api_pattern.finditer(content):
                    call = match.group(1)
                    for target in target_apis:
                        if target in call:
                            api_calls.add(target)
            except Exception:
                continue

    return api_calls


def build_feature_vector(permissions, api_calls):
    """Build a binary feature vector matching the TUANDROMD column order."""
    row = {}
    for col in TUANDROMD_COLUMNS:
        if col.startswith("L"):
            # API call column
            row[col] = 1 if col in api_calls else 0
        else:
            # Permission column
            row[col] = 1 if col in permissions else 0
    return row


def scan_apk(apk_path):
    """
    Full scan pipeline: decompile → extract → predict.

    Returns dict with:
      - verdict: "SAFE" or "MALWARE"
      - confidence: float 0-1
      - permissions_found: list of permission names
      - api_calls_found: list of API call names
      - suspicious_features: list of flagged features
      - feature_count: total features detected
    """
    result = {
        "verdict": "UNKNOWN",
        "confidence": 0.0,
        "permissions_found": [],
        "api_calls_found": [],
        "suspicious_features": [],
        "feature_count": 0,
        "error": None,
    }

    # 1. Decompile
    decompiled_dir = decompile_apk(apk_path)
    if not decompiled_dir:
        result["error"] = "Failed to decompile APK. Ensure apktool and Java are installed."
        return result

    try:
        # 2. Extract features
        manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
        permissions = extract_permissions(manifest_path)

        # Try multiple smali directories (apktool sometimes creates smali_classes2, etc.)
        api_calls = set()
        for d in os.listdir(decompiled_dir):
            if d.startswith("smali"):
                api_calls |= extract_api_calls(os.path.join(decompiled_dir, d))

        result["permissions_found"] = sorted(permissions)
        result["api_calls_found"] = sorted(api_calls)
        result["feature_count"] = len(permissions) + len(api_calls)

        # 3. Flag suspicious features
        suspicious = []
        for p in permissions:
            if p in SUSPICIOUS_PERMISSIONS:
                suspicious.append({"name": p, "type": "permission"})
        for a in api_calls:
            if a in SUSPICIOUS_APIS:
                suspicious.append({"name": a, "type": "api_call"})
        result["suspicious_features"] = suspicious

        # 4. Build feature vector and predict
        feature_dict = build_feature_vector(permissions, api_calls)

        # Load model
        with open(MODEL_PATH, "rb") as f:
            bundle = pickle.load(f)

        model = bundle["model"]
        selected_features = bundle.get("features", TUANDROMD_COLUMNS)

        # Build DataFrame with only the features the model was trained on
        row_data = {feat: feature_dict.get(feat, 0) for feat in selected_features}
        row_df = pd.DataFrame([row_data])

        # Sanitize column names (same as training)
        row_df.columns = [re.sub(r'[^\w]', '_', str(c).strip()) for c in row_df.columns]

        # Predict
        prediction = model.predict(row_df)[0]

        if hasattr(model, "predict_proba"):
            probas = model.predict_proba(row_df)[0]
            confidence = float(max(probas))
        else:
            confidence = 1.0

        result["verdict"] = "MALWARE" if prediction == 1 else "SAFE"
        result["confidence"] = confidence

    except Exception as e:
        result["error"] = str(e)
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        if decompiled_dir and os.path.exists(decompiled_dir):
            shutil.rmtree(decompiled_dir, ignore_errors=True)

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python apk_scanner.py <path_to_apk>")
    else:
        import json
        result = scan_apk(sys.argv[1])
        print(json.dumps(result, indent=2))
