document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('image-canvas');
    const ctx = canvas.getContext('2d');
    const imageNameEl = document.getElementById('image-name');
    const progressEl = document.getElementById('progress');

    let images = [];
    let currentIndex = 0;
    let currentImage = new Image();
    let boxes = [];
    let isDrawing = false;
    let startX, startY;

    // 获取需要标注的图片列表
    fetch('/api/images_to_annotate')
        .then(response => response.json())
        .then(data => {
            images = data.images;
            if (images.length > 0) {
                loadImage();
            } else {
                imageNameEl.textContent = "没有需要标注的图片。";
            }
        });

    function loadImage() {
        if (currentIndex >= images.length) {
            imageNameEl.textContent = "所有图片已标注完毕！";
            progressEl.textContent = "";
            return;
        }
        boxes = [];
        const imageName = images[currentIndex];
        currentImage.src = `/images/${imageName}`; // 从后端获取图片
        currentImage.onload = () => {
            canvas.width = currentImage.width;
            canvas.height = currentImage.height;
            redraw();
            imageNameEl.textContent = `当前图片: ${imageName}`;
            progressEl.textContent = `进度: ${currentIndex + 1} / ${images.length}`;
        };
    }

    function redraw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(currentImage, 0, 0);
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        boxes.forEach(box => {
            ctx.strokeRect(box.x, box.y, box.w, box.h);
        });
    }

    canvas.addEventListener('mousedown', (e) => {
        isDrawing = true;
        startX = e.offsetX;
        startY = e.offsetY;
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!isDrawing) return;
        redraw();
        const currentX = e.offsetX;
        const currentY = e.offsetY;
        ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
    });

    canvas.addEventListener('mouseup', (e) => {
        if (!isDrawing) return;
        isDrawing = false;
        const endX = e.offsetX;
        const endY = e.offsetY;
        boxes.push({
            x: Math.min(startX, endX),
            y: Math.min(startY, endY),
            w: Math.abs(endX - startX),
            h: Math.abs(endY - startY)
        });
        redraw();
    });

    document.getElementById('clear-btn').addEventListener('click', () => {
        boxes = [];
        redraw();
    });

    document.getElementById('prev-btn').addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            loadImage();
        }
    });

    document.getElementById('next-btn').addEventListener('click', () => {
        if (currentIndex < images.length - 1) {
            currentIndex++;
            loadImage();
        }
    });

    document.getElementById('save-btn').addEventListener('click', () => {
        const imageName = images[currentIndex];
        const yoloAnnotations = boxes.map(box => {
            const x_center = (box.x + box.w / 2) / canvas.width;
            const y_center = (box.y + box.h / 2) / canvas.height;
            const width = box.w / canvas.width;
            const height = box.h / canvas.height;
            return `0 ${x_center.toFixed(6)} ${y_center.toFixed(6)} ${width.toFixed(6)} ${height.toFixed(6)}`;
        });

        fetch('/api/save_annotation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_name: imageName,
                annotations: yoloAnnotations.join('\n')
            })
        }).then(response => {
            if (response.ok) {
                currentIndex++;
                loadImage();
            } else {
                alert('保存失败！');
            }
        });
    });
});