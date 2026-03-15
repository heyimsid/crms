document.addEventListener('DOMContentLoaded', () => {

  // ── THEME ────────────────────────────────────────────────────────
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn) {
    const icon = themeBtn.querySelector('i');
    if (localStorage.getItem('nexus_theme') === 'light') {
      document.body.classList.add('light');
      if (icon) { icon.classList.replace('fa-moon', 'fa-sun'); }
    }
    themeBtn.addEventListener('click', () => {
      document.body.classList.toggle('light');
      const light = document.body.classList.contains('light');
      localStorage.setItem('nexus_theme', light ? 'light' : 'dark');
      if (icon) {
        icon.classList.toggle('fa-moon', !light);
        icon.classList.toggle('fa-sun',   light);
      }
    });
  }

  // ── MODAL VIEW SWITCHER ──────────────────────────────────────────
  const backdrop = document.getElementById('authModal');
  const views = ['login','register','forgot','otp','reset'];
  function showView(name) {
    views.forEach(v => {
      const el = document.getElementById('view-' + v);
      if (el) el.style.display = v === name ? 'block' : 'none';
    });
  }
  function openModal(view = 'login') {
    if (!backdrop) return;
    backdrop.classList.add('open');
    showView(view);
  }
  function closeModal() {
    if (backdrop) backdrop.classList.remove('open');
  }

  // Trigger buttons (landing page)
  const signInBtn   = document.getElementById('openSignIn');
  const registerBtn = document.getElementById('openRegister');
  const heroBtn     = document.getElementById('heroGetStarted');
  const loginBtn    = document.getElementById('loginBtn'); // legacy fallback
  const heroLogin   = document.getElementById('heroLoginBtn'); // legacy fallback

  if (signInBtn)   signInBtn.addEventListener('click',   () => openModal('login'));
  if (registerBtn) registerBtn.addEventListener('click', () => openModal('register'));
  if (heroBtn)     heroBtn.addEventListener('click',     () => openModal('register'));
  if (loginBtn)    loginBtn.addEventListener('click',    () => openModal('login'));
  if (heroLogin)   heroLogin.addEventListener('click',   () => openModal('register'));

  const closeBtn = document.getElementById('closeAuth');
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', e => { if (e.target === backdrop) closeModal(); });

  // View switches
  const toReg  = document.getElementById('toRegister');
  const toLog  = document.getElementById('toLogin');
  const toForg = document.getElementById('toForgot');
  const backL  = document.getElementById('backToLogin');
  if (toReg)  toReg.addEventListener('click',  () => showView('register'));
  if (toLog)  toLog.addEventListener('click',  () => showView('login'));
  if (toForg) toForg.addEventListener('click', () => showView('forgot'));
  if (backL)  backL.addEventListener('click',  () => showView('login'));

  // ── FORGOT PASSWORD → show OTP view on submit ────────────────────
  const forgotForm = document.getElementById('forgotForm');
  if (forgotForm) {
    forgotForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const emailInput = forgotForm.querySelector('input[name="email"]');
      const email = emailInput ? emailInput.value.trim() : '';

      // Show loading state
      const btn = forgotForm.querySelector('button[type="submit"]');
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>&nbsp; Sending…';
      btn.disabled = true;

      try {
        const resp = await fetch('/forgot_password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ email })
        });
        const data = await resp.json();

        if (data.success) {
          // Populate hidden email field in OTP view
          const otpEmail = document.getElementById('otp-email-hidden');
          if (otpEmail) otpEmail.value = email;
          const subText = document.getElementById('otp-sub-text');
          if (subText) subText.textContent = `We sent a 6-digit code to ${email}.`;
          showView('otp');
        } else {
          // Show error inline
          btn.innerHTML = orig;
          btn.disabled = false;
          let errEl = forgotForm.querySelector('.inline-err');
          if (!errEl) {
            errEl = document.createElement('p');
            errEl.className = 'inline-err';
            errEl.style.cssText = 'color:var(--err);font-size:.78rem;text-align:center;margin-top:8px;';
            forgotForm.appendChild(errEl);
          }
          errEl.textContent = data.message || 'Email not found. Please try again.';
        }
      } catch {
        btn.innerHTML = orig;
        btn.disabled = false;
      }
    });
  }

  // ── OTP INPUT — auto-advance, backspace ──────────────────────────
  const otpBoxes = document.querySelectorAll('.otp-box');
  otpBoxes.forEach((box, i) => {
    box.addEventListener('input', () => {
      const val = box.value.replace(/\D/g, '');
      box.value = val.slice(-1);
      if (val && i < otpBoxes.length - 1) otpBoxes[i + 1].focus();
      combineOtp();
    });
    box.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !box.value && i > 0) {
        otpBoxes[i - 1].focus();
      }
    });
    box.addEventListener('paste', (e) => {
      const paste = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
      paste.split('').forEach((ch, j) => {
        if (otpBoxes[i + j]) otpBoxes[i + j].value = ch;
      });
      combineOtp();
      e.preventDefault();
    });
  });

  function combineOtp() {
    const combined = document.getElementById('otp-combined');
    if (combined) combined.value = [...otpBoxes].map(b => b.value).join('');
  }

  // OTP form submit → if valid go to reset view (demo client-side flow)
  const otpForm = document.getElementById('otpForm');
  if (otpForm) {
    otpForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      combineOtp();
      const combined = document.getElementById('otp-combined');
      if (!combined || combined.value.length < 6) {
        alert('Please enter all 6 digits.');
        return;
      }
      const btn = otpForm.querySelector('button[type="submit"]');
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>&nbsp; Verifying…';
      btn.disabled = true;

      try {
        const resp = await fetch('/verify_otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            email: document.getElementById('otp-email-hidden').value,
            otp: combined.value
          })
        });
        const data = await resp.json();
        if (data.success) {
          const rEmail = document.getElementById('reset-email-hidden');
          if (rEmail) rEmail.value = document.getElementById('otp-email-hidden').value;
          showView('reset');
        } else {
          btn.innerHTML = orig;
          btn.disabled = false;
          otpBoxes.forEach(b => { b.value = ''; b.style.borderColor = 'var(--err)'; });
          otpBoxes[0].focus();
          setTimeout(() => otpBoxes.forEach(b => b.style.borderColor = ''), 2000);
        }
      } catch {
        btn.innerHTML = orig;
        btn.disabled = false;
      }
    });
  }

  // Resend OTP
  const resendBtn = document.getElementById('resendOtp');
  if (resendBtn) {
    resendBtn.addEventListener('click', async () => {
      const email = document.getElementById('otp-email-hidden')?.value;
      if (!email) return;
      resendBtn.textContent = 'Sending…';
      try {
        await fetch('/forgot_password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ email })
        });
        resendBtn.textContent = 'Sent!';
        setTimeout(() => resendBtn.textContent = 'Resend OTP', 3000);
      } catch {
        resendBtn.textContent = 'Resend OTP';
      }
    });
  }

  // ── FLASH AUTO-DISMISS ────────────────────────────────────────────
  setTimeout(() => {
    const fc = document.querySelector('.flash-container');
    if (fc) {
      fc.style.transition = 'opacity 0.5s ease';
      fc.style.opacity = '0';
      setTimeout(() => fc.remove(), 500);
    }
  }, 4500);

  // ── ADD RESOURCE: Centralised disables department ─────────────────
  const resType = document.getElementById('resourceType');
  const deptSel = document.getElementById('departmentId');
  if (resType && deptSel) {
    resType.addEventListener('change', function () {
      const central = this.value === 'Centralised Facility';
      deptSel.disabled = central;
      deptSel.required = !central;
      deptSel.style.opacity = central ? '0.4' : '1';
      deptSel.style.cursor  = central ? 'not-allowed' : 'pointer';
      if (central) deptSel.value = '';
    });
  }

});
