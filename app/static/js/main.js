// ─── Nav scroll effect + height variable ─────────────────────────────────────
const nav = document.querySelector('.nav');
if (nav) {
  function setNavHeight() {
    document.documentElement.style.setProperty('--nav-h', nav.offsetHeight + 'px');
  }
  setNavHeight();
  new ResizeObserver(setNavHeight).observe(nav);
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 20);
  });
}

// ─── Image fade-in + shimmer skeleton ────────────────────────────────────────
function initImageFade() {
  // Selectors: project cards, process photos, about photo
  const imgs = document.querySelectorAll(
    '.project-card-img, .process-img, .img-wrap img'
  );

  imgs.forEach(img => {
    const parent = img.parentElement;

    // Already loaded from cache
    if (img.complete && img.naturalWidth > 0) {
      img.classList.add('img-fade', 'img-loaded');
      return;
    }

    img.classList.add('img-fade');
    parent.classList.add('img-shimmer-active');

    const onLoad = () => {
      img.classList.add('img-loaded');
      parent.classList.remove('img-shimmer-active');
    };

    img.addEventListener('load', onLoad, { once: true });
    img.addEventListener('error', onLoad, { once: true });
  });
}

document.addEventListener('DOMContentLoaded', initImageFade);


// ─── Lightbox for process images ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const processImgs = document.querySelectorAll('.process-img');
  if (!processImgs.length) return;

  const overlay = document.createElement('div');
  overlay.style.cssText = [
    'display:none', 'position:fixed', 'inset:0',
    'background:rgba(0,0,0,0.95)', 'z-index:1000',
    'align-items:center', 'justify-content:center', 'cursor:pointer'
  ].join(';');

  const overlayImg = document.createElement('img');
  overlayImg.style.cssText = 'max-width:90vw;max-height:90vh;object-fit:contain;';
  overlay.appendChild(overlayImg);
  document.body.appendChild(overlay);

  processImgs.forEach(img => {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', () => {
      overlayImg.src = img.src;
      overlay.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    });
  });

  overlay.addEventListener('click', () => {
    overlay.style.display = 'none';
    document.body.style.overflow = '';
  });
});
