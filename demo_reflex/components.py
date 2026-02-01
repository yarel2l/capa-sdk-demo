"""
Components Module
Reusable components for the CAPA Demo.
"""

import reflex as rx
from typing import Dict, Any, Optional, List, cast

# Import only the components we use directly (figures are pre-computed in state.py)
from .plotly_charts import (
    evidence_level_badge,
    confidence_interval_display,
)


# Custom Webcam component without the muted special_props issue
class SafeWebcam(rx.Component):
    """Webcam wrapper that fixes the muted prop issue in reflex-webcam."""

    library = "react-webcam"
    tag = "Webcam"
    is_default = True

    # Props
    audio: rx.Var[bool] = rx.Var.create(False)
    screenshot_format: rx.Var[str] = rx.Var.create("image/jpeg")
    mirrored: rx.Var[bool] = rx.Var.create(False)
    video_constraints: rx.Var[dict] = rx.Var.create({})

    @classmethod
    def create(cls, *children, **props) -> "SafeWebcam":
        props.setdefault("id", rx.vars.get_unique_variable_name())
        # Add muted as a boolean prop instead of special_props
        props.setdefault("muted", True)
        return cast("SafeWebcam", super().create(*children, **props))


safe_webcam = SafeWebcam.create


def upload_screenshot_safe(webcam_id: str, handler):
    """Capture cropped screenshot from webcam component - only the face area inside the oval guide."""
    # JavaScript to capture and crop to oval area using DOM queries
    crop_script = f"""
(async function() {{
    // Find video element via DOM (webcam component renders a video element)
    const video = document.querySelector('#{webcam_id} video') || document.querySelector('video');
    if (!video) {{
        console.warn('[Capture] Video element not found');
        return null;
    }}

    // Create canvas to capture screenshot
    const captureCanvas = document.createElement('canvas');
    captureCanvas.width = video.videoWidth;
    captureCanvas.height = video.videoHeight;
    const captureCtx = captureCanvas.getContext('2d');
    captureCtx.drawImage(video, 0, 0);
    const originalDataUrl = captureCanvas.toDataURL('image/jpeg', 0.92);

    if (!originalDataUrl) {{
        console.warn('[Capture] Failed to get screenshot');
        return null;
    }}

    // Load image and crop
    return await new Promise((resolve) => {{
        const img = new Image();
        img.onload = function() {{
            // Calculate crop area (matching oval guide proportions)
            const cropWidthPercent = 0.50;  // 50% width for face
            const cropHeightPercent = 0.75; // 75% height for head + chin
            const cropCenterXPercent = 0.50;
            const cropCenterYPercent = 0.45;

            const cropWidth = img.width * cropWidthPercent;
            const cropHeight = img.height * cropHeightPercent;
            const cropX = (img.width * cropCenterXPercent) - (cropWidth / 2);
            const cropY = (img.height * cropCenterYPercent) - (cropHeight / 2);

            // Clamp values to valid range
            const finalX = Math.max(0, cropX);
            const finalY = Math.max(0, cropY);
            const finalWidth = Math.min(cropWidth, img.width - finalX);
            const finalHeight = Math.min(cropHeight, img.height - finalY);

            // Create canvas and crop
            const canvas = document.createElement('canvas');
            canvas.width = finalWidth;
            canvas.height = finalHeight;
            const ctx = canvas.getContext('2d');

            // Draw cropped region
            ctx.drawImage(
                img,
                finalX, finalY, finalWidth, finalHeight,
                0, 0, finalWidth, finalHeight
            );

            const croppedDataUrl = canvas.toDataURL('image/jpeg', 0.92);
            console.log('[Capture] Cropped image:', finalWidth, 'x', finalHeight);
            resolve(croppedDataUrl);
        }};
        img.onerror = function() {{
            console.error('[Capture] Failed to load image for cropping');
            resolve(originalDataUrl);  // Fallback to original
        }};
        img.src = originalDataUrl;
    }});
}})()
"""
    return rx.call_script(
        crop_script,
        callback=handler,
    )


def face_detection_script(
    webcam_id: str,
    on_status_change,
    on_auto_capture
) -> rx.Component:
    """
    Face detection script using browser's FaceDetector API.
    Provides visual feedback and auto-capture when face is properly positioned.
    Auto-capture is always enabled by default.
    """
    script = f"""
(function() {{
    // Configuration
    const WEBCAM_ID = '{webcam_id}';
    const DETECTION_INTERVAL = 200; // ms between detection checks
    const CENTERED_HOLD_TIME = 2000; // ms to hold centered before ready
    const READY_COUNTDOWN = 3; // seconds countdown before capture

    // State
    let faceDetector = null;
    let detectionInterval = null;
    let centeredStartTime = null;
    let countdownInterval = null;
    let currentCountdown = 0;
    let lastStatus = 'scanning';
    let isCapturing = false;

    // Check if FaceDetector API is available
    const hasFaceDetector = 'FaceDetector' in window;

    // Get webcam video element via DOM query
    function getVideoElement() {{
        // Try to find video by webcam container id first, then fallback to any video
        const video = document.querySelector('#' + WEBCAM_ID + ' video') || document.querySelector('video');
        return video;
    }}

    // Initialize face detector
    async function initFaceDetector() {{
        if (hasFaceDetector) {{
            try {{
                faceDetector = new FaceDetector({{
                    fastMode: true,
                    maxDetectedFaces: 1
                }});
                console.log('[FaceDetection] FaceDetector API initialized');
                return true;
            }} catch (e) {{
                console.warn('[FaceDetection] FaceDetector init failed:', e);
                return false;
            }}
        }}
        console.log('[FaceDetection] FaceDetector API not available, using fallback');
        return false;
    }}

    // Check if face is centered in the guide oval
    function isFaceCentered(face, videoWidth, videoHeight) {{
        // Guide oval is centered at 50%, 50% with ~40% width and ~55% height
        const guideCenterX = videoWidth * 0.5;
        const guideCenterY = videoHeight * 0.45;
        const guideWidth = videoWidth * 0.4;
        const guideHeight = videoHeight * 0.55;

        // Face bounding box
        const faceBox = face.boundingBox;
        const faceCenterX = faceBox.x + faceBox.width / 2;
        const faceCenterY = faceBox.y + faceBox.height / 2;

        // Check if face center is within guide area (with margin)
        const marginX = guideWidth * 0.3;
        const marginY = guideHeight * 0.3;

        const xInRange = Math.abs(faceCenterX - guideCenterX) < marginX;
        const yInRange = Math.abs(faceCenterY - guideCenterY) < marginY;

        // Check face size is appropriate (not too small or too large)
        const minFaceSize = Math.min(videoWidth, videoHeight) * 0.15;
        const maxFaceSize = Math.min(videoWidth, videoHeight) * 0.8;
        const faceSize = Math.max(faceBox.width, faceBox.height);
        const sizeOk = faceSize >= minFaceSize && faceSize <= maxFaceSize;

        return xInRange && yInRange && sizeOk;
    }}

    // Update status (calls Reflex event handler)
    function updateStatus(status, message) {{
        if (status !== lastStatus) {{
            lastStatus = status;
            // Dispatch custom event that Reflex can handle
            window.dispatchEvent(new CustomEvent('faceDetectionStatus', {{
                detail: {{ status, message }}
            }}));
        }}
    }}

    // Start countdown for auto-capture
    function startCountdown() {{
        if (countdownInterval) return;

        currentCountdown = READY_COUNTDOWN;
        updateStatus('ready', 'Capturing in ' + currentCountdown + '...');

        countdownInterval = setInterval(() => {{
            currentCountdown--;
            if (currentCountdown > 0) {{
                updateStatus('ready', 'Capturing in ' + currentCountdown + '...');
            }} else {{
                clearInterval(countdownInterval);
                countdownInterval = null;
                triggerAutoCapture();
            }}
        }}, 1000);
    }}

    // Stop countdown
    function stopCountdown() {{
        if (countdownInterval) {{
            clearInterval(countdownInterval);
            countdownInterval = null;
            currentCountdown = 0;
        }}
    }}

    // Trigger auto-capture
    function triggerAutoCapture() {{
        if (isCapturing) return;
        isCapturing = true;

        updateStatus('capturing', 'Capturing...');

        // Click the capture button to trigger Reflex handler
        const captureBtn = document.getElementById('face-capture-btn');
        if (captureBtn) {{
            console.log('[FaceDetection] Triggering auto-capture via button click');
            captureBtn.click();
        }} else {{
            console.warn('[FaceDetection] Capture button not found');
        }}

        // Stop detection after capture
        stopDetection();
    }}

    // Fallback detection (no FaceDetector API)
    // Uses simple brightness/motion analysis as proxy
    function fallbackDetection(video) {{
        // For browsers without FaceDetector, we'll show a simpler flow
        // After 3 seconds of video feed, consider it "ready"
        if (!centeredStartTime) {{
            centeredStartTime = Date.now();
            updateStatus('detected', 'Position your face in the oval');
        }} else if (Date.now() - centeredStartTime > 3000) {{
            updateStatus('centered', 'Hold still...');
            if (Date.now() - centeredStartTime > 5000) {{
                // Check if auto-capture is enabled before starting countdown
                const autoEnabled = document.querySelector('[data-auto-capture]')?.dataset.autoCapture === 'true';
                if (autoEnabled && !countdownInterval) {{
                    startCountdown();
                }}
            }}
        }}
    }}

    // Main detection loop
    async function detectFace() {{
        if (isCapturing) return;

        const video = getVideoElement();
        if (!video || video.readyState < 2) {{
            updateStatus('scanning', 'Initializing camera...');
            return;
        }}

        // Check if auto-capture is enabled
        const autoEnabled = document.querySelector('[data-auto-capture]')?.dataset.autoCapture === 'true';

        if (!faceDetector) {{
            // Fallback mode
            fallbackDetection(video);
            return;
        }}

        try {{
            const faces = await faceDetector.detect(video);

            if (faces.length === 0) {{
                centeredStartTime = null;
                stopCountdown();
                updateStatus('scanning', 'Looking for face...');
            }} else {{
                const face = faces[0];
                const isCentered = isFaceCentered(face, video.videoWidth, video.videoHeight);

                if (isCentered) {{
                    if (!centeredStartTime) {{
                        centeredStartTime = Date.now();
                    }}

                    const holdTime = Date.now() - centeredStartTime;

                    if (holdTime < CENTERED_HOLD_TIME) {{
                        updateStatus('centered', 'Hold still...');
                    }} else if (autoEnabled) {{
                        if (!countdownInterval) {{
                            startCountdown();
                        }}
                    }} else {{
                        updateStatus('ready', 'Ready! Tap to capture');
                    }}
                }} else {{
                    centeredStartTime = null;
                    stopCountdown();
                    updateStatus('detected', 'Center your face in the oval');
                }}
            }}
        }} catch (e) {{
            console.warn('[FaceDetection] Detection error:', e);
            fallbackDetection(video);
        }}
    }}

    // Start detection loop
    async function startDetection() {{
        await initFaceDetector();

        if (detectionInterval) {{
            clearInterval(detectionInterval);
        }}

        detectionInterval = setInterval(detectFace, DETECTION_INTERVAL);
        console.log('[FaceDetection] Detection started');
    }}

    // Stop detection loop
    function stopDetection() {{
        if (detectionInterval) {{
            clearInterval(detectionInterval);
            detectionInterval = null;
        }}
        stopCountdown();
        console.log('[FaceDetection] Detection stopped');
    }}

    // Cleanup on page unload
    window.addEventListener('beforeunload', stopDetection);

    // Start detection when webcam is ready
    const checkWebcam = setInterval(() => {{
        const video = getVideoElement();
        if (video && video.readyState >= 2) {{
            clearInterval(checkWebcam);
            startDetection();
        }}
    }}, 100);

    // Expose stop function globally for cleanup
    window.stopFaceDetection = stopDetection;
    window.resetFaceDetection = () => {{
        isCapturing = false;
        centeredStartTime = null;
        stopCountdown();
        lastStatus = 'scanning';
        startDetection();
    }};
}})();
"""
    return rx.script(script)


def language_selector() -> rx.Component:
    """Language selector with flags and language name."""
    from .state import LanguageState

    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.hstack(
                    rx.cond(
                        LanguageState.is_english,
                        rx.hstack(
                            rx.text("🇺🇸", class_name="text-lg"),
                            rx.text("EN", class_name="text-sm text-slate-300 font-medium"),
                            spacing="1",
                            align="center",
                        ),
                        rx.hstack(
                            rx.text("🇪🇸", class_name="text-lg"),
                            rx.text("ES", class_name="text-sm text-slate-300 font-medium"),
                            spacing="1",
                            align="center",
                        ),
                    ),
                    rx.icon("chevron-down", size=14),
                    spacing="2",
                    align="center",
                ),
                variant="ghost",
                size="2",
                class_name="hover:bg-slate-700/50 transition-colors",
            ),
        ),
        rx.menu.content(
            rx.menu.item(
                rx.hstack(
                    rx.text("🇺🇸", class_name="text-lg"),
                    rx.text("English", class_name="ml-2"),
                    spacing="2",
                ),
                on_click=LanguageState.set_english,
            ),
            rx.menu.item(
                rx.hstack(
                    rx.text("🇪🇸", class_name="text-lg"),
                    rx.text("Español", class_name="ml-2"),
                    spacing="2",
                ),
                on_click=LanguageState.set_spanish,
            ),
            class_name="bg-slate-800 border border-slate-700",
        ),
    )


def nav_link(text: str, href: str, path: rx.Var) -> rx.Component:
    """Navigation link with active state styling."""
    # Check if this link is active (current page)
    # For root path "/" use negative logic: not /docs and not /demo
    if href == "/":
        is_active = ~path.contains("/docs") & ~path.contains("/demo")
    else:
        is_active = path.contains(href)

    return rx.link(
        rx.cond(
            is_active,
            # Active: gradient text like CAPA logo
            rx.text(
                text,
                class_name="bg-gradient-to-r from-orange-400 to-amber-400 bg-clip-text text-transparent font-medium text-sm",
            ),
            # Inactive: default slate color
            rx.text(
                text,
                class_name="text-slate-300 font-medium text-sm",
            ),
        ),
        href=href,
        class_name="px-3 py-2 rounded-lg transition-all no-underline hover:no-underline hover:bg-slate-700/50",
    )


def navbar() -> rx.Component:
    """Navigation bar component with centered menu, language selector and GitHub link."""
    # Get current page path
    current_path = rx.State.router.page.path

    return rx.box(
        rx.hstack(
            # Logo (left)
            rx.link(
                rx.image(
                    src="/logo.png",
                    alt="CAPA",
                    height="20px",
                    class_name="h-5 md:h-6",
                ),
                href="/",
                class_name="no-underline hover:opacity-80 transition-opacity",
            ),
            rx.spacer(),
            # Desktop Navigation Links (centered)
            rx.hstack(
                nav_link("About", "/", current_path),
                nav_link("Documentation", "/docs", current_path),
                nav_link("Demo", "/demo", current_path),
                spacing="1",
                class_name="hidden md:flex",
            ),
            rx.spacer(),
            # Right section: Language selector + GitHub
            rx.hstack(
                language_selector(),
                rx.link(
                    rx.button(
                        rx.icon("github", size=18),
                        variant="ghost",
                        size="2",
                        class_name="hover:bg-slate-700/50 transition-colors",
                    ),
                    href="https://github.com/yarel2l/capa-sdk",
                    is_external=True,
                ),
                spacing="3",
                align="center",
            ),
            align="center",
            width="100%",
            class_name="px-4 md:px-6 py-3 md:py-4 max-w-7xl mx-auto",
        ),
        class_name="bg-slate-900/95 backdrop-blur-sm border-b border-slate-800 sticky top-0 z-50",
        width="100%",
    )


def mobile_nav_item(icon: str, label: str, href: str, path: rx.Var) -> rx.Component:
    """Mobile bottom navigation item with icon and label."""
    # For root path "/" use negative logic: not /docs and not /demo
    if href == "/":
        is_active = ~path.contains("/docs") & ~path.contains("/demo")
    else:
        is_active = path.contains(href)

    return rx.link(
        rx.vstack(
            rx.icon(
                icon,
                size=20,
                class_name=rx.cond(
                    is_active,
                    "text-orange-400",
                    "text-slate-400",
                ),
            ),
            rx.cond(
                is_active,
                rx.text(
                    label,
                    size="1",
                    class_name="bg-gradient-to-r from-orange-400 to-amber-400 bg-clip-text text-transparent font-medium",
                ),
                rx.text(
                    label,
                    size="1",
                    class_name="text-slate-400",
                ),
            ),
            spacing="1",
            align="center",
        ),
        href=href,
        class_name="flex-1 py-2 no-underline hover:no-underline transition-all",
    )


def mobile_bottom_nav() -> rx.Component:
    """Mobile bottom navigation bar - visible only on mobile devices."""
    current_path = rx.State.router.page.path

    return rx.box(
        rx.hstack(
            mobile_nav_item("info", "About", "/", current_path),
            mobile_nav_item("book-open", "Docs", "/docs", current_path),
            mobile_nav_item("play", "Demo", "/demo", current_path),
            width="100%",
            justify="between",
            align="center",
            class_name="max-w-md mx-auto px-8",
        ),
        class_name="md:hidden fixed bottom-0 left-0 right-0 bg-slate-900/95 backdrop-blur-sm border-t border-slate-800 z-50 pb-safe",
        width="100%",
    )


def animated_face_mesh() -> rx.Component:
    """Face mesh image for hero section."""
    return rx.image(
        src="/face.png",
        alt="Face mesh",
        class_name="w-24 h-24 md:w-32 md:h-32 lg:w-40 lg:h-40 mx-auto mb-4 opacity-90",
    )


def hero_section(
    title: str,
    subtitle: str,
    description: str,
    show_animation: bool = True,
    use_logo_image: bool = False,
) -> rx.Component:
    """Hero section with gradient background and optional animated face mesh - responsive."""
    # Build content list
    content = []

    # Add animated face mesh if enabled
    if show_animation:
        content.append(animated_face_mesh())

    # Add title (logo image or text)
    if use_logo_image:
        content.append(
            rx.image(
                src="/logo.png",
                alt=title,
                class_name="h-6 md:h-8 lg:h-10 mx-auto",
            )
        )
    else:
        content.append(
            rx.heading(
                title,
                size="9",
                weight="bold",
                align="center",
                class_name="bg-gradient-to-r from-orange-400 via-amber-400 to-yellow-400 bg-clip-text text-transparent text-4xl md:text-5xl lg:text-6xl",
            )
        )

    return rx.box(
        rx.vstack(
            *content,
            rx.text(
                subtitle,
                size="6",
                align="center",
                weight="medium",
                class_name="text-slate-300 text-lg md:text-xl lg:text-2xl",
            ),
            rx.text(
                description,
                size="4",
                align="center",
                class_name="text-slate-400 max-w-2xl text-sm md:text-base px-4",
            ),
            spacing="4",
            align="center",
            class_name="py-10 md:py-16 px-4 md:px-8",
        ),
        width="100%",
        class_name="bg-gradient-to-b from-slate-900 to-slate-800",
    )


def stat_card(value: str, label: str, icon: str = "bar-chart") -> rx.Component:
    """Statistics card with icon."""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=28, class_name="text-orange-400"),
                class_name="p-3 bg-orange-500/10 rounded-xl mb-2",
            ),
            rx.heading(value, size="7", weight="bold", class_name="text-white"),
            rx.text(label, size="2", class_name="text-slate-400"),
            spacing="1",
            align="center",
        ),
        class_name="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 hover:border-orange-500/50 transition-all duration-300 min-w-[150px]",
    )


def feature_card(title: str, description: str, icon: str = "star") -> rx.Component:
    """Feature card with icon and description."""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=24, class_name="text-white"),
                class_name="p-3 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl",
            ),
            rx.heading(title, size="4", weight="bold", class_name="text-white"),
            rx.text(description, size="2", class_name="text-slate-400"),
            spacing="3",
            align="start",
        ),
        class_name="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 hover:border-orange-500/50 hover:-translate-y-1 transition-all duration-300",
    )


def metric_card(title: str, value: str, subtitle: Optional[str] = None) -> rx.Component:
    """Display a metric card."""
    return rx.box(
        rx.vstack(
            rx.text(title, size="2", weight="medium", class_name="text-slate-400"),
            rx.heading(value, size="5", weight="bold", class_name="text-white"),
            rx.cond(
                subtitle,
                rx.text(subtitle, size="1", class_name="text-slate-500"),
                rx.fragment()
            ),
            align="start",
            spacing="1",
        ),
        class_name="bg-slate-800/30 border border-slate-700/30 rounded-lg p-4 w-full",
    )


def confidence_badge(confidence: float) -> rx.Component:
    """Display confidence level with color coding."""
    color = rx.cond(
        confidence >= 0.8,
        "green",
        rx.cond(confidence >= 0.6, "amber", "red")
    )

    return rx.badge(
        f"{confidence * 100:.1f}%",
        color_scheme=color,
        size="2",
    )


def confidence_meter(value: rx.Var, label: str = "Confidence") -> rx.Component:
    """Visual confidence meter/progress bar.

    Values are clamped to 0-100% range for safety.
    Displays percentage rounded to nearest integer.
    """
    # Clamp value to valid 0-1 range
    clamped_value = rx.cond(value > 1.0, 1.0, rx.cond(value < 0.0, 0.0, value))

    color = rx.cond(
        clamped_value >= 0.8,
        "green",
        rx.cond(clamped_value >= 0.6, "amber", "red")
    )

    # Calculate percentage as integer (0-100)
    percentage_int = (clamped_value * 100).to(int)

    return rx.vstack(
        rx.hstack(
            rx.text(label, size="2", weight="medium", class_name="text-slate-300"),
            rx.spacer(),
            rx.text(percentage_int.to_string() + "%", size="2", weight="bold", class_name="text-white"),
            width="100%",
        ),
        rx.progress(value=percentage_int, color_scheme=color, width="100%", class_name="h-2"),
        width="100%",
        spacing="1",
        class_name="p-3 bg-slate-800/30 rounded-lg",
    )


def result_section(title: str, data: Dict[str, Any]) -> rx.Component:
    """Display a results section."""
    return rx.box(
        rx.vstack(
            rx.heading(title, size="5", class_name="text-white"),
            rx.divider(class_name="border-slate-700"),
            rx.foreach(
                list(data.keys()),
                lambda key: rx.hstack(
                    rx.text(f"{key}:", weight="bold", width="200px", class_name="text-slate-400"),
                    rx.text(str(data[key]), class_name="text-white"),
                    width="100%",
                    justify="between",
                )
            ),
            align="start",
            spacing="2",
            width="100%",
        ),
        class_name="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 w-full",
    )


def loading_spinner(text: str = "Processing...") -> rx.Component:
    """Display loading spinner."""
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text(text, size="4", class_name="text-slate-400"),
            spacing="3",
        ),
        width="100%",
        class_name="py-16",
    )


def error_alert(message: str) -> rx.Component:
    """Display error alert."""
    return rx.callout(
        message,
        icon="triangle_alert",
        color_scheme="red",
        role="alert",
    )


def success_alert(message: str) -> rx.Component:
    """Display success alert."""
    return rx.callout(
        message,
        icon="check",
        color_scheme="green",
        role="status",
    )


def info_card(title: str, description: str, icon: str = "info") -> rx.Component:
    """Display an info card."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=24, class_name="text-orange-400"),
                rx.heading(title, size="4", weight="bold", class_name="text-white"),
                align="center",
                spacing="2",
            ),
            rx.text(description, size="2", class_name="text-slate-400"),
            align="start",
            spacing="2",
        ),
        class_name="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 w-full",
    )


def file_upload_zone(upload_id: str, multiple: bool = False, text: str = "Select Image") -> rx.Component:
    """File upload zone component."""
    return rx.upload(
        rx.vstack(
            rx.box(
                rx.icon("upload", size=32, class_name="text-orange-400"),
                class_name="p-4 bg-orange-500/10 rounded-full mb-2",
            ),
            rx.button(
                text,
                color_scheme="orange",
                size="2",
                class_name="px-6",
            ),
            rx.text(
                "or drag and drop here",
                size="2",
                class_name="text-slate-500",
            ),
            spacing="3",
            align="center",
        ),
        id=upload_id,
        accept={"image/*": []},
        multiple=multiple,
        max_files=5 if multiple else 1,
        class_name="border-2 border-dashed border-slate-600 hover:border-orange-500 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl p-8 transition-all duration-300 cursor-pointer",
    )


def image_preview(
    image_src: rx.Var,
    has_image: rx.Var,
    on_clear,
    alt: str = "Preview"
) -> rx.Component:
    """Image preview component with clear button."""
    return rx.cond(
        has_image,
        rx.box(
            rx.vstack(
                rx.box(
                    rx.image(
                        src=image_src,
                        alt=alt,
                        class_name="max-h-64 w-auto rounded-lg object-contain",
                    ),
                    class_name="relative bg-slate-800/50 rounded-lg p-4 flex items-center justify-center",
                ),
                rx.hstack(
                    rx.text("Image loaded", size="2", class_name="text-green-400"),
                    rx.button(
                        rx.hstack(
                            rx.icon("x", size=14),
                            rx.text("Clear"),
                            spacing="1",
                        ),
                        on_click=on_clear,
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        class_name="hover:bg-red-500/20",
                    ),
                    justify="between",
                    width="100%",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            class_name="border border-slate-700 rounded-xl p-4 bg-slate-800/30",
        ),
    )


def results_grid(results: Dict[str, Any]) -> rx.Component:
    """Display results in a grid layout."""
    return rx.grid(
        rx.foreach(
            list(results.keys()),
            lambda key: metric_card(
                key.replace("_", " ").title(),
                str(results[key]),
            )
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def canon_table_row(canon: Dict[str, Any]) -> rx.Component:
    """Single row for canon measurements table."""
    return rx.table.row(
        rx.table.cell(rx.text(canon["name"], weight="medium", class_name="text-white")),
        rx.table.cell(rx.code(canon["measured"], class_name="text-orange-300 bg-slate-800 px-2 py-0.5 rounded")),
        rx.table.cell(rx.text(canon["deviation"], class_name="text-slate-300")),
        rx.table.cell(
            rx.cond(
                canon["in_range"],
                rx.badge("In Range", color_scheme="green"),
                rx.badge("Out of Range", color_scheme="red"),
            )
        ),
        rx.table.cell(rx.text(canon["confidence"], class_name="text-slate-400")),
        class_name="border-b border-slate-700/50 hover:bg-slate-800/30 transition-colors",
    )


def canon_table(canons: List[Dict[str, Any]]) -> rx.Component:
    """Formatted table for neoclassical canons."""
    return rx.vstack(
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Canon", class_name="text-slate-300 font-semibold"),
                        rx.table.column_header_cell("Measured", class_name="text-slate-300 font-semibold"),
                        rx.table.column_header_cell("Deviation", class_name="text-slate-300 font-semibold"),
                        rx.table.column_header_cell("Status", class_name="text-slate-300 font-semibold"),
                        rx.table.column_header_cell("Confidence", class_name="text-slate-300 font-semibold"),
                        class_name="bg-slate-800/50 border-b border-slate-700",
                    ),
                ),
                rx.table.body(
                    rx.foreach(canons, canon_table_row)
                ),
                width="100%",
            ),
            class_name="bg-slate-800/30 border border-slate-700/50 rounded-xl overflow-hidden w-full",
        ),
        # Status legend
        rx.hstack(
            rx.hstack(
                rx.badge("In Range", color_scheme="green", size="1"),
                rx.text("≤10% deviation", size="1", class_name="text-slate-500"),
                spacing="1",
                align="center",
            ),
            rx.hstack(
                rx.badge("Out of Range", color_scheme="red", size="1"),
                rx.text(">10% deviation", size="1", class_name="text-slate-500"),
                spacing="1",
                align="center",
            ),
            spacing="4",
            class_name="mt-2",
        ),
        width="100%",
        spacing="2",
    )


def trait_row(trait: Dict[str, str]) -> rx.Component:
    """Row for personality traits table."""
    return rx.table.row(
        rx.table.cell(rx.text(trait["trait"], weight="medium", class_name="text-slate-300")),
        rx.table.cell(rx.badge(trait["value"], color_scheme="orange")),
        class_name="border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors",
    )


def personality_table(traits: List[Dict[str, str]]) -> rx.Component:
    """Table for personality traits."""
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Trait", class_name="text-slate-300 font-semibold"),
                    rx.table.column_header_cell("Value", class_name="text-slate-300 font-semibold"),
                    class_name="bg-slate-800/50 border-b border-slate-700",
                ),
            ),
            rx.table.body(
                rx.foreach(traits, trait_row)
            ),
            width="100%",
        ),
        class_name="bg-slate-800/30 border border-slate-700/50 rounded-xl overflow-hidden",
    )


def detail_row(item: Dict[str, str]) -> rx.Component:
    """Row for detail tables."""
    return rx.table.row(
        rx.table.cell(rx.text(item["metric"], weight="medium", class_name="text-slate-300")),
        rx.table.cell(rx.code(item["value"], class_name="text-orange-300 bg-slate-800 px-2 py-0.5 rounded")),
        class_name="border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors",
    )


def details_table(items: List[Dict[str, str]]) -> rx.Component:
    """Table for detailed metrics."""
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Metric", class_name="text-slate-300 font-semibold"),
                    rx.table.column_header_cell("Value", class_name="text-slate-300 font-semibold"),
                    class_name="bg-slate-800/50 border-b border-slate-700",
                ),
            ),
            rx.table.body(
                rx.foreach(items, detail_row)
            ),
            width="100%",
        ),
        class_name="bg-slate-800/30 border border-slate-700/50 rounded-xl overflow-hidden w-full",
    )


def doc_section(title: str, content: str) -> rx.Component:
    """Documentation section with markdown content."""
    return rx.vstack(
        rx.heading(title, size="6", weight="bold", class_name="text-white"),
        rx.box(
            rx.markdown(
                content,
                class_name="prose prose-invert prose-slate max-w-none prose-headings:text-white prose-p:text-slate-300 prose-li:text-slate-300 prose-strong:text-white prose-code:text-orange-300 prose-code:bg-slate-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-slate-800 prose-pre:border prose-pre:border-slate-700 prose-a:text-orange-400 prose-table:border-slate-700 prose-th:border-slate-700 prose-td:border-slate-700",
            ),
            class_name="w-full",
        ),
        width="100%",
        align="start",
        spacing="3",
    )


def paper_card(title: str, description: str, key_findings: str = "") -> rx.Component:
    """Card for scientific papers."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("file-text", size=20, class_name="text-orange-400"),
                rx.text(title, weight="bold", size="3", class_name="text-white"),
                align="center",
                spacing="2",
            ),
            rx.text(description, size="2", class_name="text-slate-400"),
            rx.cond(
                key_findings != "",
                rx.box(
                    rx.text("Key Findings:", size="2", weight="bold", class_name="text-slate-300"),
                    rx.text(key_findings, size="2", class_name="text-slate-500"),
                    class_name="pt-2",
                ),
                rx.fragment(),
            ),
            align="start",
            spacing="2",
        ),
        class_name="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 w-full hover:border-orange-500/30 transition-colors",
    )


def api_method_card(name: str, signature: str, description: str) -> rx.Component:
    """Card for API method documentation."""
    return rx.box(
        rx.vstack(
            rx.code(name, size="3", weight="bold", class_name="text-orange-400 bg-transparent"),
            rx.box(
                rx.code(signature, size="2", class_name="text-slate-300 bg-slate-800 px-3 py-2 rounded-lg block whitespace-pre-wrap"),
                width="100%",
            ),
            rx.text(description, size="2", class_name="text-slate-400"),
            align="start",
            spacing="3",
            width="100%",
        ),
        class_name="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 w-full hover:border-orange-500/30 transition-colors",
    )


def section_header(title: str, subtitle: str = "") -> rx.Component:
    """Section header with optional subtitle."""
    return rx.vstack(
        rx.heading(title, size="7", weight="bold", class_name="text-white"),
        rx.cond(
            subtitle != "",
            rx.text(subtitle, size="3", class_name="text-slate-400"),
            rx.fragment(),
        ),
        align="start",
        spacing="1",
        width="100%",
        class_name="mb-4",
    )


def analysis_mode_card(mode: str, description: str, color: str = "orange") -> rx.Component:
    """Card for analysis mode."""
    return rx.box(
        rx.vstack(
            rx.badge(mode, color_scheme=color, size="2"),
            rx.text(description, size="2", class_name="text-slate-400"),
            align="start",
            spacing="2",
        ),
        class_name="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 min-h-[80px] hover:border-orange-500/30 transition-colors",
    )


def quick_link_button(text: str, href: str, icon: str = "arrow-right") -> rx.Component:
    """Quick link button with icon."""
    return rx.link(
        rx.button(
            rx.hstack(
                rx.text(text),
                rx.icon(icon, size=16),
                spacing="2",
                align="center",
            ),
            color_scheme="orange",
            size="3",
            class_name="hover:scale-105 transition-transform",
        ),
        href=href,
        class_name="no-underline",
    )


def docs_sidebar_item(
    label: str,
    section: str,
    icon: str,
    active_section: rx.Var,
    on_click
) -> rx.Component:
    """Sidebar item for documentation navigation."""
    is_active = active_section == section

    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=16, class_name=rx.cond(is_active, "text-orange-400", "text-slate-500")),
                class_name="w-5 flex-shrink-0",
            ),
            rx.text(
                label,
                size="2",
                weight=rx.cond(is_active, "medium", "regular"),
                class_name=rx.cond(is_active, "text-white", "text-slate-400 hover:text-slate-300"),
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        on_click=lambda: on_click(section),
        class_name=rx.cond(
            is_active,
            "px-4 py-2.5 rounded-md bg-orange-500/10 border-l-2 border-orange-400 cursor-pointer transition-all ml-1",
            "px-4 py-2.5 rounded-md hover:bg-slate-800/30 cursor-pointer transition-all border-l-2 border-transparent ml-1",
        ),
    )


def docs_sidebar_section(title: str, children: List[rx.Component]) -> rx.Component:
    """Sidebar section with title and items."""
    return rx.vstack(
        rx.text(
            title,
            size="1",
            weight="bold",
            class_name="text-slate-500 uppercase tracking-widest px-4 pt-2 pb-2 text-[11px]",
        ),
        rx.vstack(
            *children,
            spacing="0",
            width="100%",
        ),
        align="start",
        spacing="1",
        width="100%",
    )


def docs_sidebar(active_section: rx.Var, on_section_change) -> rx.Component:
    """Nextra-style documentation sidebar - responsive."""
    from .state import DocsState

    sidebar_content = rx.vstack(
        # Getting Started section
        docs_sidebar_section(
            "Getting Started",
            [
                docs_sidebar_item("Introduction", "intro", "home", active_section, on_section_change),
                docs_sidebar_item("Installation", "getting_started", "download", active_section, on_section_change),
                docs_sidebar_item("Quick Start", "quick_start", "rocket", active_section, on_section_change),
            ],
        ),
        # API Reference section
        docs_sidebar_section(
            "API Reference",
            [
                docs_sidebar_item("Core Classes", "api_core", "box", active_section, on_section_change),
                docs_sidebar_item("Configuration", "api_config", "settings", active_section, on_section_change),
                docs_sidebar_item("Result Types", "api_results", "file-json", active_section, on_section_change),
                docs_sidebar_item("Modules", "api_modules", "layers", active_section, on_section_change),
            ],
        ),
        # Guides section
        docs_sidebar_section(
            "Guides",
            [
                docs_sidebar_item("Configuration", "configuration", "sliders-horizontal", active_section, on_section_change),
                docs_sidebar_item("Examples", "examples", "code", active_section, on_section_change),
            ],
        ),
        # Science section
        docs_sidebar_section(
            "Science",
            [
                docs_sidebar_item("Scientific Foundation", "scientific", "flask-conical", active_section, on_section_change),
                docs_sidebar_item("Research Papers", "papers", "book-open", active_section, on_section_change),
            ],
        ),
        spacing="6",
        align="start",
        width="100%",
        class_name="py-6 px-3",
    )

    return rx.box(
        sidebar_content,
        class_name="hidden md:block w-60 lg:w-72 min-w-[240px] lg:min-w-[288px] h-[calc(100vh-57px)] overflow-y-auto border-r border-slate-800/80 bg-slate-900/30 sticky top-[57px]",
    )


def docs_content_wrapper(content: rx.Component) -> rx.Component:
    """Wrapper for documentation content with proper styling - responsive and centered."""
    return rx.box(
        rx.box(
            content,
            class_name="prose prose-invert prose-slate max-w-none prose-headings:text-white prose-p:text-slate-300 prose-li:text-slate-300 prose-strong:text-white prose-code:text-orange-300 prose-code:bg-slate-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none prose-pre:bg-slate-800 prose-pre:border prose-pre:border-slate-700 prose-pre:overflow-x-auto prose-a:text-orange-400 prose-a:no-underline hover:prose-a:underline prose-table:border-slate-700 prose-th:border-slate-700 prose-td:border-slate-700 prose-th:text-slate-300 prose-td:text-slate-400 prose-hr:border-slate-700 prose-table:text-sm prose-table:overflow-x-auto",
        ),
        class_name="flex-1 p-4 md:p-6 lg:p-8 max-w-4xl mx-auto w-full",
    )


def docs_mobile_nav(active_section: rx.Var, on_section_change) -> rx.Component:
    """Mobile navigation for documentation pages with searchable select."""
    # Section options with readable labels
    sections = [
        ("intro", "Introduction"),
        ("getting_started", "Installation"),
        ("quick_start", "Quick Start"),
        ("api_core", "Core Classes"),
        ("api_config", "Configuration (API)"),
        ("api_results", "Result Types"),
        ("api_modules", "Modules"),
        ("configuration", "Configuration Guide"),
        ("examples", "Examples"),
        ("scientific", "Scientific Foundation"),
        ("papers", "Research Papers"),
    ]

    return rx.box(
        rx.select.root(
            rx.select.trigger(
                placeholder="Select section...",
                class_name="w-full",
            ),
            rx.select.content(
                rx.select.group(
                    rx.select.label("Getting Started"),
                    rx.select.item("Introduction", value="intro"),
                    rx.select.item("Installation", value="getting_started"),
                    rx.select.item("Quick Start", value="quick_start"),
                ),
                rx.select.separator(),
                rx.select.group(
                    rx.select.label("API Reference"),
                    rx.select.item("Core Classes", value="api_core"),
                    rx.select.item("Configuration", value="api_config"),
                    rx.select.item("Result Types", value="api_results"),
                    rx.select.item("Modules", value="api_modules"),
                ),
                rx.select.separator(),
                rx.select.group(
                    rx.select.label("Guides"),
                    rx.select.item("Configuration Guide", value="configuration"),
                    rx.select.item("Examples", value="examples"),
                ),
                rx.select.separator(),
                rx.select.group(
                    rx.select.label("Science"),
                    rx.select.item("Scientific Foundation", value="scientific"),
                    rx.select.item("Research Papers", value="papers"),
                ),
            ),
            value=active_section,
            on_change=on_section_change,
            size="3",
        ),
        class_name="md:hidden p-4 border-b border-slate-800 bg-slate-900/50",
    )


# =============================================================================
# CAPTURE ANALYSIS COMPONENTS
# =============================================================================

def capture_mode_selector(
    is_webcam: rx.Var,
    on_webcam_click,
    on_upload_click
) -> rx.Component:
    """Toggle between Camera and Gallery capture modes - compact tabs style."""
    return rx.box(
        # Tabs container with background
        rx.hstack(
            # Camera tab
            rx.box(
                rx.hstack(
                    rx.icon(
                        "camera",
                        size=16,
                        class_name=rx.cond(
                            is_webcam,
                            "text-white",
                            "text-slate-400"
                        ),
                    ),
                    rx.text(
                        "Camera",
                        weight="medium",
                        size="2",
                        class_name=rx.cond(
                            is_webcam,
                            "text-white",
                            "text-slate-400"
                        ),
                    ),
                    spacing="2",
                    align="center",
                ),
                on_click=on_webcam_click,
                class_name=rx.cond(
                    is_webcam,
                    "cursor-pointer px-4 py-2 rounded-md bg-gradient-to-br from-orange-500 to-amber-500 shadow-sm transition-all duration-200",
                    "cursor-pointer px-4 py-2 rounded-md hover:bg-slate-700/50 transition-all duration-200"
                ),
            ),
            # Gallery tab
            rx.box(
                rx.hstack(
                    rx.icon(
                        "image",
                        size=16,
                        class_name=rx.cond(
                            ~is_webcam,
                            "text-white",
                            "text-slate-400"
                        ),
                    ),
                    rx.text(
                        "Gallery",
                        weight="medium",
                        size="2",
                        class_name=rx.cond(
                            ~is_webcam,
                            "text-white",
                            "text-slate-400"
                        ),
                    ),
                    spacing="2",
                    align="center",
                ),
                on_click=on_upload_click,
                class_name=rx.cond(
                    ~is_webcam,
                    "cursor-pointer px-4 py-2 rounded-md bg-gradient-to-br from-orange-500 to-amber-500 shadow-sm transition-all duration-200",
                    "cursor-pointer px-4 py-2 rounded-md hover:bg-slate-700/50 transition-all duration-200"
                ),
            ),
            spacing="1",
            class_name="p-1",
        ),
        class_name="inline-flex bg-slate-800/80 rounded-lg border border-slate-700/50",
    )


def webcam_capture_zone(
    webcam_component,
    on_capture,
    face_status: rx.Var = None,
    face_message: rx.Var = None,
    button_class: rx.Var = None,
    stage_title: rx.Var = None,
) -> rx.Component:
    """Webcam preview with face positioning guide, detection feedback, and animated capture button.
    Auto-capture is always enabled by default.
    """

    # Default values if not provided
    if face_status is None:
        face_status = rx.Var.create("scanning")
    if face_message is None:
        face_message = rx.Var.create("Position your face in the oval")
    if button_class is None:
        button_class = rx.Var.create("bg-gradient-to-br from-slate-500 to-slate-600")
    if stage_title is None:
        stage_title = rx.Var.create("Frontal Photo")

    # Dynamic oval guide color based on status
    oval_class = rx.cond(
        face_status == "ready",
        "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-64 border-3 border-green-400 rounded-[50%] pointer-events-none animate-pulse shadow-lg shadow-green-500/30",
        rx.cond(
            face_status == "centered",
            "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-64 border-2 border-amber-400 rounded-[50%] pointer-events-none",
            rx.cond(
                face_status == "detected",
                "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-64 border-2 border-orange-400 rounded-[50%] pointer-events-none",
                "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-64 border-2 border-dashed border-slate-500/60 rounded-[50%] pointer-events-none"
            )
        )
    )

    # Status icon based on detection state
    status_icon = rx.cond(
        face_status == "ready",
        rx.icon("circle-check", size=16, class_name="text-green-400"),
        rx.cond(
            face_status == "centered",
            rx.icon("scan-face", size=16, class_name="text-amber-400 animate-pulse"),
            rx.cond(
                face_status == "detected",
                rx.icon("user", size=16, class_name="text-orange-400"),
                rx.icon("scan", size=16, class_name="text-slate-500 animate-spin")
            )
        )
    )

    # Status message color
    status_class = rx.cond(
        face_status == "ready",
        "text-green-400 font-medium",
        rx.cond(
            face_status == "centered",
            "text-amber-400",
            rx.cond(
                face_status == "detected",
                "text-orange-400",
                "text-slate-500"
            )
        )
    )

    # Button outer styling based on status
    button_outer_class = rx.cond(
        face_status == "ready",
        "p-4 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full shadow-lg shadow-green-500/50 transition-all duration-300",
        rx.cond(
            face_status == "centered",
            "p-4 bg-gradient-to-br from-amber-500 to-orange-500 rounded-full shadow-lg shadow-amber-500/30 transition-all duration-300",
            rx.cond(
                face_status == "detected",
                "p-4 bg-gradient-to-br from-orange-500 to-amber-500 rounded-full shadow-lg shadow-orange-500/30 transition-all duration-300",
                # Default (scanning): Orange primary color
                "p-4 bg-gradient-to-br from-orange-500 to-amber-500 rounded-full shadow-lg shadow-orange-500/30 transition-all duration-300"
            )
        )
    )

    # Button content based on status - spinning ring for scanning, camera icon for ready
    button_content = rx.cond(
        face_status == "ready",
        # Ready: Show camera icon
        rx.icon("camera", size=32, class_name="text-white"),
        rx.cond(
            face_status == "capturing",
            # Capturing: Spinning loader
            rx.icon("loader", size=32, class_name="text-white animate-spin"),
            # Default/scanning/detected/centered: Spinning ring (like scan icon)
            rx.box(
                # Outer ring that spins
                rx.box(
                    class_name="w-8 h-8 rounded-full border-2 border-white/30 border-t-white animate-spin"
                ),
                class_name="relative flex items-center justify-center",
            )
        )
    )

    return rx.vstack(
        # Stage title
        rx.hstack(
            rx.text(stage_title, size="3", weight="medium", class_name="text-white"),
            spacing="2",
            align="center",
            class_name="mb-2",
        ),
        # Webcam container with face guide overlay
        rx.box(
            # Webcam feed (mirroring is handled by the webcam component's mirrored prop)
            webcam_component,
            # Face positioning guide overlay
            rx.box(
                # Oval face guide (dynamic color)
                rx.box(class_name=oval_class),
                # Shoulders guide line
                rx.box(
                    class_name="absolute bottom-8 left-1/2 -translate-x-1/2 w-72 h-0.5 bg-gradient-to-r from-transparent via-orange-400/40 to-transparent pointer-events-none",
                ),
                # Corner markers for framing
                rx.box(class_name="absolute top-4 left-4 w-6 h-6 border-l-2 border-t-2 border-orange-400/50 pointer-events-none"),
                rx.box(class_name="absolute top-4 right-4 w-6 h-6 border-r-2 border-t-2 border-orange-400/50 pointer-events-none"),
                rx.box(class_name="absolute bottom-4 left-4 w-6 h-6 border-l-2 border-b-2 border-orange-400/50 pointer-events-none"),
                rx.box(class_name="absolute bottom-4 right-4 w-6 h-6 border-r-2 border-b-2 border-orange-400/50 pointer-events-none"),
                class_name="absolute inset-0 pointer-events-none",
            ),
            # Hidden data attribute for JS - auto-capture always enabled
            rx.el.div(
                **{"data-auto-capture": "true"},
                class_name="hidden"
            ),
            class_name="relative bg-slate-800/50 rounded-xl overflow-hidden border-2 border-slate-700 w-full max-w-md mx-auto",
        ),
        # Status message
        rx.box(
            rx.text(
                face_message,
                size="2",
                class_name=status_class,
            ),
            class_name="mt-2 transition-all duration-300",
        ),
        # Capture button (animated based on status)
        rx.box(
            rx.box(
                button_content,
                class_name=button_outer_class,
            ),
            id="face-capture-btn",
            on_click=on_capture,
            class_name="mt-3 cursor-pointer hover:scale-110 transition-transform duration-300 active:scale-95",
        ),
        spacing="1",
        align="center",
        width="100%",
        class_name="py-2",
    )


def capture_photos_column(
    frontal_image: rx.Var,
    profile_image: rx.Var = None,
    image_src: rx.Var = None,
) -> rx.Component:
    """Left column with captured photos displayed side by side."""
    # Use rx.cond to select the image source
    frontal_src = rx.cond(
        frontal_image,
        frontal_image,
        image_src,
    ) if image_src else frontal_image

    return rx.hstack(
        # Frontal photo (mirrored display)
        rx.box(
            rx.box(
                rx.image(
                    src=frontal_src,
                    alt="Frontal photo",
                    class_name="w-32 h-40 object-cover rounded",
                    style={"transform": "scaleX(-1)"},  # Mirror frontal for natural look
                ),
                class_name="p-1 bg-white/10 rounded shadow-inner",
            ),
            rx.text(
                "FRONTAL",
                size="1",
                class_name="text-slate-500 uppercase tracking-widest mt-1 text-center",
            ),
            class_name="flex flex-col items-center",
        ),
        # Profile photo (optional, not mirrored)
        rx.cond(
            profile_image,
            rx.box(
                rx.box(
                    rx.image(
                        src=profile_image,
                        alt="Profile photo",
                        class_name="w-32 h-40 object-cover rounded",
                    ),
                    class_name="p-1 bg-white/10 rounded shadow-inner",
                ),
                rx.text(
                    "PROFILE",
                    size="1",
                    class_name="text-slate-500 uppercase tracking-widest mt-1 text-center",
                ),
                class_name="flex flex-col items-center",
            ),
            rx.fragment(),
        ),
        spacing="4",
        align="start",
    )


def capture_actions_column(
    on_retake,
    on_analyze,
    is_processing: rx.Var,
    has_results: rx.Var,
    results_component: rx.Component = None,
) -> rx.Component:
    """Right column with action buttons and results."""
    return rx.vstack(
        # Action buttons
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon("rotate-ccw", size=16),
                    rx.text("Start Over"),
                    spacing="2",
                ),
                on_click=on_retake,
                variant="outline",
                color_scheme="gray",
                size="3",
                disabled=is_processing,
                class_name="hover:-translate-y-0.5 transition-transform duration-200",
            ),
            rx.button(
                rx.hstack(
                    rx.icon("zap", size=16),
                    rx.text("Analyze"),
                    spacing="2",
                ),
                on_click=on_analyze,
                color_scheme="orange",
                size="3",
                disabled=is_processing,
                class_name="hover:-translate-y-0.5 transition-transform duration-200 hover:shadow-lg hover:shadow-orange-500/25",
            ),
            spacing="3",
        ),
        # Results section (shown after analysis)
        rx.cond(
            has_results,
            results_component if results_component else rx.fragment(),
            rx.fragment(),
        ),
        spacing="4",
        align="start",
        width="100%",
    )


def capture_preview(
    image_src: rx.Var,
    on_retake,
    on_analyze,
    is_processing: rx.Var,
    frontal_image: rx.Var = None,
    profile_image: rx.Var = None,
    on_retake_frontal = None,
    on_retake_profile = None,
) -> rx.Component:
    """Preview captured images - DEPRECATED: Use capture_photos_column and capture_actions_column instead."""
    # Use rx.cond to select the image source
    frontal_src = rx.cond(
        frontal_image,
        frontal_image,
        image_src,
    )

    return rx.hstack(
        # Left side - Photos side by side
        rx.hstack(
            # Frontal photo (mirrored display)
            rx.box(
                rx.box(
                    rx.image(
                        src=frontal_src,
                        alt="Frontal photo",
                        class_name="w-32 h-40 object-cover rounded",
                        style={"transform": "scaleX(-1)"},  # Mirror frontal for natural look
                    ),
                    class_name="p-1 bg-white/10 rounded shadow-inner",
                ),
                rx.text(
                    "FRONTAL",
                    size="1",
                    class_name="text-slate-500 uppercase tracking-widest mt-1 text-center",
                ),
                class_name="flex flex-col items-center",
            ),
            # Profile photo (optional, not mirrored)
            rx.cond(
                profile_image,
                rx.box(
                    rx.box(
                        rx.image(
                            src=profile_image,
                            alt="Profile photo",
                            class_name="w-32 h-40 object-cover rounded",
                        ),
                        class_name="p-1 bg-white/10 rounded shadow-inner",
                    ),
                    rx.text(
                        "PROFILE",
                        size="1",
                        class_name="text-slate-500 uppercase tracking-widest mt-1 text-center",
                    ),
                    class_name="flex flex-col items-center",
                ),
                rx.fragment(),
            ),
            spacing="4",
            align="start",
        ),
        spacing="6",
        align="start",
        width="100%",
    )


def upload_zone_enhanced(upload_id: str, on_upload) -> rx.Component:
    """Enhanced upload zone with elegant styling matching camera aesthetic."""
    return rx.upload(
        rx.vstack(
            rx.box(
                rx.icon("image-plus", size=48, class_name="text-orange-400"),
                class_name="p-6 bg-orange-500/10 rounded-full mb-4",
            ),
            rx.heading("Select from Gallery", size="4", class_name="text-white"),
            rx.text(
                "Choose a frontal photo for best results",
                size="2",
                class_name="text-slate-400 text-center",
            ),
            rx.button(
                "Browse Files",
                color_scheme="orange",
                size="3",
                variant="outline",
                class_name="mt-4",
            ),
            rx.text(
                "or drag and drop here",
                size="1",
                class_name="text-slate-500 mt-2",
            ),
            spacing="2",
            align="center",
        ),
        id=upload_id,
        accept={"image/*": []},
        max_files=1,
        on_drop=on_upload,
        class_name="border-2 border-dashed border-slate-600 hover:border-orange-500 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl p-12 transition-all duration-300 cursor-pointer min-h-[300px] flex items-center justify-center w-full",
    )


# =============================================================================
# DEMO PAGE RESULT SECTION COMPONENTS
# =============================================================================

def demo_result_section(
    title: str,
    icon: str,
    children: rx.Component,
    badge_text: Optional[str] = None,
    badge_color: str = "orange",
) -> rx.Component:
    """Generic result section container for demo page."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon, size=20, class_name="text-orange-400"),
                    class_name="p-2 bg-orange-500/10 rounded-lg shrink-0",
                ),
                rx.heading(title, size="4", weight="bold", class_name="text-white"),
                rx.cond(
                    badge_text is not None and badge_text != "",
                    rx.badge(badge_text, color_scheme=badge_color, size="1"),
                    rx.fragment(),
                ),
                spacing="3",
                align="center",
                width="100%",
            ),
            children,
            spacing="4",
            align="start",
            width="100%",
        ),
        class_name="bg-slate-800/30 border border-slate-700/50 rounded-xl p-5 w-full overflow-hidden",
    )


def wd_result_card(
    wd_value: rx.Var,
    classification: rx.Var,
    confidence: rx.Var,
    confidence_value: rx.Var,
    bizygomatic: rx.Var,
    bigonial: rx.Var,
    personality_traits: rx.Var,
) -> rx.Component:
    """WD Analysis result card for demo page."""
    return demo_result_section(
        title="WD Analysis",
        icon="users",
        badge_text="Personality",
        badge_color="blue",
        children=rx.vstack(
            # Main metrics row
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("WD Value", size="2", class_name="text-slate-400"),
                        rx.heading(wd_value, size="5", class_name="text-orange-400 font-mono"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Classification", size="2", class_name="text-slate-400"),
                        rx.badge(classification, color_scheme="orange", size="2"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Confidence meter
            confidence_meter(confidence_value, "Analysis Confidence"),
            # Measurements
            rx.box(
                rx.vstack(
                    rx.text("Facial Measurements", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Bizygomatic", size="1", class_name="text-slate-500"),
                            rx.code(bizygomatic, class_name="text-orange-300 bg-slate-800 px-2 py-1 rounded text-sm"),
                            spacing="1",
                            align="center",
                        ),
                        rx.vstack(
                            rx.text("Bigonial", size="1", class_name="text-slate-500"),
                            rx.code(bigonial, class_name="text-orange-300 bg-slate-800 px-2 py-1 rounded text-sm"),
                            spacing="1",
                            align="center",
                        ),
                        justify="center",
                        spacing="6",
                        width="100%",
                    ),
                    align="center",
                    width="100%",
                ),
                class_name="p-3 bg-slate-800/30 rounded-lg w-full",
            ),
            # Personality traits table (conditional)
            rx.cond(
                personality_traits.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.text("Personality Profile", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                        personality_table(personality_traits),
                        width="100%",
                    ),
                    class_name="w-full",
                ),
                rx.fragment(),
            ),
            spacing="4",
            width="100%",
        ),
    )


def forehead_result_card(
    angle: rx.Var,
    impulsiveness: rx.Var,
    confidence_value: rx.Var,
    height: rx.Var,
    geometry_details: rx.Var,
) -> rx.Component:
    """Forehead Analysis result card for demo page."""
    return demo_result_section(
        title="Forehead Analysis",
        icon="brain",
        badge_text="Impulsiveness",
        badge_color="purple",
        children=rx.vstack(
            # Main metrics row
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("Slant Angle", size="2", class_name="text-slate-400"),
                        rx.heading(angle, size="5", class_name="text-purple-400 font-mono"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Impulsiveness", size="2", class_name="text-slate-400"),
                        rx.badge(impulsiveness, color_scheme="purple", size="2"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Confidence meter
            confidence_meter(confidence_value, "Analysis Confidence"),
            # Forehead height
            rx.box(
                rx.hstack(
                    rx.text("Forehead Height:", size="2", class_name="text-slate-400"),
                    rx.code(height, class_name="text-purple-300 bg-slate-800 px-2 py-1 rounded"),
                    spacing="2",
                    align="center",
                ),
                class_name="p-3 bg-slate-800/30 rounded-lg w-full",
            ),
            # Geometry details (conditional)
            rx.cond(
                geometry_details.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.text("Geometry Details", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                        details_table(geometry_details),
                        width="100%",
                    ),
                    class_name="w-full",
                ),
                rx.fragment(),
            ),
            spacing="4",
            width="100%",
        ),
    )


def morphology_result_card(
    face_shape: rx.Var,
    facial_index: rx.Var,
    ratio: rx.Var,
    confidence_value: rx.Var,
    proportions: rx.Var,
) -> rx.Component:
    """Morphology Analysis result card for demo page."""
    return demo_result_section(
        title="Morphology Analysis",
        icon="scan-face",
        badge_text="Face Shape",
        badge_color="green",
        children=rx.vstack(
            # Main metric - Face Shape
            rx.box(
                rx.vstack(
                    rx.text("Face Shape", size="2", class_name="text-slate-400"),
                    rx.heading(face_shape, size="6", class_name="text-green-400"),
                    spacing="1",
                    align="center",
                ),
                class_name="p-5 bg-slate-800/50 rounded-lg text-center w-full",
            ),
            # Secondary metrics row
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("Facial Index", size="2", class_name="text-slate-400"),
                        rx.code(facial_index, class_name="text-green-300 bg-slate-800 px-2 py-1 rounded"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-3 bg-slate-800/30 rounded-lg text-center",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("W/H Ratio", size="2", class_name="text-slate-400"),
                        rx.code(ratio, class_name="text-green-300 bg-slate-800 px-2 py-1 rounded"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-3 bg-slate-800/30 rounded-lg text-center",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Confidence meter
            confidence_meter(confidence_value, "Analysis Confidence"),
            # Proportions details (conditional)
            rx.cond(
                proportions.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.text("Facial Proportions", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                        details_table(proportions),
                        width="100%",
                    ),
                    class_name="w-full",
                ),
                rx.fragment(),
            ),
            spacing="4",
            width="100%",
        ),
    )


def canons_result_card(
    overall_score: rx.Var,
    overall_score_value: rx.Var,
    measurements_list: rx.Var,
) -> rx.Component:
    """Neoclassical Canons result card for demo page."""
    return demo_result_section(
        title="Neoclassical Canons",
        icon="ruler",
        badge_text="Harmony",
        badge_color="amber",
        children=rx.vstack(
            # Overall harmony score
            rx.box(
                rx.vstack(
                    rx.text("Overall Harmony Score", size="2", class_name="text-slate-400"),
                    rx.heading(overall_score, size="6", class_name="text-amber-400 font-mono"),
                    spacing="1",
                    align="center",
                ),
                class_name="p-5 bg-slate-800/50 rounded-lg text-center w-full",
            ),
            # Confidence meter using overall score
            confidence_meter(overall_score_value, "Harmony Level"),
            # Canon measurements table (conditional)
            rx.cond(
                measurements_list.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.text("Canon Measurements", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                        canon_table(measurements_list),
                        width="100%",
                    ),
                    class_name="w-full",
                ),
                rx.fragment(),
            ),
            spacing="4",
            width="100%",
        ),
    )


def analysis_summary_header(
    confidence: rx.Var,
    processing_time: rx.Var,
    is_multi_angle: rx.Var,
    num_angles: rx.Var,
) -> rx.Component:
    """Summary header for analysis results."""
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text("Analysis Complete", size="1", class_name="text-slate-500 uppercase tracking-wide"),
                rx.hstack(
                    rx.icon("circle-check", size=20, class_name="text-green-400"),
                    rx.heading("Results Ready", size="5", class_name="text-white"),
                    spacing="2",
                    align="center",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.hstack(
                rx.vstack(
                    rx.text("Confidence", size="1", class_name="text-slate-500"),
                    rx.text(confidence, size="3", weight="bold", class_name="text-green-400"),
                    spacing="0",
                    align="center",
                ),
                rx.divider(orientation="vertical", class_name="h-10 border-slate-700"),
                rx.vstack(
                    rx.text("Time", size="1", class_name="text-slate-500"),
                    rx.text(processing_time, size="3", weight="bold", class_name="text-orange-400"),
                    spacing="0",
                    align="center",
                ),
                rx.cond(
                    is_multi_angle,
                    rx.hstack(
                        rx.divider(orientation="vertical", class_name="h-10 border-slate-700"),
                        rx.vstack(
                            rx.text("Angles", size="1", class_name="text-slate-500"),
                            rx.text(num_angles.to_string(), size="3", weight="bold", class_name="text-blue-400"),
                            spacing="0",
                            align="center",
                        ),
                        spacing="4",
                    ),
                    rx.fragment(),
                ),
                spacing="4",
                align="center",
            ),
            width="100%",
            align="center",
        ),
        class_name="bg-gradient-to-r from-slate-800/50 to-slate-800/30 border border-slate-700/50 rounded-xl p-5 w-full",
    )


# =============================================================================
# ENHANCED RESULT CARDS WITH PLOTLY CHARTS
# =============================================================================

def wd_result_card_with_charts(
    wd_value: rx.Var,
    classification: rx.Var,
    confidence: rx.Var,
    confidence_value: rx.Var,
    bizygomatic: rx.Var,
    bigonial: rx.Var,
    personality_traits: rx.Var,
    personality_radar_figure: rx.Var,
    demographic_gauge_figure: rx.Var,
    evidence_level: rx.Var,
) -> rx.Component:
    """WD Analysis result card with Plotly radar chart and demographic gauge."""
    return demo_result_section(
        title="WD Analysis",
        icon="users",
        badge_text="Personality",
        badge_color="blue",
        children=rx.vstack(
            # Main metrics row
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("WD Value", size="2", class_name="text-slate-400"),
                        rx.heading(wd_value, size="5", class_name="text-orange-400 font-mono"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Classification", size="2", class_name="text-slate-400"),
                        rx.badge(classification, color_scheme="orange", size="2"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Evidence level badge
            rx.hstack(
                rx.text("Evidence:", size="1", class_name="text-slate-500"),
                evidence_level_badge(evidence_level, "Lefevre et al. (2012) - fWHR correlations"),
                spacing="2",
                align="center",
            ),
            # Confidence meter
            confidence_meter(confidence_value, "Analysis Confidence"),
            # Measurements
            rx.box(
                rx.vstack(
                    rx.text("Facial Measurements", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Bizygomatic", size="1", class_name="text-slate-500"),
                            rx.code(bizygomatic, class_name="text-orange-300 bg-slate-800 px-2 py-1 rounded text-sm"),
                            spacing="1",
                            align="center",
                        ),
                        rx.vstack(
                            rx.text("Bigonial", size="1", class_name="text-slate-500"),
                            rx.code(bigonial, class_name="text-orange-300 bg-slate-800 px-2 py-1 rounded text-sm"),
                            spacing="1",
                            align="center",
                        ),
                        justify="center",
                        spacing="6",
                        width="100%",
                    ),
                    align="center",
                    width="100%",
                ),
                class_name="p-3 bg-slate-800/30 rounded-lg w-full",
            ),
            # Personality radar chart (using pre-computed figure)
            rx.box(
                rx.vstack(
                    rx.text("Personality Profile", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.box(
                        rx.plotly(data=personality_radar_figure),
                        class_name="w-full overflow-hidden",
                    ),
                    width="100%",
                ),
                class_name="w-full overflow-hidden",
            ),
            # Demographic percentile gauge (using pre-computed figure)
            rx.box(
                rx.vstack(
                    rx.text("Demographic Position", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.box(
                        rx.plotly(data=demographic_gauge_figure),
                        class_name="mx-auto",
                    ),
                    width="100%",
                    align="center",
                ),
                class_name="w-full overflow-hidden",
            ),
            spacing="4",
            width="100%",
        ),
    )


def forehead_result_card_with_charts(
    angle: rx.Var,
    impulsiveness: rx.Var,
    confidence_value: rx.Var,
    height: rx.Var,
    geometry_details: rx.Var,
    impulsivity_radar_figure: rx.Var,
    neuroscience_bar_figure: rx.Var,
    evidence_level: rx.Var,
) -> rx.Component:
    """Forehead Analysis result card with impulsivity radar and neuroscience bar chart."""
    return demo_result_section(
        title="Forehead Analysis",
        icon="brain",
        badge_text="Impulsiveness",
        badge_color="purple",
        children=rx.vstack(
            # Main metrics row
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("Slant Angle", size="2", class_name="text-slate-400"),
                        rx.heading(angle, size="5", class_name="text-purple-400 font-mono"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Impulsiveness", size="2", class_name="text-slate-400"),
                        rx.badge(impulsiveness, color_scheme="purple", size="2"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-4 bg-slate-800/50 rounded-lg text-center",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Evidence level badge
            rx.hstack(
                rx.text("Evidence:", size="1", class_name="text-slate-500"),
                evidence_level_badge(evidence_level, "Guerrero-Apolo et al. (2018) - FID-BIS11"),
                spacing="2",
                align="center",
            ),
            # Confidence meter
            confidence_meter(confidence_value, "Analysis Confidence"),
            # Forehead height
            rx.box(
                rx.hstack(
                    rx.text("Forehead Height:", size="2", class_name="text-slate-400"),
                    rx.code(height, class_name="text-purple-300 bg-slate-800 px-2 py-1 rounded"),
                    spacing="2",
                    align="center",
                ),
                class_name="p-3 bg-slate-800/30 rounded-lg w-full",
            ),
            # Impulsivity radar chart (using pre-computed figure)
            rx.box(
                rx.vstack(
                    rx.text("Impulsivity Profile (BIS-11)", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.box(
                        rx.plotly(data=impulsivity_radar_figure),
                        class_name="w-full overflow-hidden",
                    ),
                    width="100%",
                ),
                class_name="w-full overflow-hidden",
            ),
            # Neuroscience correlations bar chart (using pre-computed figure)
            rx.box(
                rx.vstack(
                    rx.text("Neuroscience Correlations", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.box(
                        rx.plotly(data=neuroscience_bar_figure),
                        class_name="w-full overflow-hidden",
                    ),
                    width="100%",
                ),
                class_name="w-full overflow-hidden",
            ),
            # Geometry details (conditional)
            rx.cond(
                geometry_details.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.text("Geometry Details", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                        details_table(geometry_details),
                        width="100%",
                    ),
                    class_name="w-full",
                ),
                rx.fragment(),
            ),
            spacing="4",
            width="100%",
        ),
    )


def morphology_result_card_with_charts(
    face_shape: rx.Var,
    facial_index: rx.Var,
    ratio: rx.Var,
    confidence_value: rx.Var,
    proportions: rx.Var,
    face_shape_donut_figure: rx.Var,
    proportions_bar_figure: rx.Var,
) -> rx.Component:
    """Morphology Analysis result card with face shape donut and proportions bar chart."""
    return demo_result_section(
        title="Morphology Analysis",
        icon="scan-face",
        badge_text="Face Shape",
        badge_color="green",
        children=rx.vstack(
            # Main metric - Face Shape
            rx.box(
                rx.vstack(
                    rx.text("Face Shape", size="2", class_name="text-slate-400"),
                    rx.heading(face_shape, size="6", class_name="text-green-400"),
                    spacing="1",
                    align="center",
                ),
                class_name="p-5 bg-slate-800/50 rounded-lg text-center w-full",
            ),
            # Secondary metrics row
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("Facial Index", size="2", class_name="text-slate-400"),
                        rx.code(facial_index, class_name="text-green-300 bg-slate-800 px-2 py-1 rounded"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-3 bg-slate-800/30 rounded-lg text-center",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("W/H Ratio", size="2", class_name="text-slate-400"),
                        rx.code(ratio, class_name="text-green-300 bg-slate-800 px-2 py-1 rounded"),
                        spacing="1",
                        align="center",
                    ),
                    class_name="p-3 bg-slate-800/30 rounded-lg text-center",
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # Confidence meter
            confidence_meter(confidence_value, "Analysis Confidence"),
            # Face shape distribution donut chart (using pre-computed figure)
            rx.box(
                rx.vstack(
                    rx.text("Shape Distribution", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.box(
                        rx.plotly(data=face_shape_donut_figure),
                        class_name="w-full overflow-hidden",
                    ),
                    width="100%",
                ),
                class_name="w-full overflow-hidden",
            ),
            # Proportions bar chart (using pre-computed figure)
            rx.box(
                rx.vstack(
                    rx.text("Facial Proportions", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.box(
                        rx.plotly(data=proportions_bar_figure),
                        class_name="w-full overflow-hidden",
                    ),
                    width="100%",
                ),
                class_name="w-full overflow-hidden",
            ),
            spacing="4",
            width="100%",
        ),
    )


def canons_result_card_with_charts(
    overall_score: rx.Var,
    overall_score_value: rx.Var,
    measurements_list: rx.Var,
    harmony_gauge_figure: rx.Var,
    canon_deviation_bar_figure: rx.Var,
) -> rx.Component:
    """Neoclassical Canons result card with deviation bar chart and harmony gauge."""
    return demo_result_section(
        title="Neoclassical Canons",
        icon="ruler",
        badge_text="Harmony",
        badge_color="amber",
        children=rx.vstack(
            # Overall harmony score with gauge - stacked vertically for consistent display
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("Harmony Score", size="2", class_name="text-slate-400"),
                        rx.heading(overall_score, size="5", class_name="text-amber-400 font-mono"),
                        spacing="3",
                        align="center",
                        justify="center",
                        width="100%",
                    ),
                    rx.text(
                        "Adherence to classical facial proportions",
                        size="1",
                        class_name="text-slate-500 -mt-1",
                    ),
                    rx.box(
                        rx.plotly(data=harmony_gauge_figure),
                        class_name="mx-auto",
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                class_name="p-4 bg-slate-800/50 rounded-lg w-full",
            ),
            # Canon deviations bar chart (using pre-computed figure)
            rx.box(
                rx.vstack(
                    rx.text("Canon Deviations", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                    rx.box(
                        rx.plotly(data=canon_deviation_bar_figure),
                        class_name="w-full overflow-hidden",
                    ),
                    width="100%",
                ),
                class_name="w-full overflow-hidden",
            ),
            # Canon measurements table (conditional)
            rx.cond(
                measurements_list.length() > 0,
                rx.box(
                    rx.vstack(
                        rx.text("Canon Measurements", size="2", weight="medium", class_name="text-slate-300 mb-2"),
                        canon_table(measurements_list),
                        width="100%",
                    ),
                    class_name="w-full",
                ),
                rx.fragment(),
            ),
            spacing="4",
            width="100%",
        ),
    )


def analysis_confidence_dashboard(
    confidence_dashboard_figure: rx.Var,
) -> rx.Component:
    """Dashboard showing confidence levels for all modules."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("gauge", size=18, class_name="text-orange-400"),
                rx.text("Module Confidence", size="3", weight="medium", class_name="text-slate-200"),
                spacing="2",
                align="center",
            ),
            rx.box(
                rx.plotly(data=confidence_dashboard_figure),
                class_name="w-full overflow-hidden",
            ),
            spacing="3",
            width="100%",
        ),
        class_name="bg-slate-800/30 border border-slate-700/50 rounded-xl p-4 w-full overflow-hidden",
    )
