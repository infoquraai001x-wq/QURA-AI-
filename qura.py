"""
QURA AI - Advanced QR Generator
Run: python app.py
Requirements: Flask, qrcode, Pillow
Install: pip install flask qrcode[pil] Pillow
"""

import os
import uuid
import base64
import random
import io
from flask import Flask, request, render_template_string, send_file, jsonify, url_for
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# HTML Template with advanced UI/UX
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QURA AI - Intelligent QR Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(145deg, #0b0f1c 0%, #1a1f33 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        /* Animated background grid */
        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(102, 126, 234, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(102, 126, 234, 0.05) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: 0;
        }
        .container {
            max-width: 900px;
            width: 100%;
            background: rgba(20, 25, 45, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 40px;
            padding: 35px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(102,126,234,0.2) inset;
            position: relative;
            z-index: 2;
            transition: all 0.3s ease;
        }
        /* AI Character */
        .ai-character {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            position: relative;
        }
        #aiCanvas {
            width: 120px;
            height: 120px;
            filter: drop-shadow(0 10px 20px rgba(0,0,0,0.4));
            transition: transform 0.3s;
            cursor: pointer;
        }
        #aiCanvas:hover {
            transform: scale(1.05);
        }
        h1 {
            text-align: center;
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            letter-spacing: -0.02em;
            text-shadow: 0 2px 10px rgba(167,139,250,0.3);
        }
        .subtitle {
            text-align: center;
            color: #9ca3af;
            margin-bottom: 35px;
            font-weight: 400;
            letter-spacing: 2px;
            text-transform: uppercase;
            font-size: 0.85rem;
        }
        /* Tabs for QR types */
        .qr-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .tab-btn {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            color: #cbd5e1;
            padding: 12px 24px;
            border-radius: 40px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
            backdrop-filter: blur(5px);
            flex: 0 1 auto;
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-color: transparent;
            box-shadow: 0 8px 20px rgba(102,126,234,0.3);
        }
        .tab-btn i {
            margin-right: 8px;
        }
        /* Form Panels */
        .form-panel {
            display: none;
            animation: fadeIn 0.3s ease;
        }
        .form-panel.active {
            display: block;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .input-group {
            margin-bottom: 22px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #e2e8f0;
            font-size: 0.9rem;
        }
        input, textarea, select {
            width: 100%;
            padding: 14px 18px;
            background: rgba(0,0,0,0.25);
            border: 1.5px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            font-size: 1rem;
            color: white;
            transition: all 0.2s;
            outline: none;
            font-family: 'Inter', sans-serif;
        }
        input:focus, textarea:focus, select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.2);
            background: rgba(0,0,0,0.4);
        }
        input::placeholder, textarea::placeholder {
            color: #6b7280;
        }
        .row {
            display: flex;
            gap: 15px;
        }
        .row .input-group {
            flex: 1;
        }
        /* Design options */
        .design-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        .design-option {
            background: rgba(0,0,0,0.2);
            border-radius: 16px;
            padding: 15px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
            text-align: center;
        }
        .design-option.active {
            border-color: #667eea;
            background: rgba(102,126,234,0.15);
        }
        .design-option .preview {
            width: 60px;
            height: 60px;
            margin: 0 auto 10px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .color-picker-wrap {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 15px;
        }
        input[type="color"] {
            width: 60px;
            height: 50px;
            padding: 5px;
            background: transparent;
            border: 1px solid #334155;
            border-radius: 16px;
        }
        /* Generate Button */
        .generate-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 18px 30px;
            font-size: 1.2rem;
            font-weight: 700;
            border-radius: 50px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
            margin: 30px 0 20px;
            box-shadow: 0 20px 30px -10px rgba(102,126,234,0.4);
            letter-spacing: 0.5px;
        }
        .generate-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 25px 40px -10px #667eea;
        }
        /* QR Result */
        .qr-result {
            text-align: center;
            padding: 25px;
            background: rgba(0,0,0,0.2);
            border-radius: 30px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-top: 20px;
            display: none;
        }
        .qr-result img {
            max-width: 220px;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            background: white;
            padding: 15px;
        }
        .download-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 25px;
        }
        .btn {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: white;
            padding: 12px 25px;
            border-radius: 40px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
            cursor: pointer;
            backdrop-filter: blur(5px);
        }
        .btn-primary {
            background: #10b981;
            border-color: #10b981;
        }
        .btn-primary:hover {
            background: #059669;
        }
        .footer {
            text-align: center;
            color: #6b7280;
            margin-top: 30px;
            font-size: 0.8rem;
        }
        /* File upload styling */
        .file-upload {
            border: 2px dashed #4b5563;
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            cursor: pointer;
            transition: border 0.2s;
        }
        .file-upload:hover {
            border-color: #667eea;
        }
        .file-upload input {
            display: none;
        }
        .upload-preview {
            margin-top: 15px;
        }
        .upload-preview img {
            max-width: 100%;
            max-height: 150px;
            border-radius: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- AI Character Canvas -->
        <div class="ai-character">
            <canvas id="aiCanvas" width="200" height="200"></canvas>
        </div>
        <h1>QURA AI</h1>
        <div class="subtitle">Intelligent QR Studio</div>

        <!-- QR Type Tabs -->
        <div class="qr-tabs">
            <button class="tab-btn active" data-type="url"><i>🔗</i> Website</button>
            <button class="tab-btn" data-type="email"><i>✉️</i> Email</button>
            <button class="tab-btn" data-type="phone"><i>📞</i> Phone</button>
            <button class="tab-btn" data-type="location"><i>📍</i> Location</button>
            <button class="tab-btn" data-type="photo"><i>🖼️</i> Photo</button>
        </div>

        <!-- Form Panels -->
        <form id="qrForm" enctype="multipart/form-data">
            <!-- URL Panel -->
            <div class="form-panel active" id="panel-url">
                <div class="input-group">
                    <label>Website URL</label>
                    <input type="url" name="url" placeholder="https://example.com" value="https://">
                </div>
            </div>
            <!-- Email Panel -->
            <div class="form-panel" id="panel-email">
                <div class="input-group">
                    <label>Email Address</label>
                    <input type="email" name="email" placeholder="hello@example.com">
                </div>
                <div class="input-group">
                    <label>Subject (optional)</label>
                    <input type="text" name="email_subject" placeholder="Hello">
                </div>
                <div class="input-group">
                    <label>Body (optional)</label>
                    <textarea name="email_body" rows="3" placeholder="Your message..."></textarea>
                </div>
            </div>
            <!-- Phone Panel -->
            <div class="form-panel" id="panel-phone">
                <div class="input-group">
                    <label>Phone Number</label>
                    <input type="tel" name="phone" placeholder="+1234567890">
                </div>
            </div>
            <!-- Location Panel -->
            <div class="form-panel" id="panel-location">
                <div class="row">
                    <div class="input-group">
                        <label>Latitude</label>
                        <input type="text" name="lat" placeholder="37.7749">
                    </div>
                    <div class="input-group">
                        <label>Longitude</label>
                        <input type="text" name="lng" placeholder="-122.4194">
                    </div>
                </div>
                <button type="button" id="getLocationBtn" class="btn" style="width:100%; margin-top:10px;">📍 Use My Current Location</button>
            </div>
            <!-- Photo Panel -->
            <div class="form-panel" id="panel-photo">
                <div class="file-upload" id="fileDropArea">
                    <input type="file" name="photo" id="photoInput" accept="image/*">
                    <div>📤 Click or Drag & Drop Image</div>
                    <div style="font-size:0.8rem; margin-top:8px;">Max 16MB</div>
                    <div class="upload-preview" id="photoPreview"></div>
                </div>
            </div>

            <!-- Design Options -->
            <div style="margin-top: 30px;">
                <label>🎨 QR Style</label>
                <div class="design-grid">
                    <div class="design-option active" data-style="professional">
                        <div class="preview" style="background:#000;"></div>
                        <span>Professional</span>
                    </div>
                    <div class="design-option" data-style="funny">
                        <div class="preview" style="background:linear-gradient(45deg, #f00, #0f0, #00f);"></div>
                        <span>Funny</span>
                    </div>
                    <div class="design-option" data-style="fingertype">
                        <div class="preview" style="background:radial-gradient(circle, #1a237e, #fff);"></div>
                        <span>Fingertype</span>
                    </div>
                    <div class="design-option" data-style="rounded">
                        <div class="preview" style="background:#333; border-radius:30%;"></div>
                        <span>Rounded</span>
                    </div>
                    <div class="design-option" data-style="gradient">
                        <div class="preview" style="background:linear-gradient(135deg,#667eea,#764ba2);"></div>
                        <span>Gradient</span>
                    </div>
                </div>
                <div class="color-picker-wrap">
                    <label>🎨 Foreground</label>
                    <input type="color" name="fg_color" value="#000000">
                    <label>⬜ Background</label>
                    <input type="color" name="bg_color" value="#ffffff">
                </div>
                <div class="input-group">
                    <label>➕ Embed Logo (URL, optional)</label>
                    <input type="text" name="logo_url" placeholder="https://.../logo.png">
                </div>
            </div>

            <button type="submit" class="generate-btn">✨ Generate Magic QR</button>
        </form>

        <!-- QR Result -->
        <div class="qr-result" id="qrResult">
            <img id="qrImage" src="" alt="QR Code">
            <div class="download-actions">
                <a id="downloadLink" class="btn btn-primary" download="qura_qr.png">⬇ Download PNG</a>
                <button id="copyLinkBtn" class="btn">📋 Copy Link</button>
            </div>
        </div>
        <div class="footer">QURA AI · Next-Gen QR Intelligence</div>
    </div>

    <script>
        // ---------- AI Character Animation (Canvas) ----------
        const canvas = document.getElementById('aiCanvas');
        const ctx = canvas.getContext('2d');
        let rotation = 0;
        let blink = 0;
        let smileOffset = 0;
        let time = 0;

        function drawAI() {
            ctx.clearRect(0, 0, 200, 200);
            
            // Rotating effect
            ctx.save();
            ctx.translate(100, 100);
            ctx.rotate(rotation * Math.PI / 180);
            
            // Main glowing circle
            const gradient = ctx.createRadialGradient(-20, -20, 10, 0, 0, 80);
            gradient.addColorStop(0, '#a78bfa');
            gradient.addColorStop(0.6, '#4f46e5');
            gradient.addColorStop(1, '#1e1b4b');
            ctx.fillStyle = gradient;
            ctx.shadowColor = '#667eea';
            ctx.shadowBlur = 25;
            ctx.beginPath();
            ctx.arc(0, 0, 70, 0, 2 * Math.PI);
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.strokeStyle = '#c4b5fd';
            ctx.lineWidth = 3;
            ctx.stroke();

            // Eyes
            ctx.fillStyle = '#ffffff';
            ctx.shadowBlur = 0;
            // Left eye
            ctx.beginPath();
            ctx.ellipse(-25, -15, 14, blink ? 2 : 16, 0, 0, 2 * Math.PI);
            ctx.fill();
            // Right eye
            ctx.beginPath();
            ctx.ellipse(25, -15, 14, blink ? 2 : 16, 0, 0, 2 * Math.PI);
            ctx.fill();

            // Pupils
            ctx.fillStyle = '#1e1b4b';
            ctx.beginPath();
            ctx.arc(-25, -15, 6, 0, 2 * Math.PI);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(25, -15, 6, 0, 2 * Math.PI);
            ctx.fill();
            
            // Eye shine
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(-30, -20, 2, 0, 2 * Math.PI);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(20, -20, 2, 0, 2 * Math.PI);
            ctx.fill();

            // Smile
            ctx.beginPath();
            ctx.strokeStyle = '#f472b6';
            ctx.lineWidth = 5;
            ctx.lineCap = 'round';
            ctx.arc(0, 20, 30, 0.1, Math.PI - 0.1);
            ctx.stroke();
            
            // Blush
            ctx.fillStyle = '#f472b6';
            ctx.globalAlpha = 0.3;
            ctx.beginPath();
            ctx.arc(-45, 15, 10, 0, 2 * Math.PI);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(45, 15, 10, 0, 2 * Math.PI);
            ctx.fill();
            ctx.globalAlpha = 1.0;
            
            ctx.restore();
        }

        function animateAI() {
            time++;
            rotation = (rotation + 0.5) % 360;
            // Blink every ~3 seconds
            blink = (Math.sin(time * 0.02) > 0.8) ? 1 : 0;
            drawAI();
            requestAnimationFrame(animateAI);
        }
        animateAI();

        // Click on AI to trigger smile
        canvas.addEventListener('click', () => {
            // Quick smile animation handled by time offset? Not needed, just fun.
        });

        // ---------- Tab Switching ----------
        const tabs = document.querySelectorAll('.tab-btn');
        const panels = {
            url: document.getElementById('panel-url'),
            email: document.getElementById('panel-email'),
            phone: document.getElementById('panel-phone'),
            location: document.getElementById('panel-location'),
            photo: document.getElementById('panel-photo')
        };
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const type = tab.dataset.type;
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                Object.values(panels).forEach(p => p.classList.remove('active'));
                panels[type].classList.add('active');
            });
        });

        // Design option selection
        const designOptions = document.querySelectorAll('.design-option');
        designOptions.forEach(opt => {
            opt.addEventListener('click', () => {
                designOptions.forEach(o => o.classList.remove('active'));
                opt.classList.add('active');
            });
        });

        // Get location
        document.getElementById('getLocationBtn').addEventListener('click', () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    document.querySelector('input[name="lat"]').value = pos.coords.latitude;
                    document.querySelector('input[name="lng"]').value = pos.coords.longitude;
                });
            } else {
                alert("Geolocation not supported");
            }
        });

        // Photo upload preview & drag drop
        const photoInput = document.getElementById('photoInput');
        const dropArea = document.getElementById('fileDropArea');
        const previewDiv = document.getElementById('photoPreview');
        
        dropArea.addEventListener('click', () => photoInput.click());
        photoInput.addEventListener('change', handlePhotoSelect);
        dropArea.addEventListener('dragover', (e) => { e.preventDefault(); dropArea.style.borderColor = '#667eea'; });
        dropArea.addEventListener('dragleave', () => dropArea.style.borderColor = '#4b5563');
        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dropArea.style.borderColor = '#4b5563';
            const files = e.dataTransfer.files;
            if (files.length) {
                photoInput.files = files;
                handlePhotoSelect();
            }
        });

        function handlePhotoSelect() {
            const file = photoInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewDiv.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            }
        }

        // Form submission
        const form = document.getElementById('qrForm');
        const qrResult = document.getElementById('qrResult');
        const qrImage = document.getElementById('qrImage');
        const downloadLink = document.getElementById('downloadLink');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Gather data
            const formData = new FormData(form);
            const activeTab = document.querySelector('.tab-btn.active').dataset.type;
            formData.append('qr_type', activeTab);
            
            const activeStyle = document.querySelector('.design-option.active').dataset.style;
            formData.append('style', activeStyle);
            
            // Show loading state (could transform AI)
            qrResult.style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (data.image) {
                    qrImage.src = data.image;
                    downloadLink.href = data.image;
                    qrResult.style.display = 'block';
                    // Animate AI into QR? For now just show.
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            } catch (err) {
                alert('Network error');
            }
        });

        // Copy link
        document.getElementById('copyLinkBtn').addEventListener('click', () => {
            const imgSrc = qrImage.src;
            // Create a temporary link to copy data URL? Not ideal. Could copy base64.
            navigator.clipboard.writeText(imgSrc).then(() => alert('QR data URL copied!'));
        });
    </script>
</body>
</html>
"""

# Helper functions for QR generation
def generate_qr(data, style='professional', fg='#000000', bg='#ffffff', logo_path=None):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    if style == 'professional':
        img = qr.make_image(fill_color=fg, back_color=bg).convert('RGB')
    elif style == 'funny':
        img = generate_funny_qr(qr, fg, bg)
    elif style == 'fingertype':
        img = generate_fingertype_qr(qr, fg, bg)
    elif style == 'rounded':
        img = generate_rounded_qr(qr, fg, bg)
    elif style == 'gradient':
        img = generate_gradient_qr(qr, fg, bg)
    else:
        img = qr.make_image(fill_color=fg, back_color=bg).convert('RGB')
    
    # Embed logo if provided and exists
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Resize logo to fit
            qr_width, qr_height = img.size
            logo_size = int(qr_width * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            img = img.convert("RGBA")
            img.paste(logo, pos, logo)
            img = img.convert("RGB")
        except Exception as e:
            print(f"Logo error: {e}")
    return img

def generate_funny_qr(qr, fg, bg):
    matrix = qr.get_matrix()
    module_size = 10
    border = 4
    size = (len(matrix) + 2 * border) * module_size
    img = Image.new('RGB', (size, size), bg)
    draw = ImageDraw.Draw(img)
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if matrix[row][col]:
                x = (col + border) * module_size
                y = (row + border) * module_size
                color = (random.randint(100,255), random.randint(50,200), random.randint(150,255))
                draw.rectangle([x, y, x+module_size-1, y+module_size-1], fill=color)
    return img

def generate_fingertype_qr(qr, fg, bg):
    matrix = qr.get_matrix()
    module_size = 10
    border = 4
    size = (len(matrix) + 2 * border) * module_size
    img = Image.new('RGB', (size, size), bg)
    draw = ImageDraw.Draw(img)
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if matrix[row][col]:
                x = (col + border) * module_size + module_size//2
                y = (row + border) * module_size + module_size//2
                radius = module_size//2 - 1
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=fg)
    return img

def generate_rounded_qr(qr, fg, bg):
    matrix = qr.get_matrix()
    module_size = 10
    border = 4
    size = (len(matrix) + 2 * border) * module_size
    img = Image.new('RGB', (size, size), bg)
    draw = ImageDraw.Draw(img)
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if matrix[row][col]:
                x = (col + border) * module_size
                y = (row + border) * module_size
                draw.rounded_rectangle([x, y, x+module_size-1, y+module_size-1], radius=module_size//3, fill=fg)
    return img

def generate_gradient_qr(qr, fg, bg):
    matrix = qr.get_matrix()
    module_size = 10
    border = 4
    size = (len(matrix) + 2 * border) * module_size
    img = Image.new('RGB', (size, size), bg)
    draw = ImageDraw.Draw(img)
    # Create gradient from fg to another color
    import colorsys
    rgb = tuple(int(fg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    end_color = colorsys.hls_to_rgb((h+0.3)%1, l, s)
    end_color = tuple(int(c*255) for c in end_color)
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if matrix[row][col]:
                x = (col + border) * module_size
                y = (row + border) * module_size
                ratio = col / len(matrix[row])
                r = int(rgb[0] + (end_color[0]-rgb[0])*ratio)
                g = int(rgb[1] + (end_color[1]-rgb[1])*ratio)
                b = int(rgb[2] + (end_color[2]-rgb[2])*ratio)
                draw.rectangle([x, y, x+module_size-1, y+module_size-1], fill=(r,g,b))
    return img

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        qr_type = request.form.get('qr_type', 'url')
        style = request.form.get('style', 'professional')
        fg = request.form.get('fg_color', '#000000')
        bg = request.form.get('bg_color', '#ffffff')
        logo_url = request.form.get('logo_url', '').strip()
        
        # Build data string based on type
        data = ""
        if qr_type == 'url':
            data = request.form.get('url', '').strip()
        elif qr_type == 'email':
            email = request.form.get('email', '').strip()
            subject = request.form.get('email_subject', '').strip()
            body = request.form.get('email_body', '').strip()
            data = f"mailto:{email}"
            params = []
            if subject: params.append(f"subject={subject}")
            if body: params.append(f"body={body}")
            if params: data += "?" + "&".join(params)
        elif qr_type == 'phone':
            phone = request.form.get('phone', '').strip()
            data = f"tel:{phone}"
        elif qr_type == 'location':
            lat = request.form.get('lat', '').strip()
            lng = request.form.get('lng', '').strip()
            if lat and lng:
                data = f"geo:{lat},{lng}"
            else:
                return jsonify({'error': 'Latitude and longitude required'}), 400
        elif qr_type == 'photo':
            if 'photo' not in request.files:
                return jsonify({'error': 'No photo uploaded'}), 400
            file = request.files['photo']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            # Save photo and generate URL
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Generate a public URL (for simplicity, serve via static)
            data = url_for('static', filename=f'uploads/{filename}', _external=True)
        else:
            data = request.form.get('url', '').strip()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle logo download if URL provided
        logo_path = None
        if logo_url:
            try:
                import requests
                response = requests.get(logo_url, timeout=5)
                if response.status_code == 200:
                    logo_filename = f"logo_{uuid.uuid4().hex}.png"
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
                    with open(logo_path, 'wb') as f:
                        f.write(response.content)
            except:
                pass
        
        img = generate_qr(data, style, fg, bg, logo_path)
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        return jsonify({'image': f'data:image/png;base64,{img_base64}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)