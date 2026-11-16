<template>
  <div class="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-aquamarine-exposure py-5">
    <div class="col-12 col-sm-10 col-md-8 col-lg-6 col-xl-5 col-xxl-4 px-3">
      <!-- Exposure Ring: Translucent layer fixes the harsh color vibration -->
      <div class="exposure-shield p-2 rounded-4 shadow-lg">
        <div class="card border-0 rounded-4 overflow-hidden shadow-sm">
          
          <!-- Sharp Black Layout Block -->
          <div class="card-body p-4 p-sm-5 bg-black">
            <div class="text-center mb-5">
              <h1 class="h2 fw-black text-white tracking-tight mb-2">
                Examination Portal
              </h1>
              <p class="text-light-50 small text-uppercase tracking-wider">
                System Designed to control Exams
              </p>
            </div>

            <!-- Crisp Interface Controls -->
            <div class="d-grid gap-3 col-12 mx-auto">
              <RouterLink to="/login" class="text-decoration-none">
                <button type="button" class="btn btn-light btn-lg w-100 py-2.5 fw-bold sharp-action">
                  Login to Account
                </button>
              </RouterLink>

              <RouterLink to="/register" class="text-decoration-none">
                <button type="button" class="btn btn-outline-light btn-lg w-100 py-2.5 fw-semibold sharp-secondary">
                  Create Account
                </button>
              </RouterLink>
            </div>
            
            <div class="text-center mt-5 pt-3 border-dark border-top">
              <span class="text-light-50 small font-monospace">© Ashutosh Khatiwada & co.
                <br> All rights reserved</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* High-Exposure Crisp Aquamarine Backdrop */
.bg-aquamarine-exposure {
  background: radial-gradient(circle at top left, #a6ffea 0%, #7fffd4 50%, #5ee6bd 100%);
}

.fw-black {
  font-weight: 900;
  letter-spacing: -0.5px;
}

/* Translucent Exposure Shield (Creates the blend transition) */
.exposure-shield {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

/* Text transparency levels */
.text-light-50 {
  color: rgba(255, 255, 255, 0.5) !important;
}

/* High Sharpness UI Control Elements */
.sharp-action {
  border-radius: 6px;
  background-color: #ffffff;
  color: #000000;
  border: none;
  transition: all 0.15s ease-in-out;
}
.sharp-action:hover {
  background-color: #e6e6e6;
  transform: translateY(-1px);
}

.sharp-secondary {
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  transition: all 0.15s ease-in-out;
}
.sharp-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.6);
}
</style>
